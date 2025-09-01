# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale
import logging


class WebsiteSalePaymentValidate(WebsiteSale):
    _logger = logging.getLogger(__name__)
    
    @http.route(['/shop/payment/transaction/<int:acquirer_id>'], type='json', auth="public", website=True)
    def payment_transaction(self, acquirer_id, save_token=False, so_id=None, access_token=None, token=None, **kwargs):
        """ Sobrescribimos el método payment_transaction para asegurar que el partner_id esté establecido """
        self._logger.info("=== PAYMENT TRANSACTION OVERRIDE ===")
        self._logger.info(f"Acquirer ID: {acquirer_id}")
        self._logger.info(f"SO ID: {so_id}")
        
        # Obtener la orden actual
        if so_id:
            order = request.env['sale.order'].sudo().browse(int(so_id))
        else:
            order = request.website.sale_get_order()
        
        if not order or not order.order_line:
            self._logger.error("❌ No hay orden o líneas de pedido")
            return {'error': 'No hay orden o líneas de pedido'}
        
        # Verificar y corregir el partner_id si es necesario
        if not order.partner_id or order.partner_id.id == request.website.partner_id.id:
            self._logger.warning("⚠️ Partner no establecido o es el partner genérico del sitio web")
            
            # Intentar obtener el partner_id de la sesión
            partner_id = request.session.get('partner_id')
            if partner_id:
                try:
                    partner = request.env['res.partner'].sudo().browse(partner_id)
                    if partner.exists():
                        # Actualizar la orden con el partner
                        order.sudo().write({
                            'partner_id': partner.commercial_partner_id.id or partner.id,
                            'partner_invoice_id': partner.id,
                            'partner_shipping_id': partner.id,
                        })
                        self._logger.info(f"✅ Partner establecido desde sesión: {partner.id}")
                    else:
                        self._logger.warning(f"❌ Partner de sesión no existe: {partner_id}")
                        return {'error': 'El partner asociado no existe'}
                except Exception as e:
                    self._logger.error(f"❌ Error estableciendo partner desde sesión: {e}")
                    return {'error': f'Error al establecer el partner: {str(e)}'}
            else:
                self._logger.error("❌ No hay partner_id en la sesión y es requerido para el pago")
                return {'error': 'No se ha establecido un cliente para la orden'}
        else:
            self._logger.info(f"✅ Partner ya establecido en la orden: {order.partner_id.id}")
        
        # Verificar nuevamente que el partner_id esté establecido correctamente
        if not order.partner_id or order.partner_id.id == request.website.partner_id.id:
            self._logger.error("❌ Partner no establecido después de los intentos de corrección")
            return {'error': 'No se pudo establecer un cliente válido para la orden'}
        
        # Llamar al método original
        try:
            result = super(WebsiteSalePaymentValidate, self).payment_transaction(acquirer_id, save_token, so_id, access_token, token, **kwargs)
            self._logger.info(f"✅ Resultado de payment_transaction: {result}")
            return result
        except Exception as e:
            self._logger.error(f"❌ Error en payment_transaction: {e}")
            return {'error': str(e)}
    
    @http.route(['/shop/payment/validate'], type='http', auth="public", website=True, sitemap=False)
    def payment_validate(self, transaction_id=None, sale_order_id=None, **post):
        """ Método para validar el pago """
        self._logger.info("=== PAYMENT VALIDATE ===")
        self._logger.info(f"Transaction ID: {transaction_id}")
        self._logger.info(f"Sale Order ID: {sale_order_id}")
        self._logger.info(f"POST: {post}")
        
        # Llamar al método original
        return super(WebsiteSalePaymentValidate, self).payment_validate(transaction_id, sale_order_id, **post)