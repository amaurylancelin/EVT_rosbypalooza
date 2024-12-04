#!/bin/bash

#SBATCH --partition=compute
#SBATCH --mail-type=NONE
#SBATCH --ntasks=1
#SBATCH --mem=96gb
#SBATCH --time=23:00:00
#SBATCH --job-name get
#SBATCH --output=log_%j.log

module load mambaforge
. $CONDA_PREFIX/etc/profile.d/conda.sh
conda activate /vortexfs1/home/kcarr/EVT_rossbypalooza/envs
echo "conda prefix: ${CONDA_PREFIX}"

## these are the date ranges to use:
# date_range0 = ["2021-06-20","2021-07-10"]
# date_range1 = ["2006-07-13","2006-08-02"]
# date_range2 = ["2013-06-22","2013-07-12"]


python fetch_ERA5_spatial.py --start_date $1 --end_date $2
