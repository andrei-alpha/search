import sys
import random
import time
import re

from itertools import groupby
try:
  from pympler.asizeof import asizeof
except ImportError:
  print 'Warning: cannot import pympler.asizeof'
from operator import itemgetter

from SearchNode import SearchNode

class SearchTree:
  def __init__(self):
    self.root = SearchNode()
    self.entriesDict = {}
    self.entries = []
    self.entriesName = []
    self.entriesCount = 0

  def registerDocument(self, document, name):
    if not document in self.entriesDict:
      self.entriesDict[document] = len(self.entries)
      self.entriesName.append(name)
      self.entries.append(document)

  def put(self, str, offset, document):
    if not document in self.entriesDict:
      self.entriesDict[document] = len(self.entries)
      self.entriesName.append(len(self.entries) + '.')
      self.entries.append(document)

    docRef = self.entriesDict[document]
    return self.__put(self.root, str, offset, docRef, 0)

  def __put(self, node, str, offset, docRef, depth):
    node.docs.append(docRef)
    node.offsets.append(offset)

    if not str or depth > 4:
      return
    if node.count is 1:
      node.ends += 1
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

  def get(self, prefix, fromResults, lenResults):
    self.resultCount = 0
    endRegex = re.compile('\.|\?|\!')
    results = self.__get(self.root, prefix, (prefix, fromResults, lenResults, 50, 50, endRegex))
    if len(results) == 0:
      return [["1.", "not found"]]
    return map(lambda (docRef, text): (self.entriesName[docRef], text), results)

  def suggest(self, prefix):
    endRegex = re.compile('\s|\,|\.|\?|\!')
    results = self.__get(self.root, prefix, (prefix, -1, 1000, 0, 3, endRegex))

    results = map(lambda (_, text): text[len(prefix) + 2:], results)
    results = map(lambda text: (self.__getFirstWord(text), 1), results)
    results.sort()

    suggestions = []
    for word, group in groupby(results, itemgetter(0)):
      total = sum(int(count) for word, count in group)
      suggestions.append((total, word))
    suggestions.sort()

    return suggestions[-10:][::-1]

  # Args represent prefix, fromResults, lenResults, contextBefore, contextAfter, regexSplit
  def __get(self, node, pattern, args):
    if not pattern:
      return self.__buildResultList(zip(node.docs, node.offsets), pattern, args)

    if not pattern[0] in node.next:
      entries = filter(lambda (docRef, offset): self.entries[docRef][offset:].startswith(pattern), zip(node.docs, node.offsets))
      return self.__buildResultList(entries, pattern, args)
    return self.__get(node.next[pattern[0]], pattern[1:], args)

  def __buildResultList(self, entries, pattern, args):
    (_, fromRes, lenRes, _, _, _) = args
    self.resultCount = len(entries)
    
    if len(entries) > lenRes:
      if fromRes == -1:
        entries = random.sample(entries, lenRes)
      else:
        entries = entries[fromRes:][:lenRes]
    return map(lambda (docRef, offset): (docRef, self.__getContext(docRef, offset, pattern, args)), entries)

  def __docFromRef(self, ref):
    document = self.entries[ref[0]][ref[1]:]
    return document

  def __getContext(self, docRef, offset, pattern, args):
    doc = self.entries[docRef]
    (prefix, _, _, extraBefore, extraAfter, endRegex) = args
    before = self.__firstSplit(doc[:(offset-len(prefix)+len(pattern))][::-1], extraBefore, endRegex)[::-1] if extraBefore else ''
    after  = self.__firstSplit(doc[(offset+len(pattern)):], extraAfter, endRegex) if extraAfter else ''
    return before + "*" + prefix + "*" + after

  def __firstSplit(self, str, offset, endRegex):
    space = re.compile('\s')
    match = endRegex.search(str[offset:])
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

  def __getFirstWord(self, text):
    text2 = text.lstrip("'\n.,?!: ")
    space = ' ' if len(text2) < len(text) else ''
    for i in xrange(0, len(text2)):
      if not text2[i].isalnum():
        return space + text2[:i]
    return space + text2
