# -*- coding: utf-8 -*-
"""Extensión para generar cotizaciones web con prefijo T-S."""
from odoo import api, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model
    def create(self, vals):
        """Si la orden proviene del website fuerza la secuencia web."""
        if (
            self.env.context.get("from_website")
            or vals.get("website_id")
        ) and vals.get("name", "/") in ("/", False):
            vals["name"] = self.env["ir.sequence"].next_by_code("sale.order.web") or "/"
        return super().create(vals)


class Website(models.Model):
    _inherit = "website"

    def sale_get_order(self, *args, **kwargs):
        """Inyecta el flag from_website para que el SaleOrder use la secuencia web."""
        new_self = self.with_context(dict(self.env.context, from_website=True))
        return super(Website, new_self).sale_get_order(*args, **kwargs)