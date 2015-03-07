
class SearchNode:
	instances = 0

	def __init__(self):
		SearchNode.instances += 1
		self.count = 0
		self.ends = 0
		self.refs = set()
		self.next = {}

	def getCount(self):
		return SearchNode.instances
