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
