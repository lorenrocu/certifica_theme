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
        _logger.info(f"Datos a guardar (checkout) ANTES de merge: {checkout}")
        
        # --- Asegurar que los campos personalizados lleguen a create()/write() ---
        # Algunos flujos de website_sale filtran llaves desconocidas en values_postprocess,
        # por lo que integramos directamente desde all_values antes de persistir.
        try:
            dni = (all_values.get('dni') or '').strip()
            ruc = (all_values.get('ruc') or '').strip()
            razon_social = (all_values.get('razon_social') or '').strip()
            is_invoice_requested = all_values.get('invoice_type_checkbox') == 'on' or all_values.get('invoice_type') == 'factura'

            # Establecer tipo de comprobante - TEMPORALMENTE COMENTADO PARA EVITAR ERROR
            # checkout['invoice_type'] = 'factura' if is_invoice_requested else 'boleta'

            # Inyectar documentos si vienen del formulario
            if ruc:
                checkout['ruc'] = ruc
            if dni and 'ruc' not in checkout:
                # Solo setear DNI si no hay RUC (prioridad RUC)
                checkout['dni'] = dni

            # Mapear razón social al name cuando es factura
            if is_invoice_requested and razon_social:
                checkout['name'] = razon_social

            # Calcular VAT explícitamente (prioridad RUC > DNI)
            if checkout.get('ruc'):
                checkout['vat'] = checkout['ruc']
            elif checkout.get('dni'):
                checkout['vat'] = checkout['dni']

            _logger.info(f"Datos a guardar (checkout) DESPUÉS de merge: {checkout}")
        except Exception as e:
            _logger.warning(f"No se pudo consolidar campos personalizados en checkout: {e}")
        
        Partner = request.env['res.partner']
        if mode[0] == 'new':
            try:
                # Asegurar que el partner no sea el partner público del website
                # Generar un email único si no se proporciona
                if not checkout.get('email'):
                    import time
                    checkout['email'] = f"customer_{int(time.time())}@temp.local"
                
                # Asegurar que el partner tenga un nombre válido
                if not checkout.get('name'):
                    checkout['name'] = 'Cliente'
                
                # Crear el partner con manejo de errores
                partner_id = Partner.sudo().create(checkout).id
                _logger.info(f"Partner creado exitosamente con ID: {partner_id}")
                
            except Exception as e:
                _logger.error(f"Error al crear partner: {e}")
                _logger.error(f"Datos del checkout: {checkout}")
                # Re-lanzar la excepción para que el flujo normal de errores la maneje
                raise
            
            # Log de verificación del partner creado con acceso seguro a campos
            try:
                created_partner = Partner.sudo().browse(partner_id)
                _logger.info(f"Partner creado con ID: {partner_id}")
                _logger.info(f"DNI guardado: {getattr(created_partner, 'dni', None) or 'No especificado'}")
                _logger.info(f"RUC guardado: {getattr(created_partner, 'ruc', None) or 'No especificado'}")
                _logger.info(f"VAT guardado: {getattr(created_partner, 'vat', None) or 'No especificado'}")
                _logger.info(f"Tipo de comprobante: {getattr(created_partner, 'invoice_type', None) or 'No especificado'}")
                _logger.info(f"Nombre guardado: {getattr(created_partner, 'name', None) or 'No especificado'}")
                _logger.info(f"Email guardado: {getattr(created_partner, 'email', None) or 'No especificado'}")
            except Exception as e:
                _logger.error(f"Error al acceder a campos del partner creado: {e}")
                _logger.info(f"Partner creado con ID: {partner_id} (información detallada no disponible)")
            
            # Verificar que no sea el partner público
            if partner_id == request.website.partner_id.id:
                try:
                    # Si por alguna razón es el mismo, crear uno nuevo con datos únicos
                    checkout['email'] = f"unique_{partner_id}_{int(time.time())}@temp.local"
                    partner_id = Partner.sudo().create(checkout).id
                    _logger.info(f"Partner único creado para evitar conflicto con partner público. Nuevo ID: {partner_id}")
                except Exception as e:
                    _logger.error(f"Error al crear partner único: {e}")
                    raise
                
        elif mode[0] == 'edit':
            try:
                partner_id = int(all_values.get('partner_id', 0))
                if partner_id:
                    # double check
                    order = request.website.sale_get_order()
                    shippings = Partner.sudo().search([('id', 'child_of', order.partner_id.commercial_partner_id.ids)])
                    if partner_id not in shippings.mapped('id') and partner_id != order.partner_id.id:
                        return Forbidden()
                    Partner.sudo().browse(partner_id).write(checkout)
                    _logger.info(f"Partner actualizado exitosamente con ID: {partner_id}")
                    
            except Exception as e:
                _logger.error(f"Error al actualizar partner: {e}")
                _logger.error(f"Partner ID: {partner_id}, Datos: {checkout}")
                # Re-lanzar la excepción para que el flujo normal de errores la maneje
                raise
        
        # Verificación final del partner_id antes de retornar
        if not partner_id:
            _logger.error("Error: partner_id es None o 0 al final de _checkout_form_save")
            raise ValidationError("Error al crear o actualizar el partner")
            
        _logger.info(f"_checkout_form_save completado exitosamente. Partner ID: {partner_id}")
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
            new_values['invoice_type'] = 'factura'
        else:
            new_values['invoice_type'] = 'boleta'
        _logger.info(f"Tipo de comprobante asignado: {new_values['invoice_type']}")
        
        # Agregar campos personalizados - mapear a los campos del modelo res_partner
        _logger.info(f"Procesando campos personalizados...")
        _logger.info(f"DNI en values: {values.get('dni')}")
        
        if 'dni' in values and values['dni']:
            new_values['dni'] = values['dni'].strip()
            _logger.info(f"DNI procesado: {new_values['dni']}")
        else:
            _logger.info("DNI no encontrado o vacío")
            
        # Solo incluir campos de factura si se solicita factura
        if is_invoice_requested:
            _logger.info("Procesando campos de factura...")
            if 'ruc' in values and values['ruc']:
                new_values['ruc'] = values['ruc'].strip()
                _logger.info(f"RUC procesado: {new_values['ruc']}")
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