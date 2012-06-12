/* All functions for the Medicine Registration Database will live in the
   meddb to prevent namespace pollution. */

meddb = {};

/* Functions to aid in the loading of templates and template caching. */

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

/* Functions for loading and populating medicine data. */

meddb.medicine = {};

meddb.medicine.list = function() {
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
	row.push(d.dosageform);
	if (d.procurements) {
	    row.push(d3.round(d.procurements[0].price,4));
	}
	return row;
    }
    var medicine_sort = function(a, b) {
	if ((a) && (b)) {
	    if (a.ingredients[0].inn < b.ingredients[0].inn) {
		return -1;
	    } else if (a.ingredients[0].inn > b.ingredients[0].inn) {
		return 1;
	    } else {
		return 0;
	    }
	} else {
	    return 0;
	}
    }
    meddb.template.load('medicine_list.html', function() {
	d3.json('/json/medicine/', function(data) {
	    var rows = d3.select('#meddb_container')
		.select('#meddb_medicine_list')
		.select('tbody')
		.selectAll('tr')
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
	    //rows.sort(medicine_sort);
	});
    });
    meddb.history.add(location.hash, 'All Medicine');
}

meddb.medicine.detail = function(id) {
    meddb.template.load('medicine_detail.html', function() {
	//meddb.tabber.init();
	d3.json('/json/medicine/'+id+'/', function(data) {
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
	    d3.select('#meddb_medicine_heading')
		.text(object_name());
	    var rows = d3.select('#meddb_container')
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
		row.push({ text: d.name, hash: 'product:'+d.id });
		var suppliers = [];
		d.registrations.forEach(function(item) {
		    if (item.supplier) {
			suppliers.push(item.supplier.name);
		    }
		});
		row.push({
		    text: suppliers.join(', '),
		    hash: 'supplier:'+d.registrations[0].supplier.id
		});
		var manufacturers = [];
		d.registrations.forEach(function(item) {
		    if (item.manufacturer) {
			manufacturers.push(item.manufacturer.name);
		    }
		});
		row.push({ text: manufacturers.join(', ') });
		var countries = [];
		d.registrations.forEach(function(item) {
		    countries.push(item.country.name);
		});
		row.push({ text: countries.join(', ') });
		return row;
	    }
	    d3.select('#meddb_medicine_heading')
		.text(object_name());
	    var rows = d3.select('#meddb_container')
		.select('#meddb_medicine_product')
		.select('tbody')
		.selectAll('tr')
		.data(data.products)
		.enter()
		.append('tr');
	    rows.selectAll('td')
		.data(product_data)
		.enter()
		.append('td')
		.text(function(d) { return d.text; })
		.style('cursor', function(d) { if (d.hash) { return 'pointer' } })
		.on('click', function(d) { if (d.hash) {location.hash = d.hash;} });
	    meddb.history.add(location.hash, object_name());
	});
    });
}

/* Product specific code. */

meddb.product = {};

meddb.product.detail = function(id) {
    meddb.template.load('product_detail.html', function() {
	//meddb.tabber.init();
	d3.json('/json/product/'+id+'/', function(data) {
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
	    var registration = function(d) {
		var row = [];
		row.push({
		    text: d.country.name,
		    hash: null
		});
		if (d.supplier) {
		    row.push({
			text: d.supplier.name,
			hash: 'supplier:'+d.supplier.id
		    })
		} else {
		    row.push({
			text: 'Unknown',
			hash: null
		    })
		}
		if (d.manufacturer) {
		    row.push({
			text: d.manufacturer.name,
			hash: 'manufacturer:'+d.manufacturer.id
		    })
		} else {
		    row.push({
			text: 'Unknown',
			hash: null
		    })
		}
		return row;
	    }
	    /* Populate product detail section. */
	    d3.select('#meddb_product_heading')
		.text(data.name);
	    d3.select('table#meddb_product_detail')
		.selectAll('td')
		.data(detail)
		.text(function(d) { return d; });
	    /* Populate the product registrations table. */
	    var rows = d3.select('table#meddb_product_registration')
		.select('tbody')
		.selectAll('tr')
		.data(data.registrations)
		.enter()
		.append('tr');
	    rows.selectAll('td')
		.data(registration)
		.enter()
		.append('td')
		.text(function(d) { return d.text; })
		.style('cursor', function(d) { if (d.hash) { return 'pointer' } })
		.on('click', function(d) { location.hash = d.hash; });
	    meddb.history.add(location.hash, data.name);
	});
    });
}

/* Supplier specific code. */

meddb.supplier = {};

meddb.supplier.detail = function(id) {
    meddb.template.load('supplier_detail.html', function() {
	//meddb.tabber.init();
	d3.json('/json/supplier/'+id+'/', function(data) {
	    /* Helper functions to process data. */
	    var registration = function(d) {
		var row = [];
		row.push({
		    text: d.product.name,
		    hash: '#product:'+d.product.id
		});
		row.push({
		    text: d.country.name
		});
		var formulation = [];
		d.product.medicine.ingredients.forEach(function(item) {
		    formulation.push(item.inn+' '+item.strength);
		});
		row.push({
		    text: formulation.join(' + '),
		    hash: '#medicine:'+d.product.medicine.id
		});
		return row;
	    }
	    /* Populate supplier heading section. */
	    d3.select('#meddb_supplier_heading')
		.text(data.name);
	    /* Populate the product registrations table. */
	    var rows = d3.select('table#meddb_supplier_registration')
		.select('tbody')
		.selectAll('tr')
		.data(data.registrations)
		.enter()
		.append('tr');
	    rows.selectAll('td')
		.data(registration)
		.enter()
		.append('td')
		.text(function(d) { return d.text; })
		.style('cursor', function(d) { if (d.hash) { return 'pointer' } })
		.on('click', function(d) { location.hash = d.hash; });
	    meddb.history.add(location.hash, data.name);
	});
    });
}

/* Tab changer. Bootstrap uses location.hash to change tabs
   and this breaks our history, so we use a custom tabber. */
/* TODO: This does not quite work yet and needs to be fixed. */
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

/* Navigation router. Loads the appropriate content based
   on the current hash. Additionally populates the history
   list. */
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

/* Update history and breadcrumbs. */
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
    var crumbs = d3.select('ul#meddb_breadcrumb')
	.selectAll('li')
	.data(meddb.history.list.slice(-6), function(d) { if (d) { return d.hash; } });
    var li = crumbs.enter()
	.append('li')
    li.append('a')
	.attr('href', function(d) { return d.hash; })
	.text(function(d) { return d.text; });
    li.append('span')
	.classed('divider', true)
	.text(' / ');
    crumbs.exit()
	.remove();
}


/* Initialization function. Preloads base template and
   redirects control to the navigation router. */
meddb.init = function() {
    meddb.template.load('base.html', function() {
	meddb.router();
    }, '#meddb_container');
    window.onhashchange = meddb.router;
};
meddb.init();
