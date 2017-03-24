import driver

class HostProducer():
	def __init__(self, some_string):
		self.content = some_string
	def produce_hosts(self):
		return self.content

def test_parse_LSF_nodes():
	my_hosts = HostProducer(
"""HOST_NAME          STATUS       JL/U    MAX  NJOBS    RUN  SSUSP  USUSP    RSV 
ys0101-ib          closed          -     32     16     16      0      0      0
ys0102-ib          closed          -     32     16     16      0      0      0
ys0103-ib          closed          -     32     16     16      0      0      0
ys0104-ib          closed          -     32     16     16      0      0      0
ys0105-ib          closed          -     32     16     16      0      0      0
ys0106-ib          closed          -     32     16     16      0      0      0
ys0107-ib          closed          -     32     16     16      0      0      0
ys0108-ib          closed          -     32     16     16      0      0      0
ys0109-ib          closed          -     32     16     16      0      0      0
ys6363-ib          closed          -     32     16     16      0      0      0
ys6364-ib          closed          -     32     16     16      0      0      0
ys6365-ib          closed          -     32     16     16      0      0      0
ys6366-ib          closed          -     32     16     16      0      0      0
ys6367-ib          closed          -     32     16     16      0      0      0
ys6368-ib          closed          -     32      8      8      0      0      0
ys6369-ib          closed          -     32     16     16      0      0      0
ys6370-ib          closed          -     32      4      4      0      0      0
ys6371-ib          closed          -     32     16     16      0      0      0
ys6372-ib          closed          -     32     16     16      0      0      0
ys0146-ib          ok              -     32      0      0      0      0      0
ys0214-ib          ok              -     32      0      0      0      0      0
ys0216-ib          ok              -     32      0      0      0      0      0
ys0436-ib          ok              -     32      0      0      0      0      0
ys0438-ib          ok              -     32      0      0      0      0      0
ys0439-ib          ok              -     32      0      0      0      0      0
ys0440-ib          ok              -     32      0      0      0      0      0
ys0442-ib          ok              -     32      0      0      0      0      0
ys2667-ib          ok              -     32     16      0      0      0     16
ys2869-ib          ok              -     32     16      0      0      0     16
""")
	result = driver.parse_nodes(".*ok", my_hosts.produce_hosts)
	assert result == ["ys0146-ib", "ys0214-ib", "ys0216-ib"
#ys0436-ib
#ys0438-ib
#ys0439-ib
#ys0440-ib
#ys0442-ib
#ys2667-ib
#ys2869-ib
]

def test_parse_PBS_nodes():
	my_hosts = HostProducer(
"""The PBS stuff
blah
blah
""")
	result = driver.parse_nodes("", my_hosts.produce_hosts)
	assert result == ["r1n1-whatever", "r2n2-whatever"]
