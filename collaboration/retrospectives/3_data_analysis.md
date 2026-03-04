# Milestone 3 Retrospective

## Stop Doing

In Milestone 3, there are some areas where I think I have some
vulnerabilities in my approach. First, I have delayed quantitative
validation once again. While the synthetic bias experiments have
shown good separation, I have not used metrics like segmentation
quality, such as Dice and IoU. Instead, I have been relying on the
visual judgment of the quality of the segmentation. However, this
is not sufficient as a robust and rigorous check.

Another area where I have been vulnerable is in clearly explaining
the uncertainties in the early versions of the results. While I was
aware that synthetic particles are not perfect mimics of biological
nanoparticles, I have not been very clear on this in the materials I
have sent.

Finally, there have been cases where I have assumed that correct
segmentation means correct biological interpretation. While the
masks look correct, small boundary effects can have significant
effects on distance-based metrics and clustering. I should have
robustly tested the pipeline under these conditions.

So, what are the things I should stop doing?

## Continue Doing

As Milestone 3 demonstrated, there are several strengths that can
be built on. Consolidating the work on segmentation, classification
of particles, clustering, and CSV export into a single, cohesive
pipeline transformed the disorganized process into a
well-structured, logical system of analysis.

One of the best parts of the project was the effectiveness of the
synthetic bias experiments. By designing conditions under which
spatial redistribution occurs, I was able to create a way of
testing whether the new pipeline was able to detect the effect.
This was a very effective demonstration of the scientific logic
behind the project.

Another aspect was the effectiveness of the new GUI, which made the
process accessible to biologists. It was possible to execute the
workflow without command-line experience, which was in line with
the communication strategy and the audience.

Things I should continue doing:

- Design controlled validation experiments.
- Combine several analysis processes into unified workflows.
- Develop tools that prioritize reproducibility and usability.

## Start Doing

Here’s what I’m aiming to do next. For the next set of milestones,
there are a few things that are on the agenda.

The first thing that I’m planning to do is incorporate formal
segmentation evaluation metric calculations into the pipeline.
This includes calculating the Dice coefficient and IoU, as well as
possibly boundary F1 scores, when masks are provided.

The second thing that I’m planning to do is perform a sensitivity
analysis on the pipeline. This will involve slightly moving the
boundaries of the segmentation or clustering and seeing how robust
the spatial metrics are to this.

The third thing that I’m planning to do is test the pipeline on at
least a small real-world dataset that includes experimentally
validated nanoparticle localization.

The fourth thing that I’m planning to do is incorporate automated
statistical reporting into the pipeline.

## Lessons Learned

Milestone 3 has brought to light a few undeniable truths. The
construction of a pipeline is not only about getting each component
to work but, more importantly, getting all the components to work
together.

Synthetic validation is a powerful tool, but its effectiveness is
limited to the world of computation.

Reproducibility is not an afterthought; it’s a design consideration
from the get-go.

Most importantly, however, robustness trumps all other
considerations. The ability to deliver a pipeline that works, is
interpretable, and has good documentation is much more important
than the ability to deliver a pipeline that looks pretty with all
the bells and whistles.

Milestone 3 has forced me to change my focus from “does it run?” to
“is it reliable, interpretable, and scientifically valid?”

## Strategy vs. Board

### What parts of my plan went as expected?

- The unified pipeline came together as expected, i.e.,
  segmentation, particle classification, clustering, and CSV
  export worked smoothly.
- The synthetic bias validation experiment worked as expected,
  i.e., it showed spatial redistribution detection correctly.
- GUI development proceeded as planned according to the
  communication strategy.

### What parts of my plan did not work out?

- Formal validation of segmentation using metrics like Dice and
  IoU was constantly postponed.
- I relied too much on visual inspection.
- Early communication did not spell out uncertainty as clearly
  as it should have.

### Did I need to add things that weren't in my strategy?

Yes. It turned out that sensitivity analysis and formal
segmentation metrics were needed.

Yes. It turned out that statistical reporting needed to be
integrated.

### Did I remove extra steps?

Aesthetic polishing of the GUI was toned down in favor of
functional robustness.
