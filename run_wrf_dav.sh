#!/bin/bash
#
# ===== WRF DAV NODE TEST
#
#   Run a short 149 timestep WRF restart simulation.
#
#	Maintainer: Brian Vanderwende
#	Revised:    15:53, 26 Feb 2019

# Test configuration
CASE=wrf
ACCOUNT=SCSG0001

# Run nodetester across all nodes
./nodetester --machine dav --queue system --account $ACCOUNT $CASE
