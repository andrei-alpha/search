import time

from SearchTree import SearchTree

class SearchIndex:

	def __init__(self):
		self.tree = SearchTree()

	def index(self, document, name):
		start = time.time()
		self.tree.registerDocument(document, name)
		for i in xrange(0, len(document)):
			if document[i:i+1].isalnum():
				self.tree.put(document[i:], i, document)
		latency = "{0:.2f}".format(time.time() - start)
		print 'Computed', self.tree.nodesCount(), 'search nodes (' + latency, 'seconds)'

	def indexFile(self, path, name):
		f = open(path)
		self.index(f.read(), name)

	def search(self, query):
		start = time.time()
		result = self.tree.get(query)
		latency = "{0:.2f}".format((time.time() - start) * 1000)
		print 'About', self.tree.resultsCount(), 'results (' + latency, 'milisec)'
		return {"results": result, "count": self.tree.resultsCount(), "latency": latency}

	def suggest(self, prefix):
		return self.tree.suggest(prefix)

	def examine(self):
		res = self.tree.examineAll()
		print 'refs', res[0], 'next', res[1], 'counters', res[2]