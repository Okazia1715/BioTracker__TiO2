# Setup and Run

## Create environment

conda create -n cellpose-app python=3.10 -y
conda activate cellpose-app

## Install packages

conda install -c conda-forge cellpose numpy scikit-image opencv tifffile matplotlib pandas -y

## Optional GPU support

conda install -c pytorch -c nvidia pytorch pytorch-cuda=12.1 -y

## Run application

python app.py
