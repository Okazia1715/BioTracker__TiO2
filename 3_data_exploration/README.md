# Data Exploration

This folder contains results of an exploratory analysis of the
histopathological image data used in this project.

The purpose of this step is to understand the structure, consistency,
and visual properties of the images before training a segmentation
model.

No modeling or inference is performed at this stage.

---

## Data Sources

Two datasets were analyzed during exploration:

- Raw images  
  `1_datasets/Colon_Benign_Tissue`

- Processed images (invert + contrast 1.2)  
  `2_data_preparation/Colon_Benign_Tissue_invert_contrast1p2`

The exact paths used during analysis are recorded in:

- `paths_used.txt`

---

## Visual Inspection

### Raw Images

`samples_raw.png` shows random samples from the original dataset.

These images are bright overall and display the typical pink and purple
coloration of H&E-stained histological sections.

### Processed Images

`samples_processed.png` shows random samples after preprocessing.

After inversion and contrast enhancement:

- background regions appear darker
- cellular structures appear brighter
- tissue boundaries become more distinct

This transformation is intentional and designed to support downstream
cell segmentation with Cellpose.

---

## Pixel Intensity Distributions

The following figure compares grayscale pixel intensity distributions
between raw and processed images:

- `pixel_intensity_histograms_raw_vs_processed.png`

Interpretation:

- Raw images are dominated by high-intensity (bright) pixel values
- Processed images show a strong shift toward lower intensity values

This confirms that preprocessing substantially changes the intensity
profile and increases contrast between tissue and background.

---

## Image Consistency Checks

Basic consistency checks were performed on a random subset of images
from each folder.

Results:

- All checked images are readable
- No corrupted files were detected
- All images have the same resolution: 768 × 768 pixels

Detailed reports:

- `image_size_report_raw.txt`
- `image_size_report_processed.txt`

---

## Potential Low-Contrast Images

The following files list images with the lowest grayscale intensity
standard deviation:

- `potential_outliers_raw.txt`
- `potential_outliers_processed.txt`

These images are not corrupted. They typically contain:

- large lumen regions
- more homogeneous tissue areas
- fewer high-contrast structures

They are flagged for awareness only and were not removed from the
dataset.

---

## Summary

This exploratory analysis shows that:

- the dataset is internally consistent
- preprocessing was applied as intended
- no major data quality issues are present

The observed changes in image appearance and intensity distributions
are expected and appropriate for subsequent segmentation experiments.

---

## Dataset Reference

Original dataset:
<https://www.kaggle.com/datasets/biplobdey/lung-and-colon-cancer>

Original publication:
<https://arxiv.org/abs/1912.12142v1>
