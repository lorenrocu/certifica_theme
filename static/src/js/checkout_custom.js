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
         * Manejar cambio del checkbox de tipo de comprobante
         */
        _onChangeInvoiceType: function (ev) {
            console.log('📋 CAMBIO EN CHECKBOX DE FACTURA');
            var $checkbox = $(ev.currentTarget);
            var isChecked = $checkbox.is(':checked');
            var $container = $checkbox.closest('#div_invoice_type');
            var $invoiceFields = $('#invoice_fields');
            var $razonSocial = $('#razon_social');
            var $ruc = $('#ruc');
            var $hiddenInput = this.$('#invoice_type_hidden');
            
            console.log('Checkbox marcado:', isChecked);
            console.log('Campos de factura encontrados:', $invoiceFields.length);
            console.log('Campo RUC encontrado:', $ruc.length);
            console.log('Campo Razón Social encontrado:', $razonSocial.length);
            
            // Feedback visual del checkbox
            if (isChecked) {
                console.log('✅ Activando modo FACTURA');
                $container.addClass('invoice-selected');
                console.log('Factura solicitada');
            } else {
                console.log('✅ Activando modo BOLETA');
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
                $hiddenInput.val('factura');
                
                console.log('Campos RUC y Razón Social marcados como requeridos');
                
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
                $hiddenInput.val('boleta');
                
                console.log('Campos RUC y Razón Social NO requeridos');
                
                // Limpiar valores
                $razonSocial.val('');
                $ruc.val('');
                
                // Ocultar después de la animación
                setTimeout(function() {
                    $invoiceFields.hide();
                }, 400);
            }
            
            console.log('Valor del input oculto:', $hiddenInput.val());
            
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
            console.log('🚀 EVENTO ENVÍO FORMULARIO INICIADO');
            console.log('Evento:', ev.type, 'Target:', ev.target.tagName);
            
            // Asegurar que los campos eliminados no bloqueen el envío
            this.$('input[name="street2"], input[name="zip"]').removeAttr('required');
            
            // Obtener el estado del checkbox de factura
            var isInvoiceChecked = this.$('input[name="invoice_type"]').is(':checked');
            var $dniField = this.$('#dni');
            
            // Si no está marcada la factura, asegurarse de que el DNI no bloquee el envío
            if (!isInvoiceChecked) {
                $dniField.removeAttr('required');
                $dniField.removeClass('is-invalid');
            }
            
            var isFormValid = this._validateForm();
            console.log('Resultado validación:', isFormValid);
            
            if (!isFormValid) {
                console.log('❌ FORMULARIO INVÁLIDO - Previniendo envío');
                ev.preventDefault();
                ev.stopPropagation();
                this._showValidationErrors();
                return false;
            } else {
                console.log('✅ FORMULARIO VÁLIDO - Permitiendo envío');
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
            if ($input.attr('id') === 'dni') {
                this.$('.dni-error-message').remove();
            }
            if ($input.attr('id') === 'razon_social') {
                this.$('.razon-social-error-message').remove();
            }
            
            // Remover mensaje de error general si existe
            this.$('.checkout-error-message').remove();
        },

        /**
         * Validar el formulario
         */
        _validateForm: function () {
            var self = this;
            var isValid = true;
            var isInvoiceChecked = this.$('input[name="invoice_type"]').is(':checked');
            
            // Validar campos requeridos básicos
            this.$('input[required], select[required]').each(function() {
                var $field = $(this);
                // Ignorar el DNI si no está marcada la factura
                if ($field.attr('id') === 'dni' && !isInvoiceChecked) {
                    return true;
                }
                
                if (!$field.val().trim()) {
                    $field.addClass('is-invalid');
                    isValid = false;
                } else {
                    $field.removeClass('is-invalid');
                }
            });
            
            // Validar campos de factura solo si está marcada la opción
            if (isInvoiceChecked) {
                var $ruc = this.$('#ruc');
                var $razonSocial = this.$('#razon_social');
                
                if (!$ruc.val().trim()) {
                    $ruc.addClass('is-invalid');
                    isValid = false;
                }
                
                if (!$razonSocial.val().trim()) {
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
        },

        /**
         * Manejar cambios en el campo VAT para autoselección de tipo de documento
         */
        _onVatInputChange: function (ev) {
            var self = this;
            var $vatInput = $(ev.currentTarget);
            var vatValue = $vatInput.val().trim();
            
            // Usar setTimeout para manejar el evento paste correctamente
            setTimeout(function() {
                vatValue = $vatInput.val().trim();
                self._autoSelectDocumentType(vatValue);
            }, 10);
        },

        /**
         * Autoseleccionar el tipo de documento basado en el número ingresado
         */
        _autoSelectDocumentType: function (vatValue) {
            console.log('🔍 Autoselección de tipo de documento para:', vatValue);
            
            // Buscar el selector de tipo de documento
            var $documentTypeSelect = this.$('select[name="l10n_latam_identification_type_id"]');
            
            // Si no existe el selector estándar, buscar alternativas
            if (!$documentTypeSelect.length) {
                $documentTypeSelect = this.$('select[name="vat_type"]');
            }
            if (!$documentTypeSelect.length) {
                $documentTypeSelect = this.$('select[name="document_type"]');
            }
            if (!$documentTypeSelect.length) {
                $documentTypeSelect = this.$('select').filter(function() {
                    return $(this).find('option').text().toLowerCase().includes('dni') || 
                           $(this).find('option').text().toLowerCase().includes('ruc');
                });
            }
            
            if (!$documentTypeSelect.length) {
                console.log('⚠️ No se encontró selector de tipo de documento');
                return;
            }
            
            console.log('✅ Selector de tipo de documento encontrado:', $documentTypeSelect.attr('name'));
            
            // Lógica de autoselección basada en la longitud del número
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
            
            // Aplicar la selección si se encontró una opción válida
            if (selectedValue) {
                $documentTypeSelect.val(selectedValue).trigger('change');
                console.log('✅ Tipo de documento autoseleccionado:', selectedText, 'con valor:', selectedValue);
                
                // Mostrar feedback visual temporal
                this._showDocumentTypeNotification(selectedText);
            } else {
                console.log('❌ No se encontró opción para:', selectedText);
            }
        },

        /**
         * Buscar opción en el select por texto
         */
        _findOptionByText: function ($select, textOptions) {
            var foundValue = null;
            
            $select.find('option').each(function() {
                var optionText = $(this).text().trim();
                var optionValue = $(this).val();
                
                for (var i = 0; i < textOptions.length; i++) {
                    if (optionText.toLowerCase().includes(textOptions[i].toLowerCase()) ||
                        optionValue.toLowerCase().includes(textOptions[i].toLowerCase())) {
                        foundValue = optionValue;
                        return false; // Salir del each
                    }
                }
            });
            
            return foundValue;
        },

        /**
         * Mostrar notificación temporal de autoselección
         */
        _showDocumentTypeNotification: function (documentType) {
            var $notification = $('<div class="alert alert-info document-type-notification" style="position: fixed; top: 20px; right: 20px; z-index: 9999; min-width: 300px;">' +
                '<i class="fa fa-check-circle mr-2"></i>' +
                'Tipo de documento autoseleccionado: <strong>' + documentType + '</strong>' +
                '</div>');
            
            $('body').append($notification);
            
            // Remover la notificación después de 3 segundos
            setTimeout(function() {
                $notification.fadeOut(500, function() {
                    $(this).remove();
                });
            }, 3000);
        }
    });

    return publicWidget.registry.CheckoutCustom;
});