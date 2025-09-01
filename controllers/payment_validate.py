from odoo import http
from odoo.http import request

class WebsiteSalePaymentValidateCustom(http.Controller):
    @http.route(['/shop/payment/validate'], type='http', auth="public", website=True)
    def shop_payment_validate(self, **kwargs):
        order = request.website.sale_get_order()
        acquirer = None
        
        # En Odoo 13, el payment_acquirer_id no existe directamente en sale.order
        # Necesitamos obtenerlo a través de las transacciones de pago
        if order:
            # Buscar transacciones de pago relacionadas con esta orden
            payment_transactions = request.env['payment.transaction'].sudo().search([
                ('sale_order_ids', 'in', [order.id])
            ], limit=1)
            
            if payment_transactions:
                acquirer = payment_transactions.acquirer_id
        
        return request.render('certifica_theme.payment_confirmation_page', {
            'order': order,
            'acquirer': acquirer,
        })