/* =============================================================================
   CHECKOUT CUSTOMIZATIONS - CERTIFICA THEME
   JavaScript para manejar el formulario de checkout personalizado
   ============================================================================= */

odoo.define('certifica_theme.checkout_custom', function (require) {
    'use strict';

    var publicWidget = require('web.public.widget');
    var core = require('web.core');
    var _t = core._t;

    // Widget para manejar el checkout personalizado
    publicWidget.registry.CheckoutCustom = publicWidget.Widget.extend({
        selector: '.checkout_autoformat, .custom-checkout-form',
        events: {
            'change input[name="country_id"]': '_onChangeCountry',
            'change input[name="state_id"]': '_onChangeState',
            'change input[name="invoice_type"]': '_onChangeInvoiceType',
            'submit': '_onSubmitForm',
            'input .form-control': '_onInputChange',
            'input input[name="vat"]': '_onVatInputChange',
            'keyup input[name="vat"]': '_onVatInputChange',
            'paste input[name="vat"]': '_onVatInputChange',
        },

        /**
         * Inicialización del widget
         */
        start: function () {
            this._super.apply(this, arguments);
            this._hideRemovedFields();
            this._setupFormValidation();
            this._enhanceFormUX();
        },

        /**
         * Ocultar campos eliminados (street2 y zip)
         */
        _hideRemovedFields: function () {
            // Ocultar todos los elementos relacionados con street2
            this.$('input[name="street2"], label[for="street2"], .div_street2').hide();
            this.$('.form-group:has(input[name="street2"])').hide();
            
            // Ocultar todos los elementos relacionados con zip
            this.$('input[name="zip"], label[for="zip"], .div_zip').hide();
            this.$('.form-group:has(input[name="zip"])').hide();
            
            // Remover validaciones requeridas de estos campos
            this.$('input[name="street2"], input[name="zip"]').removeAttr('required');
        },

        /**
         * Configurar validaciones del formulario
         */
        _setupFormValidation: function () {
            // Marcar campos requeridos
            var requiredFields = ['name', 'email', 'phone', 'street', 'city'];
            var self = this;
            
            requiredFields.forEach(function(fieldName) {
                var $field = self.$('input[name="' + fieldName + '"], select[name="' + fieldName + '"]');
                var $label = self.$('label[for="' + fieldName + '"]');
                
                if ($field.length && $label.length) {
                    $field.attr('required', true);
                    $label.addClass('required');
                }
            });
        },

        /**
         * Mejorar la experiencia de usuario del formulario
         */
        _enhanceFormUX: function () {
            // Agregar placeholders útiles
            this.$('input[name="name"]').attr('placeholder', 'Nombre completo');
            this.$('input[name="email"]').attr('placeholder', 'correo@ejemplo.com');
            this.$('input[name="phone"]').attr('placeholder', '+51 999 999 999');
            this.$('input[name="street"]').attr('placeholder', 'Dirección principal');
            this.$('input[name="city"]').attr('placeholder', 'Ciudad');
            
            // Agregar iconos a los campos
            this._addFieldIcons();
            
            // Mejorar el feedback visual
            this._setupFieldFeedback();
        },

        /**
         * Agregar iconos a los campos del formulario
         */
        _addFieldIcons: function () {
            var fieldIcons = {
                'name': 'fa-user',
                'email': 'fa-envelope',
                'phone': 'fa-phone',
                'street': 'fa-map-marker-alt',
                'city': 'fa-city'
            };
            
            var self = this;
            Object.keys(fieldIcons).forEach(function(fieldName) {
                var $field = self.$('input[name="' + fieldName + '"], select[name="' + fieldName + '"]');
                if ($field.length && !$field.siblings('.input-group-prepend').length) {
                    $field.wrap('<div class="input-group"></div>');
                    $field.before(
                        '<div class="input-group-prepend">' +
                        '<span class="input-group-text"><i class="fa ' + fieldIcons[fieldName] + '"></i></span>' +
                        '</div>'
                    );
                }
            });
        },

        /**
         * Configurar feedback visual para los campos
         */
        _setupFieldFeedback: function () {
            this.$('.form-control').on('blur', function() {
                var $this = $(this);
                if ($this.attr('required') && !$this.val().trim()) {
                    $this.addClass('is-invalid');
                } else {
                    $this.removeClass('is-invalid').addClass('is-valid');
                }
            });
        },

        /**
         * Manejar cambio de país
         */
        _onChangeCountry: function (ev) {
            // Lógica personalizada para cambio de país si es necesario
            console.log('País cambiado:', $(ev.currentTarget).val());
        },

        /**
         * Manejar cambio de estado/provincia
         */
        _onChangeState: function (ev) {
            // Lógica personalizada para cambio de estado si es necesario
            console.log('Estado cambiado:', $(ev.currentTarget).val());
        },

        /**
         * Manejar cambio de tipo de factura
         */
        _onChangeInvoiceType: function (ev) {
            var invoiceType = $(ev.currentTarget).val();
            console.log('Tipo de factura cambiado:', invoiceType);
            
            // Aquí puedes agregar lógica específica según el tipo de factura
            if (invoiceType === 'factura') {
                // Mostrar campos adicionales para factura
                this._showFacturaFields();
            } else {
                // Ocultar campos adicionales
                this._hideFacturaFields();
            }
        },

        /**
         * Mostrar campos adicionales para factura
         */
        _showFacturaFields: function () {
            this.$('.factura-fields').show();
            this.$('.factura-fields input').attr('required', true);
        },

        /**
         * Ocultar campos adicionales para factura
         */
        _hideFacturaFields: function () {
            this.$('.factura-fields').hide();
            this.$('.factura-fields input').removeAttr('required');
        },

        /**
         * Manejar envío del formulario
         */
        _onSubmitForm: function (ev) {
            console.log('Formulario enviado');
            // Aquí puedes agregar validaciones adicionales antes del envío
        },

        /**
         * Manejar cambios en los campos de entrada
         */
        _onInputChange: function (ev) {
            var $target = $(ev.currentTarget);
            
            // Remover clases de validación mientras el usuario escribe
            $target.removeClass('is-invalid is-valid');
        },

        /**
         * Manejar cambios en el campo VAT (RUC/DNI)
         */
        _onVatInputChange: function (ev) {
            var $vatInput = $(ev.currentTarget);
            var vatValue = $vatInput.val().replace(/\D/g, ''); // Solo números
            
            // Actualizar el valor del campo
            $vatInput.val(vatValue);
            
            // Detectar automáticamente el tipo de documento
            this._autoDetectDocumentType(vatValue);
        },

        /**
         * Detectar automáticamente el tipo de documento basado en el VAT
         */
        _autoDetectDocumentType: function (vatValue) {
            var $documentTypeSelect = this.$('select[name="l10n_latam_identification_type_id"]');
            
            if (!$documentTypeSelect.length) {
                return;
            }

            var selectedValue = null;
            var selectedText = '';
            
            if (vatValue.length === 8 && /^\d{8}$/.test(vatValue)) {
                // Es un DNI (8 dígitos numéricos)
                selectedValue = this._findOptionByText($documentTypeSelect, ['DNI', 'dni']);
                selectedText = 'DNI';
                console.log('📋 Detectado DNI de 8 dígitos');
            } else if (vatValue.length === 11 && /^\d{11}$/.test(vatValue)) {
                // Es un RUC (11 dígitos numéricos)
                selectedValue = this._findOptionByText($documentTypeSelect, ['RUC', 'ruc']);
                selectedText = 'RUC';
                console.log('📋 Detectado RUC de 11 dígitos');
            } else if (vatValue.length > 0) {
                // Número incompleto o formato no reconocido
                console.log('⚠️ Formato de documento no reconocido:', vatValue);
                return;
            } else {
                // Campo vacío, no hacer nada
                return;
            }

            // Seleccionar automáticamente el tipo de documento si se encontró
            if (selectedValue) {
                $documentTypeSelect.val(selectedValue).trigger('change');
                console.log('✅ Tipo de documento seleccionado automáticamente:', selectedText);
            }
        },

        /**
         * Buscar una opción en un select por texto
         */
        _findOptionByText: function ($select, searchTexts) {
            var foundValue = null;
            
            $select.find('option').each(function() {
                var optionText = $(this).text().trim().toLowerCase();
                
                for (var i = 0; i < searchTexts.length; i++) {
                    if (optionText.includes(searchTexts[i].toLowerCase())) {
                        foundValue = $(this).val();
                        return false; // Salir del each
                    }
                }
            });
            
            return foundValue;
        }
    });

    // Widget para manejar la página de payment
    publicWidget.registry.PaymentCustom = publicWidget.Widget.extend({
        selector: '.oe_website_sale',
        events: {
            'change input[name="pm_id"]': '_onPaymentMethodChange',
            // Asegurar que cualquier enlace a /shop/checkout desde la página de pago
            // incluya el parámetro from_payment=1
            'click a[href*="/shop/checkout"]': '_onEditLinkClick',
        },

        /**
         * Inicialización del widget
         */
        start: function () {
            this._super.apply(this, arguments);
            this._checkTransferPayment();
            this._ensureEditLinksParam();
        },

        /**
         * Fuerza que los enlaces de "Editar" en la sección de dirección del pago
         * apunten a /shop/checkout?from_payment=1
         */
        _ensureEditLinksParam: function () {
            var self = this;
            this.$('a[href*="/shop/checkout"]').each(function () {
                var $a = $(this);
                try {
                    var url = new URL($a.attr('href'), window.location.origin);
                    // Establecer o reemplazar el parámetro
                    url.searchParams.set('from_payment', '1');
                    $a.attr('href', url.toString());
                } catch (e) {
                    // Fallback simple por si el href es relativo o no válido para URL()
                    var href = $a.attr('href') || '';
                    if (href.indexOf('from_payment=1') === -1) {
                        if (href.indexOf('?') === -1) {
                            href += '?from_payment=1';
                        } else {
                            href += '&from_payment=1';
                        }
                        $a.attr('href', href);
                    }
                }
            });
        },

        /**
         * Interceptar click al enlace de editar para garantizar el parámetro
         */
        _onEditLinkClick: function (ev) {
            try {
                var href = ev.currentTarget.getAttribute('href') || '';
                if (href.indexOf('/shop/checkout') !== -1) {
                    ev.preventDefault();
                    var url = new URL(href, window.location.origin);
                    url.searchParams.set('from_payment', '1');
                    window.location.href = url.toString();
                }
            } catch (e) {
                // Ante cualquier error, redirigir de forma segura
                ev.preventDefault();
                window.location.href = '/shop/checkout?from_payment=1';
            }
        },

        /**
         * Verificar si está seleccionada la transferencia bancaria al cargar
         */
        _checkTransferPayment: function () {
            var $transferOption = this.$('input[name="pm_id"][data-provider="transfer"]:checked');
            if ($transferOption.length) {
                this._showTransferMessage($transferOption);
            }
        },

        /**
         * Manejar cambio de método de pago
         */
        _onPaymentMethodChange: function (ev) {
            var $target = $(ev.currentTarget);
            
            // Remover mensajes existentes
            this.$('.transfer-info-message').remove();
            
            // Si es transferencia bancaria, mostrar mensaje
            if ($target.data('provider') === 'transfer') {
                this._showTransferMessage($target);
            }
        },

        /**
         * Mostrar mensaje informativo para transferencia bancaria
         */
        _showTransferMessage: function ($transferInput) {
            var $cardBody = $transferInput.closest('.card-body');
            
            // Verificar si ya existe el mensaje
            if ($cardBody.find('.transfer-info-message').length === 0) {
                var messageHtml = '<div class="transfer-info-message alert alert-info mt-3 mb-0">' +
                    '<i class="fa fa-info-circle mr-2"></i>' +
                    '<strong>Información:</strong> Los datos de nuestras cuentas bancarias se mostrarán al hacer clic en "Pagar ahora".' +
                    '</div>';
                
                $cardBody.append(messageHtml);
            }
        }
    });

});