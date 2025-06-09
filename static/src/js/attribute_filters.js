odoo.define('certifica_theme.attribute_filters', function (require) {
    'use strict';
    
    var publicWidget = require('web.public.widget');
    
    publicWidget.registry.AttributeFilters = publicWidget.Widget.extend({
        selector: '.shop-filters-container',
        events: {
            'click #apply_filters_button': '_onApplyFiltersClick'
        },
        
        /**
         * Inicialización del widget
         */
        start: function () {
            var self = this;
            return this._super.apply(this, arguments).then(function() {
                // Log de inicialización
                console.log('Widget de filtros de atributos inicializado');
            });
        },
        
        /**
         * Maneja el clic en el botón de aplicar filtros
         * Recoge todos los atributos seleccionados y redirige a la URL con los filtros aplicados
         * 
         * @private
         * @param {Event} ev
         */
        _onApplyFiltersClick: function (ev) {
            ev.preventDefault();
            console.log('Botón de aplicar filtros clickeado');
            
            // Obtener todos los checkboxes seleccionados
            var $selectedAttributes = $('.js_attribute_filter:checked');
            var attributeValues = [];
            
            // Recolectar los valores de los atributos seleccionados
            $selectedAttributes.each(function() {
                attributeValues.push($(this).val());
            });
            
            console.log('Atributos seleccionados:', attributeValues);
            
            // Redirigir a la URL con los filtros
            var baseUrl = window.location.pathname;
            var searchParams = new URLSearchParams(window.location.search);
            
            // Mantener otros parámetros como la categoría y la búsqueda
            // pero eliminar los atributos anteriores
            searchParams.delete('attrib');
            
            // Agregar los atributos seleccionados
            attributeValues.forEach(function(value) {
                searchParams.append('attrib', value);
            });
            
            // Construir la nueva URL
            var queryString = searchParams.toString();
            var newUrl = baseUrl + (queryString ? '?' + queryString : '');
            
            console.log('Redirigiendo a:', newUrl);
            
            // Redirigir al usuario a la nueva URL
            window.location.href = newUrl;
        }
    });
});
