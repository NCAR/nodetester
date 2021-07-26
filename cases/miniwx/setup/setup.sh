#!/bin/bash
#
#   2-node GPU test using "miniWeather" learning code
#   https://github.com/mrnorman/miniWeather
#
#   This code only works on Casper at present, as it needs
#   GPU resources to run. Also, the Fortran version is the
#   only one that seems compatible with modern NVHPC and
#   CUDA toolkit versions. Best to avoid the others.
#

# Exit upon error
set -e

MINIWX_REPO=git@github.com:mrnorman/miniWeather.git
MINIWX_VERS=fortran
MINIWX_ACC="-ta=nvidia,cc70,ptxinfo -acc=defpresent"
MAINDIR="$( cd "$(dirname "$0")" ; pwd )"

if [[ $NCAR_HOST == cheyenne ]]; then
    echo "Error: this case is GPU only and not supported on Cheyenne"
    exit 1
else
    SUBCMD="qsub -W block=true -l gpu_type=v100 -q casper -v MPIBIN=mpirun"
fi

WRF_VERSION=3.4
# Prepare module environment
echo "Resetting module environment to defaults ..."
module purge
module load ncarenv cmake nvhpc/21.3 openmpi pnetcdf cuda/11.0.3

# Prepare build dir
mkdir -p $NCAR_HOST
cd $NCAR_HOST

# Grab and extract source
echo "Cloning miniWeather from GitHub repo ..."
git clone $MINIWX_REPO
cd miniWeather 

# Build the model
cd $MINIWX_VERS/build
./cmake_clean.sh

cmake   -DCMAKE_Fortran_COMPILER=mpif90         \
        -DPNETCDF_PATH=$NCAR_ROOT_PNETCDF       \
        -DOPENACC_FLAGS=$MINIWX_ACC             \
        -DFFLAGS=-O3                            \
        -DNX=4000                               \
        -DNZ=2000                               \
        -DSIM_TIME=200                          \
        -DOUT_FREQ=100                          \
        ..
make

# Now submit the job to generate input data
$SUBCMD $MAINDIR/gendata.pbs

# Create output directory with expected output
mkdir $MAINDIR/$NCAR_HOST/output
cp openacc $MAINDIR/$NCAR_HOST/output
cp output.nc $MAINDIR/$NCAR_HOST/output/expected_output.nc
