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
def_path 	= "/glade/scratch/" + username + "/nodetests"

# -----
# Global variables
# -----

cp 			= cp.bake("-r")
clo_dict	= {	"batch"		: ["batch system to use (PBS or LSF)"],
				"account"	: ["project account to use for jobs","SCSG0001"],
				"queue"		: ["queue on which tests are submitted","caldera"],
				"nodes"		: ["search string for nodes",'[a-z].*'],
				"case"		: ["name of test case to execute","test_ca"],
				"force"		: ["force jobs to run on reserved nodes (PBS only)","False"],
				"path"		: ["path where job output is written",def_path],
				"verbose"	: ["write more messages to logging file","False"]}

verbose		= False
log_file	= "driver.log"

# -----
# Local data structures
# -----

class job(object):
	def __init__(self, nodes = ['',''], resv = False, wait = False):
		self.name   = nodes[0].split('-')[0] + '-' + nodes[1].split('-')[0]
		self.jobid 	= ''
		self.nodes 	= nodes
		self.path	= self.name
		self.result = self.name
		self.resv	= resv
		self.done	= False
		self.wait	= wait
	
	def set_rootdir(self, root_path):
		self.path 	= os.path.join(root_path, self.path)
		self.result	= os.path.join(root_path, "results", self.result)
	
	def __eq__(self, other):
		return self.jobid == other.jobid
	
# -----
# Local routines
# -----

def log_message(level, text):
	prefix = "({})".format(datetime.now().isoformat())
	
	if verbose or level == 0:
		log_file.write("{}  {}\n".format(prefix, text[0]))
		prefix = ' ' * len(prefix)

		for line in text[1:]:
			log_file.write("{}  {}\n".format(prefix, line))

	if level == 0:
		for line in text:
			print line

def parse_nodes_lsf(node_data, resv_nodes):
	log_message(1, ["Entering parse_nodes_lsf to parse LSF node information"])

	nodes = [node.split()[0] for node in node_data]
	rstat = [node in resv_nodes for node in nodes]

	return nodes, rstat

def parse_nodes_pbs(queue, node_data):
	log_message(1, ["Entering parse_nodes_pbs to parse PBS node information"])

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
	log_message(1, ["Entering get_nodes to get node information from {}".format(batch)])

	# Get raw node information from batch system
	if batch == "LSF":
		from sh import bhosts, brsvs
		node_data 		= grep("-w", '^' + key + ".* ok", _in = bhosts()).splitlines()
		nodes, rstat 	= parse_nodes_lsf(node_data, brsvs())
	elif batch == "PBS":
		from sh import pbsnodes
		node_data 		= grep("-w", "-E", '^' + key + "|Qlist =|resv =",
							_in = pbsnodes("-a")).splitlines()
		nodes, rstat	= parse_nodes_pbs(queue, node_data)
	else:
		log_message(0, ["","ERROR:   {} is not a known batch system. Exiting ...".format(batch)])
		sys.exit(1)
	
	return nodes, rstat

def create_jobs(nodes, resv):
	num_nodes = len(nodes)
	log_message(1, ["Entering create_jobs and generating node pairs"])

	if num_nodes % 2 == 0:
		pairs = zip(nodes[::2], nodes[::-2], resv[::2] and resv[::-2])
	else:
		pairs = zip(nodes[:-1:2], nodes[-2::-2], resv[:-1:2] and resv[-2::-2])

	jobs = [job(nodes = list(item[:2]), resv = item[2]) for item in pairs]

	# If odd number of nodes, add extra pair using first node and last
	if num_nodes % 2 == 1:
		message = [	"","NOTICE:  Odd number of nodes... submitting extra job for final node",
					"         This job may not start until others are finished execution!",""]
		log_message(0, message)
		jobs.append(job(nodes = [nodes[0], nodes[-1]],
				resv = (resv[0] and resv[-1]), wait = True))

	return jobs

def check_results(jobs, log):
	log_message(1, ["Entering check_results to look for finished jobs"])

	# Check for completed jobs and log errors
	for job in jobs:
		if not job.done and os.path.exists(job.result):
			log_message(1, ["Job {} has completed and written results".format(job.name)])

			with open(job.result) as rf:
				if "ERROR" in rf.read():
					log_message(1, ["Errors detected in job {}".format(job.name)])
					log["errors"].append("   Errors detected - " + job.name)
					log["num_errors"] += 1

			job.done 			= 	True
			log["num_active"] 	-= 	1

def print_status(jobs, log):
	log_message(1, ["Entering print_status to output job log"])
	check_results(jobs, log)
	pct_submit			= 100.0 * log["num_jobs"] / log["total_jobs"]
	num_done			= log["num_jobs"] - log["num_active"]
	pct_done			= 100.0 * num_done / log["total_jobs"]
	log["last_time"]	= time.time()
	elapsed				= int(log["last_time"] - log["init_time"])
	
	tmp 	= os.system("clear")
	message = [	"Last updated at {}".format(datetime.now()),
				"   Time passed in seconds        = {}".format(elapsed),
				"   Total number of jobs in test  = {}".format(log["total_jobs"]),
				"   Number of jobs submitted      = {}".format(log["num_jobs"]),
				"   Number of queued/running jobs = {}".format(log["num_active"]),
				"   Number of finished jobs       = {}\n".format(num_done),
				"   Percent submitted of total    = {:.1f}%".format(pct_submit),
				"   Percent finished of total     = {:.1f}%\n".format(pct_done),
				"Event Log:"]
	message.extend(log["errors"])
	log_message(0, message)

def submit_jobs(jobs, args, log):
	log_message(1, ["Entering submit_jobs to schedule node tests"])
	main_dir = os.getcwd()

	for job in jobs:
		# Create job directory
		job.set_rootdir(args.path)
		cp(args.case, job.path)
		os.chdir(job.path)

		if args.batch == "LSF":
			from sh import bsub
			with open(os.path.join(job.path, "run_case.lsf"), 'r') as jf:
				temp 		= bsub(_in = jf, m = ' '.join(job.nodes),
								P = args.account, q = args.queue)
				job.jobid	= temp.split('<')[1].split('>')[0]
				log_message(1, ["Job {} submitted with bsub".format(job.name)])
		elif args.batch == "PBS":
			from sh import qsub
			sel_hosts	= "select=" + '+'.join(["ncpus=36:mpiprocs=36:host={}".format(nid) 
							for nid in job.nodes])

			if args.force:
				temp	= qsub("-l", sel_hosts, "-A",  args.account, "-q", args.queue,
							"-h", os.path.join(job.path, "run_case.pbs"))
			else:
				temp	= qsub("-l", sel_hosts, "-A",  args.account, "-q", args.queue,
							os.path.join(job.path, "run_case.pbs"))
			
			job.jobid	= temp.split('.')[0]
			log_message(1, ["Job {} submitted with qsub (hold = {})".format(job.name, args.force)])
		
		log["num_jobs"] 	+= 1
		log["num_active"]	+= 1
		os.chdir(main_dir)

		# If it's been a while, check status
		if int(time.time() - log["last_time"]) >= 10:
			print_status(jobs, log)

		log_message(1, ["Finished submitting {} jobs".format(log["num_jobs"])])

def force_run(jobs, log):
	log_message(1, ["Entering force_run to remove hold from PBS jobs"])

	# Use qrun to force jobs to run if on reserved nodes
	from sh import qrun

	for job in jobs:
		# Need to make sure last job doesn't clobber first job 
		if job.wait:
			while not jobs[0].done:
				log_message(1, ["Waiting for job {} to finish".format(jobs[0].name)])
				time.sleep(10)
				print_status(jobs, log)
		
		qrun("-H", "({})".format(")+(".join(job.nodes)), job.jobid)

		log_message(1, ["Hold released on job {}".format(job.name)])

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

	# Create directory for test
	args.path = os.path.join(args.path, datetime.now().strftime("%Y-%m-%d_%H%M%S"))
	os.makedirs(os.path.join(args.path, "results"))

	# Configure logging
	global log_file
	log_path = os.path.join(args.path, log_file)
	log_file = open(log_path, 'w')
	
	if args.verbose:
		global verbose
		verbose = True

	message = [	"Beginning node test...",
				"   Batch system  = {}".format(args.batch),
				"   Case          = {}".format(args.case),
				"   Queue         = {}".format(args.queue),
				"   Nodes         = {}".format(args.nodes),
				"   Account       = {}".format(args.account)]
	log_message(0, message)
	log_message(0, ["","Case created in: {}".format(args.path)])

	# Get node pairs
	nodes, rstat	= get_nodes(args.batch, args.queue, args.nodes)
	jobs 			= create_jobs(nodes, rstat)
	total_jobs		= len(jobs)

	if args.force:
		args.force = False

		if args.batch == "PBS":
			if username == "csgteam":
				message = [	"","WARNING: Force option will terminate any jobs currently running",
					 		"         on the selected nodes. Do you wish to proceed?",""]
				log_message(0, message)
				confirm = raw_input('Type "yes" to continue: ')

				if confirm.lower() == "yes":
					args.force = True
				else:
					log_message(0, ["","NOTICE:  User did not emphatically confirm force. Ignoring ...",""])
			else:
				log_message(0, ["","NOTICE:  Force must be run as csgteam. Ignoring ...",""])
		else:
			log_message(0, ["","NOTICE:  Can only force jobs using PBS. Ignoring ...",""])

	log_message(0, ["Submitting {} jobs to scheduler...".format(total_jobs)])

	# Test logging
	log	= { "res_path"		: os.path.join(args.path, "results"),
			"init_time" 	: time.time(),
			"num_jobs"		: 0,
			"num_active"	: 0,
			"total_jobs"	: total_jobs,
			"errors"		: [],
			"num_errors"	: 0 }
	log["last_time"] = log["init_time"]

	# Submit testing jobs and force them to run if requested
	submit_jobs(jobs, args, log)

	if args.force:
		force_run(jobs, log)

	# Until jobs are done, keep checking results
	keep_going = True

	while keep_going:
		time.sleep(10)
		print_status(jobs, log)
		keep_going = log["num_active"] > 0
		
	message = [	"","   Failure rate = {:.1f}%".format(100.0 * log["num_errors"] / log["num_jobs"]),
				"","Nodetest complete!",
				"Results in:    {}".format(os.path.join(args.path, "results")),
				"Testing log:   {}".format(log_path)]
	log_message(0, message)
	log_file.close()

# Call the main function
if __name__ == "__main__":
	main()
