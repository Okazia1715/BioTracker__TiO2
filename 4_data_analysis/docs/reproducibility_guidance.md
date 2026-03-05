# Reproducibility Guidance

In order to reproduce all results of the analysis,
please follow these steps:

1. Clone the repository.
2. Create a conda environment according to the
   setup instructions.
3. Obtain the LC25000 dataset.
4. Execute the preprocessing script.
5. Load or train a custom Cellpose model.
6. Execute the application using the following
   command: python app.py
7. Activate synthetic mode (optional).
8. Compare the results of random and accumulation
   plots in the output directory.

The parameters are logged and deterministic
when the random seed is set.
