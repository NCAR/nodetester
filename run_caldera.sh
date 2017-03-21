#!/bin/bash
#
#	run_tests.sh
#	Author:		Brian Vanderwende
#	Revised:	21 August 2016
#
#	This script prepares the environment for node tests and then
#	executes the test driver.

# Test configuration
CASE=def_ca
QUEUE=caldera
NODES=caldera
PROJ=SCSG0001
PYVER=python/2.7.7

# Prepare module environment
module reset
module lo $PYVER

# Run driver script
python driver.py LSF -c $CASE -q $QUEUE -n $NODES -p $PROJ
