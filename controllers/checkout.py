# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.exceptions import ValidationError
import logging


class WebsiteSaleCheckout(WebsiteSale):
    """
    Controlador personalizado para el checkout con campos DNI/RUC
    """
    _logger = logging.getLogger(__name__)

    def _detect_identification_type(self, vat_number):
        """
        Detectar automáticamente el tipo de identificación basándose en el número
        usando el sistema nativo de l10n_latam_base
        """
        if not vat_number:
            return False
        
        vat_clean = str(vat_number).strip()
        _logger = logging.getLogger(__name__)
        _logger.info(f"=== DETECTANDO TIPO DE IDENTIFICACIÓN PARA: {vat_clean} ===")
        
        # Buscar tipos de identificación disponibles
        identification_types = request.env['l10n_latam.identification.type'].sudo().search([
            ('active', '=', True)
        ])
        
        _logger.info(f"Tipos de identificación disponibles: {identification_types.mapped('name')}")
        
        # Detectar DNI (8 dígitos)
        if len(vat_clean) == 8 and vat_clean.isdigit():
            dni_type = identification_types.filtered(lambda x: 'dni' in x.name.lower())
            if dni_type:
                _logger.info(f"DNI detectado: {vat_clean} -> {dni_type[0].name}")
                return dni_type[0]
        
        # Detectar RUC (11 dígitos)
        elif len(vat_clean) == 11 and vat_clean.isdigit():
            ruc_type = identification_types.filtered(lambda x: 'ruc' in x.name.lower())
            if ruc_type:
                _logger.info(f"RUC detectado: {vat_clean} -> {ruc_type[0].name}")
                return ruc_type[0]
        
        # Detectar VAT con prefijos peruanos (10 dígitos)
        elif len(vat_clean) == 10 and vat_clean.startswith(('10', '20', '15', '16', '17')):
            ruc_type = identification_types.filtered(lambda x: 'ruc' in x.name.lower())
            if ruc_type:
                _logger.info(f"RUC con prefijo detectado: {vat_clean} -> {ruc_type[0].name}")
                return ruc_type[0]
        
        # Detectar DNI con prefijo 10 (10 dígitos)
        elif len(vat_clean) == 10 and vat_clean.startswith('10'):
            dni_type = identification_types.filtered(lambda x: 'dni' in x.name.lower())
            if dni_type:
                _logger.info(f"DNI con prefijo 10 detectado: {vat_clean} -> {dni_type[0].name}")
                return dni_type[0]
        
        # Buscar tipo de identificación fiscal por defecto
        default_type = identification_types.filtered(lambda x: x.is_vat)
        if default_type:
            _logger.info(f"Usando tipo de identificación fiscal por defecto: {default_type[0].name}")
            return default_type[0]
        
        _logger.info("No se pudo determinar el tipo de identificación")
        return False

    @http.route(['/shop/address'], type='http', auth="public", website=True, sitemap=False)
    def address(self, **kw):
        """
        Sobrescribimos para manejar los campos personalizados DNI, RUC y tipo de comprobante
        """
        _logger = logging.getLogger(__name__)
        _logger.info("=== ADDRESS ROUTE ===")
        _logger.info(f"KW recibidos: {kw}")
        
        # Obtener todos los valores del formulario
        all_form_values = request.httprequest.form.to_dict()
        _logger.info(f"Todos los valores del formulario: {all_form_values}")
        
        # Obtener valores específicos
        dni = all_form_values.get('dni', '').strip()
        ruc = all_form_values.get('ruc', '').strip()
        razon_social = all_form_values.get('razon_social', '').strip()
        invoice_type_checkbox = all_form_values.get('invoice_type_checkbox', '')
        invoice_type_hidden = all_form_values.get('invoice_type', 'boleta')
        
        _logger.info(f"DNI extraído: '{dni}'")
        _logger.info(f"RUC extraído: '{ruc}'")
        _logger.info(f"Razón Social extraída: '{razon_social}'")
        _logger.info(f"Checkbox factura: '{invoice_type_checkbox}'")
        _logger.info(f"Tipo oculto: '{invoice_type_hidden}'")
        
        # Determinar si se solicita factura
        is_invoice_requested = invoice_type_checkbox == '1'
        
        if is_invoice_requested:
            _logger.info("=== MODO FACTURA ===")
            if not ruc:
                _logger.warning("Se solicita factura pero no hay RUC")
                # Aquí podrías mostrar un error al usuario
            if not razon_social:
                _logger.warning("Se solicita factura pero no hay razón social")
                # Aquí podrías mostrar un error al usuario
        else:
            _logger.info("=== MODO BOLETA ===")
            if not dni:
                _logger.warning("Se solicita boleta pero no hay DNI")
                # Aquí podrías mostrar un error al usuario
        
        # Llamar al método original
        return super().address(**kw)

    def _checkout_form_save(self, mode, checkout, all_values):
        """
        Guardar el formulario de checkout con detección automática del tipo de identificación
        """
        _logger = logging.getLogger(__name__)
        _logger.info("=== CHECKOUT FORM SAVE ===")
        _logger.info(f"Mode: {mode}")
        _logger.info(f"Checkout: {checkout}")
        _logger.info(f"All values: {all_values}")
        
        # Obtener valores del formulario
        dni = all_values.get('dni', '').strip()
        ruc = all_values.get('ruc', '').strip()
        razon_social = all_values.get('razon_social', '').strip()
        is_invoice_requested = all_values.get('invoice_type_checkbox') == '1'
        invoice_type = all_values.get('invoice_type', 'boleta')
        
        _logger.info(f"DNI: {dni}")
        _logger.info(f"RUC: {ruc}")
        _logger.info(f"Razón Social: {razon_social}")
        _logger.info(f"¿Solicita factura?: {is_invoice_requested}")
        _logger.info(f"Tipo de comprobante: {invoice_type}")
        
        # Determinar qué número usar y detectar tipo automáticamente
        if is_invoice_requested and ruc:
            # Modo factura: usar RUC
            checkout['vat'] = ruc
            identification_type = self._detect_identification_type(ruc)
            if identification_type:
                checkout['l10n_latam_identification_type_id'] = identification_type.id
            _logger.info(f"Modo factura: RUC {ruc} detectado como {identification_type.name if identification_type else 'No detectado'}")
            
            # Si es empresa, usar razón social
            if razon_social:
                checkout['name'] = razon_social
                checkout['is_company'] = True
                _logger.info(f"Empresa: {razon_social}")
        else:
            # Modo boleta: usar DNI
            checkout['vat'] = dni
            identification_type = self._detect_identification_type(dni)
            if identification_type:
                checkout['l10n_latam_identification_type_id'] = identification_type.id
            _logger.info(f"Modo boleta: DNI {dni} detectado como {identification_type.name if identification_type else 'No detectado'}")
            
            # Si no es empresa, usar nombre personal
            checkout['is_company'] = False
        
        # Agregar el tipo de comprobante
        checkout['invoice_type'] = invoice_type
        
        # Filtrar solo campos válidos de res.partner
        valid_fields = ['name', 'email', 'phone', 'street', 'city', 'country_id', 'vat', 'l10n_latam_identification_type_id', 'is_company', 'invoice_type']
        filtered_checkout = {k: v for k, v in checkout.items() if k in valid_fields}
        
        _logger.info(f"Checkout filtrado: {filtered_checkout}")
        
        # Crear o actualizar el partner
        Partner = request.env['res.partner'].sudo()
        
        if mode[0] == 'edit':
            partner_id = int(mode[1])
            partner = Partner.browse(partner_id)
            partner.write(filtered_checkout)
            _logger.info(f"Partner actualizado: {partner_id}")
        else:
            partner_id = Partner.create(filtered_checkout).id
            _logger.info(f"Partner creado: {partner_id}")
        
        return partner_id

    def values_preprocess(self, order, mode, kw):
        """
        Preprocesar valores antes de guardar
        """
        _logger = logging.getLogger(__name__)
        _logger.info("=== VALUES PREPROCESS ===")
        _logger.info(f"Order: {order}")
        _logger.info(f"Mode: {mode}")
        _logger.info(f"KW: {kw}")
        
        # Obtener valores del formulario
        dni = kw.get('dni', '').strip()
        ruc = kw.get('ruc', '').strip()
        is_invoice_requested = kw.get('invoice_type_checkbox') == '1'
        
        # Crear diccionario de nuevos valores
        new_values = {}
        
        # Determinar qué número usar y detectar tipo automáticamente
        if is_invoice_requested and ruc:
            # Modo factura: usar RUC
            new_values['vat'] = ruc
            identification_type = self._detect_identification_type(ruc)
            if identification_type:
                new_values['l10n_latam_identification_type_id'] = identification_type.id
            _logger.info(f"Modo factura: RUC {ruc} detectado como {identification_type.name if identification_type else 'No detectado'}")
        else:
            # Modo boleta: usar DNI
            new_values['vat'] = dni
            identification_type = self._detect_identification_type(dni)
            if identification_type:
                new_values['l10n_latam_identification_type_id'] = identification_type.id
            _logger.info(f"Modo boleta: DNI {dni} detectado como {identification_type.name if identification_type else 'No detectado'}")
        
        _logger.info(f"Nuevos valores: {new_values}")
        return new_values

    def checkout_form_validate(self, mode, all_form_values, data_values):
        shipping_option = all_form_values.get('shipping_option')
        if shipping_option == 'pickup':
            # Solo valida lo necesario para pickup, ignora dirección
            error = {}
            error_message = []
            # Validaciones personalizadas (DNI, RUC, razón social)
            invoice_type_checkbox = all_form_values.get('invoice_type_checkbox')
            dni = all_form_values.get('dni', '').strip()
            ruc = all_form_values.get('ruc', '').strip()
            razon_social = all_form_values.get('razon_social', '').strip()
            is_invoice_requested = invoice_type_checkbox == '1'

            if is_invoice_requested:
                if not ruc:
                    error['ruc'] = 'missing'
                    error_message.append('RUC es requerido para factura')
                elif len(ruc) != 11 or not ruc.isdigit():
                    error['ruc'] = 'invalid'
                    error_message.append('RUC debe tener exactamente 11 dígitos')
                if not razon_social:
                    error['razon_social'] = 'missing'
                    error_message.append('Razón Social es requerida para factura')
            else:
                if dni:
                    if len(dni) != 8 or not dni.isdigit():
                        error['dni'] = 'invalid'
                        error_message.append('DNI debe tener exactamente 8 dígitos')
            return error, error_message
        # Si no es pickup, sigue el flujo normal
        return super(WebsiteSaleCheckout, self).checkout_form_validate(mode, all_form_values, data_values)