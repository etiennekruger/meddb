(function() {
meddb = {}
var settings = {
    'static_base_url': '',
    'data_base_url': '',
    'loader': 'standard'
};

(function(url) {
    /* Update the settings with overrides from url. */
    d3.json(url, function(data) {
	settings = data;
    });
})('meddb.json');
var standard_loader = function(url, callback) {
    if (url.slice(-5) == '.html') {
	d3.html(url, callback);
    } else {
	d3.json(url, callback);
    }
}

var jsonp_loader = function(url, callback) {
    /* Setup callback for either the HTML or JSON case. */
    var request;
    if (url.slice(-5) == '.html') {
	request = [settings.static_base_url+url.slice(0,-5)+'.jsonp'];
	meddb.callback = function(data) {
	    var fragment = document.createDocumentFragment();
	    var element = document.createElement('div');
	    element.innerHTML = data;
	    fragment.appendChild(element.firstChild);
	    callback(fragment);
	}
    } else {
	request = [settings.data_base_url+url+'?jsonp=meddb.callback'];
	meddb.callback = function(data) {
	    callback(data);
	}
    }
    /* Now add the script tag to the body. */
    d3.select('html body')
	.select('script#meddb_jsonp')
	.remove();
    d3.select('html body')
	.select('script#meddb_jsonp')
	.data(request)
	.enter()
	.append('script')
	.attr('id', 'meddb_jsonp')
	.attr('src', function(d) { return d; });
}

var load = function(url, callback) {
    /* Call the appropriate loader according to the settings. */
    if (settings.loader == 'standard') {
	standard_loader(url, callback);
    } else if (settings.loader == 'jsonp') {
	jsonp_loader(url, callback);
    }
}

meddb.template = {};
meddb.template.cache = {};

meddb.template.load = function(url, callback) {
    d3.html(url, function(fragment) {
	callback(fragment);
    });
}

meddb.template.inject = function(fragment, selector) {
    selector = selector || '#meddb_inner_container';
    var node = d3.select(selector)[0][0];
    node.innerHTML = '';
    node.appendChild(fragment);
}

meddb.template.hide = function() {
    d3.select('#meddb_page')
	.attr('id', 'meddb_page_outgoing')
	.transition()
	.style('opacity', '0')
	.style('left', '-950px')
	.remove();
    d3.select('img#meddb_loading')
	.transition()
	.duration(100)
	.style('opacity', 1);
}

meddb.template.show = function(fragment) {
    var selector = '#meddb_inner_container';
    d3.select(fragment)
	.select('.meddb_inner_page')
	.attr('id', 'meddb_page_incoming')
	.style('opacity', '0')
	.style('left', '950px');
    var node = d3.select(selector)[0][0];
    node.appendChild(fragment);
    var height = d3.select('#meddb_page_incoming')[0][0].clientHeight;
    d3.select('#meddb_page_incoming')
	.transition()
	.style('opacity', '1')
	.style('left', '0px')
	.attr('id', 'meddb_page');
    d3.select('img#meddb_loading')
	.transition()
	.duration(100)
	.style('opacity', 0);
    d3.select('#meddb_inner_container')
	.transition()
	.style('height', height+'px');
}

meddb.template.replace = function(fragment) {
    var selector = '#meddb_inner_container';
    d3.select('#meddb_page')
	.attr('id', 'meddb_page_outgoing')
	.transition()
	.style('opacity', '0')
	.remove();
    d3.select(fragment)
	.select('.meddb_inner_page')
	.attr('id', 'meddb_page_incoming')
	.style('opacity', '0')
	.style('left', '0px');
    var node = d3.select(selector)[0][0];
    node.appendChild(fragment);
    var height = d3.select('#meddb_page_incoming')[0][0].clientHeight;
    d3.select('#meddb_page_incoming')
	.transition()
	.style('opacity', '1')
	.attr('id', 'meddb_page');
    d3.select('img#meddb_loading')
	.transition()
	.duration(100)
	.style('opacity', 0);
    d3.select('#meddb_inner_container')
	.transition()
	.style('height', height+'px');
}

meddb.template.fx = function(fragment) {
    var selector = '#meddb_inner_container';
    d3.select(fragment)
	.select('.meddb_inner_page')
	.attr('id', 'meddb_page_incoming')
	.style('opacity', '0')
	.style('left', '950px');
    var node = d3.select(selector)[0][0];
    //node.innerHTML = '';
    node.appendChild(fragment);
    d3.select('#meddb_page')
	.attr('id', 'meddb_page_outgoing')
	.transition()
	.style('opacity', '0')
	.style('left', '-950px')
	.remove();
    d3.select('#meddb_page_incoming')
	.transition()
	.style('opacity', '1')
	.style('left', '0px')
	.attr('id', 'meddb_page');
}
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
	} else if (hash.substring(0,13) == '#procurement:') {
	    var id = parseInt(hash.substring(13));
	    meddb.procurement.detail(id);
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
    d3.select('ul#meddb_breadcrumb')
	.selectAll('li')
	.remove();
    var li = d3.select('ul#meddb_breadcrumb')
	.selectAll('li')
	.data(meddb.history.list.slice(-5))
	.enter()
	.append('li');
    li.append('a')
	.attr('href', function(d) { return d.hash; })
	.text(function(d) { return d.text; });
    li.append('span')
	.classed('divider', true)
	.text(' / ');
}
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
meddb.medicine = {};
var medicine_list = function(data, node) {
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
render_pack = function(procurement) {
    return procurement.container.quantity + ' '+ procurement.container.unit + ' (' + procurement.container.type +')';

}

meddb.product_row = function(d) {
    var row = [];
    var prod_name = d.product.name;

    if (d.product.name == 0) {
        prod_name = '(Name not Available)' 
    }
    row.push({
        text: prod_name,
        hash: 'product:' + d.product.id
    });

    if ((d.supplier) && (d.supplier.name != '')) {
        row.push({
            text: d.supplier.name,
            hash: 'supplier:' + d.supplier.id
        });
    } else {
        row.push({ text: '(Not Available)' });
    }
    if ((d.product.manufacturer) && (d.product.manufacturer.name != '')) {
        row.push({
            text: d.product.manufacturer.name,
            hash: 'manufacturer:' + d.product.manufacturer.id
        });
    } else {
        row.push({ text: '(Not Available)' });
    }

    row.push({
        text: d.country.name,
    });

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
            var hash = 'procurement:'+d.id;
            row.push({ text: d.country.name, hash: hash });
            var ppu = d3.round(d.price_per_unit,4);

            if (typeof ppu == 'number') {
                row.push({ text: ppu, hash: hash });
            } else {
                row.push({ text: '(Not Available)', hash: hash });
            }

            row.push({ text: d3.round(d.price_usd,4), hash: hash });
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
            row.push({ text: (d.volume ||'(Not Available)') , hash: hash });
            if (d.start_date && d.end_date) {
                row.push({ text: d.start_date+' to '+d.end_date, hash: hash });
            } else if (d.start_date) {
                row.push({ text: 'From '+d.start_date, hash: hash });
            } else if (d.end_date) {
                row.push({ text: 'Until '+d.end_date, hash: hash });
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
            .style('cursor', 'pointer')
                .on('click', function(d, i) { location.hash = d.hash; })
            .text(function(d) { return d.text; });

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
meddb.product = {};
meddb.product.detail = function(id) {
    meddb.template.hide();
    load('/product_detail.html', function(fragment) {
        load('/json/product/' + id + '/', function(data) {
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
                d.push(data.medicine.dosageform.name || '(Not Available)');

                if ((data.manufacturer) && (data.manufacturer.name != '')) {
                    d.push(data.manufacturer.name + ' - ' + data.manufacturer.country);
                } else {
                    d.push('(Not Available)');
                }

                if ((data.manufacturer.site) && (data.manufacturer.site != '')) {
                    d.push(data.manufacturer.site);
                } else {
                    d.push('(Not Available)');
                }

                return d;

            }

            var procurement = function(d) {
                var row = [];
                row.push({
                    text: d.country.name
                });
                if ((d.supplier) && (d.supplier.name != '')) {
                    row.push({
                    text: d.supplier.name,
                    hash: 'supplier:' + d.supplier.id
                    })
                } else {
                    row.push({ text: '(Not Available)' });
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
            uniq_suppliers = _.uniq(data.procurements, false, function(proc) {
                return proc.supplier.hash + proc.country.name;
            });
            var rows = d3.select(fragment)
            .select('table#meddb_product_registration')
                .select('tbody')
                .selectAll('tr')
                    .data(uniq_suppliers)
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
meddb.procurement = {};
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
		d.push({ text: d3.round(data.price_usd, 2) + ' USD'});
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
meddb.supplier = {};
meddb.supplier.detail = function(id) {
    meddb.template.hide();
    load('/supplier_detail.html', function(fragment) {
	load('/json/supplier/'+id+'/', function(data) {
	    /* Helper functions to process data. */
	    var procurement = function(d) {
        var product = d.product;

		var row = [];
		row.push({
		    text: d.product.name,
		    hash: 'product:'+d.product.id
		});
        row.push({
            text: product["pack-size"]["quantity"] + ' ' + 
                  product["pack-size"]["unit"] + ' ' + 
                  product["pack-size"]["type"],
            hash: 'product:'+ d.product.id
        });

		row.push({
		    text: d.country.name,
		});
		var ingredients = [];
		d.product.medicine.ingredients.forEach(function(i) {
		    ingredients.push(i.inn+' '+i.strength);
		});
		row.push({
		    text: ingredients.join(', '),
		    hash: 'medicine:'+d.product.medicine.id
		});
		return row;
	    }
	    /* Populate supplier heading section. */
	    d3.select(fragment)
		.select('#meddb_supplier_heading')
		.text(data.name);
	    /* Populate the supplier detail page. */
	    var details = function() {
		var row = [];
		row.push(data.website || '(Not Available)');
		row.push(data.contact || '(Not Available)');
		row.push(data.email || '(Not Available)');
		row.push(data.altemail || '(Not Available)');
		row.push(data.phone || '(Not Available)');
		row.push(data.altphone || '(Not Available)');
		row.push(data.fax || '(Not Available)');
		row.push(data.address || '(Not Available)');
		return row;
	    }
	    d3.select(fragment)
		.select('table#meddb_supplier_details')
		.selectAll('td')
		.data(details())
		.text(function(d) { return d; });
	    d3.select(fragment)
		.select('table#meddb_supplier_details')
		.select('td')
	        .data([data.website])
		.style('cursor', 'pointer')
		.on('click', function(d) { if (d) { location = d; } });
	    /* Populate the product registrations table. */
	    var rows = d3.select(fragment)
		.select('table#meddb_supplier_registration')
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
meddb.template.load('base.html', function(fragment) {
    meddb.template.inject(fragment, '#meddb_container');
    meddb.router();
});
window.onhashchange = meddb.router;})();