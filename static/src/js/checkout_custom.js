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
         * Configurar validación personalizada del formulario
         */
        _setupFormValidation: function () {
            var self = this;
            
            // Campos requeridos personalizados
            var requiredFields = [
                'name',
                'email', 
                'phone',
                'street',
                'city',
                'country_id'
            ];
            
            // Agregar indicadores visuales para campos requeridos
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
                'city': 'fa-city',
                'country_id': 'fa-globe'
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
         * Manejar cambio del checkbox de tipo de comprobante
         */
        _onChangeInvoiceType: function (ev) {
            var $checkbox = $(ev.currentTarget);
            var isChecked = $checkbox.is(':checked');
            var $container = $checkbox.closest('#div_invoice_type');
            var $invoiceFields = $('#invoice_fields');
            var $razonSocial = $('#razon_social');
            var $ruc = $('#ruc');
            
            // Feedback visual del checkbox
            if (isChecked) {
                $container.addClass('invoice-selected');
                console.log('Factura solicitada');
            } else {
                $container.removeClass('invoice-selected');
                console.log('Boleta solicitada');
            }
            
            // Mostrar/ocultar campos de facturación
            if (isChecked) {
                // Mostrar campos con animación
                $invoiceFields.removeClass('hide').addClass('show').show();
                
                // Hacer campos requeridos
                $razonSocial.attr('required', 'required');
                $ruc.attr('required', 'required');
                
                // Enfocar el primer campo
                setTimeout(function() {
                    $razonSocial.focus();
                }, 400);
                
            } else {
                // Ocultar campos con animación
                $invoiceFields.removeClass('show').addClass('hide');
                
                // Remover validaciones requeridas
                $razonSocial.removeAttr('required').removeClass('is-invalid');
                $ruc.removeAttr('required').removeClass('is-invalid');
                
                // Limpiar valores
                $razonSocial.val('');
                $ruc.val('');
                
                // Ocultar después de la animación
                setTimeout(function() {
                    $invoiceFields.hide();
                }, 400);
            }
            
            // Agregar clase CSS para animación del checkbox
            $container.addClass('checkbox-changed');
            setTimeout(function() {
                $container.removeClass('checkbox-changed');
            }, 300);
        },

        /**
         * Manejar envío del formulario
         */
        _onSubmitForm: function (ev) {
            // Asegurar que los campos eliminados no bloqueen el envío
            this.$('input[name="street2"], input[name="zip"]').removeAttr('required');
            
            // Validación personalizada
            if (!this._validateForm()) {
                ev.preventDefault();
                this._showValidationErrors();
                return false;
            }
        },

        /**
         * Manejar cambios en los inputs
         */
        _onInputChange: function (ev) {
            var $input = $(ev.currentTarget);
            if ($input.hasClass('is-invalid')) {
                $input.removeClass('is-invalid');
            }
            
            // Limpiar mensajes de error específicos
            if ($input.attr('id') === 'ruc') {
                this.$('.ruc-error-message').remove();
            }
            
            // Remover mensaje de error general si existe
            this.$('.checkout-error-message').remove();
        },

        /**
         * Validar el formulario
         */
        _validateForm: function () {
            var isValid = true;
            var self = this;
            
            // Validar campos requeridos
            this.$('input[required], select[required]').each(function() {
                var $field = $(this);
                if (!$field.val() || !$field.val().trim()) {
                    $field.addClass('is-invalid');
                    isValid = false;
                }
            });
            
            // Validar email
            var $email = this.$('input[name="email"]');
            if ($email.length && $email.val()) {
                var emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                if (!emailRegex.test($email.val())) {
                    $email.addClass('is-invalid');
                    isValid = false;
                }
            }
            
            // Validar RUC si está visible y requerido
            var $ruc = this.$('#ruc');
            if ($ruc.length && $ruc.is(':visible') && $ruc.attr('required')) {
                var rucValue = $ruc.val().trim();
                var rucRegex = /^[0-9]{11}$/;
                
                if (!rucValue) {
                    $ruc.addClass('is-invalid');
                    isValid = false;
                } else if (!rucRegex.test(rucValue)) {
                    $ruc.addClass('is-invalid');
                    isValid = false;
                    // Mostrar mensaje específico para RUC
                    if (!this.$('.ruc-error-message').length) {
                        $ruc.after('<div class="invalid-feedback ruc-error-message">El RUC debe tener exactamente 11 dígitos</div>');
                    }
                }
            }
            
            // Validar Razón Social si está visible y requerida
            var $razonSocial = this.$('#razon_social');
            if ($razonSocial.length && $razonSocial.is(':visible') && $razonSocial.attr('required')) {
                var razonValue = $razonSocial.val().trim();
                if (!razonValue || razonValue.length < 3) {
                    $razonSocial.addClass('is-invalid');
                    isValid = false;
                }
            }
            
            return isValid;
        },

        /**
         * Mostrar errores de validación
         */
        _showValidationErrors: function () {
            var $firstInvalid = this.$('.is-invalid').first();
            if ($firstInvalid.length) {
                $firstInvalid.focus();
                
                // Mostrar mensaje de error
                if (!this.$('.checkout-error-message').length) {
                    this.$el.prepend(
                        '<div class="alert alert-danger checkout-error-message">' +
                        '<i class="fa fa-exclamation-triangle mr-2"></i>' +
                        'Por favor, complete todos los campos requeridos correctamente.' +
                        '</div>'
                    );
                }
                
                // Scroll al mensaje de error
                $('html, body').animate({
                    scrollTop: this.$('.checkout-error-message').offset().top - 100
                }, 500);
            }
        }
    });

    return publicWidget.registry.CheckoutCustom;
});