#!/bin/bash
#
# ===== WRF CHEYENNE NODE TEST
#
#   Run a short 149 timestep WRF restart simulation.
#
#	Maintainer: Brian Vanderwende
#	Revised:   17:18, 18 Jul 2021

# Test configuration
CASE=wrf
ACCOUNT=SCSG0001

# Run nodetester
bin/nodetester --machine cheyenne --queue system --account $ACCOUNT $CASE
