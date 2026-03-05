
# Pipeline

## Figure caption, Pipeline diagram

**Figure X. Computational pipeline for cell segmentation and nanoparticle
analysis.** RGB microscopy images are converted to grayscale and segmented
using a custom-trained Cellpose model. Particle information is obtained either
from experimental particle maps via Laplacian-of-Gaussian (LoG) spot detection
or by synthetic generation of fluorescent-like particles.

When synthetic particles are used, the image set is randomly split into two
groups: (i) random placement and (ii) accumulation placement with 5× bias
inside cells. Particle centers are mapped onto labeled masks to classify
particle localization as background, cell boundary, or inside-cell. The
pipeline exports masks, particle maps, overlay images, per-image statistics,
and summary plots comparing both groups.

---

## Analysis parameters

| Component            | Parameter                  | Value      | Notes |
|----------------------|----------------------------|------------|------|
| Cell segmentation    | Model                      | colon1–5   | Human-in-the-loop training |
| Cell segmentation    | Input channels             | grayscale  | RGB → grayscale |
| Cell segmentation    | Diameter                   | user / auto| Auto from first masks |
| GPU                  | Availability check         | enabled    | `cellpose.core.use_gpu()` |
| Particle detection   | Method (experimental)      | LoG        | `blob_log` |
| Particle detection   | min_sigma                  | 0.8        | Smallest spots |
| Particle detection   | max_sigma                  | 2.5        | Largest spots |
| Particle detection   | num_sigma                  | 10         | Scales tested |
| Particle detection   | threshold                  | 0.05       | Sensitivity |
| Synthetic particles  | Small diameter             | 3 px       | Gaussian-like kernel |
| Synthetic particles  | Big diameter               | 5 px       | Gaussian-like kernel |
| Synthetic particles  | Counts per image           | user input | Defaults: 25 + 25 |
| Synthetic particles  | Overlap constraint         | no overlap | Placement rule |
| Synthetic split      | Group assignment           | ~50/50     | Saved to CSV |
| Accumulation mode    | Sampling bias inside cells | 5×         | vs outside |
| Overlay export       | PNG saving                 | OpenCV     | Faster on Windows |

---

## Processing Steps

1. Grayscale conversion of RGB images.
2. Cell segmentation using Cellpose.
3. Particle detection or synthetic generation.
4. Classification of particles as:
   - background
   - boundary
   - inside cell
5. Distance-to-boundary calculation.
6. Cluster detection.
7. Statistical aggregation across images.

Results are saved as masks, overlays, particle maps,
summary tables, and comparative plots.

## Quantification outputs (synthetic mode)

When synthetic particles are used, `stats_per_image.csv` is generated for both
subfolders. Each row corresponds to one image and includes:

- `particles_on_background`
- `particles_in_cells_total`
- `particles_on_boundary`
- `particles_inside_not_boundary`
- `mean_particles_per_cell_total`
- `mean_particles_on_boundary_per_cell`
- `mean_particles_inside_not_boundary_per_cell`

Additional spatial metrics:

- `clusters_count`
- `frac_near_boundary_le_2px`
- `mean_distance_to_boundary_px`

---

## Plot outputs

The `plots/` folder contains nine figures. Each plot shows both synthetic
groups with different colors. One point corresponds to one image.

1. Particles on background
2. Mean particles per cell (boundary + inside)
3. Particles in cells total
4. Particles on boundary
5. Particles inside (not boundary)
6. Mean particles inside (not boundary) per cell
7. Number of clusters per image
8. Fraction of in-cell particles within 2 px of boundary
9. Mean distance to boundary for in-cell particles

---

## Limitations

1. Segmentation evaluation is primarily qualitative (visual inspection) and
based on training behavior rather than a held-out test set.

2. Experimental particle detection uses a general LoG approach. While robust,
it may require parameter tuning for different acquisition settings.

3. Synthetic particles represent simplified accumulation scenarios and do not
capture complex physicochemical interactions.

4. The current implementation is per-image. It does not model temporal data,
cell tracking, or inter-cell spatial correlations beyond simple clustering.

Despite these limitations, the pipeline provides a reproducible framework for
batch processing and comparative analysis of particle localization.

## Sources of Uncertainty

While segmentation visually improved across model versions, no
formal validation set was used. Therefore, segmentation performance
cannot be quantified using standard metrics such as Dice coefficient
or IoU.

Synthetic accumulation scenarios provide controlled validation of the
pipeline logic but do not validate biological realism.

All results depend on correct mask boundaries. Boundary misclassification
propagates directly to localization metrics.

Finally, augmentation in the LC25000 dataset may introduce patterns
that do not reflect real biological variability.
