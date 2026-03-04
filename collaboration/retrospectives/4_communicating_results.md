# Retrospective

## Stop Doing

Looking back at this project, I can see some mistakes that I could
have avoided. First, I extended the scope of the project. I got
overly enthusiastic about incorporating the Cellpose training, the
Cellpose-SAM concepts, the GUI, the synthetic experiments, the
clustering analysis, the reproducibility architecture, and the
communication concepts all at once. I didn’t finish one layer before
moving on to the next. Instead, I jumped between them.

Second, I didn’t include the formal validation metrics. Although the
synthetic “random vs. accumulation” concept was good, I didn’t
include the segmentation metrics such as the Dice score and the IoU.
I didn’t include the inferential statistics either. Although the
conditions showed good visual results, I was overly reliant on the
qualitative confidence rather than the quantitative results.

Third, I made my early communication drafts too technical. I was
aware that my target audience would be biologists who might not
trust “Black Box AI.” I got too caught up in the technical details
of the architecture, when I should have focused on the audience
clarity from the very beginning.

What I will do differently for the next project:

I will not extend the scope of the project. I will include the
statistical tests from the beginning. I will keep the audience
clarity in mind from the beginning.

---

There are a few things that I am proud of that I want to continue
doing. One of the best decisions I made was designing the
controlled synthetic validation framework. This allowed me to
create known conditions of spatial bias, which I could use to test
whether the tool actually detected the redistribution, rather than
just counting the number of particles. This was a big source of
pride for me.

Another thing that I am proud of is that I made sure that the tool
was reproducible from the very beginning. I never overwrote the
images, and I made sure that I was keeping all the steps of the
process transparent. This was a big source of pride for me, as I
knew that this was exactly what my target audience needed to build
trust.

Another decision that I made that I am proud of was that I decided
to create the tool with a GUI, rather than leaving it as a
script-based tool. This was a big source of pride for me, as I
wanted to make sure that I was thinking about the user, not just
the developer. I want to continue to create tools that allow people
who are not programmers to use advanced machine learning
techniques.

Most importantly, I was proud of how I was able to tie together the
concepts of segmentation, classification, clustering, and exporting
to a CSV. This felt more like building a tool, rather than running a
model.

---

## Starting now

For my upcoming projects, I'm planning to take my limits to the
next level. I'm planning to integrate statistical tests into my
workflow. This way, my outputs will be ready to publish. I'm
planning to include effect sizes, p-values, and confidence
intervals.

Next, I'm planning to include segmentation evaluation metrics into
my training process for custom models. For example, if I'm training
my model on Cellpose or trying out Cellpose-SAM, I'm planning to
include segmentation metrics.

Another big change I'm planning to make is to switch from synthetic
particles to real-world nanoparticle data. This way, I can test the
relevance of my results.

Lastly, I'm planning to test my software on real people. I'm sure a
biology student will reveal many usability assumptions I'm
currently unaware of.

---

## Lessons Learned

I learned more than just how to use deep learning techniques. Deep
learning is only scientifically relevant if it is embedded in a
well-structured and validated workflow. While a segmentation model
is a good start, it is not a solution without a quantification
pipeline to back it up.

In this project, I also saw that a controlled experiment, while
synthetic, is a powerful way to objectively evaluate a
computational system.

Perhaps most importantly, however, I saw that scientific software
development is a systems problem. It is not just about writing
code, but about understanding the user, creating a validation
strategy, and communicating effectively.

This project moved my focus from “using a model” to “building a
scientific framework.” That, I think, is the greatest lesson of
all.

## Strategy vs. Board

### What parts of my plan went as expected?

- The approach to communication was centered on audience limits,
  building trust, and ensuring repeatability.
- The documentation and workflow presentation remained faithful
  to the goal of clear and structured communication.

### What parts of my plan did not work out?

- The drafts were too technical for the intended audience.
- I approached the explanation from a developer perspective
  rather than a biologist perspective.

### Did I need to add things that weren't in my strategy?

Yes. I had to emphasize the importance of data integrity and the
fact that raw data remains unaltered, as a way to build trust.

I also added clearer audience personas to define the direction
of the communication.

### Did I remove extra steps?

I removed excessive architectural detail that was not helpful
to the audience.
