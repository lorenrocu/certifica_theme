odoo.define('certifica_theme.custom_search', function (require) {
    'use strict';

    var publicWidget = require('web.public.widget');

    publicWidget.registry.CustomSearch = publicWidget.Widget.extend({
        selector: '.header-search .search-form',
        events: {
            'submit': '_onSearchSubmit',
        },

        /**
         * @override
         */
        start: function () {
            this.$input = this.$('input.search-input');
            return this._super.apply(this, arguments);
        },

        //--------------------------------------------------------------------------
        // Handlers
        //--------------------------------------------------------------------------

        /**
         * Handles the search form submission.
         *
         * @private
         * @param {Event} ev
         */
        _onSearchSubmit: function (ev) {
            ev.preventDefault();
            var searchTerm = this.$input.val().trim();
            if (searchTerm) {
                var searchUrl = '/shop?search=' + encodeURIComponent(searchTerm);
                window.location.href = searchUrl;
            }
        },
    });

    return publicWidget.registry.CustomSearch;
});