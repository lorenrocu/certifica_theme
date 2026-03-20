# -*- coding: utf-8 -*-

from odoo import models, api
import logging

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def _get_combination_info(self, combination=False, product_id=False,
                              add_qty=1, pricelist=False,
                              parent_combination=False, only_template=False):
        """
        Sobreescribe _get_combination_info para reemplazar el valor de
        virtual_available (que website_sale_stock usa en su widget JS)
        con el stock físico real calculado directamente desde stock.quant.

        website_sale_stock inyecta 'virtual_available' en este dict,
        que incluye pedidos de compra pendientes (stock previsto).
        Nosotros lo reemplazamos con la cantidad física real en
        ubicaciones internas.
        """
        res = super(ProductTemplate, self)._get_combination_info(
            combination=combination,
            product_id=product_id,
            add_qty=add_qty,
            pricelist=pricelist,
            parent_combination=parent_combination,
            only_template=only_template,
        )

        # Si website_sale_stock añadió virtual_available, lo reemplazamos
        if 'virtual_available' in res:
            try:
                pid = res.get('product_id', product_id)
                if pid:
                    quants = self.env['stock.quant'].sudo().search([
                        ('product_id', '=', pid),
                        ('location_id.usage', '=', 'internal'),
                    ])
                    qty_on_hand = sum(quants.mapped('quantity'))
                    reserved = sum(quants.mapped('reserved_quantity'))
                    real_qty = max(0.0, qty_on_hand - reserved)
                    res['virtual_available'] = real_qty
                    _logger.debug(
                        'certifica_theme: product_id=%s real_qty=%s '
                        '(was virtual_available=%s)',
                        pid, real_qty, res.get('virtual_available'))
            except Exception as e:
                _logger.warning(
                    'certifica_theme: error computing real stock: %s', e)

        return res
