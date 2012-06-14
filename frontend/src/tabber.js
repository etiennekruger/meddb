meddb.tabber = {};

meddb.tabber.init = function() {
    var change = function() {
	meddb.tabber.change(this.href.split('#tab:')[1]);
	return false;
    }
    d3.selectAll('a[href^="#tab:"]')
	.on('click', change);
}

meddb.tabber.onclick = function(item) {
    meddb.tabber.change(item.href.split('#tab:')[1]);
    item.parentNode.className += ' active';
    return false;
}

meddb.tabber.change = function(tab) {
    d3.select('div#meddb_inner_container')
	.select('div.tab-content')
	.selectAll('div.tab-pane')
	.classed('active', false);
    d3.select('div#meddb_inner_container')
	.select('div.tab-content')
	.select('div.tab-pane#'+tab)
	.classed('active', true);
    d3.select('div#meddb_inner_container')
	.select('ul.nav.nav-tabs')
	.selectAll('li')
	.classed('active', false);
    d3.select('div#meddb_inner_container')
	.select('ul.nav.nav-tabs')
	.select('li>a[href="#tab:'+tab+'"]')
	.classed('active', true);
}
