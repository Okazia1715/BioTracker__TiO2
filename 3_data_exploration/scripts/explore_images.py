"""
This script helps you quickly understand what the histology images look like.

It compares two folders:
- the original images (raw)
- the processed images (inverted + contrast 1.2)

It saves a few simple outputs:
- random sample grids from both folders
- a short size/readability report for both folders
- pixel intensity histograms (raw vs processed)
- a short list of potentially odd images (very low contrast / near-uniform)

All outputs are saved to `3_data_exploration/`.
"""

from pathlib import Path
import random
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image, UnidentifiedImageError


# -----------------------------
# Project root (auto)
# -----------------------------
ROOT = (
    Path(__file__).resolve().parents[2]
)  # scripts -> 3_data_exploration -> project root

# -----------------------------
# CONFIG (edit if needed)
# -----------------------------
RAW_DIR = ROOT / "1_datasets" / "Colon_Benign_Tissue"
PROC_DIR = ROOT / "2_data_preparation" / "Colon_Benign_Tissue_invert_contrast1p2"
OUT_DIR = ROOT / "3_data_exploration"
# -----------------------------

OUT_DIR.mkdir(parents=True, exist_ok=True)

IMG_EXTS = {".jpg", ".jpeg", ".png", ".tif", ".tiff"}


def list_images(folder: Path):
    return sorted(
        [p for p in folder.rglob("*") if p.is_file() and p.suffix.lower() in IMG_EXTS]
    )


def load_rgb(path: Path) -> np.ndarray:
    im = Image.open(path).convert("RGB")
    return np.array(im, dtype=np.uint8)


def image_stats(arr: np.ndarray):
    gray = (0.299 * arr[..., 0] + 0.587 * arr[..., 1] + 0.114 * arr[..., 2]).astype(
        np.float32
    )
    return {
        "h": arr.shape[0],
        "w": arr.shape[1],
        "mean_intensity": float(gray.mean()),
        "std_intensity": float(gray.std()),
        "min_intensity": float(gray.min()),
        "max_intensity": float(gray.max()),
    }


def save_sample_grid(images, title, out_path, n=12, cols=4):
    n = min(n, len(images))
    picks = random.sample(images, n)

    rows = int(np.ceil(n / cols))
    plt.figure(figsize=(cols * 3.2, rows * 3.2))

    for i, p in enumerate(picks, start=1):
        plt.subplot(rows, cols, i)
        try:
            arr = load_rgb(p)
            plt.imshow(arr)
            plt.title(p.name, fontsize=8)
            plt.axis("off")
        except (UnidentifiedImageError, OSError, ValueError):
            plt.text(0.5, 0.5, f"Could not open:\n{p.name}", ha="center", va="center")
            plt.axis("off")

    plt.suptitle(title, fontsize=14)
    plt.tight_layout()
    plt.savefig(out_path, dpi=200)
    plt.close()


def save_size_report(folder: Path, images, out_path, sample_limit=500):
    sizes = {}
    unreadable = 0
    checked = 0

    subset = (
        images if len(images) <= sample_limit else random.sample(images, sample_limit)
    )

    for p in subset:
        try:
            with Image.open(p) as im:
                im = im.convert("RGB")
                sizes[im.size] = sizes.get(im.size, 0) + 1
                checked += 1
        except (UnidentifiedImageError, OSError, ValueError):
            unreadable += 1

    lines = []
    lines.append(f"Folder: {folder.resolve()}")
    lines.append(f"Checked images: {checked}")
    lines.append(f"Unreadable/corrupted images: {unreadable}")
    lines.append("Image size counts (W x H):")
    for (w, h), c in sorted(sizes.items(), key=lambda x: -x[1]):
        lines.append(f"  {w} x {h}: {c}")

    out_path.write_text("\n".join(lines), encoding="utf-8")


def save_histograms(raw_images, proc_images, out_path_png, n=80):
    """
    Compare pixel intensity distributions between raw and processed folders.
    We sample up to n images from each folder.
    """
    n_raw = min(n, len(raw_images))
    n_proc = min(n, len(proc_images))

    raw_picks = random.sample(raw_images, n_raw)
    proc_picks = random.sample(proc_images, n_proc)

    raw_vals = []
    proc_vals = []

    for p in raw_picks:
        try:
            arr = load_rgb(p)
            gray = (
                0.299 * arr[..., 0] + 0.587 * arr[..., 1] + 0.114 * arr[..., 2]
            ).astype(np.uint8)
            raw_vals.append(gray.ravel())
        except (UnidentifiedImageError, OSError, ValueError):
            continue

    for p in proc_picks:
        try:
            arr = load_rgb(p)
            gray = (
                0.299 * arr[..., 0] + 0.587 * arr[..., 1] + 0.114 * arr[..., 2]
            ).astype(np.uint8)
            proc_vals.append(gray.ravel())
        except (UnidentifiedImageError, OSError, ValueError):
            continue

    if not raw_vals or not proc_vals:
        print("[WARN] Not enough readable images to build histograms.")
        return

    raw_vals = np.concatenate(raw_vals)
    proc_vals = np.concatenate(proc_vals)

    plt.figure(figsize=(10, 5))
    plt.hist(raw_vals, bins=50, alpha=0.6, label="Raw (grayscale)")
    plt.hist(proc_vals, bins=50, alpha=0.6, label="Processed (grayscale)")
    plt.title("Pixel Intensity Distribution (Sampled Images)")
    plt.xlabel("Intensity (0-255)")
    plt.ylabel("Frequency")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_path_png, dpi=200)
    plt.close()


def save_outlier_list(images, out_path, n=300):
    subset = images if len(images) <= n else random.sample(images, n)

    rows = []
    for p in subset:
        try:
            arr = load_rgb(p)
            s = image_stats(arr)
            rows.append(
                (
                    p.as_posix(),
                    s["mean_intensity"],
                    s["std_intensity"],
                    s["min_intensity"],
                    s["max_intensity"],
                )
            )
        except (UnidentifiedImageError, OSError, ValueError):
            continue

    rows_sorted = sorted(rows, key=lambda x: x[2])[:20]

    lines = [
        "Potential low-contrast / near-uniform images (lowest std first):",
        "path, mean, std, min, max",
    ]
    for r in rows_sorted:
        lines.append(f"{r[0]}, {r[1]:.2f}, {r[2]:.2f}, {r[3]:.0f}, {r[4]:.0f}")

    out_path.write_text("\n".join(lines), encoding="utf-8")


def main():
    if not RAW_DIR.exists():
        raise FileNotFoundError(f"RAW_DIR not found: {RAW_DIR.resolve()}")
    if not PROC_DIR.exists():
        raise FileNotFoundError(f"PROC_DIR not found: {PROC_DIR.resolve()}")

    raw_images = list_images(RAW_DIR)
    proc_images = list_images(PROC_DIR)

    if not raw_images:
        raise FileNotFoundError(f"No images found in RAW_DIR: {RAW_DIR.resolve()}")
    if not proc_images:
        raise FileNotFoundError(f"No images found in PROC_DIR: {PROC_DIR.resolve()}")

    random.seed(42)

    # Save path summary so you never mix folders again
    (OUT_DIR / "paths_used.txt").write_text(
        f"RAW_DIR:  {RAW_DIR.resolve()}\nPROC_DIR: {PROC_DIR.resolve()}\n",
        encoding="utf-8",
    )

    # 1) Visual sanity checks
    save_sample_grid(
        raw_images,
        title="Random Samples (RAW folder)",
        out_path=OUT_DIR / "samples_raw.png",
        n=12,
        cols=4,
    )

    save_sample_grid(
        proc_images,
        title="Random Samples (Processed folder: invert + contrast 1.2)",
        out_path=OUT_DIR / "samples_processed.png",
        n=12,
        cols=4,
    )

    # 2) Consistency checks (sizes/readability)
    save_size_report(
        RAW_DIR, raw_images, OUT_DIR / "image_size_report_raw.txt", sample_limit=500
    )
    save_size_report(
        PROC_DIR,
        proc_images,
        OUT_DIR / "image_size_report_processed.txt",
        sample_limit=500,
    )

    # 3) Intensity distributions (raw vs processed)
    save_histograms(
        raw_images,
        proc_images,
        OUT_DIR / "pixel_intensity_histograms_raw_vs_processed.png",
        n=80,
    )

    # 4) Simple outlier lists
    save_outlier_list(raw_images, OUT_DIR / "potential_outliers_raw.txt", n=300)
    save_outlier_list(proc_images, OUT_DIR / "potential_outliers_processed.txt", n=300)

    print("EDA complete. Outputs saved to:", OUT_DIR.resolve())
    print("Created files:")
    for p in sorted(OUT_DIR.glob("*")):
        if p.is_file():
            print(" -", p.name)


if __name__ == "__main__":
    main()
