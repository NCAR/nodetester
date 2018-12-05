#!/bin/bash
#
# ===== WRF DAV NODE TEST
#
#   Run a short 149 timestep WRF restart simulation.
#
#	Maintainer: Brian Vanderwende
#	Revised:    09:13, 04 Oct 2018

# Test configuration
CASE=wrf
ACCOUNT=SCSG0001
CNC=$(sinfo -N -t IDLE | grep casper | wc -l)
ONC=$(sinfo -N -t IDLE | grep -e geyser -e caldera -e pronghorn | wc -l)

# Run nodetester across all nodes
#./nodetester --machine dav --queue system --account $ACCOUNT $CASE

# Run nodetester on Casper
#./nodetester --machine dav --queue system --options "-C casper" --nodes $CNC --account $ACCOUNT $CASE

# Run nodetester on old DAV (geyser, caldera, pronghorn)
#./nodetester --machine dav --queue system --options "-C geyser|caldera|pronghorn" --nodes $ONC --account $ACCOUNT $CASE
