"""
BioTracker_TiO2

What it does
- Select folder with RGB PNG images
- Select trained Cellpose model file (custom .pth path)
- Optionally select folder with existing particle maps (*_particles.tif)
- If no particle maps: generate synthetic fluorescent-like nanoparticles
  * user-defined counts: small + big per image
  * auto-split ~50/50 into:
      - out_dir/random        -> particles sampled uniformly
      - out_dir/accumulation  -> particles sampled with 5x bias inside cells
- Run Cellpose segmentation to get cell masks
- Save outputs:
  * masks (tif)
  * particle map used/generated (tif)
  * overlay PNG (colored masks + particle dots)
  * split_assignment.csv (if generated)
  * stats_per_image.csv (per subfolder)
  * plots/*.png (summary plots across both subfolders)

Notes about existing particle maps
- Existing particle maps (*_particles.tif) are not fully specified, so spot detection is done
  with a generic LoG (blob_log) method.
"""

from __future__ import annotations

import csv
import inspect
import threading
import traceback
import time
from pathlib import Path
from typing import Callable, Any

import cv2
import numpy as np
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

import matplotlib.pyplot as plt
import tifffile as tiff
from cellpose import models, core
from skimage import io, color, exposure
from skimage.color import label2rgb
from skimage.feature import blob_log


# -----------------------------
# CONFIG for extra stats
# -----------------------------
CLUSTER_EPS_PX = 6  # dilation radius for clustering (pixels)
NEAR_BOUNDARY_PX = 2.0  # "near boundary" threshold (pixels)


# -----------------------------
# Utility: safe image loading
# -----------------------------
def load_rgb_png(path: Path) -> np.ndarray:
    """Load an RGB PNG as uint8 array (H, W, 3)."""
    img = io.imread(str(path))
    if img.ndim == 2:
        img = np.stack([img] * 3, axis=-1)
    if img.shape[-1] == 4:
        img = img[..., :3]
    if img.dtype != np.uint8:
        img = exposure.rescale_intensity(img, out_range=(0, 255)).astype(np.uint8)
    return img


def ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


# -----------------------------
# Cellpose eval: pass only supported kwargs
# -----------------------------
def _supported_kwargs(func: Any) -> set[str]:
    try:
        sig = inspect.signature(func)
        return {k for k in sig.parameters.keys() if k not in ("self",)}
    except Exception:
        return set()


def cellpose_eval(
    model: models.CellposeModel,
    img: np.ndarray,
    *,
    channels: list[int],
    diameter: float | None,
    prefer_kwargs: dict[str, Any] | None = None,
) -> tuple[np.ndarray, Any, Any]:
    """
    Call model.eval with only the kwargs supported by the installed Cellpose version.
    prefer_kwargs: desired args (e.g., augment=False), filtered by signature.
    """
    kw: dict[str, Any] = {}
    if prefer_kwargs:
        kw.update(prefer_kwargs)

    kw["channels"] = channels
    kw["diameter"] = diameter

    allowed = _supported_kwargs(model.eval)
    kw = {k: v for k, v in kw.items() if k in allowed}

    return model.eval(img, **kw)


# -----------------------------
# Diameter estimation (no size_model needed)
# -----------------------------
def estimate_diameter_from_masks(
    masks: np.ndarray,
    fallback: float = 250.0,
    min_area_px: int = 50,
    p_low: float = 10.0,
    p_high: float = 90.0,
    clip_low: float = 150.0,
    clip_high: float = 350.0,
) -> float:
    """
    Estimate representative cell diameter from instance masks.
    area -> equivalent-circle diameter: d = 2 * sqrt(area / pi)
    """
    if masks.size == 0:
        return float(fallback)

    m = masks.astype(np.int32, copy=False)
    n = int(m.max())
    if n <= 0:
        return float(fallback)

    areas = np.bincount(m.ravel(), minlength=n + 1)[1:]  # skip 0
    areas = areas[areas >= int(min_area_px)]
    if areas.size == 0:
        return float(fallback)

    diams = 2.0 * np.sqrt(areas.astype(np.float32) / np.pi)

    lo = float(np.percentile(diams, p_low))
    hi = float(np.percentile(diams, p_high))
    diams = diams[(diams >= lo) & (diams <= hi)]
    if diams.size == 0:
        return float(fallback)

    est = float(np.median(diams))
    if not np.isfinite(est) or est <= 0:
        return float(fallback)

    return float(np.clip(est, clip_low, clip_high))


# -----------------------------
# Particles: synthetic fluorescent spots
# -----------------------------
def gaussian_spot_kernel(diameter_px: int) -> np.ndarray:
    """Create a small Gaussian-like kernel approximating a fluorescent spot."""
    r = max(1, diameter_px // 2)
    sigma = diameter_px / 3.0
    ax = np.arange(-r, r + 1, dtype=np.float32)
    xx, yy = np.meshgrid(ax, ax)
    kern = np.exp(-(xx**2 + yy**2) / (2 * sigma**2))
    kern /= kern.max() + 1e-8
    return kern


def place_spot(
    img_float: np.ndarray,
    y: int,
    x: int,
    kernel: np.ndarray,
    peak: float = 1.0,
) -> None:
    """Add kernel-centered spot into img_float at (y, x)."""
    kh, kw = kernel.shape
    r_y = kh // 2
    r_x = kw // 2

    y0 = y - r_y
    x0 = x - r_x
    y1 = y0 + kh
    x1 = x0 + kw

    H, W = img_float.shape
    yy0 = max(0, y0)
    xx0 = max(0, x0)
    yy1 = min(H, y1)
    xx1 = min(W, x1)

    ky0 = yy0 - y0
    kx0 = xx0 - x0
    ky1 = ky0 + (yy1 - yy0)
    kx1 = kx0 + (xx1 - xx0)

    img_float[yy0:yy1, xx0:xx1] += peak * kernel[ky0:ky1, kx0:kx1]


def sample_positions_no_overlap(
    mask_in_cells: np.ndarray,
    n: int,
    diameter_px: int,
    bias_inside: float,
    rng: np.random.Generator,
    existing_centers: list[tuple[int, int, int]],
    max_tries: int = 20000,
) -> list[tuple[int, int, int]]:
    """
    Sample particle centers with inside/outside bias and enforce no overlap.
    Returns list of (y, x, diameter_px).
    """
    H, W = mask_in_cells.shape
    r = max(1, diameter_px // 2)

    valid = np.zeros((H, W), dtype=bool)
    if H > 2 * r and W > 2 * r:
        valid[r : H - r, r : W - r] = True

    inside = valid & mask_in_cells
    outside = valid & (~mask_in_cells)
    inside_coords = np.argwhere(inside)
    outside_coords = np.argwhere(outside)

    if inside_coords.size == 0 and outside_coords.size == 0:
        return []

    w_inside = bias_inside if inside_coords.size > 0 else 0.0
    w_outside = 1.0 if outside_coords.size > 0 else 0.0

    if w_inside == 0.0 and w_outside == 0.0:
        all_coords = np.argwhere(valid)
        inside_coords = all_coords
        outside_coords = all_coords
        w_inside, w_outside = 1.0, 1.0

    chosen: list[tuple[int, int, int]] = []

    def overlaps(y_: int, x_: int, d_: int) -> bool:
        rr = max(1, d_ // 2)
        for yy, xx, dd in existing_centers + chosen:
            r2 = max(1, dd // 2)
            min_dist = rr + r2
            if (y_ - yy) * (y_ - yy) + (x_ - xx) * (x_ - xx) < (min_dist * min_dist):
                return True
        return False

    tries = 0
    while len(chosen) < n and tries < max_tries:
        tries += 1
        p_inside = w_inside / (w_inside + w_outside + 1e-12)
        use_inside = rng.random() < p_inside

        pool = (
            inside_coords if use_inside and inside_coords.size > 0 else outside_coords
        )
        if pool.size == 0:
            pool = inside_coords if inside_coords.size > 0 else outside_coords
        if pool.size == 0:
            break

        idx = int(rng.integers(0, len(pool)))
        y, x = pool[idx]
        yy = int(y)
        xx = int(x)

        if not overlaps(yy, xx, diameter_px):
            chosen.append((yy, xx, diameter_px))

    return chosen


def generate_synthetic_particles(
    masks: np.ndarray,
    mode: str,
    n_small: int,
    n_big: int,
    small_d: int = 3,
    big_d: int = 5,
    seed: int | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Generate a synthetic particle map (uint8) and centers (N,2) (y,x).

    mode:
    - "random": uniform sampling inside/outside (bias=1)
    - "accumulation": 5x bias inside cells
    """
    H, W = masks.shape
    in_cells = masks > 0
    rng = np.random.default_rng(seed)

    spots = np.zeros((H, W), dtype=np.float32)
    centers_full: list[tuple[int, int, int]] = []

    k_small = gaussian_spot_kernel(small_d)
    k_big = gaussian_spot_kernel(big_d)

    bias = 5.0 if mode == "accumulation" else 1.0

    small = sample_positions_no_overlap(
        in_cells, n_small, small_d, bias, rng, centers_full
    )
    centers_full.extend(small)
    big = sample_positions_no_overlap(in_cells, n_big, big_d, bias, rng, centers_full)
    centers_full.extend(big)

    for y, x, d in centers_full:
        peak = float(rng.uniform(0.75, 1.0))
        if d == small_d:
            place_spot(spots, y, x, k_small, peak=peak)
        else:
            place_spot(spots, y, x, k_big, peak=peak)

    if spots.max() > 0:
        spots = spots / spots.max()

    particle_u8 = (spots * 255.0).clip(0, 255).astype(np.uint8)
    centers_yx = np.array([(y, x) for (y, x, _d) in centers_full], dtype=int)
    return particle_u8, centers_yx


# -----------------------------
# Existing particle map -> detect particles
# -----------------------------
def load_particle_tif_any(path: Path) -> np.ndarray:
    """
    Load particle tif robustly. If multi-page/multi-channel, take the first 2D plane.
    Returns float image normalized to [0,1].
    """
    arr = tiff.imread(str(path))
    arr = np.asarray(arr)

    if arr.ndim == 3:
        if arr.shape[-1] <= 4:
            arr2 = arr[..., :3] if arr.shape[-1] >= 3 else arr[..., 0]
            if arr2.ndim == 3:
                arr2 = (
                    0.299 * arr2[..., 0] + 0.587 * arr2[..., 1] + 0.114 * arr2[..., 2]
                )
            arr = arr2
        else:
            arr = arr[0]
    elif arr.ndim > 3:
        while arr.ndim > 2:
            arr = arr[0]

    arr = arr.astype(np.float32)
    mn = float(arr.min())
    mx = float(arr.max())
    if mx > mn:
        arr = (arr - mn) / (mx - mn)
    else:
        arr = np.zeros_like(arr, dtype=np.float32)
    return arr


def detect_particles_log(p_img_float: np.ndarray) -> np.ndarray:
    """Detect spots using LoG. Returns centers (N, 2) as (y, x)."""
    blobs = blob_log(
        p_img_float,
        min_sigma=0.8,
        max_sigma=2.5,
        num_sigma=10,
        threshold=0.05,
    )
    if blobs.size == 0:
        return np.zeros((0, 2), dtype=int)
    return np.round(blobs[:, :2]).astype(int)


# -----------------------------
# Overlay rendering (Cellpose-like)
# -----------------------------
def make_overlay(
    rgb: np.ndarray, masks: np.ndarray, centers_yx: np.ndarray
) -> np.ndarray:
    """Colored masks blended over image + particle centers as red dots."""
    base = rgb.astype(np.float32) / 255.0
    mask_rgb = label2rgb(
        label=masks,
        image=base,
        bg_label=0,
        alpha=0.45,
        image_alpha=1.0,
        kind="overlay",
    )
    out = (mask_rgb * 255.0).clip(0, 255).astype(np.uint8)

    for y, x in centers_yx:
        cv2.circle(out, (int(x), int(y)), 2, (255, 0, 0), thickness=-1)

    return out


# -----------------------------
# Statistics: background / boundary / inside + clusters + distance-to-boundary
# -----------------------------
def count_clusters_from_centers(
    centers_yx: np.ndarray,
    shape_hw: tuple[int, int],
    eps_px: int = CLUSTER_EPS_PX,
) -> int:
    """
    Fast clustering without sklearn:
    - draw centers as 1px dots
    - dilate with radius eps_px (connect nearby points)
    - count connected components
    """
    if centers_yx.size == 0:
        return 0

    H, W = shape_hw
    img = np.zeros((H, W), dtype=np.uint8)
    ys = centers_yx[:, 0].clip(0, H - 1)
    xs = centers_yx[:, 1].clip(0, W - 1)
    img[ys, xs] = 255

    k = 2 * int(eps_px) + 1
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k))
    dil = cv2.dilate(img, kernel, iterations=1)

    num, _labels = cv2.connectedComponents((dil > 0).astype(np.uint8))
    # connectedComponents counts background as 0, so clusters = num-1
    return max(0, int(num - 1))


def compute_particle_stats(
    centers_yx: np.ndarray, masks: np.ndarray
) -> dict[str, float]:
    """
    Returns per-image stats:
    - n_cells
    - particles_total
    - particles_on_background
    - particles_in_cells_total
    - particles_on_boundary
    - particles_inside_not_boundary
    - mean_particles_per_cell_total
    - mean_particles_on_boundary_per_cell
    - mean_particles_inside_not_boundary_per_cell
    - clusters_count
    - frac_near_boundary_le_2px (only for in-cell particles)
    - mean_distance_to_boundary_px (only for in-cell particles)
    """
    H, W = masks.shape
    n_cells = int(masks.max())

    # boundary mask (1px rim)
    cell_bin = (masks > 0).astype(np.uint8)
    kernel3 = np.ones((3, 3), dtype=np.uint8)
    eroded = cv2.erode(cell_bin, kernel3, iterations=1)
    boundary = (cell_bin == 1) & (eroded == 0)

    # distance-to-boundary (pixels) for inside-cell pixels:
    # Make image where interior pixels are 1, boundary/outside are 0
    interior = (cell_bin == 1) & (~boundary)
    dt = cv2.distanceTransform(interior.astype(np.uint8), cv2.DIST_L2, 3)

    if centers_yx.size == 0:
        return {
            "n_cells": float(n_cells),
            "particles_total": 0.0,
            "particles_on_background": 0.0,
            "particles_in_cells_total": 0.0,
            "particles_on_boundary": 0.0,
            "particles_inside_not_boundary": 0.0,
            "mean_particles_per_cell_total": 0.0,
            "mean_particles_on_boundary_per_cell": 0.0,
            "mean_particles_inside_not_boundary_per_cell": 0.0,
            "clusters_count": 0.0,
            "frac_near_boundary_le_2px": 0.0,
            "mean_distance_to_boundary_px": 0.0,
        }

    ys = centers_yx[:, 0].clip(0, H - 1)
    xs = centers_yx[:, 1].clip(0, W - 1)
    labels = masks[ys, xs].astype(np.int32)

    on_bg = labels == 0
    in_cells = labels > 0
    on_boundary = in_cells & boundary[ys, xs]
    inside_not_boundary = in_cells & (~boundary[ys, xs])

    particles_total = int(labels.size)
    n_bg = int(np.sum(on_bg))
    n_in_cells = int(np.sum(in_cells))
    n_boundary = int(np.sum(on_boundary))
    n_inside = int(np.sum(inside_not_boundary))

    denom_cells = float(n_cells) if n_cells > 0 else 0.0
    mean_per_cell_total = (n_in_cells / denom_cells) if denom_cells > 0 else 0.0
    mean_boundary_per_cell = (n_boundary / denom_cells) if denom_cells > 0 else 0.0
    mean_inside_per_cell = (n_inside / denom_cells) if denom_cells > 0 else 0.0

    # clusters (use all centers, including background, as "on photo")
    clusters = count_clusters_from_centers(centers_yx, (H, W), eps_px=CLUSTER_EPS_PX)

    # distances to boundary for in-cell particles only
    dist_in = (
        dt[ys[in_cells], xs[in_cells]]
        if np.any(in_cells)
        else np.array([], dtype=np.float32)
    )
    if dist_in.size > 0:
        mean_dist = float(np.mean(dist_in))
        frac_near = float(np.mean(dist_in <= float(NEAR_BOUNDARY_PX)))
    else:
        mean_dist = 0.0
        frac_near = 0.0

    return {
        "n_cells": float(n_cells),
        "particles_total": float(particles_total),
        "particles_on_background": float(n_bg),
        "particles_in_cells_total": float(n_in_cells),
        "particles_on_boundary": float(n_boundary),
        "particles_inside_not_boundary": float(n_inside),
        "mean_particles_per_cell_total": float(mean_per_cell_total),
        "mean_particles_on_boundary_per_cell": float(mean_boundary_per_cell),
        "mean_particles_inside_not_boundary_per_cell": float(mean_inside_per_cell),
        "clusters_count": float(clusters),
        "frac_near_boundary_le_2px": float(frac_near),
        "mean_distance_to_boundary_px": float(mean_dist),
    }


def write_stats_csv(path: Path, rows: list[dict[str, float | str]]) -> None:
    if not rows:
        return
    ensure_dir(path.parent)
    headers = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=headers)
        w.writeheader()
        for r in rows:
            w.writerow(r)


def save_plots_two_groups(
    out_dir: Path, stats_random: list[dict], stats_acc: list[dict]
) -> None:
    """
    Create figures, each contains BOTH groups (random vs accumulation) in different colors.
    One point = one image.
    """
    plots_dir = out_dir / "plots"
    ensure_dir(plots_dir)

    stats_random = sorted(stats_random, key=lambda d: str(d.get("image", "")))
    stats_acc = sorted(stats_acc, key=lambda d: str(d.get("image", "")))

    def plot_metric(
        metric: str, title: str, fname: str, ylabel: str | None = None
    ) -> None:
        plt.figure(figsize=(11, 5))

        xr = np.arange(len(stats_random))
        xa = np.arange(len(stats_acc))

        yr = np.array([float(d.get(metric, 0.0)) for d in stats_random], dtype=float)
        ya = np.array([float(d.get(metric, 0.0)) for d in stats_acc], dtype=float)

        plt.plot(xr, yr, marker="o", linestyle="None", label="random")
        plt.plot(
            xa, ya, marker="o", linestyle="None", label="accumulation (5x in cells)"
        )

        plt.title(title)
        plt.xlabel("Image index (within each subgroup, sorted by name)")
        plt.ylabel(ylabel if ylabel else metric)
        plt.legend()
        plt.tight_layout()
        plt.savefig(str(plots_dir / fname), dpi=200)
        plt.close()

    # Existing 6 plots
    plot_metric(
        "particles_on_background",
        "Particles on BACKGROUND (per image)",
        "01_particles_on_background.png",
        ylabel="count",
    )
    plot_metric(
        "mean_particles_per_cell_total",
        "Mean particles per CELL (boundary + inside), per image",
        "02_mean_particles_per_cell_total.png",
        ylabel="particles / cell",
    )
    plot_metric(
        "particles_in_cells_total",
        "Particles IN CELLS total (boundary + inside), per image",
        "03_particles_in_cells_total.png",
        ylabel="count",
    )
    plot_metric(
        "particles_on_boundary",
        "Particles on CELL BOUNDARY, per image",
        "04_particles_on_boundary.png",
        ylabel="count",
    )
    plot_metric(
        "particles_inside_not_boundary",
        "Particles INSIDE cell (NOT boundary), per image",
        "05_particles_inside_not_boundary.png",
        ylabel="count",
    )
    plot_metric(
        "mean_particles_inside_not_boundary_per_cell",
        "Mean particles inside cell (NOT boundary) per CELL, per image",
        "06_mean_particles_inside_not_boundary_per_cell.png",
        ylabel="particles / cell",
    )

    # NEW plots requested
    plot_metric(
        "clusters_count",
        f"Number of CLUSTERS per image (eps={CLUSTER_EPS_PX}px)",
        "07_clusters_count.png",
        ylabel="clusters",
    )
    plot_metric(
        "frac_near_boundary_le_2px",
        f"Fraction of in-cell particles within {NEAR_BOUNDARY_PX:g}px of boundary (per image)",
        "08_fraction_near_boundary.png",
        ylabel="fraction (0–1)",
    )
    plot_metric(
        "mean_distance_to_boundary_px",
        "Mean distance to cell boundary for in-cell particles (per image)",
        "09_mean_distance_to_boundary.png",
        ylabel="pixels",
    )


# -----------------------------
# Core processing
# -----------------------------
ProgressCB = Callable[[int, int, str], None]
LogCB = Callable[[str], None]


def _prepare_out_dirs(base_out: Path) -> tuple[Path, Path, Path]:
    masks_dir = base_out / "masks"
    parts_dir = base_out / "particles"
    ovl_dir = base_out / "overlays"
    ensure_dir(masks_dir)
    ensure_dir(parts_dir)
    ensure_dir(ovl_dir)
    return masks_dir, parts_dir, ovl_dir


def run_batch(
    images_dir: Path,
    model_path: Path,
    out_dir: Path,
    have_particles: bool,
    particles_dir: Path | None,
    diameter: float,
    use_gpu: bool,
    n_small: int,
    n_big: int,
    progress_cb: ProgressCB | None = None,
    log_cb: LogCB | None = None,
) -> None:
    """
    Run Cellpose on a folder and save masks/particles/overlays.
    If have_particles=False:
      randomly split images ~50/50 into:
        out_dir/random (mode=random)
        out_dir/accumulation (mode=accumulation)
      plus build stats + plots for both subfolders.
    """
    ensure_dir(out_dir)

    gpu_ok = core.use_gpu()
    if log_cb:
        log_cb(f"GPU available (cellpose.core.use_gpu): {gpu_ok}")
    if use_gpu and not gpu_ok:
        use_gpu = False
        if log_cb:
            log_cb("GPU requested, but not available -> switching to CPU.")

    if log_cb:
        log_cb(f"Loading Cellpose model: {model_path}")
    model = models.CellposeModel(pretrained_model=str(model_path), gpu=use_gpu)

    pngs = sorted([p for p in images_dir.glob("*.png") if p.is_file()])
    if not pngs:
        raise FileNotFoundError(f"No PNG files found in: {images_dir}")

    mode_for_image: dict[str, str] = {}
    if not have_particles:
        rng = np.random.default_rng()
        perm = rng.permutation(len(pngs))
        half = len(pngs) // 2

        idx_random = set(perm[:half].tolist())
        for i, p in enumerate(pngs):
            mode_for_image[p.name] = "random" if i in idx_random else "accumulation"

        assign_path = out_dir / "split_assignment.csv"
        with assign_path.open("w", encoding="utf-8") as f:
            f.write("image,mode\n")
            for p in pngs:
                f.write(f"{p.name},{mode_for_image[p.name]}\n")

        if log_cb:
            n_r = sum(1 for v in mode_for_image.values() if v == "random")
            n_a = len(mode_for_image) - n_r
            log_cb(
                f"Auto-split enabled: random={n_r}, accumulation={n_a} "
                f"(saved: {assign_path.name})"
            )

    diam_used = float(diameter) if (diameter and diameter > 0) else None
    if diam_used is None:
        if log_cb:
            log_cb("Auto diameter: segmenting the first image to estimate diameter...")

        rgb0 = load_rgb_png(pngs[0])
        gray0 = color.rgb2gray(rgb0).astype(np.float32)

        masks0, _f0, _s0 = cellpose_eval(
            model,
            gray0,
            channels=[0, 0],
            diameter=None,
            prefer_kwargs={"augment": False, "batch_size": 1},
        )
        masks0 = masks0.astype(np.int32, copy=False)
        diam_used = estimate_diameter_from_masks(masks0, fallback=250.0)

        if log_cb:
            log_cb(
                f"Estimated diameter from masks = {diam_used:g}px (reused for all images)"
            )

    if have_particles:
        masks_dir, parts_dir, ovl_dir = _prepare_out_dirs(out_dir)
        out_dirs_by_mode = {"with_particles": (masks_dir, parts_dir, ovl_dir)}
    else:
        masks_r, parts_r, ovl_r = _prepare_out_dirs(out_dir / "random")
        masks_a, parts_a, ovl_a = _prepare_out_dirs(out_dir / "accumulation")
        out_dirs_by_mode = {
            "random": (masks_r, parts_r, ovl_r),
            "accumulation": (masks_a, parts_a, ovl_a),
        }

    stats_rows_random: list[dict[str, float | str]] = []
    stats_rows_acc: list[dict[str, float | str]] = []

    for i, p in enumerate(pngs):
        if progress_cb:
            progress_cb(i, len(pngs), f"Processing {p.name}")

        t0 = time.perf_counter()

        rgb = load_rgb_png(p)
        gray = color.rgb2gray(rgb).astype(np.float32)

        t1 = time.perf_counter()

        masks, _flows, _styles = cellpose_eval(
            model,
            gray,
            channels=[0, 0],
            diameter=diam_used,
            prefer_kwargs={"augment": False, "batch_size": 1},
        )
        masks = masks.astype(np.int32)

        t2 = time.perf_counter()

        if have_particles:
            masks_dir, parts_dir, ovl_dir = out_dirs_by_mode["with_particles"]

            if particles_dir is None:
                raise ValueError("Particles folder is not set.")

            particle_path = particles_dir / f"{p.stem}_particles.tif"
            if not particle_path.exists():
                alt = particles_dir / f"{p.stem}.tif"
                if alt.exists():
                    particle_path = alt
                else:
                    raise FileNotFoundError(
                        f"Particle map not found for {p.name}: expected {particle_path.name}"
                    )

            p_float = load_particle_tif_any(particle_path)
            centers = detect_particles_log(p_float)
            particle_img_u8 = (p_float * 255).astype(np.uint8)
            part_out = parts_dir / f"{p.stem}_particles_used.tif"
            mode_msg = "with_particles"
        else:
            mode = mode_for_image[p.name]
            masks_dir, parts_dir, ovl_dir = out_dirs_by_mode[mode]

            particle_img_u8, centers = generate_synthetic_particles(
                masks=masks,
                mode=mode,
                n_small=int(n_small),
                n_big=int(n_big),
                small_d=3,
                big_d=5,
                seed=None,
            )
            part_out = parts_dir / f"{p.stem}_particles_generated.tif"
            mode_msg = mode

        tiff.imwrite(str(part_out), particle_img_u8.astype(np.uint8))

        mask_out = masks_dir / f"{p.stem}_masks.tif"
        tiff.imwrite(str(mask_out), masks.astype(np.uint16))

        ovl = make_overlay(rgb, masks, centers)
        ovl_out = ovl_dir / f"{p.stem}_overlay.png"
        cv2.imwrite(str(ovl_out), cv2.cvtColor(ovl, cv2.COLOR_RGB2BGR))

        stats = compute_particle_stats(centers, masks)
        stats_row = {"image": p.name, **stats}

        if not have_particles:
            if mode_msg == "random":
                stats_rows_random.append(stats_row)
            elif mode_msg == "accumulation":
                stats_rows_acc.append(stats_row)

        t3 = time.perf_counter()

        if log_cb:
            dmsg = f"AUTO→{diam_used:g}" if diameter <= 0 else f"{diameter:g}"
            log_cb(
                f"{p.name}: mode={mode_msg} | diameter={dmsg} | "
                f"load={(t1 - t0):.3f}s, eval={(t2 - t1):.3f}s, post/save={(t3 - t2):.3f}s"
            )

    if not have_particles:
        stats_path_r = out_dir / "random" / "stats_per_image.csv"
        stats_path_a = out_dir / "accumulation" / "stats_per_image.csv"
        write_stats_csv(stats_path_r, stats_rows_random)
        write_stats_csv(stats_path_a, stats_rows_acc)

        save_plots_two_groups(out_dir, stats_rows_random, stats_rows_acc)

        if log_cb:
            log_cb(f"Saved stats: {stats_path_r}")
            log_cb(f"Saved stats: {stats_path_a}")
            log_cb(f"Saved plots to: {out_dir / 'plots'}")

    if progress_cb:
        progress_cb(len(pngs), len(pngs), "Done")
    if log_cb:
        if have_particles:
            log_cb(f"Saved results to: {out_dir}")
        else:
            log_cb(
                f"Saved results to: {out_dir / 'random'} and {out_dir / 'accumulation'}"
            )


# -----------------------------
# BioTracker_TiO2 GUI
# -----------------------------
class App(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("BioTracker_TiO2")
        self.geometry("780x720")

        self.images_dir = tk.StringVar()
        self.model_path = tk.StringVar()

        self.have_particles = tk.BooleanVar(value=False)
        self.particles_dir = tk.StringVar()

        self.diameter = tk.StringVar(value="250")
        self.use_gpu = tk.BooleanVar(value=True)

        self.n_small = tk.StringVar(value="25")
        self.n_big = tk.StringVar(value="25")

        self.out_dir = tk.StringVar()

        self.worker: threading.Thread | None = None
        self._build()

    def _build(self) -> None:
        pad = {"padx": 10, "pady": 6}
        frm = ttk.Frame(self)
        frm.pack(fill="both", expand=True)

        ttk.Label(frm, text="1) Folder with PNG images:").grid(
            row=0, column=0, sticky="w", **pad
        )
        ttk.Entry(frm, textvariable=self.images_dir, width=72).grid(
            row=1, column=0, sticky="we", **pad
        )
        ttk.Button(frm, text="Browse...", command=self.pick_images_dir).grid(
            row=1, column=1, sticky="e", **pad
        )

        ttk.Label(frm, text="2) Trained Cellpose model file:").grid(
            row=2, column=0, sticky="w", **pad
        )
        ttk.Entry(frm, textvariable=self.model_path, width=72).grid(
            row=3, column=0, sticky="we", **pad
        )
        ttk.Button(frm, text="Browse...", command=self.pick_model_file).grid(
            row=3, column=1, sticky="e", **pad
        )

        ttk.Label(frm, text="3) Output folder (results will be saved here):").grid(
            row=4, column=0, sticky="w", **pad
        )
        ttk.Entry(frm, textvariable=self.out_dir, width=72).grid(
            row=5, column=0, sticky="we", **pad
        )
        ttk.Button(frm, text="Browse...", command=self.pick_out_dir).grid(
            row=5, column=1, sticky="e", **pad
        )

        ttk.Checkbutton(
            frm,
            text="I already have particle maps (*_particles.tif)",
            variable=self.have_particles,
            command=self.toggle_particles_ui,
        ).grid(row=6, column=0, sticky="w", **pad)

        ttk.Label(frm, text="Particle maps folder:").grid(
            row=7, column=0, sticky="w", **pad
        )

        self.ent_particles = ttk.Entry(
            frm, textvariable=self.particles_dir, width=72, state="disabled"
        )
        self.ent_particles.grid(row=8, column=0, sticky="we", **pad)

        self.btn_particles = ttk.Button(
            frm, text="Browse...", command=self.pick_particles_dir, state="disabled"
        )
        self.btn_particles.grid(row=8, column=1, sticky="e", **pad)

        ttk.Label(
            frm,
            text=(
                "If no particle maps: images are auto-split 50/50 into "
                "out_dir/random (random) and out_dir/accumulation (5x inside). "
                "Stats + plots are saved in out_dir/plots."
            ),
            wraplength=720,
        ).grid(row=9, column=0, columnspan=2, sticky="w", **pad)

        pfrm = ttk.Frame(frm)
        pfrm.grid(row=10, column=0, sticky="w", **pad)
        ttk.Label(pfrm, text="Particles per image:").pack(side="left")
        ttk.Label(pfrm, text="small=").pack(side="left", padx=(10, 2))
        ttk.Entry(pfrm, textvariable=self.n_small, width=6).pack(side="left")
        ttk.Label(pfrm, text="big=").pack(side="left", padx=(10, 2))
        ttk.Entry(pfrm, textvariable=self.n_big, width=6).pack(side="left")

        dfrm = ttk.Frame(frm)
        dfrm.grid(row=11, column=0, sticky="w", **pad)
        ttk.Label(dfrm, text="Cell diameter (px):").pack(side="left")
        ttk.Entry(dfrm, textvariable=self.diameter, width=8).pack(side="left", padx=8)
        ttk.Button(dfrm, text="Auto", command=self.set_diameter_auto).pack(
            side="left", padx=6
        )
        ttk.Checkbutton(
            dfrm, text="Use GPU (if available)", variable=self.use_gpu
        ).pack(side="left", padx=14)

        self.btn_run = ttk.Button(frm, text="Run", command=self.on_run)
        self.btn_run.grid(row=12, column=0, sticky="w", **pad)

        self.pb = ttk.Progressbar(
            frm, orient="horizontal", length=540, mode="determinate"
        )
        self.pb.grid(row=13, column=0, sticky="we", **pad)
        self.lbl_status = ttk.Label(frm, text="Idle")
        self.lbl_status.grid(row=13, column=1, sticky="e", **pad)

        ttk.Label(frm, text="Log:").grid(row=14, column=0, sticky="w", **pad)
        self.txt = tk.Text(frm, height=18, width=98)
        self.txt.grid(row=15, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)

        frm.columnconfigure(0, weight=1)
        frm.rowconfigure(15, weight=1)

    def set_diameter_auto(self) -> None:
        self.diameter.set("0")
        self.log("Diameter set to AUTO (0).")

    def toggle_particles_ui(self) -> None:
        if self.have_particles.get():
            self.ent_particles.configure(state="normal")
            self.btn_particles.configure(state="normal")
        else:
            self.ent_particles.configure(state="disabled")
            self.btn_particles.configure(state="disabled")

    def pick_images_dir(self) -> None:
        d = filedialog.askdirectory()
        if d:
            self.images_dir.set(d)
            if not self.out_dir.get():
                self.out_dir.set(str(Path(d) / "cellpose_results"))

    def pick_model_file(self) -> None:
        f = filedialog.askopenfilename(filetypes=[("Model files", "*.*")])
        if f:
            self.model_path.set(f)

    def pick_particles_dir(self) -> None:
        d = filedialog.askdirectory()
        if d:
            self.particles_dir.set(d)

    def pick_out_dir(self) -> None:
        d = filedialog.askdirectory()
        if d:
            self.out_dir.set(d)

    def log(self, s: str) -> None:
        self.txt.insert("end", s + "\n")
        self.txt.see("end")
        self.update_idletasks()

    def set_progress(self, i: int, n: int, status: str) -> None:
        self.pb["maximum"] = max(1, n)
        self.pb["value"] = i
        self.lbl_status.config(text=status)
        self.update_idletasks()

    def validate_inputs(
        self,
    ) -> tuple[Path, Path, Path, bool, Path | None, float, bool, int, int]:
        images_dir = Path(self.images_dir.get().strip())
        model_path = Path(self.model_path.get().strip())

        out_dir_raw = self.out_dir.get().strip()
        out_dir = (
            Path(out_dir_raw) if out_dir_raw else (images_dir / "cellpose_results")
        )

        if not images_dir.exists():
            raise FileNotFoundError("Images folder does not exist.")
        if not model_path.exists():
            raise FileNotFoundError("Model file does not exist.")

        pd_dir: Path | None
        if self.have_particles.get():
            pd_raw = self.particles_dir.get().strip()
            pd_dir = Path(pd_raw)
            if not pd_dir.exists():
                raise FileNotFoundError("Particles folder does not exist.")
        else:
            pd_dir = None

        try:
            diameter = float(self.diameter.get().strip())
        except ValueError:
            diameter = 0.0

        use_gpu = bool(self.use_gpu.get())

        try:
            n_small = int(float(self.n_small.get().strip()))
        except ValueError:
            n_small = 25
        try:
            n_big = int(float(self.n_big.get().strip()))
        except ValueError:
            n_big = 25

        if n_small < 0 or n_big < 0:
            raise ValueError("Particle counts must be >= 0.")

        return (
            images_dir,
            model_path,
            out_dir,
            self.have_particles.get(),
            pd_dir,
            diameter,
            use_gpu,
            n_small,
            n_big,
        )

    def on_run(self) -> None:
        if self.worker is not None and self.worker.is_alive():
            messagebox.showinfo("Busy", "Processing is already running.")
            return

        try:
            args = self.validate_inputs()
        except (FileNotFoundError, ValueError) as e:
            messagebox.showerror("Input error", str(e))
            return

        self.btn_run.configure(state="disabled")
        self.txt.delete("1.0", "end")
        self.set_progress(0, 1, "Starting...")

        def target() -> None:
            try:
                run_batch(
                    images_dir=args[0],
                    model_path=args[1],
                    out_dir=args[2],
                    have_particles=args[3],
                    particles_dir=args[4],
                    diameter=args[5],
                    use_gpu=args[6],
                    n_small=args[7],
                    n_big=args[8],
                    progress_cb=lambda i, n, st: self.after(
                        0, self.set_progress, i, n, st
                    ),
                    log_cb=lambda s: self.after(0, self.log, s),
                )
                self.after(
                    0, messagebox.showinfo, "Done", "Processing finished successfully."
                )
            except Exception as e:  # noqa: BLE001
                err = "".join(traceback.format_exception(type(e), e, e.__traceback__))
                self.after(0, self.log, "ERROR:\n" + err)
                self.after(0, messagebox.showerror, "Error", str(e))
            finally:
                self.after(0, self.btn_run.configure, {"state": "normal"})

        self.worker = threading.Thread(target=target, daemon=True)
        self.worker.start()


if __name__ == "__main__":
    App().mainloop()
