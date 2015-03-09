import sys
import random
import re

from itertools import groupby
from pympler.asizeof import asizeof
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

    def get(self, prefix):
        self.resultCount = 0
        results = self.__get(self.root, prefix, (prefix, 15, 50, 50))
        if len(results) == 0:
            return ["not found"]
        return map(lambda (docRef, text): (self.entriesName[docRef], text), results)

    def suggest(self, prefix):
        results = self.__get(self.root, prefix, (prefix, 99999, 0, 10))
        pattern = '\*' + prefix + '\*'
        results = map(lambda (_, text): re.sub(r'%s[^a-zA-Z0-9]+' % pattern, '_', text), results)
        results = map(lambda text: re.sub(r'%s' % pattern, '', text), results)
        results = map(lambda text: (re.findall(r"[\w']+", text)[0].strip("'"), 1), results)
        results.sort()

        suggestions = []
        for word, group in groupby(results, itemgetter(0)):
            total = sum(int(count) for word, count in group)
            suggestions.append((total, word))
        suggestions.sort()
        return suggestions[-10:][::-1]

    def __get(self, node, pattern, args):
        if not pattern:
            docs = map(lambda docRef: self.entries[docRef], node.docs)
            return self.__buildResultList(zip(node.docs, docs, node.offsets), pattern, args)

        if not pattern[0] in node.next:
            docs = map(lambda docRef: self.entries[docRef], node.docs)
            entries = filter(lambda (docRef, doc, offset): doc[offset:].startswith(pattern), zip(node.docs, docs, node.offsets))
            return self.__buildResultList(entries, pattern, args)
        return self.__get(node.next[pattern[0]], pattern[1:], args)

    def __buildResultList(self, entries, pattern, args):
        (_, maxres, _, _) = args
        self.resultCount = len(entries)
        entries = entries if len(entries) < maxres else random.sample(entries, maxres)
        return map(lambda (docRef, doc, offset): (docRef, self.__getContext(doc, offset, pattern, args)), entries)

    def __docFromRef(self, ref):
        document = self.entries[ref[0]][ref[1]:]
        return document

    def __getContext(self, doc, offset, pattern, args):
        (prefix, _, extraBefore, extraAfter) = args
        before = self.__firstSplit(doc[:(offset-len(prefix)+len(pattern))][::-1], extraBefore)[::-1] if extraBefore else ''
        after  = self.__firstSplit(doc[(offset+len(pattern)):], extraAfter) if extraAfter else ''
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
