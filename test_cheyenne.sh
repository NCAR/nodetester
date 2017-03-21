#!/bin/bash
#
#	run_cheyenne.sh
#	Author:		Brian Vanderwende
#	Revised:	21 August 2016
#
#	This script prepares the environment for node tests and then
#	executes the test driver.

# Test configuration
CASE=test_ch
QUEUE=special
NODES=r1i0n*
PROJ=SCSG0001
PYVER=python/2.7.13

# Prepare module environment
module reset >& /dev/null
module lo $PYVER

# Run driver script
python driver.py PBS -c $CASE -q $QUEUE -p $PROJ -n $NODES
