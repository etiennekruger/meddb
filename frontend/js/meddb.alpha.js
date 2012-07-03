(function() {
meddb = {}
var settings = {
    'static_base_url': 'http://meddb.medicinesinfohub.net',
    'data_base_url': 'http://meddb.medicinesinfohub.net',
    'loader': 'jsonp'
}
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
meddb.router = function() {
    var hash = location.hash;
    var last = meddb.history.list[meddb.history.list.length-1];
    if ((last) && (hash == last.hash)) {
	return;
    }
    //console.log('Routing to '+hash);
    if ((hash == '') || (hash == '#')) {
	location.hash = 'medicine';
    } else if (hash.substring(0,5) == '#tab:') {
	/* Handle switching of tabs. */
	var tab = hash.substring(5);
	meddb.tabber.change(tab);
	//if (last) {
	//    location.replace(last);
	//}
    } else {
	var text = '';
	if (hash == '#medicine') {
	    meddb.medicine.list();
	} else if (hash.substring(0,10) == '#medicine:') {
	    var id = parseInt(hash.substring(10));
	    meddb.medicine.detail(id);
	} else if (hash.substring(0,9) == '#product:') {
	    var id = parseInt(hash.substring(9));
	    meddb.product.detail(id);
	} else if (hash.substring(0,10) == '#supplier:') {
	    var id = parseInt(hash.substring(10));
	    meddb.supplier.detail(id);
	} else if (hash.substring(0,5) == '#tab:') {
	    /* Handle switching of tabs. */
	    var tab = hash.substring(5);
	    d3.select('div#meddb_inner_container')
		.select('div.tab-content')
		.selectAll('div.tab-pane')
		.classed('active', false);
	    d3.select('div#meddb_inner_container')
		.select('div.tab-content')
		.select('div.tab-pane#'+tab)
		.classed('active', true);
	}
    }
}
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
meddb.medicine = {};
var medicine_list = function(data, node) {
    var row_data = function(d) {
	var row = [];
	var formulation = [];
	var strength = [];
	d.ingredients.forEach(function(item) {
	    formulation.push(item.inn);
	    strength.push(item.strength);
	});
	row.push(formulation.join(' + '));
	row.push(strength.join(' + '));
	row.push(d.dosageform.name);
	row.push(d3.round(d.avgprice,4));
	row.push(d3.round(d.mshprice,4) || '');
	return row;
    }
    var tbody = d3.select(node)
	.select('#meddb_medicine_list')
	.select('tbody');
    tbody.selectAll('tr')
	.remove();
    var rows = tbody.selectAll('tr')
	.data(data)
	.enter()
	.append('tr')
	.style('cursor', 'pointer')
	.on('click', function(d) { location.hash = 'medicine:'+d.id; });
    rows.selectAll('td')
	.data(row_data)
	.enter()
	.append('td')
	.text(function(d) { return d; });
}

meddb.medicine.data = {};
meddb.medicine.list = function() {
    meddb.template.hide();
    load('/medicine_list.html', function(fragment) {
	load('/json/medicine/', function(data) {
	    meddb.medicine.data = data;
	    medicine_list(data, fragment);
	    meddb.history.add(location.hash, 'All Medicine');
	    meddb.template.show(fragment);
	    d3.select('#meddb_medicine_search')
		.on('keyup', function() { meddb.medicine.filter(this.value) });
	});
    });
}

meddb.medicine.filter = function(filter) {
    /* Filter the data for the live search. */
    var filtered = [];
    meddb.medicine.data.forEach(function(item) {
	var match = 0;
	item.ingredients.forEach(function(ingredient) {
	    var inn = ingredient.inn.toLowerCase();
	    if (inn.indexOf(filter.toLowerCase()) != -1) {
		match++;
	    }
	});
	if (match > 0) {
	    filtered.push(item);
	}
    });
    medicine_list(filtered, d3.select('div.meddb_inner_page')[0][0])
}
meddb.medicine.detail = function(id) {
    meddb.template.hide();
    load('/medicine_detail.html', function(fragment) {
	load('/json/medicine/'+id+'/', function(data) {
	    /* Helper functions to process data. */
	    var object_name = function() {
		var formulation = [];
		data.ingredients.forEach(function(item) {
		    formulation.push(item.inn+' '+item.strength);
		});
		return formulation.join(' + ');
	    }
	    /* Populate procurements table. */
	    var procurement_data = function(d) {
		var row = [];
		row.push(d.country.name);
		row.push(d3.round(d.price,4));
		row.push(d.validity);
		return row;
	    }
	    d3.select(fragment)
		.select('#meddb_medicine_heading')
		.text(object_name());
	    var rows = d3.select(fragment)
		.select('#meddb_medicine_procurement')
		.select('tbody')
		.selectAll('tr')
		.data(data.procurements)
		.enter()
		.append('tr');
	    rows.selectAll('td')
		.data(procurement_data)
		.enter()
		.append('td')
		.text(function(d) { return d; });
	    /* Populate products table. */
	    var product_data = function(d) {
		var row = [];
		row.push({
		    text: d.product.name,
		    hash: 'product:'+d.product.id
		});
		if (d.supplier) {
		    row.push({
			text: d.supplier.name,
			hash: 'supplier:'+d.supplier.id
		    });
		} else {
		    row.push({ text: '' });
		}
		if (d.manufacturer) {
		    row.push({
			text: d.manufacturer.name,
			hash: 'manufacturer:'+d.manufacturer.id
		    });
		} else {
		    row.push({ text: '' });
		}
		row.push({
		    text: d.country.name,
		});
		return row;
	    }
	    var rows = d3.select(fragment)
		.select('#meddb_medicine_product')
		.select('tbody')
		.selectAll('tr')
		.data(data.procurements)
		.enter()
		.append('tr');
	    rows.selectAll('td')
		.data(product_data)
		.enter()
		.append('td')
		.text(function(d) { return d.text; })
		.style('cursor', function(d) { if (d.hash) { return 'pointer' } })
		.on('click', function(d) { if (d.hash) {location.hash = d.hash;} });
	    /* Add the medicine prices graph. */
	    var prices_data = function() {
		//var countries = ['DRC', 'Lesotho', 'Malawi', 'Mozambique',
		//		 'South Africa', 'Tanzania', 'Zambia', 'Zimbabwe'];
		var countries = ['Kenya', 'Uganda', 'Tanzania'];
		var prices = {};
		data.procurements.forEach(function(item) {
		    if (typeof(prices[item.country.name]) == 'undefined') {
			prices[item.country.name] = [];
		    }
		    prices[item.country.name].push(item.price);
		});
		graph_data = [];
		countries.forEach(function(country) {
		    var d = { 'key': country }
		    if ((prices[country]) && (prices[country].length > 0)) {
			d.value = d3.sum(prices[country]) / prices[country].length;
		    } else {
			d.value = 0;
		    }
		    graph_data.push(d);
		});
		return graph_data;
	    }
	    var prices_max = function(d) {
		var sum = 0, count = 0, max = 0;
		d.forEach(function(i) {
		    if (i.value > 0) {
			sum += i.value;
			if (i.value > max) {
			    max = i.value;
			}
			count++;
		    }
		});
		return d3.max([sum*2/count, data.mshprice*1.1, max*1.1]);
	    }
	    var graph_data = prices_data();
	    var graph_max = prices_max(graph_data);
	    var prices_graph = {
		width: 940,
		height: 95,
		node: d3.select(fragment).select('#meddb_medicine_prices')[0][0],
		bar : {
		    'height': 25,
		    'margin': 10,
		    'max': graph_max,
		    'background': '#dfe7e5'
		},
		colors: ['#08c', '#08c', '#08c', '#08c',
			 '#08c', '#08c', '#08c', '#08c'],
		data : graph_data
	    }
	    if (data.mshprice) {
		prices_graph.line = { 'constant': d3.round(data.mshprice,4) };
	    }
	    d3.select(fragment)
		.select('#meddb_medicine_prices').html('');
	    var graph = new HorizontalBarGraph(prices_graph);
	    /* Add history option. */
	    meddb.history.add(location.hash, object_name());
	    meddb.template.show(fragment);
	});
    });
}
meddb.product = {};
meddb.product.detail = function(id) {
    meddb.template.hide();
    load('/product_detail.html', function(fragment) {
	load('/json/product/'+id+'/', function(data) {
	    /* Helper functions to process data. */
	    var detail = function() {
		var d = [];
		var formulation = [];
		var strength = [];
		data.medicine.ingredients.forEach(function(item) {
		    formulation.push(item.inn);
		    strength.push(item.strength);
		});
		d.push(formulation.join(' + '));
		d.push(strength.join(' + '));
		return d;
	    }
	    var procurement = function(d) {
		var row = [];
		row.push({
		    text: d.country.name
		});
		if (d.supplier) {
		    row.push({
			text: d.supplier.name,
			hash: 'supplier:'+d.supplier.id
		    })
		} else {
		    row.push({ text: '' });
		}
		if (d.manufacturer) {
		    row.push({
			text: d.manufacturer.name,
			hash: 'manufacturer:'+d.manufacturer.id
		    })
		} else {
		    row.push({ text: '' });
		}
		return row;
	    }
	    /* Populate product detail section. */
	    d3.select(fragment)
		.select('#meddb_product_heading')
		.text(data.name);
	    d3.select(fragment)
		.select('table#meddb_product_detail')
		.selectAll('td')
		.data(detail)
		.text(function(d) { return d; });
	    /* Populate the product registrations table. */
	    var rows = d3.select(fragment)
		.select('table#meddb_product_registration')
		.select('tbody')
		.selectAll('tr')
		.data(data.procurements)
		.enter()
		.append('tr');
	    rows.selectAll('td')
		.data(procurement)
		.enter()
		.append('td')
		.text(function(d) { return d.text; })
		.style('cursor', function(d) { if (d.hash) { return 'pointer' } })
		.on('click', function(d) { location.hash = d.hash; });
	    meddb.history.add(location.hash, data.name);
	    meddb.template.show(fragment);
	});
    });
}
meddb.supplier = {};
meddb.supplier.detail = function(id) {
    meddb.template.hide();
    load('/supplier_detail.html', function(fragment) {
	load('/json/supplier/'+id+'/', function(data) {
	    /* Helper functions to process data. */
	    var procurement = function(d) {
		var row = [];
		row.push({
		    text: d.product.name,
		    hash: 'product:'+d.product.id
		});
		row.push({
		    text: d.country.name,
		});
		var ingredients = [];
		d.product.medicine.ingredients.forEach(function(i) {
		    ingredients.push(i.inn+' '+i.strength);
		});
		row.push({
		    text: ingredients.join(', '),
		    hash: 'medicine:'+d.product.medicine.id
		});
		return row;
	    }
	    /* Populate supplier heading section. */
	    d3.select(fragment)
		.select('#meddb_supplier_heading')
		.text(data.name);
	    /* Populate the supplier detail page. */
	    var details = function() {
		var row = [];
		row.push(data.website || 'None');
		row.push(data.contact || 'None');
		row.push(data.email || 'None');
		row.push(data.altemail || 'None');
		row.push(data.phone || 'None');
		row.push(data.altphone || 'None');
		row.push(data.fax || 'None');
		row.push(data.address || 'None');
		return row;
	    }
	    d3.select(fragment)
		.select('table#meddb_supplier_details')
		.selectAll('td')
		.data(details())
		.text(function(d) { return d; });
	    d3.select(fragment)
		.select('table#meddb_supplier_details')
		.select('td')
	        .data([data.website])
		.style('cursor', 'pointer')
		.on('click', function(d) { if (d) { location = d; } });
	    /* Populate the product registrations table. */
	    var rows = d3.select(fragment)
		.select('table#meddb_supplier_registration')
		.select('tbody')
		.selectAll('tr')
		.data(data.procurements)
		.enter()
		.append('tr');
	    rows.selectAll('td')
		.data(procurement)
		.enter()
		.append('td')
		.text(function(d) { return d.text; })
		.style('cursor', function(d) { if (d.hash) { return 'pointer' } })
		.on('click', function(d) { location.hash = d.hash; });
	    meddb.history.add(location.hash, data.name);
	    meddb.template.show(fragment);
	});
    });
}
meddb.template.load('base.html', function(fragment) {
    meddb.template.inject(fragment, '#meddb_container');
    meddb.router();
});
window.onhashchange = meddb.router;})();