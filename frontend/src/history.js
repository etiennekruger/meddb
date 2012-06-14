meddb.history = {};
meddb.history.list = [];

meddb.history.add = function(hash, text) {
    var last = meddb.history.list[meddb.history.list.length-1];
    if ((last) && (hash == last.hash)) {
	return;
    }
    meddb.history.list.push({
	hash: hash,
	text: text
    });
    d3.select('ul#meddb_breadcrumb')
	.selectAll('li')
	.remove();
    var li = d3.select('ul#meddb_breadcrumb')
	.selectAll('li')
	.data(meddb.history.list.slice(-5))
	.enter()
	.append('li');
    li.append('a')
	.attr('href', function(d) { return d.hash; })
	.text(function(d) { return d.text; });
    li.append('span')
	.classed('divider', true)
	.text(' / ');
}
