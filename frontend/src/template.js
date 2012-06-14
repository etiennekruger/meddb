meddb.template = {};
meddb.template.cache = {};

meddb.template.load = function(url, callback, selector) {
    selector = selector || '#meddb_inner_container';
    var inject = function(data) {
	d3.select(selector)[0][0]
	    .innerHTML = '';
	d3.select(selector)[0][0]
	    .appendChild(data);
    }
    if (meddb.template.cache[url]) {
	inject(meddb.template.cache[url]);
	callback();
    }
    d3.html(url, function(data) {
	meddb.template.cache[url] = data;
	inject(data);
	callback();
    });
}
