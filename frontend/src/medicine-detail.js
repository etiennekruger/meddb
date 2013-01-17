meddb.medicine.detail = function(id, sort, reverse, replace) {
    if (replace != true) {
	meddb.template.hide();
    }
    if (sort == undefined) { sort = 'country'; }
    if (reverse == undefined) { reverse = false; }
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
		var ppu = d3.round(d.price_per_unit,4);
		if (typeof ppu == 'number') {
		    row.push(ppu);
		} else {
		    row.push('(Not Available)');
		}
		row.push(d3.round(d.price,4));
		row.push(d.incoterm || '(Not Available)');
		if (d.pack) {
		    row.push(d.container.quantity+' '+d.container.unit+' ('+d.container.type+')');
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
	    /* Sorting code. */
	    var sorter = function(a, b) {
		var a_sort = '';
		var b_sort = '';
		if (sort == 'country') {
		    a_sort = a.country.name;
		    b_sort = b.country.name;
		} else if (sort == 'price_per_unit') {
		    a_sort = a.price_per_unit;
		    b_sort = b.price_per_unit;		    
		} else if (sort == 'price') {
		    a_sort = a.price;
		    b_sort = b.price;		    
		} else if (sort == 'incoterm') {
		    a_sort = a.incoterm;
		    b_sort = b.incoterm;		    
		} else if (sort == 'pack_size') {
		    a_sort = a.container.quantity;
		    b_sort = b.container.quantity;		    
		} else if (sort == 'volume') {
		    a_sort = a.volume;
		    b_sort = b.volume;		    
		} else if (sort == 'start_date') {
		    a_sort = a.start_date;
		    b_sort = b.start_date;		    
		}
		if (reverse) {
		    if (a_sort > b_sort) {
			return -1;
		    } else if (b_sort > a_sort) {
			return 1;
		    } else {
			return 0;
		    }
		    
		} else {
		    if (a_sort > b_sort) {
			return 1;
		    } else if (b_sort > a_sort) {
			return -1;
		    } else {
			return 0;
		    }
		}
	    }
	    var sort_actions = [
		{'sort': 'country', 'reverse': false},
		{'sort': 'price_per_unit', 'reverse': false},
		{'sort': 'price', 'reverse': false},
		{'sort': 'incoterm', 'reverse': false},
		{'sort': 'pack_size', 'reverse': false},
		{'sort': 'volume', 'reverse': false},
		{'sort': 'start_date', 'reverse': false}
	    ];
	    for (i in sort_actions) {
		sort_actions[i].append = '';
		if (sort_actions[i].sort == sort) {
		    sort_actions[i].reverse = !reverse;
		    if (reverse) {
			sort_actions[i].append = '&#9660;';
		    } else {
			sort_actions[i].append = '&#9650;';
		    }
		}
	    }
	    d3.select(fragment)
		.select('#meddb_medicine_procurement')
		.select('thead')
		.selectAll('th')
		.data(sort_actions)
		.attr('cursor', 'pointer')
		.html(function(d, i) { return d3.select(this).html() + d.append })
		.on('click', function(d, i) { meddb.medicine.detail(id, d.sort, d.reverse, true); });
	    /* Sorting done. */
	    d3.select(fragment)
		.select('#meddb_medicine_heading')
		.text(object_name());
	    var rows = d3.select(fragment)
		.select('#meddb_medicine_procurement')
		.select('tbody')
		.selectAll('tr')
		.data(data.procurements.sort(sorter))
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
	    /* Add the medicine prices graph. */
	    var prices_data = function() {
		var prices = {};
		data.procurements.forEach(function(item) {
		    if (typeof(prices[item.country.name]) == 'undefined') {
			prices[item.country.name] = [];
		    }
		    prices[item.country.name].push({ 'price' : item.price,
						     'packsize' : item.pack.quantity,
						     'volume' : item.volume });
		});
		graph_data = [];
		for (country in prices) {
		    var d = { 'key': country }
		    var p = prices[country];
		    if ((prices[country]) && (prices[country].length > 0)) {
			var sum = 0;
			var tot = 0;
			for (index in p) {
			    var price = p[index];
			    sum += price.price*price.volume;
			    tot += price.volume*price.packsize;
			}
			d.value = sum/tot;
			//d.value = d3.sum(p.per_unit) / prices[country].length;
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
	    if (replace == true) {
		meddb.template.replace(fragment);
	    } else {
		/* Add history option. */
		meddb.history.add(location.hash, object_name());
		meddb.template.show(fragment);
	    }
	});
    });
}
