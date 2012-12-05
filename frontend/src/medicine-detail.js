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
		var ppu = d3.round(d.price_per_unit,8);
		if (typeof ppu == 'number') {
		    row.push(ppu);
		} else {
		    row.push('(Not Available)');
		}
		row.push(d3.round(d.price,4));
		row.push(d.incoterm || '(Not Available)');
		if (d.pack) {
		    row.push(d.pack.quantity+' '+d.pack.name);
		} else {
		    row.push('(Not Available)');
		}
		row.push(d.volume || '(Not Available)');
		if (d.start_date && d.end_date) {
		    row.push(d.start_date+' to '+d.end_date);
		} else if (d.start_date) {
		    row.push('From '+d.start_date);
		} else if (d.end_date) {
		    row.push('Until '+d.end_date);
		} else {
		    row.push('(Not Available)');
		}
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
		if ((d.supplier) && (d.supplier.name != '')) {
		    row.push({
			text: d.supplier.name,
			hash: 'supplier:'+d.supplier.id
		    });
		} else {
		    row.push({ text: '(Not Available)' });
		}
		if ((d.manufacturer) && (d.manufacturer.name != '')) {
		    row.push({
			text: d.manufacturer.name,
			hash: 'manufacturer:'+d.manufacturer.id
		    });
		} else {
		    row.push({ text: '(Not Available)' });
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
		.data(data.procurements);
	    rows.enter()
		.append('tr');
	    rows.selectAll('td')
		.data(product_data)
		.enter()
		.append('td')
		.text(function(d) { return d.text; })
		.style('cursor', function(d) { if (d.hash) { return 'pointer' } })
		.on('click', function(d) { if (d.hash) {location.hash = d.hash;} });
	    /* Make the table sortable. */
	    /*
	    function sort_asc(a, b) {
		if (isNumber(a) && isNumber(b)) {
		    return a - b;
		} else if (isString(a) && isString(b) {
		    a.localeCompare(b);
		} else {
		    return 0;
		}
	    }
	    function sort_desc(a, b) {
		if (isNumber(a) && isNumber(b)) {
		    return b - a;
		} else if (isString(a) && isString(b) {
		    b.localeCompare(a);
		} else {
		    return 0;
		}
	    }
	    var headers = d3.select('#meddb_medicine_product')
		.select('thead')
		.selectAll('th')
		.on('click', function(d, i) {
		    console.log(d);
		    if (!d) { d = -1; };
		    if (!d) {
			d = 1;
			rows.sort(sort_asc);
		    } else {
			d = -1;
			rows.sort(sort_desc);
		    }
		});
	    */
	    /* Add the medicine prices graph. */
	    var prices_data = function() {
		var prices = {};
		data.procurements.forEach(function(item) {
		    if (typeof(prices[item.country.name]) == 'undefined') {
			prices[item.country.name] = [];
		    }
		    prices[item.country.name].push(item.price_per_unit);
		});
		graph_data = [];
		console.log(prices);
		for (country in prices) {
		    var d = { 'key': country }
		    if ((prices[country]) && (prices[country].length > 0)) {
			d.value = d3.sum(prices[country]) / prices[country].length;
		    } else {
			d.value = 0;
		    }
		    graph_data.push(d);
		}
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
		height: graph_data.length * 25 + 20,
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
		prices_graph.line = { 'constant': data.mshprice,
				      'text': 'MSH: $' + d3.round(data.mshprice,4) };
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
