meddb.template.load('base.html', function(fragment) {
    meddb.template.inject(fragment, '#meddb_container');
    meddb.router();
});
window.onhashchange = meddb.router;