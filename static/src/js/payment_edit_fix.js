odoo.define('certifica_theme.payment_edit_fix', function (require) {
'use strict';

var publicWidget = require('web.public.widget');

// Widget para modificar los enlaces de editar en la página de pago
publicWidget.registry.PaymentEditFix = publicWidget.Widget.extend({
    selector: '.oe_website_sale', // Selector para páginas de venta
    
    start: function () {
        var self = this;
        
        // Solo ejecutar en la página de pago
        if (window.location.pathname === '/shop/payment') {
            this._fixEditLinks();
        }
        
        return this._super.apply(this, arguments);
    },
    
    _fixEditLinks: function () {
        var self = this;
        
        // Buscar todos los enlaces que contengan 'checkout' en su href
        var checkoutLinks = $('a[href*="checkout"]');
        
        checkoutLinks.each(function() {
            var $link = $(this);
            var currentHref = $link.attr('href');
            
            // Si el enlace no tiene ya el parámetro from_payment, agregarlo
            if (currentHref && !currentHref.includes('from_payment=1')) {
                var separator = currentHref.includes('?') ? '&' : '?';
                var newHref = currentHref + separator + 'from_payment=1';
                $link.attr('href', newHref);
                
                console.log('Fixed edit link:', currentHref, '->', newHref);
            }
        });
        
        // También buscar enlaces por texto "Editar" o "Edit"
        var editLinks = $('a:contains("Editar"), a:contains("Edit")');
        
        editLinks.each(function() {
            var $link = $(this);
            var currentHref = $link.attr('href');
            
            // Si el enlace contiene checkout o address, modificarlo
            if (currentHref && (currentHref.includes('checkout') || currentHref.includes('address'))) {
                if (!currentHref.includes('from_payment=1')) {
                    var separator = currentHref.includes('?') ? '&' : '?';
                    var newHref = currentHref + separator + 'from_payment=1';
                    $link.attr('href', newHref);
                    
                    console.log('Fixed edit text link:', currentHref, '->', newHref);
                }
            }
        });
        
        // Buscar enlaces con iconos de editar
        var iconEditLinks = $('a i.fa-edit, a i.fa-pencil').parent();
        
        iconEditLinks.each(function() {
            var $link = $(this);
            var currentHref = $link.attr('href');
            
            if (currentHref && (currentHref.includes('checkout') || currentHref.includes('address'))) {
                if (!currentHref.includes('from_payment=1')) {
                    var separator = currentHref.includes('?') ? '&' : '?';
                    var newHref = currentHref + separator + 'from_payment=1';
                    $link.attr('href', newHref);
                    
                    console.log('Fixed icon edit link:', currentHref, '->', newHref);
                }
            }
        });
    }
});

return publicWidget.registry.PaymentEditFix;

});