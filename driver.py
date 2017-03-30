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

username	= os.environ["USER"]
test_root 	= "/glade/scratch/" + username + "/nodetests"

# -----
# Global variables
# -----

cp 			= cp.bake("-r")
clo_dict	= {	"batch"		: ["batch system to use (PBS or LSF)"],
				"project"	: ["project allocation to use for jobs","SCSG0001"],
				"queue"		: ["queue on which tests are submitted","caldera"],
				"nodes"		: ["search string for nodes",'[a-z].*'],
				"case"		: ["name of test case to execute","test_ca"],
				"force"		: ["force jobs to run on reserved nodes (PBS only)","False"]}

# -----
# Local data structures
# -----

class job(object):
	def __init__(self, nodes = ['',''], rstat = False, wait = False):
		self.name   = nodes[0].split('-')[0] + '-' + nodes[1].split('-')[0]
		self.jobid 	= ''
		self.nodes 	= nodes
		self.path	= self.name
		self.result = self.name
		self.rstat	= rstat
		self.done	= False
		self.wait	= wait
	
	def set_rootdir(self, root_path, tid):
		self.path 	= '/'.join((root_path, tid, self.path))
		self.result	= '/'.join((root_path, tid, "results", self.result))
	
	def __eq__(self, other):
		return self.jobid == other.jobid
	
# -----
# Local routines
# -----

def parse_nodes_lsf(node_data, resv_nodes):
	nodes = [node.split()[0] for node in node_data]
	rstat = [node in resv_nodes for node in nodes]

	return nodes, rstat

def parse_nodes_pbs(queue, node_data):
	# Check if queue is a PBS reservation
	resv	= queue.startswith(('R','S'))
	node	= None
	nodes 	= []
	rstat	= []

	for item in node_data:
		if item[0] != ' ':
			node 	= [item]
			is_resv = [False]
		elif node:
			if "resv" in item and not resv:
				is_resv = [True]

			if queue in item:
				nodes 	+= 	node
				rstat	+= 	is_resv
				node	=	None

	return nodes, rstat

def get_nodes(batch, queue, key):
	# Get raw node information from batch system
	if batch == "LSF":
		from sh import bhosts, brsvs
		node_data 		= grep("-w", '^' + key + " .*ok", _in = bhosts()).splitlines()
		nodes, rstat 	= parse_nodes_lsf(node_data, brsvs())
	elif batch == "PBS":
		from sh import pbsnodes
		node_data 		= grep("-w", "-E", '^' + key + "|Qlist =|resv =",
							_in = pbsnodes("-a")).splitlines()
		nodes, rstat	= parse_nodes_pbs(queue, node_data)
	else:
		print "\nERROR:   {} is not a known batch system. Exiting ...".format(batch)
		sys.exit(1)
	
	return nodes, rstat

def create_jobs(nodes, resv):
	num_nodes = len(nodes)

	if num_nodes % 2 == 0:
		pairs = zip(nodes[::2], nodes[::-2], resv[::2] and resv[::-2])
	else:
		pairs = zip(nodes[:-1:2], nodes[-2::-2], resv[:-1:2] and resv[-2::-2])

	jobs = [job(nodes = list(item[:2]), rstat = item[2]) for item in pairs]

	# If odd number of nodes, add extra pair using first node and last
	if num_nodes % 2 == 1:
		print "\nNOTICE:  Odd number of nodes... submitting extra job for final node"
		print "         This job may not start until others are finished execution!\n"
		jobs.append(job(nodes = [nodes[0], nodes[-1]],
				rstat = (resv[0] and resv[-1]), wait = True))

	return jobs

def check_results(jobs, log):
	# Check for completed jobs and log errors
	for job in jobs:
		if not job.done and os.path.exists(job.result):
			with open(job.result) as rf:
				if "ERROR" in rf.read():
					log["errors"].append("   Errors detected - " + job.name)
					log["num_errors"] += 1

			job.done 			= 	True
			log["num_active"] 	-= 	1

def print_status(jobs, log):
	check_results(jobs, log)
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

def submit_jobs(tid, jobs, args, log):
	main_dir = os.getcwd()

	for job in jobs:
		# Create job directory
		job.set_rootdir(test_root, tid)
		cp(args.case, job.path)
		os.chdir(job.path)

		if args.batch == "LSF":
			from sh import bsub
			with open(job.path + "/run_case.lsf", 'r') as jf:
				temp 		= bsub(_in = jf, m = ' '.join(job.nodes),
								P = args.project, q = args.queue)
				job.jobid	= temp.split('<')[1].split('>')[0]
		elif args.batch == "PBS":
			from sh import qsub
			sh 			= "select=" + '+'.join(["ncpus=36:mpiprocs=36:host={}".format(nid) 
							for nid in job.nodes])
			temp 		= qsub("-l", sh, "-A",  args.project, "-q", args.queue,
							job.path + "/run_case.pbs")
			job.jobid	= temp.split('.')[0]
		
		log["num_jobs"] 	+= 1
		log["num_active"]	+= 1
		os.chdir(main_dir)

		# If it's been a while, check status
		if int(time.time() - log["last_time"]) >= 10:
			print_status(jobs, log)

def force_run(jobs, log):
	# Use qrun to force jobs to run if on reserved nodes
	from sh import qrun

	for job in jobs:
		# Need to make sure last job doesn't clobber first job 
		if job.wait:
			while not jobs[0].done:
				time.sleep(10)
				print_status(jobs, log)
		
		qrun("-H", "({})".format(")+(".join(job.nodes)), job.jobid)

		if int(time.time() - log["last_time"]) >= 10:
			print_status(jobs, log)

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
		elif values[1] == "False":
			parser.add_argument('-' + key[0], "--" + key, help = values[0],
					action = "store_true")
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
	tid = datetime.now().strftime("%Y-%m-%d_%H%M%S")
	os.makedirs(test_root + '/' + tid + "/results")

	print "\nCase created in: {}".format(test_root + '/' + tid)

	# Get node pairs
	nodes, rstat	= get_nodes(args.batch, args.queue, args.nodes)
	jobs 			= create_jobs(nodes, rstat)
	total_jobs		= len(jobs)

	print "Submitting {} jobs to scheduler...".format(total_jobs)

	# Test logging
	log	= { "init_time" 	: time.time(),
			"num_jobs"		: 0,
			"num_active"	: 0,
			"total_jobs"	: total_jobs,
			"errors"		: [],
			"num_errors"	: 0 }
	log["last_time"] = log["init_time"]

	# Submit testing jobs and force them to run if requested
	submit_jobs(tid, jobs, args, log)

	if args.force:
		if args.batch == "PBS":
			if username == "csgteam":
				print "\nWARNING: Force option will terminate any jobs currently running"
				print "         on the selected nodes. Do you wish to proceed?\n"
				confirm = raw_input('Type "yes" to continue: ')

				if confirm.lower() == "yes":
					force_run(jobs, log)
				else:
					print "\nNOTICE:  User did not emphatically confirm force. Ignoring ...\n"
			else:
				print "\nNOTICE:  Force must be run as csgteam. Ignoring ...\n"
		else:
			print "\nNOTICE:  Can only force jobs using PBS. Ignoring ...\n"

	# Until jobs are done, keep checking results
	keep_going = True

	while keep_going:
		time.sleep(10)
		print_status(jobs, log)
		keep_going = log["num_active"] > 0
		
	print "\n   Failure rate = {:.1f}%".format(100.0 * log["num_errors"] / log["num_jobs"])
	print "\nNodetest complete!"
	print "Results in: {}".format(test_root + '/' + tid + "/results")

# Call the main function
if __name__ == "__main__":
	main()
