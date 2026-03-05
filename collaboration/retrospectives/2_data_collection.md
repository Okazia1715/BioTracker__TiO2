# Milestone 2 Retrospective

## Stop Doing

There are some things that I should stop doing during Milestone 2.
First of all, I should avoid jumping into technical solutions
before clearly clarifying the problem statement. This is because I
was comfortable with computational tools and should have sharpened
my problem statement before jumping into technical solutions.

Secondly, I should avoid making assumptions that are not clearly
clarified as I did during Milestone 2. For instance, I should have
clearly clarified that structural image-based modeling is not about
explaining the biology of the results. This is because I knew that
in my head, but I should have clearly clarified it.

Thirdly, I should avoid having a broad approach to the biology of
the problem. For instance, I should have clearly clarified that
nanoparticles and tissues involve toxicology, pathology, and cell
biology, and should have stuck to computationally feasible
approaches.

Therefore, some of the things that I should stop doing are:

• Jumping into technical solutions before sharpening the problem
statement.

• Assuming that some things are obvious without clearly clarifying
them.

• Assuming that some things are computationally feasible without
clearly clarifying them.

## Continue Doing

As we move forward, Milestone 2 highlighted some strengths that
should be continued. One of them is keeping the modeling grounded in
reality through lab experience. The disconnect between biology
experiments and the type of results we want is significant. The
project is making significant strides in reducing this disconnect.

Another thing that was very effective was applying systems thinking
to understand the domain we are dealing with. Understanding it as a
dance between industrial production, biological complexity, and
experimental and computational analysis helped us understand how we
could intervene in a meaningful way.

Another thing that was done well was reproducibility. The raw data
is intact, preprocessing scripts are version-controlled, and we
have a clean and logical directory structure. This is something we
should continue with.

Things I should continue keeping in mind:

- Using systems thinking for complex domains.
- Reproducibility as a fundamental assumption.
- Creating pipelines that connect wet lab and analysis.

## Start Doing

I have a few ideas on how I can improve this work in the future.
First, I should have integrated validation into my design. Rather
than wondering, “Can this be modeled?” I should have been
wondering, “How can I validate this?” Second, I should have been
more skeptical. For example, how robust is the segmentation when
there is variability in staining? How does the spatial metrics
change with small boundary effects? This should have been
investigated experimentally, not just theorized. Third, I should
have used some real data in my validation. While simulated
nanoparticles are useful, having some experimental data on real
nanoparticles would have increased the overall biological
relevance of my work. Finally, I should have been clearer on what
my pipeline does not measure. By being clearer on what my pipeline
does not measure, I can improve my work scientifically, not weaken
it.

## Lessons Learned

Milestone 2 reminded us of a number of important truths. How we
define the problem determines the scope and direction of our work:
a poorly defined problem can make the entire project feel
unwinnable, whereas a well-defined problem with a clear structure
makes progress something that can be quantified and tracked. Data
boundaries determine what we can hope to achieve: without ground
truth and with limited computing resources, some outcomes are
simply off the table. These boundaries are not weaknesses, they
define our design space. Thinking in systems isn’t just a fuzzy
concept, it has real-world payoff as a guide to where machine
learning can be useful and where it can’t in biology.

## Strategy vs. Board

### What parts of my plan went as expected?

The use of a systems thinking approach for organizing the domain
worked out well. Combining lab work and computational modeling
stayed true to overall plan strategy.

Reproducibility planning, including directory structures,
version control, and raw data preservation, progressed as
planned.

### What parts of my plan did not work out?

I began too soon with computational thinking before fully
stabilizing problem framing.

The scope of biological interpretation was initially too large
for computational modeling.

### Did I need to add things that weren't in my strategy?

Yes. I had to explicitly differentiate between structural
modeling and biological causality.

Additionally, validation thinking had to be brought into the
process sooner than originally planned.

### Did I remove extra steps?

Yes. Attempts at incorporating toxicology and pathology were
minimized beyond what was needed for computational modeling.
