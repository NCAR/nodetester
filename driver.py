# -----
#	driver.py
#	Author:		Brian Vanderwende
#	Revised:	27 March, 2017
#
#	This script queries available nodes, assigns node pairs, and runs a job
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
clo_dict	= {	"batch"		: ["batch system to use (PBS or LSF)"],
				"project"	: ["project allocation to use for jobs","SCSG0001"],
				"queue"		: ["queue on which tests are submitted","caldera"],
				"nodes"		: ["search string for nodes",'[a-z]'],
				"case"		: ["name of test case to execute","test_ca"],
				"force"		: ["force jobs to run on reserved nodes (PBS only)","False"]}

# -----
# Local data structures
# -----

class job(object):
	def __init__(self, nodes = ['',''], rstat = False):
		self.name   = nodes[0].split('-')[0] + '-' + nodes[1].split('-')[0]
		self.jobid 	= ''
		self.nodes 	= nodes
		self.path	= self.name
		self.result = self.name
		self.rstat	= rstat
		self.done	= False
	
	def set_rootdir(root_path, tid):
		self.path 	= '/'.join((root_path, tid, self.path))
		self.result	= '/'.join((root_path, tid, "results", self.result))

# -----
# Local routines
# -----

def parse_nodes_lsf(node_data, resv_nodes):
	nodes = [node.split()[0] for node in nodes]
	rstat = [node in resv_nodes for node in nodes]

	return nodes, rstat

def parse_nodes_pbs(queue, node_data):
	# Check if queue is a PBS reservation
	resv	= queue.startswith(('R','S'))
	nodes 	= []
	rstat	= []

	for item in node_data:
		if item[0] != ' ':
			node = [item]
		elif queue in item:
			if "resv" in item and resv:
				rstat += [True]
			else
				rstat += [False]

			nodes += node

	return nodes, rstat

def get_nodes(batch, queue, key):
	# Get raw node information from batch system
	if batch == "LSF":
		from sh import bhosts, brsvs
		node_data 		= grep('^' + key + ".*ok", _in = bhosts()).splitlines()
		nodes, rstat 	= parse_nodes_lsf(node_data, brsvs())
	elif batch == "PBS":
		from sh import pbsnodes
		node_data 		= grep("-E", '^' + key + "|state =|Qlist =|resv =",
							_in = pbsnodes("-a")).splitlines()
		nodes, rstat	= parse_nodes_pbs(queue, node_data)
	else:
		print "Error: {} is not a known batch system. Exiting ...".format(batch)
		sys.exit(1)
	
	return nodes, rstat

def create_jobs(nodes, resv):
	if len(nodes) % 2 == 0:
		pairs = zip(nodes[::2], nodes[::-2], resv[::2] and resv[::-2])
	else:
		pairs = zip(nodes[:-1:2], nodes[-2::-2], resv[:-1:2] and resv[:-1:-2])

	jobs = [job(nodes = list(item[:2]), rstat = item[2]) for item in pairs]

	# If odd number of nodes, add extra pair using first node and last
	if len(nodes) % 2 == 1:
		print "   Note: odd number of nodes... submitting extra job for final node"
		print "         This job may not start until others are finished execution!"
		jobs.append(job(nodes = [nodes[0], nodes[-1]], rstat = (resv[0] and resv[-1])))

	return jobs

def check_results(jobs, log):
	# Check for completed jobs and log errors
	for n in xrange(len(jobs)):
		if os.path.exists(jobs[n].result):
			with open(jobs[n].result) as rf:
				if "ERROR" in rf.read():
					log["errors"].append("   Errors detected - " + jobs[n].name)

				jobs[n].done = True

	# Remove non-active jobs
	jobs = [n for n in jobs if n.done]

	return jobs

def print_status(jobs, log):
	jobs				= check_results(jobs, log)
	log["num_active"] 	= len(jobs)
	pct_submit			= 100.0 * log["num_jobs"] / log["total_jobs"]
	num_done			= log["num_jobs"] - log["num_active"]
	pct_done			= 100.0 * num_done / log["total_jobs"]
	log["last_time"]	= time.time()
	
	tmp = os.system("clear")
	print "Time passed - {} seconds".format(int(log["last_time"] - log["init_time"]))
	print "   Total number of jobs in test  = {}".format(log["total_jobs"])
	print "   Number of jobs submitted      = {}".format(log["num_jobs"])
	print "   Number of queued/running jobs = {}".format(log["num_active"])
	print "   Number of finished jobs       = {}\n".format(num_done)
	print "   Percent submitted of total    = {:.1f}%".format(pct_submit)
	print "   Percent finished of total     = {:.1f}%\n".format(pct_done)
	print "Event Log:"
	print '\n'.join(log["errors"])

	return jobs

def submit_jobs(tid, jobs, args, log):
	main_dir = os.getcwd()

	for job in jobs[:]:
		# Create job directory
		job.set_rootdir(test_root, tid)
		cp(args.case, job.path)
		os.chdir(job.path)

		if args.batch == "LSF":
			from sh import bsub
			with open(job.path + "/run_test.lsf", 'r') as jf:
				bsub(_in = jf, m = ' '.join(job.nodes), P = args.project, q = args.queue)
		elif args.batch == "PBS":
			from sh import qsub
			sh = "select=" + '+'.join(["ncpus=36:mpiprocs=36:host={}".format(nid) 
					for nid in job.nodes])
			qsub("-l", sh, "-A",  args.project, "-q", args.queue, job.path + "/run_test.pbs")
		
		log["num_jobs"] += 1
		os.chdir(main_dir)

		# If it's been a while, check status
		if int(time.time() - log["last_time"]) >= 10:
			jobs = print_status(jobs, log)
		
	return jobs

def force_run(jobs, log):
	# Use qrun to force jobs to run if on reserved nodes
	from sh import qrun

	for job in jobs[:]:
		qrun("-H", "({})".format(")+(".join(job.nodes)))

		if int(time.time() - log["last_time"]) >= 10:
			jobs = print_status(jobs, log)
	
	return jobs

# -----
# Main execution
# -----

def main():
	# Define command-line arguments
	parser = argparse.ArgumentParser(prog = "driver.py",
				description = "Run small jobs to test node health.")

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
	nodes, rstat	= get_nodes(args.batch, args.nodes)
	jobs 			= create_jobs(nodes, rstat)
	total_jobs		= len(jobs)

	print "Submitting {} jobs to scheduler...".format(total_jobs)

	# Test logging
	log	= { "init_time" 	: time.time(),
			"num_jobs"		: 0,
			"num_active"	: 0,
			"total_jobs"	: total_jobs,
			"errors"		: []}
	log["last_time"] = log["init_time"]

	# Submit testing jobs and force them to run if requested
	jobs = submit_jobs(tid, jobs, args, log)

	if args.force:
		if args.batch = "PBS":
			jobs = force_run(jobs, log)
		else:
			print "Warning: cannot force jobs on res nodes in LSF. Ignoring ..."

	# Until jobs are done, keep checking results
	keep_going = True

	while keep_going:
		time.sleep(10)
		jobs = print_status(jobs, log)
		keep_going = log["num_active"] > 0
		
	print "\nNodetest complete!"
	print "Results in: {}".format(test_root + '/' + tid + "/results")

# Call the main function
if __name__ == "__main__":
	main()
