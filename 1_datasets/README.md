# Dataset

## Dataset Overview

This project uses a subset of the
**LC25000 – Lung and Colon Cancer Histopathological Images**
dataset.

The original dataset consists of
**25,000 histopathological RGB images**
distributed evenly across **five tissue classes**
(5,000 images per class).
All images are stored in **JPEG format**
with a resolution of **768 × 768 pixels**.

The images were generated from an original collection of
**HIPAA-compliant and validated histopathological sources**
and expanded to 25,000 samples using
data augmentation techniques.

**Original tissue classes:**

1. Lung benign tissue
2. Lung adenocarcinoma
3. Lung squamous cell carcinoma
4. Colon adenocarcinoma
5. Colon benign tissue

> *“All images are de-identified, HIPAA compliant, validated,
> and freely available for download to AI researchers.”*
> — Borkowski et al., 2019

**Kaggle dataset link:**
*[https://www.kaggle.com/datasets/biplobdey/lung-and-colon-cancer]*

**Original publication:**
*[https://arxiv.org/abs/1912.12142v1]*

---

## Dataset Usage in This Project

Although the original dataset contains five tissue classes,
**this project uses only a single subset**:

> **Colon benign tissue**

Only images belonging to this class are included in the
analysis and modeling pipeline.
All other tissue classes are excluded from this project.

---

### GitHub Repository Display Limitations

## Dataset Availability Notice

Due to GitHub repository size limitations, only a subset of the
images is included in this repository.

Specifically, the first **10 images** from each dataset are stored
locally for demonstration and reproducibility purposes:

- `raw`
- `invert_contrast1p2`
- `results`

These example images allow the pipeline to be demonstrated and the
analysis workflow to be reproduced without requiring the full dataset.

The complete dataset can be downloaded from Kaggle:

[Colon Microscopy Dataset for Segmentation (Kaggle)](https://www.kaggle.com/datasets/alonaniechvieieva/colon-microscopy-dataset-for-segmentation)

In addition, due to repository size constraints, only the dataset
folder used in this project (`Colon_Benign_Tissue`) is included in
the repository structure.

To reproduce the full-scale experiments, download the complete
dataset from Kaggle and place it into the corresponding directories
according to the repository structure.

---

## Dataset Classification

If classified according to common data taxonomy,
this dataset can be described as:

- **Unstructured data** —
  RGB histopathological images
- **Primary data** —
  collected from biological tissue samples
  as reported by the authors
- **Public data** —
  freely available via Kaggle and
  academic publication
- **Small dataset** —
  manageable on a single machine
  without distributed computing

---

## Data Quality Considerations

### Privacy and Ethics

All images are de-identified, HIPAA compliant,
validated, and publicly available,
as stated in the original publication.

### Completeness

The dataset does not contain missing values
in the traditional tabular sense.
Completeness can be assessed by verifying that
all image files are readable, non-corrupted,
and conform to the expected image resolution
and file format.

### Accuracy

According to the original publication,
the images originate from validated
histopathological sources.
However, label accuracy depends on
expert annotation and cannot be
independently verified without access
to additional clinical ground truth.

### Consistency

The dataset is internally consistent in terms of
image dimensions, file format,
and class definitions,
as described by the authors.
Potential inconsistencies can be identified
through automated checks of image metadata
and directory structure.

### Timeliness

The dataset was published in 2019.
