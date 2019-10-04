#!/bin/bash -l
#SBATCH -J conus-wrf
#SBATCH -n 32
#SBATCH -N 2
#SBATCH --ntasks-per-node 16
#SBATCH -t 05:00
#SBATCH -A SCSG0001
#SBATCH -p system
#SBATCH -o wrfpt2.log

# Setup environment
export TMPDIR=/glade/scratch/$USER/tmp
mkdir -p $TMPDIR

module purge
module reset

# Run wrf.exe
srun ./wrf.exe

# Save log files
mkdir -p logs.wrfpt2
mv rsl.* logs.wrfpt2
