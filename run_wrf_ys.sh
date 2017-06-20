#!/bin/bash
#
#	run_wrf_ys.sh
#	Author:		Brian Vanderwende
#	Updated:	21 March 2017
#
#	This script prepares the environment for node tests and then
#	executes the test driver.

# Test configuration
OUTDIR=/glade/scratch/${USER}/nodetests/wrf_ys
CASE=cases/wrf_ys
QUEUE=special
NODES=ys[0-6].*
PROJ=SCSG0001
COMPVER=intel/16.0.3
NCVER=netcdf/4.4.1
PYVER=python/2.7.7

# Prepare module environment
source /glade/apps/opt/lmod/lmod/localinit/localinit.sh
module purge >& /dev/null
module lo ncarenv ncarbinlibs $COMPVER $NCVER $PYVER >& /dev/null

# Run driver script
python driver.py LSF -c $CASE -q $QUEUE -n $NODES -a $PROJ -p $OUTDIR --verbose
