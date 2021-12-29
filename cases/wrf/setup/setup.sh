#!/bin/bash
#
#   149-timestep WRF Pairwise Test
#
#   If you need to regenerate executables and input data for the WRF case,
#   you should perform all of these steps on every system you wish to test
#   (e.g., Cheyenne AND Casper).

# Exit upon error
set -e

# Use PBS for all systems
if [[ $NCAR_HOST == cheyenne ]] || [[ $NCAR_HOST == laramie ]]; then
    SUBCMD="qsub -W block=true -q system -v MPIBIN=mpiexec_mpt"
else
    SUBCMD="qsub -W block=true -q casper -v MPIBIN=mpirun"
fi

WRF_VERSION=3.4
MAINDIR="$( cd "$(dirname "$0")" ; pwd )"

# Prepare module environment
echo "Resetting module environment to defaults ..."
module purge
module reset

# Grab input files from Campaign Storage
if [[ ! -d data ]]; then
    echo "Retrieving input data for WRF case ..."
    gci cget -r cisl/csg/nodetester/wrf/:data/
fi

# Prepare build dir
mkdir -p $NCAR_HOST/run
cd $NCAR_HOST

# Grab and extrace source
echo "Unpacking WRF V${WRF_VERSION} ..."
tar -xf ~wrfhelp/SOURCE_CODE/WRFV${WRF_VERSION}.tar.gz
cd WRFV${WRF_VERSION}

# Perform config of WRF for dmpar (numbers may change based on version)
case $LMOD_FAMILY_COMPILER in
    intel)
        COPT=15
        ;;
    gnu|gcc)
        COPT=34
        ;;
    cce)
        COPT=46
        ;;
esac

echo "Configuring WRF with compile option $COPT ..."
./configure << EOF
$COPT
1
EOF

# Now compile
echo "Compiling WRF for em_real run ..."
./compile em_real |& tee compile.log

# Set up to run real
echo "Running real.exe ..."
ln -s $PWD/run/* ../run/
cd ../run
rm namelist.input
ln -s $MAINDIR/data/met_em* .
ln -s $MAINDIR/namelist.real namelist.input
cp $MAINDIR/*.pbs .

$SUBCMD real.pbs

# Run WRF for spin-up
echo "Running wrf.exe for case spin-up ..."
rm namelist.input
ln -s $MAINDIR/namelist.wrfpt1 namelist.input

$SUBCMD wrfpt1.pbs

# Run WRF to generate verification data
echo "Running wrf.exe to generate case data ..."
rm namelist.input
ln -s $MAINDIR/namelist.wrfpt2 namelist.input

$SUBCMD wrfpt2.pbs

# Store output
echo "Organizing case output in $PWD/output ..."
cd ../
mkdir -p output

COPYLIST='*.TBL *.formatted namelist.input RRTMG* wrf.exe'

for CPF in $COPYLIST; do
    cp run/$CPF output/
done

mv run/wrfout_d01_2001-10-25_03:00:00 output/expected_wrfout_d01_2001-10-25_03:00:00
mv run/wrfrst_d01_2001-10-25_00:00:00 output/
mv run/wrfbdy_d01 output/
cp $MAINDIR/wrf_stats output/

cat > output/info << EOF
WRF Pairwise Test Case
----------------------
System:     $NCAR_HOST
Origin:     $(date)
WRF:        $WRF_VERSION

$(module list)
EOF
