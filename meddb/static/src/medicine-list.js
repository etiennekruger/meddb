var medicine_list = function(data, node) {
    mixpanel.track("Medicine List");
    var row_data = function(d) {
	var row = [];
	var formulation = [];
	var strength = [];
	d.ingredients.forEach(function(item) {
	    formulation.push(item.inn);
	    strength.push(item.strength);
	});
	row.push(d.name || formulation.join(' + '));
	row.push(strength.join(' + '));
	row.push(d.dosageform.name);
	row.push(d3.round(d.avgprice,4));
	row.push(d3.round(d.mshprice,4) || '');
	return row;
    }
    var row_sort = function(a, b) {
	var a_formulation = [];
	var b_formulation = [];
	a.ingredients.forEach(function(item) {
	    a_formulation.push(item.inn);
	});
	b.ingredients.forEach(function(item) {
	    b_formulation.push(item.inn);
	});
	a_sort = a.name || a_formulation.join(' + ');
	b_sort = b.name || b_formulation.join(' + ');
	if (a_sort > b_sort) {
	    return 1;
	} else if (b_sort > a_sort) {
	    return -1;
	} else {
	    return 0;
	}
    }
    var tbody = d3.select(node)
	.select('#meddb_medicine_list')
	.select('tbody');
    tbody.selectAll('tr')
	.remove();
    var rows = tbody.selectAll('tr')
	.data(data.sort(row_sort))
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
