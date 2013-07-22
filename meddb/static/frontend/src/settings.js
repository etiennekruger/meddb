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
