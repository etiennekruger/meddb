var standard_loader = function(url, callback) {
    if (url.slice(-5) == '.html') {
	d3.html(url, callback);
    } else {
	d3.json(url, callback);
    }
}

var jsonp_loader = function(url, callback) {
    /* Setup callback for either the HTML or JSON case. */
    var request;
    if (url.slice(-5) == '.html') {
	request = [settings.static_base_url+url.slice(0,-5)+'.jsonp'];
	meddb.callback = function(data) {
	    var fragment = document.createDocumentFragment();
	    var element = document.createElement('div');
	    element.innerHTML = data;
	    fragment.appendChild(element.firstChild);
	    callback(fragment);
	}
    } else {
	request = [settings.data_base_url+url+'?jsonp=meddb.callback'];
	meddb.callback = function(data) {
	    callback(data);
	}
    }
    /* Now add the script tag to the head. */
    d3.select('html')
	.select('script#meddb_jsonp')
	.remove();
    d3.select('html')
	.select('script#meddb_jsonp')
	.data(request)
	.enter()
	.append('script')
	.attr('id', 'meddb_jsonp')
	.attr('src', function(d) { return d; });
}

var load = function(url, callback) {
    /* Call the appropriate loader according to the settings. */
    if (settings.loader == 'standard') {
	standard_loader(url, callback);
    } else if (settings.loader == 'jsonp') {
	jsonp_loader(url, callback);
    }
}

