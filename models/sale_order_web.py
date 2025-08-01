# -*- coding: utf-8 -*-
"""Extensión para generar cotizaciones web con prefijo T-S."""
from odoo import api, models
import logging

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model
    def create(self, vals):
        """Intercepta la creación de órdenes para aplicar secuencia web cuando corresponda."""
        _logger.info("SaleOrder.create called with vals: %s", vals)
        _logger.info("Context: %s", self.env.context)
        
        # Si tiene website_id, es una orden web
        if vals.get("website_id") and vals.get("name", "/") in ("/", False):
            old_name = vals.get("name")
            vals["name"] = self.env["ir.sequence"].next_by_code("sale.order.web") or "/"
            _logger.info("Web order detected - Changed name from %s to %s", old_name, vals["name"])
        
        return super().create(vals)

    @api.model
    def _get_website_sale_order(self, partner, website_id, force_create=False, code=None, force_pricelist=False, update_pricelist=False):
        """Override del método interno para forzar secuencia web en órdenes nuevas."""
        _logger.info("_get_website_sale_order called")
        
        # Llamar al método padre primero
        order = super()._get_website_sale_order(
            partner=partner, 
            website_id=website_id, 
            force_create=force_create, 
            code=code, 
            force_pricelist=force_pricelist, 
            update_pricelist=update_pricelist
        )
        
        # Si se creó una nueva orden y tiene el nombre por defecto, cambiarla
        if order and order.name and order.name.startswith('S') and order.website_id:
            new_name = self.env["ir.sequence"].next_by_code("sale.order.web")
            if new_name:
                _logger.info("Updating existing order name from %s to %s", order.name, new_name)
                order.sudo().write({'name': new_name})
        
        return order


class Website(models.Model):
    _inherit = "website"

    def sale_get_order(self, *args, **kwargs):
        """Inyecta el flag from_website para que el SaleOrder use la secuencia web."""
        _logger.info("Website.sale_get_order called")
        new_self = self.with_context(dict(self.env.context, from_website=True))
        return super(Website, new_self).sale_get_order(*args, **kwargs)