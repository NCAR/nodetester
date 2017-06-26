#!/bin/bash
#
#	test_pbsres.sh
#	Author:		Brian Vanderwende
#	Revised:	18 Apr 2017
#
#	This script prepares the environment for node tests and then
#	executes the test driver.

# Test configuration (create a reservation and use that)
OUTDIR=/glade/scratch/${USER}/nodetests/pbsres
CASE=cases/test_ch
QUEUE=R1351948
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
python driver.py PBS -c $CASE -q $QUEUE -a $PROJ -p $OUTDIR --verbose --force
