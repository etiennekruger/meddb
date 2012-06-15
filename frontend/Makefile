# See the README for installation instructions.

NODE_PATH ?= ./node_modules
JS_COMPILER = $(NODE_PATH)/uglify-js/bin/uglifyjs

all: \
	js/meddb.alpha.js \
	js/meddb.alpha.min.js

js/meddb.alpha.js: \
	src/start.js \
	src/main.js \
	src/settings.js \
	src/jsonp.js \
	src/template.js \
	src/router.js \
	src/history.js \
	src/tabber.js \
	src/medicine.js \
	src/medicine-list.js \
	src/medicine-detail.js \
	src/product.js \
	src/product-detail.js \
	src/supplier.js \
	src/supplier-detail.js \
	src/init.js \
	src/end.js

js/meddb.alpha.min.js: js/meddb.alpha.js Makefile
	@rm -f $@
	$(JS_COMPILER) < $< > $@

js/meddb.alpha.js: Makefile
	@rm -f $@
	cat $(filter %.js,$^) > $@
	@chmod a-w $@

clean:
	rm -f js/meddb.*.js
