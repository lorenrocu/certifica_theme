# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale
import logging

_logger = logging.getLogger(__name__)


class WebsiteSalePaymentOverride(WebsiteSale):
    """
    Controlador que sobrescribe completamente el flujo de pago para evitar el AssertionError
    """
    
    def _ensure_valid_partner(self, order):
        """
        Asegura que el partner esté correctamente asignado al pedido
        """
        _logger.info("=== VERIFICANDO PARTNER VÁLIDO ===")
        
        if not order:
            return False, "No hay pedido válido"
        
        # Verificar que el partner esté asignado y sea diferente al website partner
        if not order.partner_id:
            _logger.error("No hay partner asignado al pedido")
            return False, "No hay partner asignado"
        
        if order.partner_id.id == request.website.partner_id.id:
            _logger.error("Partner del pedido es el mismo que el website partner")
            return False, "Partner inválido"
        
        # Verificar campos mínimos
        if not order.partner_id.name:
            _logger.error("Partner sin nombre")
            return False, "Partner sin nombre"
        
        if not order.partner_id.email:
            _logger.error("Partner sin email")
            return False, "Partner sin email"
        
        _logger.info(f"✅ Partner válido: {order.partner_id.name} (ID: {order.partner_id.id})")
        return True, "Partner válido"
    
    @http.route(['/shop/payment/transaction'], type='json', auth="public", website=True)
    def payment_transaction(self, **post):
        """
        Sobrescribimos completamente el método payment_transaction para evitar el AssertionError
        """
        _logger.info("=== PAYMENT TRANSACTION OVERRIDE ===")
        _logger.info(f"Post data: {post}")
        
        # Obtener el pedido actual
        order = request.website.sale_get_order()
        
        if not order or not order.order_line:
            _logger.error("No hay pedido válido o líneas de pedido")
            return {'error': 'No hay pedido válido'}
        
        # Verificar que el partner esté correctamente asignado
        is_valid, message = self._ensure_valid_partner(order)
        if not is_valid:
            _logger.error(f"Partner no válido: {message}")
            return {'error': message}
        
        # Obtener el acquirer del formulario
        acquirer_id = post.get('acquirer_id')
        if not acquirer_id:
            _logger.error("No se especificó acquirer_id")
            return {'error': 'Acquirer no especificado'}
        
        try:
            acquirer = request.env['payment.acquirer'].sudo().browse(int(acquirer_id))
            if not acquirer.exists():
                _logger.error(f"Acquirer {acquirer_id} no encontrado")
                return {'error': 'Acquirer no válido'}
        except (ValueError, TypeError):
            _logger.error(f"Acquirer_id inválido: {acquirer_id}")
            return {'error': 'Acquirer_id inválido'}
        
        _logger.info(f"✅ Acquirer válido: {acquirer.name}")
        
        # Crear la transacción de pago
        try:
            # Crear la transacción con el partner correcto
            transaction = request.env['payment.transaction'].sudo().create({
                'acquirer_id': acquirer.id,
                'reference': order.name,
                'amount': order.amount_total,
                'currency_id': order.currency_id.id,
                'partner_id': order.partner_id.id,
                'sale_order_ids': [(6, 0, [order.id])],
                'state': 'draft',
            })
            
            _logger.info(f"✅ Transacción creada: {transaction.reference}")
            
            # Si el acquirer es de prueba, simular el pago
            if acquirer.state == 'test':
                _logger.info("🔄 Acquirer de prueba, simulando pago exitoso")
                transaction.sudo().write({'state': 'done'})
                order.sudo().write({'state': 'sale'})
                return {'success': True, 'transaction_id': transaction.id}
            
            # Para acquirers reales, redirigir al formulario de pago
            if hasattr(acquirer, 's2s_form_process'):
                # Procesar formulario S2S si está disponible
                result = acquirer.s2s_form_process(post)
                if result:
                    return result
            
            # Redirigir al formulario de pago del acquirer
            if hasattr(acquirer, 's2s_form_render'):
                form_html = acquirer.s2s_form_render(transaction.id, post)
                return {
                    'form_html': form_html,
                    'transaction_id': transaction.id
                }
            
            # Fallback: redirigir a la URL del acquirer
            if acquirer.redirect_form_view_id:
                return {
                    'redirect_url': f'/payment/process/{transaction.id}',
                    'transaction_id': transaction.id
                }
            
            _logger.warning("No se pudo determinar el flujo de pago del acquirer")
            return {'error': 'Flujo de pago no disponible'}
            
        except Exception as e:
            _logger.error(f"❌ Error creando transacción: {str(e)}")
            return {'error': f'Error creando transacción: {str(e)}'}
    
    @http.route(['/shop/payment'], type='http', auth="public", website=True, sitemap=False)
    def payment(self, **post):
        """
        Sobrescribimos el método payment para asegurar que el partner esté correctamente asignado
        """
        _logger.info("=== PAYMENT ROUTE OVERRIDE ===")
        
        # Obtener el pedido actual
        order = request.website.sale_get_order()
        
        if not order or not order.order_line:
            _logger.warning("No hay pedido válido, redirigiendo a /shop/cart")
            return request.redirect('/shop/cart')
        
        # Verificar que el partner esté correctamente asignado
        is_valid, message = self._ensure_valid_partner(order)
        if not is_valid:
            _logger.warning(f"Partner no válido: {message}, redirigiendo a /shop/address")
            return request.redirect('/shop/address')
        
        # Llamar al método padre para mostrar la página de pago
        return super(WebsiteSalePaymentOverride, self).payment(**post)
    
    @http.route(['/shop/payment/validate'], type='http', auth="public", website=True)
    def payment_validate(self, **post):
        """
        Sobrescribimos el método payment_validate para manejar la confirmación del pago
        """
        _logger.info("=== PAYMENT VALIDATE OVERRIDE ===")
        
        # Obtener el pedido actual
        order = request.website.sale_get_order()
        
        if not order:
            _logger.warning("No hay pedido para validar")
            return request.redirect('/shop/cart')
        
        # Llamar al método padre
        try:
            result = super(WebsiteSalePaymentOverride, self).payment_validate(**post)
            _logger.info("✅ Pago validado exitosamente")
            return result
        except Exception as e:
            _logger.error(f"❌ Error en payment_validate: {str(e)}")
            # Redirigir a una página de error o al carrito
            return request.redirect('/shop/cart')
