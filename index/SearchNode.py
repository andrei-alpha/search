import array

class SearchNode:
	instances = 0

	def __init__(self):
		SearchNode.instances += 1
		self.count = 0
		self.ends = 0
		self.docs = array.array('i')
		self.offsets = array.array('i')
		self.next = {}

	def getCount(self):
		return SearchNode.instances
