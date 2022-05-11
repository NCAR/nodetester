# nodetester
A script to test node integrity using simple n-node tests with commonly used applications.

## How to use
To use the node tester,navigate to `/glade/work/csgteam/nodetester`. From there, you can start the node tester in one of two ways. Pre-configured launch scripts exist in the format `run_<CASE>_<MACHINE>.sh`. Alternatively, you may invoke `nodetester` manually:

```
Usage: nodetester [options] CASE

This script will submit and monitor a selected node test using
the specified machine configuration.

Options:
    -a, --account       the account/project code to which jobs are charged
    -f, --force         submit node tests even if requested nodes are not free
    -h, --help          display this help and exit
    -m, --machine       which machine to test (cheyenne or dav)
    -n, --nodes         the number of nodes to test (-1 for all available)
    -o, --options       specify any other scheduler options for the main job
    -p, --path          override the default path for test output
    -q, --queue         the queue on which jobs are run
    --reservation       reservation you wish to use (optional name after =)
    --route             specify a routing queue to submit to (dav)
    -s, --seed          specify the seed used to pair nodes
```

### What happens next?

The script will submit a single batch job that will launch MPI runs on n-number of nodes for every requested node in the chosen queue. Note that it will take GPFS some time to create run directories for all of the runs, so please be patient for large node counts. If there are an odd number of nodes, relative to the node-per-run setting of that test case, an extra run will be performed to ensure complete coverage.

When finished, the script will list any nodes that reported errors, and provide the path for all result files - in your/csgteam's scratch space. The path will look something like `/glade/scratch/$USER/nodetests/CASE/TIME`. The contents of this directory depend on the case you are running, but all cases will contain the following files of note:

* main.log - recorded status updates from the main script
* runs - directories containing each individual run
* pass/fail - inventories of runs in each status

## Available test cases

At the moment, the following test cases are available in the csgteam install of nodetester. If you would like to contribute a case, please prepare it for csgteam and document its usage here.

### WRF Pairwise case details

*Designer: Brian*
*Systems:  Cheyenne, Casper*
*Nodes:    2*

This case uses version 4.4 of WRF, built with the default modules on each system.

The case runs for three hours of simulation time across a 425x300x35 grid point domain. Two I/O operations occur - loading restart and boundary data and writing one output file. In total, 149 timesteps of model integration are run. Basic physics options are enabled.

**Run scripts: run_wrf_chey.sh, run_wrf_dav.sh**

#### Rebuilding the WRF case

If the system software is upgraded or the case files are missing, you can recreate the case files using the "setup.sh" script located within `cases/wrf/setup/`. Note that this script will build and run WRF, so it will take upwards of an hour to complete. It's best to run it before you need to test!

### MiniWeather case details

*Designer: Brian*
*Systems:  Casper*
*Nodes:    2*

This case runs a GPU job using the OpenACC Fortran version of the MiniWeather app. The number of time steps and timings are verified. No I/O testing is done with this test.
