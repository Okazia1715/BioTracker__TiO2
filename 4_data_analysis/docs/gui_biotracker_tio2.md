
# GUI Application for Cell Segmentation and Particle Analysis

## File: `app.py`

This document describes the graphical user interface implemented in `app.py`.
The application provides a desktop front end for a reproducible batch pipeline
that combines:

- Cell segmentation using a custom Cellpose model
- Particle handling (experimental maps or synthetic generation)
- Quantitative metrics per image (synthetic mode)
- Export of masks, particle maps, overlays, and summary plots

The GUI is designed for users without programming experience while keeping all
processing steps transparent.

---

## Purpose and design principles

The application was built with the following goals:

- Accessibility for non-programmers
- Reproducible folder-level processing
- Standardized output structure for downstream analysis
- Visual outputs for quality control (QC)
- Support for experimental and synthetic particle inputs

Long-running computations are executed in a background thread to keep the UI
responsive.

---

## Features

- Folder selection for PNG microscopy images
- Selection of custom-trained Cellpose model
- Optional particle map input
- Synthetic particle generation
- Adjustable number of particles
- Automatic statistical analysis
- Graph generation across subfolders

Processing runs in background threads to keep the interface responsive.

---

## Input data

### Microscopy images

- Input format: RGB PNG (`*.png`)
- Each image is processed independently using identical settings.
- RGB images are converted to grayscale prior to Cellpose inference.

### Cellpose model

- Users provide a trained model path (custom model folder or `.pth` file).
- The model is loaded once and reused for all images in the batch.

### Particle maps (optional)

If experimental particle maps are available, they can be provided as TIFF
files matching image names.

Supported naming:

- `<stem>_particles.tif` (preferred)
- `<stem>.tif` (fallback)

Because experimental maps are not standardized, the application converts each
TIFF to a single 2D float image in `[0, 1]` before spot detection.

---

## GUI controls and parameters

### Output folder

The application writes results to a user-selected output directory. If not
provided, it defaults to `cellpose_results` inside the image folder.

### Diameter

- The user can set a numeric diameter (pixels), or set `0` for auto mode.
- Auto mode estimates a diameter once on the first image, then reuses it for
all images to avoid repeated slow auto-calculation.

Auto estimation is computed from the first segmentation result by converting
cell areas to an equivalent-circle diameter and taking a robust median.

### GPU

- GUI option: "Use GPU (if available)"
- The app checks `cellpose.core.use_gpu()` and falls back to CPU if needed.

This prevents silent failures when CUDA is not configured correctly.

### Particle counts (synthetic mode)

When synthetic particles are used, the user sets:

- number of small particles per image (default 25)
- number of big particles per image (default 25)

Particle sizes are fixed:

- small diameter = 3 px
- big diameter = 5 px

---

## Processing pipeline

For each input image, the following steps are executed:

1. Load RGB PNG and convert to grayscale
2. Segment cells with Cellpose
3. Particle handling:
   - experimental: LoG spot detection on TIFF map
   - synthetic: generate particle map + center coordinates
4. Classify particles relative to the mask:
   - background (outside cells)
   - boundary (on the cell rim)
   - inside (in cell, not on boundary)
5. Export results (masks, particle maps, overlays)
6. If synthetic mode is used:
   - compute per-image statistics
   - generate comparative plots across both synthetic groups

---

## Synthetic particle generation and auto-splitting

If no experimental particle maps are provided, the app auto-splits the image
set approximately 50/50 into two subfolders:

- `random`:
particles sampled uniformly inside/outside cells (no bias)
- `accumulation`:
particles sampled with a 5× higher probability inside cells

The assignment is saved as `split_assignment.csv`.

A no-overlap constraint is enforced during placement based on particle
diameter.

---

## Output structure

### Experimental particle maps provided

```text
output_directory/
├── masks/
├── particles/
└── overlays/
```

### Synthetic particles generated

```text
output_directory/
├── random/
│   ├── masks/
│   ├── particles/
│   ├── overlays/
│   └── stats_per_image.csv
├── accumulation/
│   ├── masks/
│   ├── particles/
│   ├── overlays/
│   └── stats_per_image.csv
├── split_assignment.csv
└── plots/
    ├── 01_particles_on_background.png
    ├── 02_mean_particles_per_cell_total.png
    ├── 03_particles_in_cells_total.png
    ├── 04_particles_on_boundary.png
    ├── 05_particles_inside_not_boundary.png
    ├── 06_mean_particles_inside_not_boundary_per_cell.png
    ├── 07_clusters_count.png
    ├── 08_fraction_near_boundary.png
    └── 09_mean_distance_to_boundary.png
```

---

## Notes on performance

- PNG writing uses OpenCV for faster saving on Windows.
- Diameter auto-estimation runs only once (first image) to keep runtime
reasonable.
- If GPU is enabled and available, Cellpose inference is significantly faster
than CPU for larger images.

---

## Summary

`app.py` encapsulates a complete segmentation + particle analysis workflow in
a reproducible desktop tool. It supports both experimental particle maps and
synthetic simulation scenarios, and produces standardized outputs plus
summary plots for reporting.
