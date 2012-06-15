meddb.template = {};
meddb.template.cache = {};

meddb.template.load = function(url, callback) {
    //if (meddb.template.cache[url]) {
    //    var fragment = meddb.template.cache[url];
    //    callback(fragment.cloneNode(true));
    //}
    d3.html(url, function(fragment) {
	//meddb.template.cache[url] = fragment;
	callback(fragment.cloneNode(true));
    });
}

meddb.template.inject = function(fragment, selector) {
    selector = selector || '#meddb_inner_container';
    var node = d3.select(selector)[0][0];
    node.innerHTML = '';
    node.appendChild(fragment);
}

meddb.template.hide = function() {
    d3.select('#meddb_page')
	.attr('id', 'meddb_page_outgoing')
	.transition()
	.style('opacity', '0')
	.style('left', '-950px')
	.remove();
    d3.select('img#meddb_loading')
	.transition()
	.duration(100)
	.style('opacity', 1);
}

meddb.template.show = function(fragment) {
    var selector = '#meddb_inner_container';
    d3.select(fragment)
	.select('.meddb_inner_page')
	.attr('id', 'meddb_page_incoming')
	.style('opacity', '0')
	.style('left', '950px');
    var node = d3.select(selector)[0][0];
    node.appendChild(fragment);
    d3.select('#meddb_page_incoming')
	.transition()
	.style('opacity', '1')
	.style('left', '0px')
	.attr('id', 'meddb_page');
    d3.select('img#meddb_loading')
	.transition()
	.duration(100)
	.style('opacity', 0);
}

meddb.template.fx = function(fragment) {
    var selector = '#meddb_inner_container';
    d3.select(fragment)
	.select('.meddb_inner_page')
	.attr('id', 'meddb_page_incoming')
	.style('opacity', '0')
	.style('left', '950px');
    var node = d3.select(selector)[0][0];
    //node.innerHTML = '';
    node.appendChild(fragment);
    d3.select('#meddb_page')
	.attr('id', 'meddb_page_outgoing')
	.transition()
	.style('opacity', '0')
	.style('left', '-950px')
	.remove();
    d3.select('#meddb_page_incoming')
	.transition()
	.style('opacity', '1')
	.style('left', '0px')
	.attr('id', 'meddb_page');
}
