# WRF_nodetest
A system stability test script for Yellowstone and Cheyenne that uses WRF jobs

## How to use
To use the WRF node tester, simply navigate to `/glade/p/work/csgteam/WRF_nodetest`. From there, run one of the starter scripts, either `run_yellowstone.sh` or `run_cheyenne.sh`.

### What happens next?

The script will submit short WRF jobs to pairs of nodes for every node in the respective system's special queue. Note that it will take LSF/PBS some time to submit all of the jobs, so the entire script should run in about 20-30 minutes.

When finished, the script will list any node-pairs that reported errors, and provide the path for all result files - in your/csgteam's scratch space.

## WRF case details

The case uses version 3.8.1 of WRF, built with the following:

* Intel Compiler v16.0.3
* IBM POE (Yellowstone) / SGI MPT 2.15f (Cheyenne)
* NetCDF v4.4.1 (Yellowstone) / NetCDF v4.4.1.1 (Cheyenne)

The case runs for three hours of simulation time across a 425x300x35 grid point domain. Two I/O operations occur - loading restart and boundary data and writing one output file. In total, 149 timesteps of model integration are run. Basic physics options are enabled.
