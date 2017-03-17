#!/bin/bash
#
#	run_yellowstone.sh
#	Author:		Brian Vanderwende
#	Updated:	21 August 2016
#
#	This script prepares the environment for node tests and then
#	executes the test driver.

# Test configuration
CASE=def_ys
QUEUE=special
NODES=ys[0-6]
PROJ=SCSG0001

# Test environment
COMPVER=intel/12.1.5
NCVER=netcdf/4.3.0
PYVER=python/2.7.7

# Prepare module environment
module purge
module lo ncarenv ncarbinlibs $COMPVER ncarcompilers $NCVER $PYVER

# Run driver script
python driver.py -c $CASE -q $QUEUE -n $NODES -p $PROJ
