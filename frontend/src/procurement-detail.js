meddb.procurement.detail = function(id) {
    meddb.template.hide();
    load('/procurement_detail.html', function(fragment) {
	load('/json/procurement/'+id+'/', function(data) {
	    /* Helper functions to process data. */
	    var detail = function() {
		var d = [];
		if ((data.product) && (data.product.name)) {
		    d.push({ text: data.product.name, hash: 'product:'+data.product.id });
		} else {
		    d.push({ text: '(Not Available)' });
		}
		d.push({ text: data.container.quantity+' '+data.container.unit+' '+data.container.type });
		d.push({ text: data.volume+' (in packs of '+(data.packsize || 'unknown size')+')' });
		d.push({ text: d3.round(data.price, 2)+' '+data.currency.code });
		d.push({ text: data.incoterm.name || '(Not Available)' });
		if ((data.supplier) && (data.supplier.name)) {
		    d.push({ text: data.supplier.name, hash: 'supplier:'+data.supplier.id });
		} else {
		    d.push({ text: '(Not Available)' });
		}
		if ((data.manufacturer) && (data.manufacturer.name)) {
		    d.push({
                text: data.manufacturer.name + ' - ' + data.manufacturer.country,
                hash: 'manufacturer:' + data.manufacturer.id
            });
		} else {
		    d.push({ text: '(Not Available)' });
		}
		d.push({ text: data.country.name || '(Not Available)' });
		d.push({ text: data.method || '(Not Available)' });
		if ((data.start_date) && (data.end_date)) {
		    d.push({ text: data.start_date+' to '+data.end_date });
		} else if (data.start_date) {
		    d.push({ text: 'From '+data.start_date });
		} else if (data.end_date) {
		    d.push({ text: 'Until '+data.end_date });
		}
		return d;
	    }
	    /* Populate product detail section. */
	    d3.select(fragment)
		.select('table#meddb_procurement_detail')
		.selectAll('td')
		.data(detail)
		.text(function(d) { return d.text; })
		.style('cursor', function(d) { if (d.hash) { return 'pointer' } })
		.on('click', function(d) { location.hash = d.hash; })
	    meddb.history.add(location.hash, 'Procurement '+data.id);
	    meddb.template.show(fragment);
	});
    });
}
