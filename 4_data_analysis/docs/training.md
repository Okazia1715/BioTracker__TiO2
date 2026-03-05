# Cellpose Model Training and Iterative Refinement

This document describes the training procedure used to develop custom Cellpose
models for adipocyte segmentation in gastrointestinal tissue images. Training
followed a human-in-the-loop workflow, where segmentation outputs were
iteratively inspected and corrected to improve performance on a limited set of
expert-annotated examples.

---

## Motivation for custom training

Pretrained Cellpose models are designed for broad generalization. When applied
to gastrointestinal tissue images, they showed limitations such as:

- inaccurate segmentation of large adipocytes
- merging of adjacent cells
- false positives in complex background regions

To address this, a task-specific model was trained using a small but curated
set of corrected masks.

---

## Human-in-the-loop strategy

Training consisted of repeated cycles:

1. Apply the current model to a subset of images
2. Visually inspect segmentation outputs
3. Manually correct segmentation errors
4. Add corrected masks to the training dataset
5. Retrain the model using updated annotations

This strategy progressively adapts the model to dataset-specific morphology
while minimizing the need for large annotation sets.

---

## Model versions

Five consecutive versions were trained: `colon1` → `colon5`.

| Model  | Training images | Purpose |
|--------|-----------------|---------|
| colon1 | 1               | Initial baseline |
| colon2 | incremental     | Refinement cycle |
| colon3 | incremental     | Refinement cycle |
| colon4 | incremental     | Refinement cycle |
| colon5 | 8               | Final stabilized model |

Each version incorporates corrections discovered in the previous iteration.

---

## Training configuration (example)

- Framework: Cellpose
- Optimizer: AdamW
- Learning rate: 1e-5
- Weight decay: 0.1
- Epochs: 100
- Test set: not explicitly defined

Due to limited annotated data, evaluation relied on training behavior and
qualitative visual inspection rather than a formal held-out benchmark.

---

## Training loss evolution (summary)

### Early model (colon1)

- initial loss ~ 8.9
- final loss ~ 1.55
- trained on a single image
- high variance and limited robustness

### Final model (colon5)

- initial loss ~ 4.7
- final loss ~ 0.99
- trained on eight corrected images
- more stable convergence and improved consistency

---

## Integration into the GUI pipeline

The final model (`colon5`) is integrated into `app.py` for inference. The GUI
loads the model once and applies it to all images in the selected folder.

Diameter handling in the GUI supports:

- user-defined diameter in pixels
- auto-diameter mode, estimated once from the first segmentation masks

---

## Reproducibility notes

- Training parameters were kept consistent across model versions.
- Each model version is stored separately to preserve the training history.
- The repository structure enables tracking model evolution over time.

---

## Possible extensions

- Add a held-out validation subset
- Evaluate with Dice / IoU metrics
- Expand training to additional cell types or tissues
- Add robustness checks across microscopes and acquisition protocols

## Evaluation Limitations

Due to limited annotated data, training evaluation relied primarily on
loss convergence and qualitative visual inspection.

No independent test set was defined. Therefore, segmentation
generalization performance cannot be quantitatively reported.

Future work should include:

- Held-out validation subset
- Dice/IoU benchmarking
- Cross-dataset validation

## Note

As a result of GitHub repository size restrictions, the Cellpose
models have also been made available as part of the project dataset
on Kaggle.

[https://www.kaggle.com/datasets/alonaniechvieieva/colon-microscopy-dataset-for-segmentation]

These models can be downloaded from the dataset and subsequently
placed into the models/ directory.

When using these models for segmentation, it is advised that the
colon5 model is used, as it is the final model resulting from the
human-in-the-loop training process and provides the most stable
results on the microscopy images used in this project.
