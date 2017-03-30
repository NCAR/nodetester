# nodetester
A system stability test script for Yellowstone and Cheyenne that runs simple node-pair test jobs.

## How to use
To use the node tester, simply navigate to `/glade/p/work/csgteam/nodetester`. From there, run one of the starter scripts, either `run_*_ys.sh` or `run_*_ch.sh`.

### What happens next?

The script will submit short batch jobs to pairs of nodes for every node in the respective system's special queue. Note that it will take LSF/PBS some time to submit all of the jobs, so the entire script should run in about 20-30 minutes.

When finished, the script will list any node-pairs that reported errors, and provide the path for all result files - in your/csgteam's scratch space.

### How reservations are handled

The way the script handles reservations depends on which scheduler is being used. As PBS treats reservations as a queue, you are able to submit to reservation queues when using it.

If you submit a standard queue (e.g., special), the script will submit jobs to every node in the queue, even if they are reserved. If you are using PBS and submitting as csgteam, you can use the *--force* option to make PBS run the jobs. Note that if existing jobs are running on the reserved nodes, they will be killed with that option.

## Available test cases

At the moment, the following test cases are available in the csgteam install of nodetester. If you would like to contribute a case, please prepare it for csgteam and document its usage here.

### WRF case details

*Designer: Brian*

This case uses version 3.8.1 of WRF, built with the following:

* Intel Compiler v16.0.3
* IBM POE (Yellowstone) / SGI MPT 2.15f (Cheyenne)
* NetCDF v4.4.1 (Yellowstone) / NetCDF v4.4.1.1 (Cheyenne)

The case runs for three hours of simulation time across a 425x300x35 grid point domain. Two I/O operations occur - loading restart and boundary data and writing one output file. In total, 149 timesteps of model integration are run. Basic physics options are enabled.

**Run scripts: run_wrf_ys.sh and run_wrf_ch.sh**
