render_pack = function(procurement) {
    return procurement.container.quantity + ' '+ procurement.container.unit + ' (' + procurement.container.type +')';

}

meddb.product_row = function(d) {
    var row = [];
    var prod_name = d.product.name;
    var tracker = {}

    if (d.product.name == 0) {
        prod_name = '(Name not Available)' 
    }
    row.push({
        text: prod_name,
        hash: 'product:' + d.product.id
    });

    tracker["Product Name"] = prod_name
    tracker["Product ID"] = d.product.id
    

    if ((d.supplier) && (d.supplier.name != '')) {
        tracker["Supplier"] = d.supplier.name
        row.push({
            text: d.supplier.name,
            hash: 'supplier:' + d.supplier.id
        });
    } else {
        supplier_name = '(Not Available)';
        row.push({ text: supplier_name });
        tracker["Supplier"] = supplier_name;
    }

    if ((d.product.manufacturer) && (d.product.manufacturer.name != '')) {
        tracker["Manufacturer"] = d.product.manufacturer.name;
        row.push({
            text: d.product.manufacturer.name,
            hash: 'manufacturer:' + d.product.manufacturer.id
        });
    } else {
        manufacturer_name = '(Not Available)';
        row.push({ text: manufacturer_name });
        tracker["Manufacturer"] = manufacturer_name;
    }

    row.push({
        text: d.country.name,
    });
    tracker["Country"] = d.country.name;

    mixpanel.track("Medicine Detail", tracker);

    return row;
}

meddb.products = function(rows) {
}

meddb.medicine.detail = function(id, sort, reverse, replace) {
    if (replace != true) {
	meddb.template.hide();
    }
    if (sort == undefined) { sort = 'country'; }
    if (reverse == undefined) { reverse = false; }
    load('/medicine_detail.html', function(fragment) {
	load('/json/medicine/' + id+'/', function(data) {
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
            var hash = 'procurement:' + d.id;
            row.push({ text: d.country.name, hash: hash });
            var ppu = d3.round(d.price_per_unit, 4);

            if (typeof ppu == 'number') {
                row.push({ text: ppu, hash: hash });
            } else {
                row.push({ text: '(Not Available)', hash: hash });
            }

            row.push({ text: d3.round(d.price_usd,4), hash: hash });
            if (d.manufacturer) {
                row.push({ text: d.manufacturer.name, hash:hash });
                row.push({ text: d.manufacturer.country, hash:hash });
            } else {
                row.push({ text: '(Not Available)', hash: hash });
                row.push({ text: '(Not Available)', hash: hash });
            }
                
            if (typeof ppu == 'number') {
                row.push({ text: d3.round((ppu / data.mshprice),4), hash: hash });
            } else {
                row.push({ text: '(Not Available)', hash: hash });
            }
            row.push({ text: (d.incoterm.name || '(Not Available)'), hash: hash });
            //row.push({ text: d.container.quantity+' '+d.container.unit+' ('+d.container.type+')', hash: hash });
            row.push({
                text: render_pack(d),
                hash: hash 
            });

            row.push({ text: (d.volume || '(Not Available)') , hash: hash });
            if (d.start_date && d.end_date) {
                row.push({ text: d.start_date +' to '+ d.end_date, hash: hash });
            } else if (d.start_date) {
                row.push({ text: 'From '+ d.start_date, hash: hash });
            } else if (d.end_date) {
                row.push({ text: 'Until '+ d.end_date, hash: hash });
            } else {
                row.push({ text: '(Not Available)', hash: hash });
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
		    a_sort = a.price_usd;
		    b_sort = b.price_usd;		    
		} else if (sort == 'msh_ratio') {
		    a_sort = a.price_per_unit;
		    b_sort = b.price_per_unit;		    
		} else if (sort == 'incoterm') {
		    a_sort = a.incoterm;
		    b_sort = b.incoterm;		    
		} else if (sort == 'manufacturer') {
		    a_sort = a.manufacturer;
		    b_sort = b.manufacturer;		    
		} else if (sort == 'manufacturer_country') {
		    a_sort = a.manufacturer.country;
		    b_sort = b.manufacturer.country;		    
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
		{'sort': 'manufacturer', 'reverse': false},
		{'sort': 'manufacturer_country', 'reverse': false},
		{'sort': 'msh_ratio', 'reverse': false},
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
                .style('cursor', 'pointer')
                .html(function(d, i) {
                    return d3.select(this).html() + d.append 
                })
                .on('click', function(d, i) {
                    meddb.medicine.detail(id, d.sort, d.reverse, true);
                });

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
            .style('cursor', 'pointer')
            .on('click', function(d, i) { location.hash = d.hash; })
            .text(function(d) {return d.text; });

        var proc_rows = {};
        for (idx in data.procurements) {
            var row = meddb.product_row(data.procurements[idx]);
            var prod_id = row[0].hash;

            var product = row[0];
            var supplier = row[1];
            var manufacturer = row[2];
            var country = row[3];
            
            if (product.hash in proc_rows) {
                var p = proc_rows[product.hash]
                p[3].push(country);
                p[1].push(supplier);
            } else {
                var p = [
                    product,
                    [supplier],
                    manufacturer,
                    [country]
                ]
                proc_rows[product.hash] = p;
            }
        }
        
        proc_values = _.values(proc_rows);
	    /* Populate products table. */
	    var rows = d3.select(fragment)
            .select('#meddb_medicine_product')
            .select('tbody')
            .selectAll('tr')
            .data(proc_values)

        click_if_hash = function(el) {
            if (el.hash) {
                location.hash = el.hash;
            }
        }

        point_if_hash = function(el) {
            if (el.hash) {
                return 'pointer' 
            }
        }

        return_text = function(el) {
            return el.text;
        }

	    rows
            .enter()
            .append('tr')
            .each(function(d, i) {
                d3.select(this).selectAll('td')
                    .data(d)
                    .enter()
                    .append('td')
                    .each(function(cell, i) {
                        if (_.isArray(cell)) {
                            var uniq_elements = _.uniq(cell, false, return_text)
                            d3.select(this).selectAll('span')
                                .data(uniq_elements)
                                .enter()
                                .append('span')
                                .classed('multi-element', true)
                                .text(return_text)
                                .style('cursor', point_if_hash)
                                .on('click', click_if_hash);
                        } else {
                            return d3.select(this).text(return_text);
                        }
                    })
                    .style('cursor', point_if_hash)
                    .on('click', click_if_hash);
            });
        
	    /* Add the medicine prices graph. */
	    var prices_data = function() {
		var prices = {};
		data.procurements.forEach(function(item) {
            label = item.country.name + ' - ' + render_pack(item);
		    if (typeof(prices[label]) == 'undefined') {
			prices[label] = [];
		    }
		    prices[label].push({ 'price' : item.price_usd,
						     'packsize' : item.container.quantity,
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
            colors: ['#08c', '#08c', '#08c', '#08c', '#08c', '#08c', '#08c', '#08c'],
            data : graph_data
	    }

	    if (data.mshprice) {
                prices_graph.line = {
                    'constant': data.mshprice,
                    'text': 'MSH: $' + d3.round(data.mshprice, 4) + ' (2012 Median Buyer Price)' 
                };
        }

        d3.select(fragment).select('#meddb_medicine_prices').html('');
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
