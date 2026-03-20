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
        Sobreescribe _get_combination_info para SIEMPRE inyectar el stock
        físico real calculado directamente desde stock.quant.
        """
        res = super(ProductTemplate, self)._get_combination_info(
            combination=combination,
            product_id=product_id,
            add_qty=add_qty,
            pricelist=pricelist,
            parent_combination=parent_combination,
            only_template=only_template,
        )

        if not isinstance(res, dict):
            return res

        try:
            # Obtener el product.product ID
            pid = res.get('product_id') or product_id
            if pid:
                # Buscar por product.product ID directamente
                quants = self.env['stock.quant'].sudo().search([
                    ('product_id', '=', pid),
                    ('location_id.usage', '=', 'internal'),
                ])
            else:
                # Si no hay product_id, buscar por todas las variantes del template
                variant_ids = self.sudo().product_variant_ids.ids
                quants = self.env['stock.quant'].sudo().search([
                    ('product_id', 'in', variant_ids),
                    ('location_id.usage', '=', 'internal'),
                ])

            qty_on_hand = sum(quants.mapped('quantity'))
            reserved = sum(quants.mapped('reserved_quantity'))
            real_qty = qty_on_hand - reserved

            # SIEMPRE establecer virtual_available con el stock real
            old_val = res.get('virtual_available', 'NOT_SET')
            res['virtual_available'] = real_qty

            _logger.warning(
                '=== CERTIFICA STOCK: product_id=%s, quants=%s, '
                'on_hand=%s, reserved=%s, real_qty=%s, old_virtual=%s',
                pid, len(quants), qty_on_hand, reserved, real_qty, old_val)

        except Exception as e:
            _logger.warning(
                '=== CERTIFICA STOCK: ERROR: %s', e)

        return res
