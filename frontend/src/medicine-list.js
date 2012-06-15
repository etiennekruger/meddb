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
	row.push(d3.round(d.mshprice,4) || '');
	return row;
    }
    meddb.template.hide();
    meddb.template.load('medicine_list.html', function(fragment) {
	d3.json('/json/medicine/', function(data) {
	    var rows = d3.select(fragment)
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
	    meddb.history.add(location.hash, 'All Medicine');
	    meddb.template.show(fragment);
	});
    });
}
