# Machine-Learning–Based Analysis of Nanoparticle Accumulation

This repository contains a computational pipeline for microscopy image
analysis with a focus on adipocyte segmentation and nanoparticle localization.
The project combines custom Cellpose models with a desktop GUI to enable
reproducible batch processing without direct code usage.

The pipeline supports exploratory and quantitative studies where manual image
analysis is time-consuming and difficult to scale. By integrating machine
learning segmentation with automated particle analysis, the project provides a
consistent framework for extracting interpretable metrics.

---

## Project overview

The workflow consists of three main stages:

1. Cell segmentation using a custom-trained Cellpose model
2. Particle handling:
   - experimental particle maps (`*_particles.tif`) with LoG spot detection
   - synthetic particles with two placement regimes (random vs accumulation)
3. Quantitative analysis and visualization:
   - standardized exports
   - per-image statistics (synthetic mode)
   - summary plots comparing both groups

All steps are integrated into a desktop application (`app.py`) that can run
folder-level analysis with fixed, logged parameters.

---

## Findings Summary

The analysis demonstrates that the pipeline can detect spatial bias in
particle localization under controlled synthetic conditions.

When accumulation bias is applied (5× inside cells), quantitative
metrics consistently reflect:

- Increased in-cell particle counts
- Decreased distance to boundary
- Higher cluster formation

These results confirm that the segmentation + classification pipeline
operates consistently and reproducibly.

However, biological conclusions remain provisional due to the absence
of real nanoparticle ground-truth validation.

---

## Repository structure (example)

```text

├── README.md
├── app.py
├── models/
│   ├── colon1/
│   ├── colon2/
│   ├── colon3/
│   ├── colon4/
│   └── colon5/
├── docs/
│   ├── overview.md
│   ├── non_technical_summary.md
│   ├── gui_app.md
│   ├── pipeline.md
│   ├── training.md
│   ├── technical_analysis.md
│   ├── reproducibility_guidance.md
│   └── setup.md
├── results/
│   ├── split_assignment.csv
│   ├── accumulation/
│   │   ├── stats_per_image.csv
│   │   ├── masks/
│   │   ├── overlays/
│   │   └── particles/
│   ├── random/
│   │   ├── stats_per_image.csv
│   │   ├── masks/
│   │   ├── overlays/
│   │   └── particles/
│   └── plots/

```

---

## Key features

- Custom Cellpose model adapted to gastrointestinal adipocyte morphology
- Human-in-the-loop iterative refinement (colon1 → colon5)
- Batch processing of RGB PNG microscopy images
- Optional experimental particle maps with LoG spot detection
- Synthetic particle generation with no-overlap constraint
- Automatic random split into two synthetic conditions:
  - random placement
  - accumulation placement (5× bias inside cells)
- Export of masks, particle maps, overlays
- Per-image statistics and comparative plots for both groups
- GUI suitable for non-programmers

---

## Getting started

1. Install dependencies from `requirements.txt`
2. Run the application:

```bash
python app.py
```

1. Select:
   - input image folder
   - trained model path
   - output directory
   - (optional) particle maps folder
2. Set:
   - diameter (or Auto)
   - GPU option
   - number of synthetic particles
3. Run batch processing

---

## Outputs

If synthetic particles are enabled, results include:

- Two subfolders: `random/` and `accumulation/`
- `split_assignment.csv` recording image-to-group mapping
- `stats_per_image.csv` in both subfolders
- `plots/` with summary figures comparing both conditions

---

## Scope and limitations

This tool is research-oriented and optimized for the tissue types and imaging
settings used during development. Applying it to new datasets may require
parameter tuning or additional model training.

---

## Dataset Availability

Due to GitHub repository size limitations, only a small subset of the
images used in this project is included in this repository.

Specifically, the first **10 images** from each dataset used in the
analysis are stored locally for demonstration and reproducibility:

- `raw`
- `invert_contrast1p2`
- `results`

These example images allow users to run the pipeline, inspect the
outputs, and reproduce the workflow without downloading the full dataset.

The complete dataset can be obtained from Kaggle:

[Colon Microscopy Dataset for Segmentation (Kaggle)](https://www.kaggle.com/datasets/alonaniechvieieva/colon-microscopy-dataset-for-segmentation)

When the repository is viewed through the GitHub web interface,
the number of files displayed in dataset folders may appear smaller
than the full dataset used during development.

To reproduce the full analysis workflow and experiments, download
the dataset from Kaggle and place the images into the appropriate
directories according to the repository structure described above.

This approach keeps the repository within GitHub size limits while
ensuring that the entire workflow remains fully reproducible.
