#!/bin/bash
#
#	run_wrf_ch.sh
#	Author:		Brian Vanderwende
#	Revised:	21 March 2017
#
#	This script prepares the environment for node tests and then
#	executes the test driver.

# Test configuration
CASE=wrf_ch
QUEUE=regular
ACCOUNT=SCSG0001
NODES=5

# Run nodetester
./nodetester -c $CASE -q $QUEUE -a $ACCOUNT -n $NODES
