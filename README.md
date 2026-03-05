# BioTracker_TiO2: Application of the cutting-edge deep-learning cell recognition tools for nanoparticles biophysical research

**Project presentation:**  
[View the project presentation](https://github.com/Okazia1715/BioTracker__TiO2/blob/main/6_final_presentation/Niechvieieva_Alona_Artifact.pptx)

While modern microscopy technologies produce copious quantities of
detailed images, translating this information into dependable
quantitative measurements remains a significant challenge.

In many cases, analysis is still performed through manual annotation
and visual inspection. This process is inherently slow, subjective,
and difficult to reproduce at scale.

This project explores how modern deep learning methods can bridge
this gap by combining automated cell segmentation with spatial
analysis of particles in microscopy images.

To improve accessibility, the project also provides a desktop
application with a graphical user interface (GUI), allowing users
to run the full analysis pipeline without requiring programming
knowledge. The goal is to bridge the gap between computational
experts and experimental researchers.

---

## Workflow Overview

The **BioTracker_TiO2** workflow begins with raw microscopy images,
which undergo preprocessing to enhance image contrast.

Cells in the images are segmented using the **Cellpose** model,
which is specifically designed for biological microscopy data.

Particles can either:

- be loaded from existing particle maps, or
- be synthetically generated to create controlled experimental
  conditions for testing the analysis pipeline.

The position of each particle relative to segmented cells is then
classified to determine whether it is:

- outside the cell
- on the cell boundary
- inside the cell

The final outputs include visual overlays and quantitative
measurements describing particle localization patterns. These
results are stored in structured formats to allow comparisons
between different experimental conditions.

---

## Key Features

This project combines modern deep learning segmentation with a
practical workflow designed for microscopy-based research.

Cell segmentation is performed using **Cellpose**, a deep-learning
model capable of generalizing across different biological cell
types.

Recent developments such as **Cellpose-SAM**, which integrates
Cellpose with the **Segment Anything Model (SAM)**, demonstrate the
potential of vision foundation models for biological image
analysis.

To make these tools accessible in biological laboratories, a custom
desktop application was developed that integrates:

- cell segmentation
- particle localization
- visualization
- statistical analysis

All processing steps are explicitly defined to ensure that analyses
can be reproduced and verified.

---

## Application

A graphical desktop application was developed to simplify the
workflow and make it accessible to non-programmers.

The application allows users to:

- Load a dataset of microscopy images
- Automatically segment cells
- Import or generate particle maps
- Analyze spatial particle distributions
- Export both visual and numerical results

This application lowers the barrier to advanced microscopy image
analysis for researchers and students without programming
experience.

---

## Outputs

The workflow generates both visual and numerical outputs.

Visual outputs include:

- segmentation masks
- overlay images showing cells and particles

Quantitative outputs include structured tables and statistical
plots summarizing particle localization patterns across images.

Together, these outputs enable exploratory analysis while also
supporting reproducible scientific workflows.

---

## Dataset Availability

Due to GitHub file size limitations, only a subset of images is
included in this repository.

The dataset used in this project is available on Kaggle:

[Colon Microscopy Dataset for Segmentation](https://www.kaggle.com/datasets/alonaniechvieieva/colon-microscopy-dataset-for-segmentation)

The sample images and all the models for Cellpose included in this
repository allow users to test
the workflow and reproduce the pipeline without downloading the
full dataset.
