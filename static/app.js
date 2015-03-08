$(function() {
	$('#main').keyup(function(e) {
		query($(this).val())
    	$('#autocomplete').val($(this).val() + ' wise')
	});
})

function query(input) {
	if (input.length == 0) {
		$('#results').html('')
		return;
	}
	$.ajax({
	    url: "/backend/query",
        data: { "query": input, },
        type: "post",
	      success: function(results){
            $('#results').html(format(JSON.parse(results)))
        },
    });
}

function format(results) {
	html = '';
	for (var i in results) {
		results[i] = results[i].replace(/\*([a-zA-Z0-9]*[^\*]*)\*/g, "<b>$1</b>")
		html += '<div class="result">' + results[i].replace(/\n/gi, "<br>") + '</div>'
	}
	return html
}