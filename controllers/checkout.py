# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.exceptions import ValidationError


class WebsiteSaleCheckout(WebsiteSale):
    """
    Controlador personalizado para el checkout con campos DNI/RUC
    """

    @http.route(['/shop/address'], type='http', auth="public", website=True, sitemap=False)
    def address(self, **kw):
        """
        Sobrescribimos el método address para manejar DNI, RUC y tipo de comprobante
        """
        Partner = request.env['res.partner'].with_context(show_address=1).sudo()
        order = request.website.sale_get_order()

        redirection = self.checkout_redirection(order)
        if redirection:
            return redirection

        mode = (False, False)
        can_edit_vat = False
        values, errors = {}, {}

        partner_id = int(kw.get('partner_id', -1))

        # IF PUBLIC ORDER
        if order.partner_id.id == request.website.partner_id.id:
            mode = ('new', 'billing')
            can_edit_vat = True
        # IF ORDER LINKED TO A PARTNER
        else:
            if partner_id > 0:
                if partner_id == order.partner_id.id:
                    mode = ('edit', 'billing')
                else:
                    shippings = Partner.search([('id', 'child_of', order.partner_id.commercial_partner_id.ids)])
                    if partner_id in shippings.mapped('id'):
                        mode = ('edit', 'shipping')
                    else:
                        return Forbidden()
                if mode and partner_id != -1:
                    values = Partner.browse(partner_id)
            else:
                mode = ('new', 'shipping')
            can_edit_vat = order.partner_id.can_edit_vat()

        # IF POSTED
        if 'submitted' in kw:
            pre_values = self.values_preprocess(order, mode, kw)
            errors, error_msg = self.checkout_form_validate(mode, kw, pre_values)
            post, errors, error_msg = self.values_postprocess(order, mode, pre_values, errors, error_msg)

            if errors:
                errors['error_message'] = error_msg
                values = kw
            else:
                partner_id = self._checkout_form_save(mode, post, kw)
                
                # Asegurar que el partner creado no sea el partner público
                if partner_id == request.website.partner_id.id:
                    # Forzar la creación de un nuevo partner único
                    import time
                    unique_data = post.copy()
                    unique_data['email'] = f"forced_unique_{int(time.time())}@temp.local"
                    partner_id = request.env['res.partner'].sudo().create(unique_data).id
                
                if mode[1] == 'billing':
                    order.partner_id = partner_id
                    order.with_context(not_self_saleperson=True).onchange_partner_id()
                    order.partner_invoice_id = partner_id
                elif mode[1] == 'shipping':
                    order.partner_shipping_id = partner_id

                # TDE FIXME: don't ever do this
                order.message_partner_ids = [(4, partner_id), (3, request.website.partner_id.id)]
                
                # Verificación final antes de continuar
                if order.partner_id.id == request.website.partner_id.id:
                    # Si aún es el partner público, forzar cambio
                    order.partner_id = partner_id
                    order.partner_invoice_id = partner_id
                
                if not errors:
                    return request.redirect(kw.get('callback') or '/shop/payment')

        country = request.env['res.country']
        if kw.get('country_id'):
            country = country.browse(int(kw.get('country_id')))
        render_values = {
            'website_sale_order': order,
            'partner_id': partner_id,
            'mode': mode,
            'checkout': values,
            'can_edit_vat': can_edit_vat,
            'country': country,
            'countries': country.search([]),
            'states': country.state_ids,
            'error': errors,
            'callback': kw.get('callback'),
            'only_services': order and order.only_services or False
        }
        return request.render("website_sale.address", render_values)

    def _checkout_form_save(self, mode, checkout, all_values):
        """
        Sobrescribimos para manejar los campos personalizados DNI, RUC y tipo de comprobante
        """
        import logging
        _logger = logging.getLogger(__name__)
        
        _logger.info("=== CHECKOUT DEBUG - _checkout_form_save ===")
        _logger.info(f"Mode: {mode}")
        _logger.info(f"Datos a guardar (checkout): {checkout}")
        
        Partner = request.env['res.partner']
        if mode[0] == 'new':
            # Asegurar que el partner no sea el partner público del website
            # Generar un email único si no se proporciona
            if not checkout.get('email'):
                import time
                checkout['email'] = f"customer_{int(time.time())}@temp.local"
            
            # Asegurar que el partner tenga un nombre válido
            if not checkout.get('name'):
                checkout['name'] = 'Cliente'
            
            # Crear el partner
            partner_id = Partner.sudo().create(checkout).id
            
            # Log de verificación del partner creado
            created_partner = Partner.sudo().browse(partner_id)
            _logger.info(f"Partner creado con ID: {partner_id}")
            _logger.info(f"Documento guardado: {created_partner.vat_document_number}")
            _logger.info(f"Tipo documento guardado: {created_partner.vat_document_type_id.name if created_partner.vat_document_type_id else 'Sin tipo'}")
            _logger.info(f"Nombre guardado: {created_partner.name}")
            _logger.info(f"Email guardado: {created_partner.email}")
            
            # Verificar que no sea el partner público
            if partner_id == request.website.partner_id.id:
                # Si por alguna razón es el mismo, crear uno nuevo con datos únicos
                checkout['email'] = f"unique_{partner_id}_{int(time.time())}@temp.local"
                partner_id = Partner.sudo().create(checkout).id
                
        elif mode[0] == 'edit':
            partner_id = int(all_values.get('partner_id', 0))
            if partner_id:
                # double check
                order = request.website.sale_get_order()
                shippings = Partner.sudo().search([('id', 'child_of', order.partner_id.commercial_partner_id.ids)])
                if partner_id not in shippings.mapped('id') and partner_id != order.partner_id.id:
                    return Forbidden()
                Partner.sudo().browse(partner_id).write(checkout)
        return partner_id

    def values_preprocess(self, order, mode, values):
        """
        Preprocesamos los valores del formulario incluyendo DNI, RUC y tipo de comprobante
        """
        import logging
        _logger = logging.getLogger(__name__)
        
        # Log de depuración: datos recibidos del formulario
        _logger.info("=== CHECKOUT DEBUG - values_preprocess ===")
        _logger.info(f"Datos recibidos del formulario: {values}")
        _logger.info(f"Mode: {mode}")
        
        new_values = super(WebsiteSaleCheckout, self).values_preprocess(order, mode, values)
        
        # Verificar si se solicita factura
        is_invoice_requested = values.get('invoice_type_checkbox') == 'on' or values.get('invoice_type') == 'factura'
        _logger.info(f"¿Se solicita factura? {is_invoice_requested}")
        _logger.info(f"invoice_type_checkbox: {values.get('invoice_type_checkbox')}")
        _logger.info(f"invoice_type: {values.get('invoice_type')}")
        
        # Mapear el tipo de comprobante al campo correcto del modelo
        if is_invoice_requested:
            new_values['l10n_latam_identification_type_id'] = 2  # Factura
        else:
            new_values['l10n_latam_identification_type_id'] = 1  # Boleta
        _logger.info(f"Tipo de comprobante asignado: {'factura' if is_invoice_requested else 'boleta'}")
        
        # Agregar campos personalizados - mapear al modelo correcto
        _logger.info(f"Procesando campos personalizados...")
        _logger.info(f"DNI en values: {values.get('dni')}")
        
        if 'dni' in values and values['dni']:
            new_values['vat_document_number'] = values['dni'].strip()
            # Establecer tipo de documento como DNI (ID 1 típicamente)
            new_values['vat_document_type_id'] = 1
            _logger.info(f"DNI procesado: {new_values['vat_document_number']}")
        else:
            _logger.info("DNI no encontrado o vacío")
            
        # Solo incluir campos de factura si se solicita factura
        if is_invoice_requested:
            _logger.info("Procesando campos de factura...")
            if 'ruc' in values and values['ruc']:
                new_values['vat_document_number'] = values['ruc'].strip()
                # Establecer tipo de documento como RUC (ID 2 típicamente)
                new_values['vat_document_type_id'] = 2
                _logger.info(f"RUC procesado: {new_values['vat_document_number']}")
            if 'razon_social' in values and values['razon_social']:
                new_values['name'] = values['razon_social'].strip()  # Mapear razón social al nombre
                _logger.info(f"Razón social procesada: {new_values['name']}")
        else:
            _logger.info("Campos de RUC no requeridos para boleta")
            
        _logger.info(f"Valores finales procesados: {new_values}")
        _logger.info("=== FIN CHECKOUT DEBUG - values_preprocess ===")
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
            is_invoice_requested = invoice_type_checkbox == 'on'

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