(function($) {
    $.fn.fk_filter = function(verbose_name) {
        return this.each(function() {
            var stash = [];
            $(this).attr('size', 2); // Force a multi-row <select>
            $(this).find('option[value=""]').remove(); // Remove the '-----'

            // Create the wrappers
            var outerwrapper = $('<div />', {
                'class': 'selector selector-single'
            });
            $(this).wrap(outerwrapper);
            var innerwrapper = $('<div />', {
                'class': 'selector-available'
            });
            $(this).wrap(innerwrapper);

            // Creates Header
            var header = $('<h2 />', {
                'text': interpolate(gettext('Available %s'), [verbose_name])
            }).insertBefore(this);

            // Creates search bar
            var searchbar = $('<p />', {
                'html': '<img src="' + window.__admin_media_prefix__ + 'img/admin/selector-search.gif"> <input type="text" id="' + $(this).attr('id') + '_input">',
                'class': 'selector-filter'
            }).insertBefore(this);

            var select = $(this);
            var filter = $('#' + $(this).attr('id') + '_input');

            filter.bind('keyup.fkfilter', function(evt) {
                /*
                Procedure for filtering options::

                    * Detach the select from the DOM so each change doesn't
                      trigger the browser to re-render.
                    * Iterate through the stash list for matches
                    * ``matched`` is incremented whenever an stashed select
                      option is matched so that we don't have to search
                      recently appended options twice.
                    * Iterate through select's options and stash mismatched
                      options
                    * Attach the select back into the DOM for rendering.
                */
                var i, size, option, options;
                var pattern = filter.val();
                var parent = select.parent();
                var matched = 0;

                // detach from DOM
                select.detach();

                // Iterate through the excluded list for matches
                size = stash.length;
                for (i = 0; i < size; i++) {
                    if (stash[i].text.indexOf(pattern) !== -1) {
                        select.append(stash.splice(i--, 1));
                        matched++;
                        size--;
                    }
                }

                // Iterate through existing options for matches
                options = select.children();
                size = options.length - matched;
                for(i = 0; i < size; i++) {
                    if (options[i].text.indexOf(pattern) === -1) {
                        option = $(options[i]).detach();
                        stash.push(option[0]);
                    }
                }

                // Attach back onto the DOM
                parent.append(select);
            });
        });
    };
})(django.jQuery);
