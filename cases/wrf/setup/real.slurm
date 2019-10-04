#!/bin/bash -l
#SBATCH -J conus-wrf
#SBATCH -n 4
#SBATCH -N 1
#SBATCH -t 05:00
#SBATCH -A SCSG0001
#SBATCH -p dav
#SBATCH -o real.log

# Setup environment
export TMPDIR=/glade/scratch/$USER/tmp
mkdir -p $TMPDIR

module purge
module reset

# Run real.exe
srun ./real.exe

# Save log files
mkdir -p logs.real
mv rsl.* logs.real
