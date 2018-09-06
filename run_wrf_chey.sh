#!/bin/bash
#
# ===== WRF CHEYENNE NODE TEST
#
#   Run a short 149 timestep WRF restart simulation.
#
#	Maintainer: Brian Vanderwende
#	Revised:    09:11, 06 Sep 2018

# Test configuration
CASE=wrf
ACCOUNT=SCSG0001

# Run nodetester
./nodetester --machine chey --queue system --account $ACCOUNT --nodes -1 $CASE
