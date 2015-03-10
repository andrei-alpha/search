$(function() {
	$('#main').keyup(function(e) {
		query($(this).val())
	});
})

function query(input) {
	if (input.length == 0) {
		$('#results').html('')
		$('#resultsStats').html('')
		$('#autocomplete').val('')
		return;
	}
	var start = new Date().getTime();
	$.ajax({
	    url: "/backend/query",
        data: { "query": input, },
        type: "post",
	      success: function(data){
	      	console.log("(Results after " + (new Date().getTime() - start) + " msec)")
            processData(JSON.parse(data))
        },
    });
}

function processData(data) {
	results = data["results"]
	count = data["count"]
	time = data["latency"]
	if (data["suggestions"].length) {
		suggestion = data["suggestions"][0][1].replace('_', ' ')
		$('#autocomplete').val($('#main').val() + suggestion)
	}

	$('#resultsStats').html('About ' + count + ' results (' + time + ' milliseconds)')
	html = ''
	for (var i in results) {
		name = results[i][0]; text = results[i][1];
		text = text.replace(/\*([a-zA-Z0-9]*[^\*]*)\*/g, '<font color="red">$1</font>')
		html += formatResult(name, text.replace(/\n/gi, "<br>"))
	}
	$('#results').html(html)
}

function formatResult(name, text) {
	html = '<div class="result">'
	html += '<div class="result-name">' + name + '</div>'
	html += '<div class="result-text">' + text + '</div>'
	html += '</div>'
	return html;
}
