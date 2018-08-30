# nodetester
A script to test node integrity using simple node-pair tests with commonly used applications.

## How to use
To use the node tester,navigate to `/glade/work/csgteam/nodetester`. From there, you can start the node tester in one of two ways. Pre-configured launch scripts exist in the format `run_<CASE>_<MACHINE>.sh`. Alternatively, you may invoke `nodetester` manually:

```
nodetester [options] CASE

Options:
    -a, --account   the account/project code to which jobs are charged
    -f, --force     submit node tests even if requested nodes are not free
    -h, --help      display this help and exit
    -n, --nodes     the number of nodes to test (-1 for all available)
    -p, --path      override the default path for test output
    -q, --queue     the queue on which jobs are run
```

### What happens next?

The script will submit a single batch job that will launch MPI runs on pairs of nodes for every requested node in the chosen queue. Note that it will take GPFS some time to create run directories for all of the runs, so please be patient for large node counts.

When finished, the script will list any nodes that reported errors, and provide the path for all result files - in your/csgteam's scratch space.

### How reservations are handled

Reservation support is currently disabled in this version of the nodetester, as PBS's reservation system is fundamentally broken. Should that situation change, reservation support will be re-implemented.

## Available test cases

At the moment, the following test cases are available in the csgteam install of nodetester. If you would like to contribute a case, please prepare it for csgteam and document its usage here.

### WRF case details

*Designer: Brian*
*Systems:  Cheyenne*

This case uses version 3.8.1 of WRF, built with the following:

* Intel Compiler v16.0.3
* SGI MPT 2.15f
* NetCDF v4.4.1.1

The case runs for three hours of simulation time across a 425x300x35 grid point domain. Two I/O operations occur - loading restart and boundary data and writing one output file. In total, 149 timesteps of model integration are run. Basic physics options are enabled.

**Run scripts: run_wrf_ch.sh**
