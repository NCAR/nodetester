import unittest, driver

class parse_LSF(unittest.TestCase):
	# Tests for parse_nodes_lsf

	resv_data = """
RSVID        TYPE      USER       NCPUS          RSV_HOSTS     TIME_WINDOW
wrfrt        user     wrfrt       0/10560    ys0407-ib:0/32    3/30/21/40-3/31/1/55                
                                             ys0334-ib:0/32
"""

	def test_parse_nodes_lsf(self):
		"""Can we parse two good LSF nodes?"""

		node_data = [	"ys0146-ib          ok              -     32      0      0      0      0      0",
						"ys2667-ib          ok              -     32     16      0      0      0     16"	]

		nodes, rstat = driver.parse_nodes_lsf(node_data, self.resv_data)

		self.assertEqual(nodes, ["ys0146-ib","ys2667-ib"])
		self.assertEqual(rstat, [False, False])

	def test_parse_nodes_lsf_detect_reserved(self):
		"""Can we detect a reserved LSF node?"""

		node_data = [	"ys0407-ib          ok              -     32      0      0      0      0      0",
						"ys2667-ib          ok              -     32     16      0      0      0     16"	]

		nodes, rstat = driver.parse_nodes_lsf(node_data, self.resv_data)

		self.assertEqual(rstat, [True, False])

class parse_PBS(unittest.TestCase):
	# Tests for parse_nodes_pbs

	def test_parse_nodes_pbs(self):
		"""Can we parse two good PBS nodes?"""
		
		node_data = [	"r5i6n25",
						"     resources_available.Qlist = system,special,ampsrt,capability,premium,regular,economy,standby,small,share",
						"r5i6n26",
						"     resources_available.Qlist = system,special,ampsrt,capability,premium,regular,economy,standby,small,share"	]

		nodes, rstat = driver.parse_nodes_pbs("regular", node_data)

		self.assertEqual(nodes, ["r5i6n25","r5i6n26"])
		self.assertEqual(rstat, [False, False])

	def test_parse_nodes_pbs_detect_reserved(self):
		"""Can we detect a reserved PBS node?"""

		node_data = [	"r5i6n25",
						"     resv = R1009849.chadmin1",
						"     resources_available.Qlist = system,special,ampsrt,capability,premium,regular,economy,standby,small,share",
						"r5i6n26",
						"     resources_available.Qlist = system,special,ampsrt,capability,premium,regular,economy,standby,small,share"	]

		nodes, rstat = driver.parse_nodes_pbs("regular", node_data)

		self.assertEqual(rstat, [True, False])

	def test_parse_nodes_pbs_use_reserved(self):
		"""Can we detect a reserved PBS node?"""

		node_data = [	"r5i6n25",
						"     resv = R1009849.chadmin1",
						"     resources_available.Qlist = system,special,ampsrt,capability,premium,regular,economy,standby,small,share",
						"r5i6n26",
						"     resources_available.Qlist = system,special,ampsrt,capability,premium,regular,economy,standby,small,share",
						"r5i6n27",
						"     resv = R1009849.chadmin1",
						"     resources_available.Qlist = system,special,ampsrt,capability,premium,regular,economy,standby,small,share"	]

		nodes, rstat = driver.parse_nodes_pbs("R1009849", node_data)

		self.assertEqual(nodes, ["r5i6n25","r5i6n27"])
		self.assertEqual(rstat, [False, False])

if __name__ == "__main__":
	unittest.main()
