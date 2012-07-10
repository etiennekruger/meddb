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
		var countries = data.procurements.map(function(el) { return el.country.name; });
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
