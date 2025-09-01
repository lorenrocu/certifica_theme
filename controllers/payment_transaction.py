# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale
import logging

_logger = logging.getLogger(__name__)

class WebsiteSalePaymentTransaction(WebsiteSale):
    """
    Controlador personalizado para manejar transacciones de pago
    y evitar la validación de partner_id
    """
    
    @http.route(['/shop/payment/transaction/<int:acquirer_id>'], type='json', auth="public", website=True)
    def payment_transaction(self, acquirer_id, save_token=False, verify_validity=False, **kwargs):
        """ Método que sobrescribe el payment_transaction original para evitar la validación de partner_id """
        
        # Obtener la orden actual
        order = request.website.sale_get_order()
        _logger.info(f"=== PROCESANDO PAYMENT TRANSACTION PERSONALIZADO ===\nOrder: {order.name if order else 'None'}")
        
        if not order or not order.order_line or acquirer_id is None:
            _logger.error("❌ No hay orden válida o acquirer_id")
            return {'error': 'No hay una orden válida o método de pago seleccionado'}
        
        # Verificar si el partner_id es el mismo que website.partner_id
        if order.partner_id.id == request.website.partner_id.id:
            _logger.warning("⚠️ Partner_id es igual a website.partner_id, asignando un partner temporal")
            
            # Buscar un partner existente o crear uno temporal
            Partner = request.env['res.partner'].sudo()
            temp_partner = Partner.search([('email', '=', 'cliente_temporal@certifica.com')], limit=1)
            
            if not temp_partner:
                _logger.info("Creando partner temporal para la transacción")
                temp_partner = Partner.create({
                    'name': 'Cliente Temporal',
                    'email': 'cliente_temporal@certifica.com',
                    'phone': '999999999',
                    'street': 'Dirección Temporal',
                    'city': 'Lima',
                    'country_id': 173,  # Perú
                })
            
            # Actualizar la orden con el partner temporal
            order.sudo().write({
                'partner_id': temp_partner.id,
                'partner_invoice_id': temp_partner.id,
                'partner_shipping_id': temp_partner.id,
            })
            
            # Actualizar la sesión
            request.session['partner_id'] = temp_partner.id
            _logger.info(f"✅ Partner temporal asignado: {temp_partner.id}")
        
        # Continuar con el flujo normal usando super()
        try:
            # Llamar al método original
            result = super(WebsiteSalePaymentTransaction, self).payment_transaction(
                acquirer_id=acquirer_id,
                save_token=save_token,
                verify_validity=verify_validity,
                **kwargs
            )
            _logger.info("✅ Transacción de pago procesada correctamente")
            return result
        except Exception as e:
            _logger.error(f"❌ Error en payment_transaction: {str(e)}")
            return {'error': str(e)}