#!/bin/bash

#SBATCH --partition=compute
#SBATCH --mail-type=NONE
#SBATCH --ntasks=1
#SBATCH --mem=96gb
#SBATCH --time=23:00:00
#SBATCH --job-name fetch 
#SBATCH --output=log_%j.log

module load mambaforge
. $CONDA_PREFIX/etc/profile.d/conda.sh
conda activate /vortexfs1/home/kcarr/EVT_rossbypalooza/envs
echo "conda prefix: ${CONDA_PREFIX}"


python fetch_ERA5_google.py
