#!/bin/bash
#
# ===== WRF DAV NODE TEST
#
#   Run a short OpenACC GPU code
#
#	Maintainer: Brian Vanderwende
#	Revised:   22:28, 25 Jul 2021

# Test configuration
CASE=miniwx
ACCOUNT=SCSG0001

# Run nodetester across all nodes
bin/nodetester --machine dav --route casper --queue v100 --account $ACCOUNT $CASE
