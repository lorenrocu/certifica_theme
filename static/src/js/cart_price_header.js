odoo.define('certifica_theme.cart_price_header', function (require) {
    'use strict';

    var publicWidget = require('web.public.widget');

    publicWidget.registry.CartPriceHeader = publicWidget.Widget.extend({
        selector: '.oe_website_sale .oe_cart',
        
        start: function () {
            var self = this;
            return this._super.apply(this, arguments).then(function () {
                // Verificar que estamos en la página del carrito
                if (window.location.pathname === '/shop/cart') {
                    self._updatePriceHeader();
                }
            });
        },

        _updatePriceHeader: function () {
            // Buscar el encabezado de precio en la tabla del carrito
            var $priceHeader = this.$('th.text-center.td-price');
            
            if ($priceHeader.length > 0) {
                // Cambiar el texto de "Precio" a "Precio Unitario"
                $priceHeader.text('Precio Unitario');
                console.log('Texto del encabezado de precio actualizado a "Precio Unitario"');
            } else {
                // Intentar con otros selectores posibles
                var $altPriceHeader = this.$('th:contains("Precio")');
                if ($altPriceHeader.length > 0) {
                    $altPriceHeader.text('Precio Unitario');
                    console.log('Texto del encabezado de precio actualizado a "Precio Unitario" (selector alternativo)');
                } else {
                    console.log('No se encontró el encabezado de precio en la tabla del carrito');
                }
            }
        }
    });

    return publicWidget.registry.CartPriceHeader;
});