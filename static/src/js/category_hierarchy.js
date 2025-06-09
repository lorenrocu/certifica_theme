odoo.define('certifica_theme.category_hierarchy', function (require) {
    'use strict';
    
    var publicWidget = require('web.public.widget');
    var core = require('web.core');
    var _t = core._t;
    
    publicWidget.registry.CategoryHierarchy = publicWidget.Widget.extend({
        selector: '.category-hierarchy',
        events: {
            'click .category-toggle': '_onToggleClick',
            'click .subcategory-toggle': '_onToggleClick'
        },
        
        /**
         * Inicialización del widget
         */
        start: function () {
            var self = this;
            return this._super.apply(this, arguments).then(function() {
                // Auto-expandir la categoría activa al cargar
                self._expandActiveCategory();
            });
        },
        
        /**
         * Maneja el clic en los toggles de categorías y subcategorías
         * 
         * @private
         * @param {Event} ev
         */
        _onToggleClick: function (ev) {
            ev.preventDefault();
            ev.stopPropagation();
            
            var $target = $(ev.currentTarget);
            var categoryId = $target.data('category-id');
            var $icon = $target.find('i');
            var $subcategories = $('#subcategories-' + categoryId);
            
            if ($subcategories.length) {
                if ($subcategories.is(':visible')) {
                    $subcategories.slideUp(200);
                    $icon.removeClass('fa-minus-square-o').addClass('fa-plus-square-o');
                } else {
                    $subcategories.slideDown(200);
                    $icon.removeClass('fa-plus-square-o').addClass('fa-minus-square-o');
                }
            }
        },
        
        /**
         * Expande automáticamente la categoría activa y sus padres
         * 
         * @private
         */
        _expandActiveCategory: function () {
            var $activeLink = this.$('a.active');
            
            if ($activeLink.length) {
                // Expandir todas las categorías padre de la categoría activa
                $activeLink.parents('ul.subcategory-list, ul.grandchild-list').each(function() {
                    var $subcategories = $(this);
                    var categoryId = $subcategories.attr('id').replace('subcategories-', '');
                    
                    // Mostrar el contenedor de subcategorías
                    $subcategories.show();
                    
                    // Actualizar el ícono del toggle
                    var $toggle = $('[data-category-id="' + categoryId + '"]');
                    if ($toggle.length) {
                        $toggle.find('i')
                            .removeClass('fa-plus-square-o')
                            .addClass('fa-minus-square-o');
                    }
                });
            }
        }
    });
    

});
