# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale
import logging

_logger = logging.getLogger(__name__)


class WebsiteSalePaymentFlow(WebsiteSale):
    """
    Controlador personalizado para manejar el flujo de pago y evitar el AssertionError
    """
    
    @http.route(['/shop/payment'], type='http', auth="public", website=True, sitemap=False)
    def payment(self, **post):
        """
        Sobrescribimos el método payment para asegurar que el partner esté correctamente asignado
        """
        _logger.info("=== PAYMENT ROUTE - VERIFICANDO PARTNER ===")
        
        # Obtener el pedido actual
        order = request.website.sale_get_order()
        
        if not order or not order.order_line:
            _logger.warning("No hay pedido válido, redirigiendo a /shop/cart")
            return request.redirect('/shop/cart')
        
        # Verificar que el partner esté correctamente asignado
        if not order.partner_id or order.partner_id.id == request.website.partner_id.id:
            _logger.warning("Partner no válido o es el mismo que el website")
            
            # Buscar si hay un partner en la sesión
            session_partner_id = request.session.get('partner_id')
            if session_partner_id:
                partner = request.env['res.partner'].sudo().browse(session_partner_id)
                if partner.exists():
                    # Asignar el partner al pedido
                    order.write({
                        'partner_id': partner.commercial_partner_id.id or partner.id,
                        'partner_invoice_id': partner.id,
                        'partner_shipping_id': partner.id,
                    })
                    _logger.info(f"✅ Partner de sesión {partner.id} asignado al pedido {order.id}")
                    # Limpiar la sesión
                    request.session.pop('partner_id', None)
                else:
                    _logger.error("Partner de sesión no válido")
                    return request.redirect('/shop/address')
            else:
                _logger.error("No hay partner válido, redirigiendo a /shop/address")
                return request.redirect('/shop/address')
        
        # Verificar que el partner tenga los campos mínimos requeridos
        if not order.partner_id.name or not order.partner_id.email:
            _logger.warning("Partner sin campos mínimos requeridos, redirigiendo a /shop/address")
            return request.redirect('/shop/address')
        
        _logger.info(f"✅ Partner válido: {order.partner_id.name} (ID: {order.partner_id.id})")
        
        # Llamar al método padre para mostrar la página de pago
        return super(WebsiteSalePaymentFlow, self).payment(**post)
    
    @http.route(['/shop/payment/transaction'], type='json', auth="public", website=True)
    def payment_transaction(self, **post):
        """
        Sobrescribimos el método payment_transaction para evitar el AssertionError
        """
        _logger.info("=== PAYMENT TRANSACTION ROUTE ===")
        
        # Obtener el pedido actual
        order = request.website.sale_get_order()
        
        if not order or not order.order_line:
            return {'error': 'No hay pedido válido'}
        
        # Verificar que el partner esté correctamente asignado
        if not order.partner_id or order.partner_id.id == request.website.partner_id.id:
            _logger.error("Partner no válido en payment_transaction")
            return {'error': 'Partner no válido'}
        
        # Verificar que el partner tenga los campos mínimos
        if not order.partner_id.name or not order.partner_id.email:
            _logger.error("Partner sin campos mínimos en payment_transaction")
            return {'error': 'Partner incompleto'}
        
        _logger.info(f"✅ Partner válido para transacción: {order.partner_id.name}")
        
        # Ahora llamar al método padre con el partner correctamente asignado
        try:
            result = super(WebsiteSalePaymentFlow, self).payment_transaction(**post)
            _logger.info("✅ Transacción de pago procesada exitosamente")
            return result
        except Exception as e:
            _logger.error(f"❌ Error en payment_transaction: {str(e)}")
            return {
                'error': 'Error en la transacción de pago',
                'details': str(e)
            }
    
    @http.route(['/shop/payment/validate'], type='http', auth="public", website=True)
    def payment_validate(self, **post):
        """
        Sobrescribimos el método payment_validate para manejar la confirmación del pago
        """
        _logger.info("=== PAYMENT VALIDATE ROUTE ===")
        
        # Obtener el pedido actual
        order = request.website.sale_get_order()
        
        if not order:
            _logger.warning("No hay pedido para validar")
            return request.redirect('/shop/cart')
        
        # Llamar al método padre
        try:
            result = super(WebsiteSalePaymentFlow, self).payment_validate(**post)
            _logger.info("✅ Pago validado exitosamente")
            return result
        except Exception as e:
            _logger.error(f"❌ Error en payment_validate: {str(e)}")
            # Redirigir a una página de error o al carrito
            return request.redirect('/shop/cart')
