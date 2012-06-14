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
	row.push(d.dosageform.name);
	row.push(d3.round(d.avgprice,4));
	//if (d.procurements) {
	//    row.push(d3.round(d.procurements[0].price,4));
	//}
	return row;
    }
    var medicine_sort = function(a, b) {
	if ((a) && (b)) {
	    if (a.ingredients[0].inn < b.ingredients[0].inn) {
		return -1;
	    } else if (a.ingredients[0].inn > b.ingredients[0].inn) {
		return 1;
	    } else {
		return 0;
	    }
	} else {
	    return 0;
	}
    }
    meddb.template.load('medicine_list.html', function() {
	d3.json('/json/medicine/', function(data) {
	    var rows = d3.select('#meddb_container')
		.select('#meddb_medicine_list')
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
	    //rows.sort(medicine_sort);
	});
    });
    meddb.history.add(location.hash, 'All Medicine');
}
