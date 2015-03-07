import random

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
		node.refs.add((docRef, offset))

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
			for newStr, ref in zip(strs, node.refs):
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
		results = self.__get(self.root, prefix)
		if len(results) > 0:
			results = map(lambda entry: prefix + entry, results)
		else:
			results = "not found"
		return results

	def __get(self, node, prefix):
		if not prefix:
			docs = map(lambda (docRef, offset): (self.entries[docRef], offset), node.refs)
			self.resultCount = len(docs)
			docs = docs if len(docs) < 15 else random.sample(docs, 15)
			return map(lambda (doc, offset): self.__firstSplit(doc[offset:], 50) + "...", docs)

		if not prefix[0] in node.next:
			return []
		return self.__get(node.next[prefix[0]], prefix[1:])

	def __docFromRef(self, ref):
		document = self.entries[ref[0]][ref[1]:]
		return document

	def __firstSplit(self, str, offset):
		index = str[offset:].find(' ')
		return str[:offset+index]

	def nodesCount(self):
		return self.root.getCount()

	def resultsCount(self):
		return self.resultCount