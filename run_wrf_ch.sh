#!/bin/bash
#
#	run_wrf_ch.sh
#	Author:		Brian Vanderwende
#	Revised:	21 March 2017
#
#	This script prepares the environment for node tests and then
#	executes the test driver.

# Test configuration
OUTDIR=/glade/scratch/${USER}/nodetests/wrf_ch
CASE=cases/wrf_ch
QUEUE=system
PROJ=SCSG0001
COMPVER=intel/16.0.3
MPIVER=mpt/2.15f
NCVER=netcdf/4.4.1.1
PYVER=python/2.7.13

# Prepare module environment
source /glade/u/apps/ch/modulefiles/default/localinit/localinit.sh
module purge >& /dev/null
module lo ncarenv $COMPVER $NCVER $MPIVER $PYVER >& /dev/null

# Run driver script
python driver.py PBS -c $CASE -q $QUEUE -a $PROJ -p $OUTDIR --force --verbose
