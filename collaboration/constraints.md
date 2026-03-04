# Constraints

## External Constraints

The project is subjected to various constraints based on data
availability, computing environment, and the research landscape.

Publicly accessible histology data sets such as the LC25000 colon data
set were not originally intended for nanoparticle localization tasks.

Ground truth data on intracellular particle accumulation is not
accessible, and factors such as resolution, staining variability, and
compression pose challenges on segmentation.

Thus, the pipeline is required to operate without perfect reference
data and must demonstrate robustness to real-world variability.

Computational constraints are also a limitation.

GPU availability is not guaranteed, and the effectiveness of the
pipeline is based on CUDA availability.

Large data sets may not fit within the laptop's memory.

Thus, the pipeline is required to operate on CPU-only computers although
at a reduced rate, and the graphical user interface must remain
memory-efficient.

Finally, the requirement to follow open science practices implies a
requirement for a well-structured directory structure, version control
of scripts, transparent preprocessing steps, and deterministic outputs
wherever possible.

This requirement is based on the need for structured outputs and
documentation rather than automation itself.

---

## Internal Constraints  Involuntary

These constraints are derived from the project context and development
conditions.

The work is conducted under the constraints of milestone-based academic
deadlines, which define the development cycles.

Implementation needs to be balanced with the development of
accompanying documentation and communication.

Therefore, the scope of implemented features is prioritized over the
scope for extensive experimental exploration.

The project is conducted by a single researcher, which limits the scope
for parallel development and requires manual testing.

Furthermore, the graphical interface, without the scope for a UI/UX
development team, focuses on functionality over aesthetics.

The domain scope is narrow.

The project focuses on the following:

Colon histology
Cell segmentation
Localization of synthetic and detected nanoparticles

This does not include:

Multi-organ comparisons
Live-cell imaging
Temporal modeling

---

## Internal Constraints  Voluntary

Apart from the external constraints, there are intentional designs that
aim to achieve reproducibility and scientific integrity.

The workflow is designed to protect the raw data from being overwritten
or modified. The images are not overwritten, and all processed images
are stored in separate directories. This is an additional constraint
that forces reproducibility and integrity.

The process follows a set path: image inversion, contrast enhancement,
segmentation, and quantification. There are no hidden normalization
techniques used here. This might not give us the desired degree of
flexibility, but it provides transparency.

The decision to create a graphical user interface rather than a simple
script increases the complexity of the code but makes the software more
accessible to others. This is an additional constraint that forces us to
create a user-friendly interface.

The software provides reproducible output, which includes segmentation
masks, particle maps, overlays, and CSV tables for per-cell and summary
data. It does not use any proprietary formats or binary states, which
makes the output easily readable by others.