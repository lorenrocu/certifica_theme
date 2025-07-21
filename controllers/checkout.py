# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.exceptions import ValidationError


class WebsiteSaleCheckout(WebsiteSale):
    @http.route(['/shop/payment/transfer'], type='http', auth='public', website=True, sitemap=False)
    def payment_transfer(self, **kw):
        """
        Renderiza la página con instrucciones para el pago por transferencia bancaria.
        """
        return request.render('certifica_theme.transfer_form', {})

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
        new_values = super(WebsiteSaleCheckout, self).values_preprocess(order, mode, values)
        
        # Verificar si se solicita factura
        is_invoice_requested = values.get('invoice_type_checkbox') == 'on' or values.get('invoice_type') == 'factura'
        
        # Agregar campos personalizados solo si son necesarios
        if 'dni' in values:
            new_values['dni'] = values['dni']
            
        # Solo incluir campos de factura si se solicita factura
        if is_invoice_requested:
            if 'ruc' in values:
                new_values['ruc'] = values['ruc']
            if 'razon_social' in values:
                new_values['name'] = values['razon_social']  # Mapear razón social al nombre
        else:
            # Si no se solicita factura, asegurarse de que no se incluyan estos campos
            new_values.pop('ruc', None)
            new_values.pop('razon_social', None)
            
        return new_values

    def checkout_form_validate(self, mode, all_form_values, data_values):
        """
        Validamos el formulario incluyendo validaciones para DNI y RUC
        """
        error = dict()
        error_message = []

        # Llamar validación original
        error, error_message = super(WebsiteSaleCheckout, self).checkout_form_validate(mode, all_form_values, data_values)

        # Validaciones personalizadas
        invoice_type = all_form_values.get('invoice_type', 'boleta')
        invoice_type_checkbox = all_form_values.get('invoice_type_checkbox')
        dni = all_form_values.get('dni', '').strip()
        ruc = all_form_values.get('ruc', '').strip()
        razon_social = all_form_values.get('razon_social', '').strip()
        
        # Determinar el tipo real basado en el checkbox
        is_invoice_requested = invoice_type_checkbox == 'on' or invoice_type == 'factura'
        
        print(f"=== VALIDACIÓN SERVIDOR ===")
        print(f"invoice_type: {invoice_type}")
        print(f"invoice_type_checkbox: {invoice_type_checkbox}")
        print(f"is_invoice_requested: {is_invoice_requested}")
        print(f"dni: '{dni}'")
        print(f"ruc: '{ruc}'")
        print(f"razon_social: '{razon_social}'")

        if is_invoice_requested:
            print("Validando para FACTURA")
            # Para factura se requiere RUC y Razón Social
            if not ruc:
                error['ruc'] = 'missing'
                error_message.append('RUC es requerido para factura')
                print("❌ RUC faltante")
            elif len(ruc) != 11 or not ruc.isdigit():
                error['ruc'] = 'invalid'
                error_message.append('RUC debe tener exactamente 11 dígitos')
                print("❌ RUC formato inválido")
            else:
                print("✅ RUC válido")
            
            if not razon_social:
                error['razon_social'] = 'missing'
                error_message.append('Razón Social es requerida para factura')
                print("❌ Razón Social faltante")
            else:
                print("✅ Razón Social válida")
        else:
            print("Validando para BOLETA")
            # Para boleta, DNI es completamente opcional
            # Solo validar formato si se proporciona un valor
            if dni:
                if len(dni) != 8 or not dni.isdigit():
                    error['dni'] = 'invalid'
                    error_message.append('DNI debe tener exactamente 8 dígitos')
                    print("❌ DNI formato inválido")
                else:
                    print("✅ DNI válido")
            else:
                print("✅ DNI no proporcionado - es opcional")
            
            # Ignorar completamente los campos de factura
            if 'ruc' in error:
                del error['ruc']
            if 'razon_social' in error:
                del error['razon_social']
        
        print(f"Errores encontrados: {len(error)}")
        print(f"Mensajes de error: {error_message}")

        return error, error_message