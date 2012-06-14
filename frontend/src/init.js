meddb.template.load('base.html', function() {
    meddb.router();
}, '#meddb_container');
window.onhashchange = meddb.router;