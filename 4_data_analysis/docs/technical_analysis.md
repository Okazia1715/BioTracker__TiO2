# Technical Analysis and Results

## Rationale for Chosen Techniques

The cell segmentation process utilized the custom-trained model
of Cellpose. This choice was influenced by its ability to conduct
generalist cell segmentation with diameter-aware scaling and its
effectiveness in dealing with heterogeneous cell types.
Gastrointestinal adipocytes have diverse sizes and clearness
of boundaries.

The human-in-the-loop approach was used for training due to
data scarcity. Instead of relying on annotated data for every
case, corrections were made for each iteration of the model
before retraining. This increased performance for specific
tasks and minimized data requirements.

The particle detection in experimental mode utilized
Laplacian of Gaussian spot detection. This approach has been
shown to be robust for moderate intensity changes and works
for circular bright objects. It also doesn’t require supervised
learning and is appropriate for data sets without annotated
information for the particles.

The generation of synthetic data for particles was used for
assessing specific accumulation patterns without ground truth
information for nanoparticle data sets. Introducing bias in
location allowed for assessing specific changes in location
metrics for the computational pipeline.

---

## Quantitative Metrics

For each image, the following metrics were computed:

- particles_on_background
- particles_on_boundary
- particles_inside_not_boundary
- particles_in_cells_total
- mean_particles_per_cell_total
- clusters_count
- frac_near_boundary_le_2px
- mean_distance_to_boundary_px

In the comparative plots for the random and accumulation
group, some differences can be observed.

In the accumulation group, the value for the quantity
"particles_in_cells_total" increases in a consistent manner
relative to the random group.

Meanwhile, the value for the quantity
"mean_distance_to_boundary_px" tends to decrease in the
accumulation group, which further strengthens the spatial
relationship with the cell interiors.

Cluster density also tends to increase in the biased
placement group.

---

## Statistical Interpretation

The separation between groups was visually observable in
multiple metrics.

However, I did not conduct formal hypothesis testing at
this stage. This milestone focuses on reproducible
quantification rather than inferential statistics.

---

## Possible Flaws in the Analysis

- No held-out segmentation benchmark
- Limited annotated training images (n=8)
- No real nanoparticle ground truth
- Augmented dataset origin
- Per-image analysis only
- No temporal dynamics modeled

---

## Alternative Approaches

There are a number of alternative approaches that could
be explored in future work.

First, for cell segmentation, a comparison of the current
Cellpose model with other prominent architectures, such as
U-Net, could be conducted to ascertain whether any
improvements in segmentation accuracy are due to
fundamental differences in architectures.

Furthermore, for cell segmentation, a more quantitative
assessment of segmentation accuracy could be achieved by
including standard accuracy measures, such as Dice Score,
Intersection over Union (IoU), etc. This could provide a
more quantitative assessment of segmentation accuracy,
rather than relying on visual inspection alone.

Additionally, in future work, if datasets of annotated
nanoparticles become available, a better detection of
particles could be achieved by utilizing supervised
models, rather than relying on LoG detection.

From a spatial analysis point of view, a better analysis
could be conducted by including simple statistical
comparisons between groups. This could be achieved by
including mean comparisons, confidence intervals,
hypothesis tests, etc. This could provide a better
understanding of group separation.

Additionally, a more in-depth analysis could be conducted
by assessing how each cell differs from neighboring cells
in terms of particle count. This could provide a better
understanding of whether particle localization differs
across regions of tissue, rather than relying on a simple
image-by-image analysis.
