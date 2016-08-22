# -----
#	driver.py
#	Author:		Brian Vanderwende
#	Updated:	21 August 2016
#
#	This script queries available nodes, assigns node pairs, and runs a WRF job
#	on those pairs to test the integrity of the nodes and interconnects. The
#	script periodically checks the status of all node-pair jobs and reports
#	on completion percentages.
# -----

from plumbum import local
from datetime import datetime
import os, time, argparse 

# -----
# Hard-coded settings
# -----

test_root = "/glade/scratch/" + os.environ("USER") + "/nodetests"

# -----
# Global variables
# -----

log 		= []
clo_dict	= {	"project"	: ["project allocation to use for jobs","SCSG0001"],
				"queue"		: ["queue on which tests are submitted","caldera"],
				"nodes"		: ["search string for nodes",None],
				"case"		: ["name of test case to execute","def_ca"] }

# -----
# Local routines
# -----

def get_nodes(key):
	# Define interface to POSIX/LSF commands
	bhosts = local["bhosts"] | local["grep"][key]
	
	# Execute and store node/host names
	nodes = bhosts().splitlines()
	nodes = [node.split()[0] for node in nodes]

	return nodes

def create_pairs(nodes):
	if len(nodes) % 2 == 0:
		pairs = zip(nodes[::2], nodes[::-2])
	else:
		pairs = zip(nodes[:-1:2], nodes[-2::-2])

	pairs = [list(item) for item in pairs]

	# If odd number of nodes, add extra pair using first node and last
	if len(nodes) % 2 == 1:
		print "   Warning: odd number of nodes... submitting extra job to test"
		print "            final node. This job may not start until others are"
		print "            finished execution!"
		pairs.append([nodes[0], nodes[-1]])

	return pairs

def init_tests(tid, pairs, args):
	# Define interface to POSIX/LSF commands
	copy = local["cp"]["-r"]
	bsub = local["bsub"]
	test = local["echo"]

	# List containing pair job name
	jobs = []

	# For each pair, create directory from case
	for nodes in pairs:
		name = nodes[0].split('-')[0] + '-' + nodes[1].split('-')[0]
		jobs.append(test_root + '/' + tid + "/results/" + name)
		nodes.append(test_root + '/' + tid + '/'+ name)
		copy(args.case, nodes[2])

	# For each pair, submit job
	for nodes in pairs:
		(bsub < (nodes[2] + "/runwrf.job"))("-q",args.queue,"-P",args.project,	\
				"-m",' '.join(nodes[0:2]),"-cwd",nodes[2])

	return jobs

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

# -----
# Main execution
# -----

def main():
	# Define command-line arguments
	parser = argparse.ArgumentParser(prog = "driver.py",						\
			description = "Run WRF jobs to test system integrity.",				\
			usage = "python %(prog)s [options]")

	for key, values in sorted(clo_dict.iteritems()):
		parser.add_argument('-' + key[0], "--" + key, help = values[0],			\
				default = values[1])

	# Handle optional arguments
	args = parser.parse_args()

	if not args.nodes:
		args.nodes = args.queue

	args.nodes += ".*ok"

	print "Beginning node test..."
	print "   Case    = {}".format(args.case)
	print "   Queue   = {}".format(args.queue)
	print "   Nodes   = {}".format(args.nodes)
	print "   Project = {}".format(args.project)

	# Create directory for test
	tid = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
	os.makedirs(test_root + '/' + tid + "/results")

	print "\nCase created in: {}".format(test_root + '/' + tid)

	# Get node pairs
	nodes = get_nodes(args.nodes)
	pairs = create_pairs(nodes)

	print "Submitting {} jobs to scheduler...".format(len(pairs))

	# Prepare pair run directories and submit jobs
	jobs = init_tests(tid, pairs, args)

	# Until jobs are done, keep checking results
	num_total	= len(jobs)
	num_active 	= num_total
	init_time	= time.time()

	print "Beginning logging. Please wait..."

	while num_active > 0:
		time.sleep(10)
		
		jobs 		= check_results(jobs)
		num_active 	= len(jobs)
		pct_done	= 100.0 * (num_total - num_active) / num_total

		tmp = os.system("clear")
		print "Time passed - {} seconds".format(int(time.time() - init_time))
		print "   Total number of jobs  = {}".format(num_total)
		print "   Number of active jobs = {}".format(num_active)
		print "   Percent complete      = {}".format(pct_done)
		print "\nEvent Log:"
		print '\n'.join(log)

	print "\nNodetest complete!"
	print "Results in: {}".format(test_root + '/' + tid + "/results")

# Call the main function
if __name__ == "__main__":
	main()
