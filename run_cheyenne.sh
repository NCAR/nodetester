#!/bin/bash
#
#	run_cheyenne.sh
#	Author:		Brian Vanderwende
#	Revised:	21 March 2017
#
#	This script prepares the environment for node tests and then
#	executes the test driver.

# Test configuration
CASE=def_ch
QUEUE=special
PROJ=SCSG0001
COMPVER=intel/16.0.3
MPIVER=mpt/2.15f
NCVER=netcdf/4.4.1.1
PYVER=python/2.7.13

# Prepare module environment
module purge
module lo ncarenv $COMPVER $NCVER $MPIVER $PYVER

# Run driver script
python driver.py PBS -c $CASE -q $QUEUE -p $PROJ
