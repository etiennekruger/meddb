var standard_loader = function(url, callback) {
    console.log('standard loader not implemented yet');
}

var jsonp_loader = function(url, callback) {
    /* Setup callback for either the HTML or JSON case. */
    var request;
    if (url.slice(-5) == '.html') {
	request = [settings.base_url+url.slice(0,-5)+'.jsonp'];
	meddb.callback = function(data) {
	    var fragment = document.createDocumentFragment();
	    var element = document.createElement('div');
	    element.innerHTML = data;
	    fragment.appendChild(element.firstChild);
	    callback(fragment);
	}
    } else {
	request = [settings.base_url+url+'?jsonp=meddb.callback'];
	meddb.callback = function(data) {
	    callback(data);
	}
    }
    /* Now add the script tag to the head. */
    var tag = d3.select('head')
	.select('script#meddb_jsonp')
	.data(request);
    tag.enter()
	.append('script')
	.attr('id', 'meddb_jsonp')
	.attr('src', function(d) { return d; });
    tag.exit()
	.remove();
}

var load = function(url, callback) {
    /* Call the appropriate loader according to the settings. */
    if (settings.loader == 'standard') {
	standard_loader(url, callback);
    } else if (settings.loader == 'jsonp') {
	jsonp_loader(url, callback);
    }
}

