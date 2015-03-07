from index import SearchIndex

if __name__ == "__main__":
	
	index = SearchIndex()

	# Index a sample file
	index.indexFile('shakespeare/romeo_juliet')
