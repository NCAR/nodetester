#!/bin/bash
#
# ===== WRF DAV NODE TEST
#
#   Run a short 149 timestep WRF restart simulation.
#
#	Maintainer: Brian Vanderwende
#	Revised:   22:42, 20 Jul 2021

# Test configuration
CASE=wrf
ACCOUNT=SCSG0001

# Run nodetester across all nodes
bin/nodetester --machine dav --queue system --account $ACCOUNT $CASE
