meddb.procurement.detail = function(id) {
    var tracker = {}
    var not_available = '(Not Available)';
    meddb.template.hide();
    load('/procurement_detail.html', function(fragment) {
	load('/json/procurement/'+id+'/', function(data) {
	    /* Helper functions to process data. */
	    var detail = function() {
            var d = [];
            if ((data.product) && (data.product.name)) {
                d.push({ text: data.product.name, hash: 'product:'+data.product.id });
                tracker["Product Name"] = data.product.name;
            } else {
                d.push({ text: not_available });
                tracker["Product Name"] = not_available;
            }

            d.push({ text: data.container.quantity+' '+data.container.unit+' '+data.container.type });
            d.push({ text: data.volume+' (in packs of '+(data.packsize || 'unknown size')+')' });
            d.push({ text: d3.round(data.price_usd, 2) + ' USD'});
            d.push({ text: data.incoterm.name || '(Not Available)' });

            if ((data.supplier) && (data.supplier.name)) {
                d.push({ text: data.supplier.name, hash: 'supplier:'+data.supplier.id });
                tracker["Supplier"] = data.supplier.name;
            } else {
                d.push({ text: not_available});
                tracker["Supplier"] = not_available
            }

            if ((data.manufacturer) && (data.manufacturer.name)) {
                d.push({
                    text: data.manufacturer.name + ' - ' + data.manufacturer.country,
                    hash: 'manufacturer:' + data.manufacturer.id
                });
                tracker["Manufacturer"] = data.manufacturer.name;
            } else {
                d.push({ text: not_available });
                tracker["Manufacturer"] = not_available;
            }

            country = data.country.name || not_available;
            method = data.method.name || not_available;
            tracker["Country"] = country;
            tracker["Method"] = method;

            d.push({ text: country });
            d.push({ text: data.method || not_available });

            if ((data.start_date) && (data.end_date)) {
                d.push({ text: data.start_date+' to '+data.end_date });
            } else if (data.start_date) {
                d.push({ text: 'From '+data.start_date });
            } else if (data.end_date) {
                d.push({ text: 'Until '+data.end_date });
            }
            mixpanel.track("Procurement Detail", tracker);
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
