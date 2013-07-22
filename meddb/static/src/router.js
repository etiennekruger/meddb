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
