/* All functions for the Medicine Registration Database will live in the
   meddb to prevent namespace pollution. */

meddb = {};
meddb.history = [];

/* Functions to aid in the loading of templates and template caching. */

meddb.template = {};
meddb.template.cache = {};

meddb.template.load = function(url, callback) {
    var inject = function(data) {
	d3.select('#meddb_container')[0][0]
	    .innerHTML = '';
	d3.select('#meddb_container')[0][0]
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
	if (d.procurements) {
	    row.push(d3.round(d.procurements[0].price,4));
	}
	return row;
    }
    meddb.template.load('medicine_list.html', function() {
	d3.json('/json/medicine/', function(data) {
	    var rows = d3.select('#meddb_container')
		.select('#meddb_list')
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
	});
    });
}

meddb.medicine.detail = function(id) {
    meddb.template.load('medicine_detail.html', function() {
	d3.json('/json/medicine/'+id+'/', function(data) {
	    /* Helper functions to process data. */
	    var row_data = function(d) {
		var row = [];
		row.push(d.country.name);
		row.push(d3.round(d.price,4));
		return row;
	    }
	    var object_name = function() {
		var row = [];
		var formulation = [];
		var strength = [];
		data.ingredients.forEach(function(item) {
		    formulation.push(item.inn);
		    strength.push(item.strength);
		});
		row.push(formulation.join(' + '));
		row.push(strength.join(' + '));
		return row.join(' ');
	    }
	    /* Enable navigation using tabs. */
	    d3.selectAll('div.tab-pane')
		.classed('active', false);
	    d3.select('ul.nav.nav-tabs')
		.selectAll('li')
		.on('click', function(d) {
		    d3.select('div#'+this.attr('date-pane'))
			.classed('active', true);
		    
		});
	    /* Populate procurements table. */
	    d3.select('#meddb_heading')
		.text('Medicine: '+object_name());
	    var rows = d3.select('#meddb_container')
		.select('#meddb_medicine_procurement')
		.select('tbody')
		.selectAll('tr')
		.data(data.procurements)
		.enter()
		.append('tr');
	    rows.selectAll('td')
		.data(row_data)
		.enter()
		.append('td')
		.text(function(d) { return d; });
	});
    });
}

/* Navigation router. Loads the appropriate content based
   on the current hash. Additionally populates the history
   list. */
meddb.router = function() {
    var hash = location.hash;
    meddb.history.push(hash);
    if (hash == '') {
	meddb.medicine.list();
    } else if (hash == '#') {
	meddb.medicine.list();
    } else if (hash == '#medicine') {
	meddb.medicine.list();
    } else if (hash.substring(0, 10) == '#medicine:') {
	var id = parseInt(hash.substring(10));
	meddb.medicine.detail(id);
    }
}

/* Initialization function. Preloads base template and
   redirects control to the navigation router. */
function() {
    meddb.template.load('base.html', function() {
	meddb.router();
    });
    window.onhashchange = meddb.router;
}();
