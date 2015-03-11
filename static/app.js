var resultsPerPage = 10;

$(function() {
	$('#main').keyup(function(e) {
		query($(this).val(), 0, resultsPerPage)
	});
})

function query(input, from, count) {
	if (input.length == 0) {
		$('#results').html('')
		$('#resultsStats').html('')
		$('#autocomplete').val('')
		$('#resultsPages').html('');
		return;
	}
	var start = new Date().getTime();
	$.ajax({
	    url: "/backend/query",
        data: { "query": input, "from": from, "count": count,},
        type: "post",
	      success: function(data){
	      	console.log("(Results after " + (new Date().getTime() - start) + " msec)")
            processData(input, JSON.parse(data), Math.floor((from + count) / count))
        },
    });
}

function processData(input, data, currentPage) {
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

	$('#resultsPages').html('');
	html = '<table><tr>';
	var pages = Math.floor((count + resultsPerPage - 1) / resultsPerPage);
	var leftPage = Math.max(currentPage - 5, 1);
	var rightPage = Math.min(leftPage + 10, pages + 1);

	if (leftPage != 1) {
		action = 'query(' + "'" + input + "'" + ',' + (currentPage - 2) * resultsPerPage + ',' + resultsPerPage + ')';
		html += '<td><a class="fl" onclick="' + action + '"> Previous </a></td>';
	} else {
		html += '<td><a class="fl" style="visibility:hidden"> Previous </a></td>'
	}
	for (var i = leftPage; i < rightPage; ++i) {
		action = 'query(' + "'" + input +  "'" + ',' + (i - 1) * resultsPerPage + ',' + resultsPerPage + ')';
		if (i != currentPage)
			html += '<td><a class="fl" onclick="' + action + '">' + i +  '</a></td>';
		else
			html += '<td><a class="flx">' + i + '</a></td>';
	}
	if (rightPage <= pages) {
		action = 'query(' +  "'" + input + "'" + ',' + currentPage * resultsPerPage + ',' + resultsPerPage + ')';
		html += '<td><a class="fl" onclick="' + action + '"> Next </a></td>';
	}
	html += '</tr></table>'
	$('#resultsPages').html(html);
}

function formatResult(name, text) {
	html = '<div class="result">'
	html += '<div class="result-name">' + name + '</div>'
	html += '<div class="result-text">' + text + '</div>'
	html += '</div>'
	return html;
}
