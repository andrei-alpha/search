import sys
import random
import re
from pympler.asizeof import asizeof

from SearchNode import SearchNode

class SearchTree:

	def __init__(self):
		self.root = SearchNode()
		self.entriesDict = {}
		self.entries = []
		self.entriesCount = 0

	def put(self, str, offset, document):
		if not document in self.entriesDict:
			self.entriesDict[document] = len(self.entries)
			self.entries.append(document)

		docRef = self.entriesDict[document]
		return self.__put(self.root, str, offset, docRef, 0)

	def __put(self, node, str, offset, docRef, depth):
		node.docs.append(docRef)
		node.offsets.append(offset)

		if not str:
			return

		# stop recursion
		if node.count is 1:
			node.ends += 1
			return
		if depth > 10:
			return

		# we have to split
		if node.ends > 10:
			strs = map(lambda x: self.__docFromRef(x), node.refs)
			for newStr, ref in zip(strs, zip(node.docs, node.offsets)):
				if not newStr:
					continue

				if not newStr[0] in node.next:
					node.next[newStr[0]] = SearchNode()
				self.__put(node.next[newStr[0]], newStr[1:], ref[1] + 1, ref[0])
			node.ends = 0

		if not str[0] in node.next:
			node.next[str[0]] = SearchNode()
		self.__put(node.next[str[0]], str[1:], offset + 1, docRef, depth + 1)

	def get(self, prefix):
		self.resultCount = 0
		results = self.__get(self.root, prefix, prefix)
		if len(results) == 0:
			results = ["not found"]
		return results

	def __get(self, node, pattern, prefix):
		if not pattern:
			docs = map(lambda docRef: self.entries[docRef], node.docs)
			self.resultCount = len(docs)
			docs = docs if len(docs) < 15 else random.sample(docs, 15)
			return map(lambda (doc, offset): self.__getContext(doc, offset, prefix), zip(docs, node.offsets))

		if not pattern[0] in node.next:
			return []
		return self.__get(node.next[pattern[0]], pattern[1:], prefix)

	def __docFromRef(self, ref):
		document = self.entries[ref[0]][ref[1]:]
		return document

	def __getContext(self, doc, offset, prefix):
		before = self.__firstSplit(doc[:(offset-len(prefix))][::-1], 50)[::-1]
		after  = self.__firstSplit(doc[offset:], 50)
		return before + "*" + prefix + "*" + after

	def __firstSplit(self, str, offset):
		end = re.compile('\.|\?|\!')
		space = re.compile('\s')
		match = end.search(str[offset:])
		match = match if match else space.search(str[offset:])
		index = match.start() if match else 0
		return str[:offset+index]

	def nodesCount(self):
		return self.root.getCount()

	def resultsCount(self):
		return self.resultCount

	def examine(self):
		return self.__examineAll(self.root)

	def __examine(self, node):
		res = [[0,0,0]]
		res[0][0] = asizeof(node.docs) + asizeof(node.offsets)
		res[0][1] = sys.getsizeof(node.next)
		res[0][2] = asizeof(node.count) + asizeof(node.ends)
		for val in node.next:
			res.append( self.__examine(node.next[val]))
		return reduce(lambda x,y: [x[0] + y[0], x[1] + y[1], x[2] + y[2]], res)

