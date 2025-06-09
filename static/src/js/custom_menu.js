/**
 * Solución mejorada para:
 * 1. Actualizar el contador del carrito
 * 2. Añadir productos al carrito mediante AJAX sin redireccionar
 */

odoo.define('certifica_theme.cart_update', function (require) {
    'use strict';
    
    var sAnimations = require('website.content.snippets.animation');
    var core = require('web.core');
    var _t = core._t;
    var ajax = require('web.ajax');
    
    // Widget principal para gestionar el carrito
    sAnimations.registry.CartUpdater = sAnimations.Class.extend({
        selector: 'body',
        
        /**
         * @override
         */
        start: function () {
            this._super.apply(this, arguments);
            this._actualizarContadorCarrito();
            this._setupEventListeners();
            return this;
        },
        
        /**
         * Configura los event listeners para los botones de agregar al carrito
         */
        _setupEventListeners: function () {
            var self = this;
            
            // Escuchar envío de formularios de carrito y convertirlo a AJAX
            $(document).on('submit', '.add_to_cart_form', function(e) {
                e.preventDefault(); // Prevenir el envío normal del formulario
                
                var $form = $(this);
                var formData = $form.serializeArray();
                var formObject = {};
                
                // Convertir array de datos del formulario a objeto
                $.each(formData, function(_, field) {
                    formObject[field.name] = field.value;
                });
                
                // Añadir producto al carrito mediante AJAX
                self._agregarAlCarritoAjax($form, formObject);
                return false;
            });
            
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
        
        /**
         * Añade un producto al carrito mediante AJAX
         */
        _agregarAlCarritoAjax: function($form, formData) {
            var self = this;
            var $button = $form.find('button.a-submit');
            var originalText = $button.html();
            
            // Cambiar el texto del botón para indicar que se está procesando
            $button.html('<i class="fa fa-spinner fa-spin"></i> Agregando...');
            $button.prop('disabled', true);
            
            // Hacer la petición AJAX
            ajax.jsonRpc('/shop/cart/update_json', 'call', formData)
                .then(function(data) {
                    // Actualizar el contador del carrito
                    self._actualizarContadorCarrito();
                    
                    // Cambiar el texto del botón para indicar éxito brevemente
                    $button.html('<i class="fa fa-check"></i> Agregado');
                    $button.removeClass('btn-primary').addClass('btn-success');
                    
                    // Mostrar notificación de éxito
                    self._mostrarNotificacion('Producto agregado al carrito', 'success');
                    
                    // Restaurar el botón después de un tiempo
                    setTimeout(function() {
                        $button.html(originalText);
                        $button.prop('disabled', false);
                        $button.removeClass('btn-success').addClass('btn-primary');
                    }, 1500);
                })
                .catch(function(error) {
                    console.error('Error al agregar al carrito:', error);
                    
                    // Restaurar el botón
                    $button.html(originalText);
                    $button.prop('disabled', false);
                    
                    // Mostrar notificación de error
                    self._mostrarNotificacion('Error al agregar el producto', 'danger');
                });
        },
        
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
});