# -----
#	driver.py
#	Author:		Brian Vanderwende
#	Revised:	21 August 2016
#
#	This script queries available nodes, assigns node pairs, and runs a WRF job
#	on those pairs to test the integrity of the nodes and interconnects. The
#	script periodically checks the status of all node-pair jobs and reports
#	on completion percentages.
# -----

from sh import grep, cp
from datetime import datetime
import sys, os, time, argparse 

# -----
# Hard-coded settings
# -----

test_root = "/glade/scratch/" + os.environ["USER"] + "/nodetests"

# -----
# Global variables
# -----

cp 			= cp.bake("-r")
log 		= []
init_time	= 0
last_time	= 0
num_jobs	= 0
clo_dict	= {	"batch"		: ["batch system to use (PBS or LSF)"],
				"project"	: ["project allocation to use for jobs","SCSG0001"],
				"queue"		: ["queue on which tests are submitted","caldera"],
				"nodes"		: ["search string for nodes",'.'],
				"case"		: ["name of test case to execute","def_ca"] }

# -----
# Local routines
# -----

def get_nodes(batch, key):
	# Execute and store node/host names
	if batch == "LSF":
		from sh import bhosts as host_list
		key += ".*ok"
	elif batch == "PBS":
		from sh import pbsnodes as host_list
		dead_hosts 	= host_list.bake("-l")
		host_list	= host_list.bake("-a")
	else:
		print "Error: {} is not a known batch system. Exiting ...".format(batch)
		sys.exit(1)
		
	nodes = grep(key, _in = grep("-v","^    ", _in = host_list())).splitlines()
	nodes = [node.split()[0] for node in nodes]
	
	# If PBS, need to find and remove dead hosts
	if batch == "PBS":
		dead_nodes 	= dead_hosts().splitlines()
		dead_nodes 	= [dead_node.split()[0] for dead_node in dead_nodes]
		nodes		= [node for node in nodes if node not in dead_nodes]
	
	return nodes

def create_pairs(nodes):
	if len(nodes) % 2 == 0:
		pairs = zip(nodes[::2], nodes[::-2])
	else:
		pairs = zip(nodes[:-1:2], nodes[-2::-2])

	pairs = [list(item) for item in pairs]

	# If odd number of nodes, add extra pair using first node and last
	if len(nodes) % 2 == 1:
		print "   Note: odd number of nodes... submitting extra job for final node"
		print "         This job may not start until others are finished execution!"
		pairs.append([nodes[0], nodes[-1]])

	return pairs

def check_results(jobs):
	# Check for completed jobs and log errors
	for n in xrange(len(jobs)):
		if os.path.exists(jobs[n]):
			with open(jobs[n]) as file:
				result = file.read()

				if "ERROR" in result:
					log.append("   Errors detected - " + jobs[n].split('/')[-1])

				jobs[n] = 'r'

	# Remove non-active jobs
	jobs = [n for n in jobs if n != 'r']

	return jobs

def print_status(jobs):
	global num_jobs, last_time, init_time, log
	jobs 		= check_results(jobs)
	num_active 	= len(jobs)
	pct_done	= 100.0 * (num_jobs - num_active) / num_jobs
	last_time	= time.time()
	
	tmp = os.system("clear")
	print "Time passed - {} seconds".format(int(last_time - init_time))
	print "   Total jobs submitted  = {}".format(num_jobs)
	print "   Number of active jobs = {}".format(num_active)
	print "   Percent complete      = {}".format(pct_done)
	print "\nEvent Log:"
	print '\n'.join(log)

	return jobs

def init_tests(tid, pairs, args):
	global num_jobs, last_time
	jobs 		= []
	main_dir	= os.getcwd()

	for nodes in pairs:
		# Create job directory
		name = nodes[0].split('-')[0] + '-' + nodes[1].split('-')[0]
		nodes.append(test_root + '/' + tid + '/'+ name)
		cp(args.case, nodes[2])
		os.chdir(nodes[2])

		if args.batch == "LSF":
			from sh import bsub
			with open(nodes[2] + "/runwrf.job", 'r') as jf:
				bsub(_in = jf, m = ' '.join(nodes[0:2]), P = args.project, q = args.queue)
		elif args.batch == "PBS":
			from sh import qsub
			sh = "select=" + '+'.join(["ncpus=36:mpiprocs=36:host={}".format(nid) 
					for nid in nodes[0:2]])
			qsub("-l", sh, "-A",  args.project, "-q", args.queue, nodes[2] + "/runwrf.job")
		
		# If it's been a while, check status
		num_jobs += 1
		os.chdir(main_dir)
		jobs.append(test_root + '/' + tid + "/results/" + name)

		if int(time.time() - last_time) >= 10:
			jobs = print_status(jobs)
		
	return jobs

# -----
# Main execution
# -----

def main():
	global init_time, last_time

	# Define command-line arguments
	parser = argparse.ArgumentParser(prog = "driver.py",
				description = "Run WRF jobs to test system integrity.")

	for key, values in sorted(clo_dict.iteritems()):
		if len(values) == 1:
			parser.add_argument(key, help = values[0])
		else:
			parser.add_argument('-' + key[0], "--" + key, help = values[0],
					default = values[1])

	# Handle arguments
	args 		= parser.parse_args()
	args.batch 	= args.batch.upper()

	print "Beginning node test..."
	print "   Batch system  = {}".format(args.batch)
	print "   Case          = {}".format(args.case)
	print "   Queue         = {}".format(args.queue)
	print "   Nodes         = {}".format(args.nodes)
	print "   Project       = {}".format(args.project)

	# Create directory for test
	tid = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
	os.makedirs(test_root + '/' + tid + "/results")

	print "\nCase created in: {}".format(test_root + '/' + tid)

	# Get node pairs
	nodes = get_nodes(args.batch, args.nodes)
	pairs = create_pairs(nodes)

	print "Submitting {} jobs to scheduler...".format(len(pairs))

	# Prepare pair run directories and submit jobs
	init_time	= time.time()
	last_time	= init_time
	jobs 		= init_tests(tid, pairs, args)

	# Until jobs are done, keep checking results
	while len(jobs) > 0:
		time.sleep(10)
		jobs = print_status(jobs)
		
	print "\nNodetest complete!"
	print "Results in: {}".format(test_root + '/' + tid + "/results")

# Call the main function
if __name__ == "__main__":
	main()
