import json
import os
import threading

from bottle import Bottle, static_file, request, run
from index import SearchIndex

app = Bottle()

@app.route('/')
def index():
  return static_file('index.html', root='')

@app.route('/backend/query', method='POST')
def query():
	query = request.forms.get('query')
	fromResults = int(request.forms.get('from'))
	lenResults = int(request.forms.get('count'))

	results = search.search(query, fromResults, lenResults)
	results['suggestions'] = search.suggest(query)
	return json.dumps(results, ensure_ascii=False, encoding='utf8')

@app.route('/static/<filename>')
def server_static(filename):
    return static_file(filename, root='static')

def indexFiles(path):
	# Index all shakespeare operas
	for file in os.listdir(path):
		if not os.path.isdir(path + '/' + file):
			search.indexFile(path + '/' + file, file.replace("_", " ").title())

if __name__ == "__main__":
	search = SearchIndex()
	t = threading.Thread(target=indexFiles, args = ('shakespeare',))
	t.daemon = True
	t.start()

	run(app, reloader=False, host='localhost', port=8080, debug=True)
