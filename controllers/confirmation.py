from odoo import http
from odoo.http import request

class WebsiteSaleConfirmationCustom(http.Controller):
    @http.route(['/shop/confirmation'], type='http', auth="public", website=True)
    def shop_confirmation(self, **kwargs):
        order = request.website.sale_get_order()
        acquirer = None
        if order and order.payment_acquirer_id:
            acquirer = order.payment_acquirer_id
        return request.render('theme_inventive.inventive_congratulations_page', {
            'order': order,
            'acquirer': acquirer,
        }) 