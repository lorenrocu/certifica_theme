# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError

class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def create(self, vals):
        """
        Al crear un partner, mapear DNI o RUC al campo VAT
        """
        import logging
        _logger = logging.getLogger(__name__)
        
        _logger.info("=== CREATE PARTNER ===")
        _logger.info(f"Valores recibidos: {vals}")
        
        # Mapear DNI o RUC al campo VAT si están presentes
        if 'dni' in vals and vals['dni']:
            vals['vat'] = vals['dni'].strip()
            _logger.info(f"DNI mapeado a VAT: {vals['vat']}")
        elif 'ruc' in vals and vals['ruc']:
            vals['vat'] = vals['ruc'].strip()
            _logger.info(f"RUC mapeado a VAT: {vals['vat']}")
        
        _logger.info(f"Valores después de mapeo VAT: {vals}")
        
        # Crear el partner
        result = super(ResPartner, self).create(vals)
        
        _logger.info(f"Partner creado con ID: {result.id}")
        _logger.info(f"VAT final: {result.vat}")
        _logger.info("=== FIN CREATE PARTNER ===")
        
        return result

    def write(self, vals):
        """
        Al actualizar un partner, mapear DNI o RUC al campo VAT
        """
        import logging
        _logger = logging.getLogger(__name__)
        
        _logger.info("=== WRITE PARTNER ===")
        _logger.info(f"Partners a actualizar: {self.ids}")
        _logger.info(f"Valores recibidos: {vals}")
        
        # Mapear DNI o RUC al campo VAT si están presentes
        if 'dni' in vals and vals['dni']:
            vals['vat'] = vals['dni'].strip()
            _logger.info(f"DNI mapeado a VAT: {vals['vat']}")
        elif 'ruc' in vals and vals['ruc']:
            vals['vat'] = vals['ruc'].strip()
            _logger.info(f"RUC mapeado a VAT: {vals['vat']}")
        
        _logger.info(f"Valores después de mapeo VAT: {vals}")
        
        # Actualizar el partner
        result = super(ResPartner, self).write(vals)
        
        _logger.info(f"Partner actualizado exitosamente")
        _logger.info("=== FIN WRITE PARTNER ===")
        
        return result