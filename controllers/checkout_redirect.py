# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale
import logging

_logger = logging.getLogger(__name__)


class WebsiteSaleCheckoutRedirect(WebsiteSale):
    """
    Controlador específico para manejar la redirección después del checkout
    y evitar que se recargue la página de address
    """
    
    @http.route(['/shop/address'], type='http', auth="public", website=True, sitemap=False)
    def address(self, **kw):
        """
        Sobrescribimos el método address para manejar la redirección correctamente
        """
        _logger.info("=== ADDRESS ROUTE - CHECKOUT REDIRECT ===")
        _logger.info(f"Method: {request.httprequest.method}")
        _logger.info(f"KW recibidos: {kw}")
        
        # Si es POST con datos del formulario, procesar y redirigir
        if request.httprequest.method == 'POST':
            _logger.info("🔄 POST detectado, procesando formulario de checkout")
            
            # Obtener todos los valores del formulario
            all_form_values = request.httprequest.form.to_dict()
            _logger.info(f"Valores del formulario: {all_form_values}")
            
            # Verificar si es un envío válido del formulario
            if len(all_form_values) > 1:  # Más que solo el token CSRF
                _logger.info("✅ Formulario válido detectado, procesando checkout")
                
                # Procesar el checkout usando el controlador original
                try:
                    # Llamar al método del controlador de checkout
                    checkout_controller = request.env['ir.http'].session.proxy(request).env['website'].get_controller('checkout')
                    if hasattr(checkout_controller, 'address'):
                        result = checkout_controller.address(**kw)
                        _logger.info("✅ Checkout procesado por controlador original")
                        return result
                    else:
                        _logger.warning("Controlador de checkout no encontrado")
                except Exception as e:
                    _logger.error(f"❌ Error procesando checkout: {e}")
                
                # Si no se pudo procesar, hacer redirección manual
                _logger.info("🔄 Redirección manual a /shop/payment")
                return request.redirect('/shop/payment')
            
            else:
                _logger.info("⚠️ Formulario incompleto, mostrando página de address")
        
        # Si es GET o formulario incompleto, mostrar la página normalmente
        _logger.info("📄 Mostrando página de address")
        return super(WebsiteSaleCheckoutRedirect, self).address(**kw)
    
    @http.route(['/shop/checkout/process'], type='http', auth="public", website=True, methods=['POST'], csrf=False)
    def checkout_process(self, **post):
        """
        Endpoint específico para procesar el checkout y redirigir
        """
        _logger.info("=== CHECKOUT PROCESS ENDPOINT ===")
        _logger.info(f"Post data: {post}")
        
        try:
            # Obtener el pedido actual
            order = request.website.sale_get_order()
            
            if not order or not order.order_line:
                _logger.warning("No hay pedido válido")
                return request.redirect('/shop/cart')
            
            # Procesar los datos del formulario
            # Aquí puedes agregar la lógica específica de tu checkout
            
            # Redirigir a la página de pago
            _logger.info("🔄 Redirigiendo a /shop/payment")
            return request.redirect('/shop/payment')
            
        except Exception as e:
            _logger.error(f"❌ Error en checkout_process: {e}")
            return request.redirect('/shop/address')
    
    @http.route(['/shop/checkout/validate'], type='http', auth="public", website=True, methods=['POST'], csrf=False)
    def checkout_validate(self, **post):
        """
        Endpoint para validar el checkout antes de redirigir
        """
        _logger.info("=== CHECKOUT VALIDATE ENDPOINT ===")
        _logger.info(f"Post data: {post}")
        
        try:
            # Obtener el pedido actual
            order = request.website.sale_get_order()
            
            if not order or not order.order_line:
                _logger.warning("No hay pedido válido")
                return request.redirect('/shop/cart')
            
            # Validar que el partner esté asignado
            if not order.partner_id or order.partner_id.id == request.website.partner_id.id:
                _logger.warning("Partner no válido, redirigiendo a address")
                return request.redirect('/shop/address')
            
            # Si todo está bien, redirigir a payment
            _logger.info("✅ Checkout válido, redirigiendo a payment")
            return request.redirect('/shop/payment')
            
        except Exception as e:
            _logger.error(f"❌ Error en checkout_validate: {e}")
            return request.redirect('/shop/address')
