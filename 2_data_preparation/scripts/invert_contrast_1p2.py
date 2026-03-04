""""

This script preprocesses histology images by:
- inverting pixel intensities
- increasing contrast by a fixed factor (default: 1.2)

The goal is to improve visual characteristics of images before
cell segmentation with Cellpose. Raw images are not modified;
processed images are saved into a separate output directory.
"""

import argparse
from pathlib import Path

import numpy as np
from PIL import Image

def apply_contrast_uint8(img_u8: np.ndarray, factor: float) -> np.ndarray:
    """
    Contrast around mid-gray 128 for uint8 images:
        out = (img - 128) * factor + 128
    """
    x = img_u8.astype(np.float32)
    y = (x - 128.0) * factor + 128.0
    y = np.clip(y, 0, 255).astype(np.uint8)
    return y


def process_image(
    path: Path, out_path: Path, contrast_factor: float, invert: bool
) -> None:
    im = Image.open(path)

    # Convert to RGB to have consistent behavior
    if im.mode not in ("RGB", "L"):
        im = im.convert("RGB")

    arr = np.array(im)

    # Invert intensities
    if invert:
        arr = 255 - arr

    # Apply contrast (per-channel for RGB; same formula works)
    if arr.dtype != np.uint8:
        arr = np.clip(arr, 0, 255).astype(np.uint8)

    arr = apply_contrast_uint8(arr, contrast_factor)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(arr).save(out_path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--in_dir", required=True, type=str, help="Input folder with images"
    )
    ap.add_argument(
        "--out_dir",
        required=True,
        type=str,
        help="Output folder to save processed images",
    )
    ap.add_argument(
        "--contrast",
        default=1.2,
        type=float,
        help="Contrast factor (e.g. 1.2 means +20%)",
    )
    ap.add_argument("--invert", action="store_true", help="Invert image intensities")
    ap.add_argument(
        "--exts",
        default=".png,.jpg,.jpeg,.tif,.tiff",
        type=str,
        help="Comma-separated extensions",
    )
    ap.add_argument(
        "--overwrite", action="store_true", help="Overwrite output if exists"
    )
    args = ap.parse_args()

    in_dir = Path(args.in_dir)
    out_dir = Path(args.out_dir)
    exts = {e.strip().lower() for e in args.exts.split(",") if e.strip()}

    if not in_dir.exists():
        raise FileNotFoundError(f"Input folder not found: {in_dir}")

    paths = [p for p in in_dir.iterdir() if p.is_file() and p.suffix.lower() in exts]
    paths = sorted(paths)

    if not paths:
        print(f"[WARN] No images found in {in_dir} with extensions {sorted(exts)}")
        return

    n_done = 0
    n_skip = 0

    for p in paths:
        out_path = out_dir / p.name
        if out_path.exists() and not args.overwrite:
            n_skip += 1
            continue
        process_image(p, out_path, contrast_factor=args.contrast, invert=args.invert)
        n_done += 1

    print(f"[INFO] Input : {in_dir}")
    print(f"[INFO] Output: {out_dir}")
    print(f"[INFO] Contrast factor: {args.contrast}")
    print(f"[INFO] Invert: {args.invert}")
    print(f"[INFO] Done: {n_done}, skipped: {n_skip}")


if __name__ == "__main__":
    main()
