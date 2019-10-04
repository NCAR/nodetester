#!/bin/bash
#
#   149-timestep WRF Pairwise Test
#
#   If you need to regenerate executables and input data for the WRF case,
#   you should perform all of these steps on every system you wish to test
#   (e.g., Cheyenne AND Casper).

# Exit upon error
set -e

# Detect batch system
if which qsub >& /dev/null; then
    JSCHED=pbs SUBCMD="qsub -W block=true"
else
    JSCHED=slurm SUBCMD="sbatch --wait"
fi

MAINDIR="$( cd "$(dirname "$0")" ; pwd )"

# Prepare module environment
module purge
module reset

# Grab input files from Campaign Storage
if [[ ! -d data ]]; then
    gci cget -r cisl/csg/nodetester/wrf/:data/
fi

# Prepare build dir
SYSID=$(hostname | tr -d '[0-9]')
mkdir -p $SYSID/run
cd $SYSID

# Grab and extrace source
tar -xvf ~wrfhelp/SOURCE_CODE/WRFV4.1.1.TAR
cd WRFV4.1.1

# Perform config of WRF for dmpar (numbers may change based on version)
case $LMOD_FAMILY_COMPILER in
    intel)
        COPT=15
        ;;
    gnu)
        COPT=34
        ;;
    pgi)
        COPT=54
        ;;
esac

./configure << EOF
$COPT
1
EOF

# Now compile
./compile em_real |& tee compile.log

# Set up to run real
ln -s $PWD/run/* ../run/
cd ../run
rm namelist.input
ln -s $MAINDIR/data/met_em* .
ln -s $MAINDIR/namelist.real namelist.input
cp $MAINDIR/real.$JSCHED real.job

$SUBCMD real.job

# Run WRF for spin-up
rm namelist.input
ln -s $MAINDIR/namelist.wrfpt1 namelist.input
cp $MAINDIR/wrfpt1.$JSCHED wrfpt1.job

$SUBCMD wrfpt1.job

# Run WRF to generate verification data
rm namelist.input
ln -s $MAINDIR/namelist.wrfpt2 namelist.input
cp $MAINDIR/wrfpt2.$JSCHED wrfpt2.job

$SUBCMD wrfpt2.job

# Store output
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
