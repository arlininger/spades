#!/bin/bash

#SBATCH --job-name=spades             # Job name
#SBATCH --ntasks=24                   # Run on a single CPU
#SBATCH --output=spades.log           # Standard output and error log
pwd; hostname; date

cd $SLURM_SUBMIT_DIR

srun /clusterfs/usr/bin/python3 run_spades.py