meddb.template = {};
meddb.template.cache = {};

meddb.template.load = function(url, callback) {
    d3.html(url, function(fragment) {
	callback(fragment);
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
    var height = d3.select('#meddb_page_incoming')[0][0].clientHeight;
    d3.select('#meddb_page_incoming')
	.transition()
	.style('opacity', '1')
	.style('left', '0px')
	.attr('id', 'meddb_page');
    d3.select('img#meddb_loading')
	.transition()
	.duration(100)
	.style('opacity', 0);
    d3.select('#meddb_inner_container')
	.transition()
	.style('height', height+'px');
    console.log('height:'+height);
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
