#!/bin/bash

#SBATCH --job-name=spades             # Job name
#SBATCH --output=spades.log           # Standard output and error log
#SBATCH --ntasks=24

cd $SLURM_SUBMIT_DIR

# /usr/bin/mpiexec --mca plm_base_verbose 10 -n 24 /clusterfs/usr/bin/python3 run_spades.py
/usr/bin/mpiexec -n 24 /clusterfs/usr/bin/python3 run_spades.py

