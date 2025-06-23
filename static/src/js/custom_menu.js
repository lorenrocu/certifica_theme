console.log('certifica_theme.cart_update cargado');

/**
 * Solución mejorada para:
 * 1. Actualizar el contador del carrito
 * 2. Añadir productos al carrito mediante AJAX sin redireccionar
 */

odoo.define('certifica_theme.cart_update', function (require) {
    'use strict';
    
    var publicWidget = require('web.public.widget');
    var ajax = require('web.ajax');
    
    // Widget principal para gestionar el carrito
    publicWidget.registry.CartUpdater = publicWidget.Widget.extend({
        selector: 'body',
        
        /**
         * @override
         */
        start: function () {
            this._actualizarContadorCarrito();
            this._setupEventListeners();
            return this._super.apply(this, arguments);
        },
        
        /**
         * Configura los event listeners para los botones de agregar al carrito
         */
        _setupEventListeners: function () {
            var self = this;
            
            // DESHABILITADO: Usar el sistema estándar de Odoo para evitar duplicaciones
            // El widget WebsiteSale de Odoo ya maneja correctamente el carrito
            // Solo mantenemos la actualización del contador después de cambios en el DOM
            
            // Observar cambios en el DOM para otras interacciones
            if (window.MutationObserver) {
                var observer = new MutationObserver(function(mutations) {
                    if (mutations.some(function(m) {
                        return m.addedNodes.length || m.removedNodes.length;
                    })) {
                        self._actualizarContadorCarrito();
                    }
                });
                
                observer.observe(document.body, {
                    childList: true,
                    subtree: true
                });
            }
        },
        
        // MÉTODO ELIMINADO: _agregarAlCarritoAjax
        // Ahora usamos el sistema estándar de Odoo que maneja correctamente el carrito
        
        /**
         * Muestra una notificación temporal
         */
        _mostrarNotificacion: function(mensaje, tipo) {
            // Crear elemento de notificación
            var $notificacion = $('<div class="alert alert-' + tipo + ' cart-notification">' +
                                 '<i class="fa ' + (tipo === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle') + '"></i> ' +
                                 mensaje +
                                 '</div>');
            
            // Eliminar notificaciones anteriores
            $('.cart-notification').remove();
            
            // Agregar al DOM
            $('body').append($notificacion);
            
            // Posicionar
            $notificacion.css({
                'position': 'fixed',
                'top': '80px',
                'right': '20px',
                'z-index': '9999',
                'box-shadow': '0 2px 10px rgba(0,0,0,0.1)',
                'min-width': '250px',
                'max-width': '100%',
                'padding': '15px',
                'border-radius': '4px',
                'opacity': '0',
                'transform': 'translateY(-20px)'
            });
            
            // Animar entrada
            setTimeout(function() {
                $notificacion.css({
                    'opacity': '1',
                    'transform': 'translateY(0)',
                    'transition': 'all 0.3s ease'
                });
            }, 10);
            
            // Remover después de un tiempo
            setTimeout(function() {
                $notificacion.css({
                    'opacity': '0',
                    'transform': 'translateY(-20px)'
                });
                setTimeout(function() {
                    $notificacion.remove();
                }, 300);
            }, 3000);
        },
        
        /**
         * Obtiene la cantidad actual del carrito y actualiza los contadores
         */
        _actualizarContadorCarrito: function () {
            var self = this;
            
            // Usar la ruta estándar de Odoo para obtener datos del carrito
            ajax.jsonRpc('/shop/cart/count', 'call', {})
                .then(function (cantidad) {
                    self._actualizarVisualizacionCarrito(cantidad);
                })
                .catch(function(error) {
                    console.error('Error al obtener la cantidad del carrito:', error);
                });
        },
        
        /**
         * Actualiza todos los badges con la cantidad del carrito
         */
        _actualizarVisualizacionCarrito: function (cantidad) {
            console.log('Actualizando cantidad del carrito:', cantidad);
            var $badgeDesktop = $('.cart-icon .badge');
            var $badgeMobile = $('.cart-icon-mobile .badge');
            
            if (cantidad && parseInt(cantidad) > 0) {
                $badgeDesktop.text(cantidad).css('display', 'flex');
                $badgeMobile.text(cantidad).css('display', 'flex');
            } else {
                $badgeDesktop.text('0').css('display', 'none');
                $badgeMobile.text('0').css('display', 'none');
            }
        }
    });
    return publicWidget.registry.CartUpdater;
});