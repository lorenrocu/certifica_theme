# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    website_real_qty = fields.Float(
        string='Stock Real (Web)',
        compute='_compute_website_real_qty',
    )

    def _compute_website_real_qty(self):
        """
        Calcula el stock físico real consultando stock.quant directamente,
        ignorando el contexto de warehouse de la sesión del usuario web.
        Esto evita que qty_available (que depende del warehouse context)
        muestre valores incorrectos en el frontend.
        """
        for product in self:
            quants = self.env['stock.quant'].search([
                ('product_id.product_tmpl_id', '=', product.id),
                ('location_id.usage', '=', 'internal'),
            ])
            qty_on_hand = sum(quants.mapped('quantity'))
            reserved = sum(quants.mapped('reserved_quantity'))
            product.website_real_qty = max(0.0, qty_on_hand - reserved)


class ProductProduct(models.Model):
    _inherit = 'product.product'

    website_real_qty = fields.Float(
        string='Stock Real (Web)',
        compute='_compute_product_website_real_qty',
    )

    def _compute_product_website_real_qty(self):
        """
        Igual que en product.template pero para la variante específica.
        Lo usa website_sale_stock para mostrar disponibilidad por variante.
        """
        for product in self:
            quants = self.env['stock.quant'].search([
                ('product_id', '=', product.id),
                ('location_id.usage', '=', 'internal'),
            ])
            qty_on_hand = sum(quants.mapped('quantity'))
            reserved = sum(quants.mapped('reserved_quantity'))
            product.website_real_qty = max(0.0, qty_on_hand - reserved)
