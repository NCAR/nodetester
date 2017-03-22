#!/bin/bash
#
#	run_tests.sh
#	Author:		Brian Vanderwende
#	Revised:	21 August 2016
#
#	This script prepares the environment for node tests and then
#	executes the test driver.

# Test configuration
CASE=test_ca
QUEUE=caldera
NODES=caldera
PROJ=SCSG0001
COMPVER=intel/16.0.3
NCVER=netcdf/4.4.1
PYVER=python/2.7.7

# Prepare module environment
source /glade/apps/opt/lmod/lmod/localinit/localinit.sh
module purge >& /dev/null
module lo ncarenv ncarbinlibs $COMPVER $NCVER $PYVER >& /dev/null

# Run driver script
python driver.py LSF -c $CASE -q $QUEUE -n $NODES -p $PROJ
