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
        """
        _logger.warning(
            '=== CERTIFICA STOCK: _get_combination_info CALLED === '
            'product_id=%s, self=%s', product_id, self.ids)

        res = super(ProductTemplate, self)._get_combination_info(
            combination=combination,
            product_id=product_id,
            add_qty=add_qty,
            pricelist=pricelist,
            parent_combination=parent_combination,
            only_template=only_template,
        )

        _logger.warning(
            '=== CERTIFICA STOCK: result keys=%s, '
            'virtual_available in res? %s',
            list(res.keys()) if isinstance(res, dict) else 'NOT_DICT',
            'virtual_available' in res if isinstance(res, dict) else 'N/A')

        # Si website_sale_stock añadió virtual_available, lo reemplazamos
        if isinstance(res, dict) and 'virtual_available' in res:
            old_val = res['virtual_available']
            pid = res.get('product_id', product_id)
            _logger.warning(
                '=== CERTIFICA STOCK: FOUND virtual_available=%s, '
                'product_id=%s, computing real qty...', old_val, pid)
            try:
                if pid:
                    quants = self.env['stock.quant'].sudo().search([
                        ('product_id', '=', pid),
                        ('location_id.usage', '=', 'internal'),
                    ])
                    qty_on_hand = sum(quants.mapped('quantity'))
                    reserved = sum(quants.mapped('reserved_quantity'))
                    real_qty = max(0.0, qty_on_hand - reserved)
                    res['virtual_available'] = real_qty
                    _logger.warning(
                        '=== CERTIFICA STOCK: REPLACED! '
                        'old=%s -> new=%s (on_hand=%s, reserved=%s, '
                        'quants_count=%s)',
                        old_val, real_qty, qty_on_hand, reserved, len(quants))
            except Exception as e:
                _logger.warning(
                    '=== CERTIFICA STOCK: ERROR computing real stock: %s', e)

        return res

