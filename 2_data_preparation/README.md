# Non-Technical Modeling Explanation

## How I Modeled the Problem Domain

My broader research interest is the biological impact of
nanoparticles on GI tissue. Ideally, this would involve
analyzing images from microscopy data where the nanoparticles
are easily identifiable on the exposed tissue samples.
However, this is not feasible under the given time, access,
and scope constraints. Instead, I chose to simplify the
approach by using a modeling strategy.

Instead of directly modeling the exposure to nanoparticles,
I chose to model the structural organization of healthy
colon tissue as a computationally measurable system. To this
end, I am using publicly available histopathological images
of healthy colon tissue, which is a stable biological
baseline. These images allow me to segment the cell
structures using a machine learning model.

Once cell boundaries are segmented, object localization may
be computed in relation to these boundaries. In my
experimental setup, objects similar to nanoparticles are
simulated. This enables me to verify whether or not a
computational workflow may classify objects as being inside
or outside cells in a reproducible fashion.

In conclusion, rather than simulating biological exposure,
I simulated a reproducible workflow that may later be used
for analyzing nanoparticle data.

## Possible Flaws in This Approach

However, there are significant limitations to this modeling
approach. I modeled nanoparticles rather than detecting
biological particles. There is only healthy tissue in this
dataset, and no pathological data is provided. Also, there is
augmented data present in the LC25000 dataset, which could
be artificial.

Lastly, quantification of data is heavily reliant on
segmentation accuracy. Incorrect cell boundary data could
affect localization results. Also, image modeling only
provides data for physical interaction and does not provide
any data for biochemical interaction.
