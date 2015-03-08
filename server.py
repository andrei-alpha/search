import json

from bottle import Bottle, static_file, request, run
from index import SearchIndex

app = Bottle()
search = SearchIndex()
search.indexFile('shakespeare/romeo_juliet')

@app.route('/')
def index():
  return static_file('index.html', root='')

@app.route('/backend/query', method='POST')
def query():
	query = request.forms.get('query')
	results = search.search(query)
	return json.dumps(results)

@app.route('/static/<filename>')
def server_static(filename):
    return static_file(filename, root='static')

run(app, reloader=True, host='localhost', port=8080, debug=True)
