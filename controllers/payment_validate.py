from odoo import http
from odoo.http import request

class WebsiteSalePaymentValidateCustom(http.Controller):
    @http.route(['/shop/payment/validate'], type='http', auth="public", website=True)
    def shop_payment_validate(self, **kwargs):
        order = request.website.sale_get_order()
        acquirer = None
        if order and order.payment_acquirer_id:
            acquirer = order.payment_acquirer_id
        return request.render('theme_inventive.inventive_congratulations_page', {
            'order': order,
            'acquirer': acquirer,
        }) 