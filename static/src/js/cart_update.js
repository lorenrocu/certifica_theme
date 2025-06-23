odoo.define('certifica_theme.cart_quantity_updater', function (require) {
    'use strict';

    var publicWidget = require('web.public.widget');
    var rpc = require('web.rpc');

    publicWidget.registry.WebsiteSale.include({
        _onClickAdd: function (ev) {
            var self = this;
            this._super.apply(this, arguments).then(function () {
                self._updateCartQuantity();
            });
        },

        _updateCartQuantity: function () {
            rpc.query({
                route: '/shop/cart/quantity',
                params: {},
            }).then(function (data) {
                $('.my_cart_quantity').text(data.cart_quantity || 0);
            });
        }
    });
});