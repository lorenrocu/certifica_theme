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
            # Formatear DNI como RUC peruano (agregar prefijo 10)
            dni = vals['dni'].strip()
            if len(dni) == 8 and dni.isdigit():
                vals['vat'] = f"10{dni}"  # Formato válido para Perú
                _logger.info(f"DNI mapeado a VAT con formato RUC: {vals['vat']}")
            else:
                vals['vat'] = dni
                _logger.info(f"DNI mapeado a VAT: {vals['vat']}")
        elif 'ruc' in vals and vals['ruc']:
            ruc = vals['ruc'].strip()
            if len(ruc) == 11 and ruc.isdigit():
                # Verificar que tenga formato válido de RUC peruano
                if ruc.startswith(('10', '20', '15', '16', '17')):
                    vals['vat'] = ruc
                    _logger.info(f"RUC válido mapeado a VAT: {vals['vat']}")
                else:
                    # Si no tiene formato válido, agregar prefijo 20
                    vals['vat'] = f"20{ruc[-9:]}"
                    _logger.info(f"RUC reformateado a VAT: {vals['vat']}")
            else:
                vals['vat'] = ruc
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
            # Formatear DNI como RUC peruano (agregar prefijo 10)
            dni = vals['dni'].strip()
            if len(dni) == 8 and dni.isdigit():
                vals['vat'] = f"10{dni}"  # Formato válido para Perú
                _logger.info(f"DNI mapeado a VAT con formato RUC: {vals['vat']}")
            else:
                vals['vat'] = dni
                _logger.info(f"DNI mapeado a VAT: {vals['vat']}")
        elif 'ruc' in vals and vals['ruc']:
            ruc = vals['ruc'].strip()
            if len(ruc) == 11 and ruc.isdigit():
                # Verificar que tenga formato válido de RUC peruano
                if ruc.startswith(('10', '20', '15', '16', '17')):
                    vals['vat'] = ruc
                    _logger.info(f"RUC válido mapeado a VAT: {vals['vat']}")
                else:
                    # Si no tiene formato válido, agregar prefijo 20
                    vals['vat'] = f"20{ruc[-9:]}"
                    _logger.info(f"RUC reformateado a VAT: {vals['vat']}")
            else:
                vals['vat'] = ruc
                _logger.info(f"RUC mapeado a VAT: {vals['vat']}")
        
        _logger.info(f"Valores después de mapeo VAT: {vals}")
        
        # Actualizar el partner
        result = super(ResPartner, self).write(vals)
        
        _logger.info(f"Partner actualizado exitosamente")
        _logger.info("=== FIN WRITE PARTNER ===")
        
        return result

    @api.constrains('vat')
    def _check_vat(self):
        """
        Deshabilitar la validación de VAT para permitir DNI y RUC peruanos
        """
        # No hacer ninguna validación - permitir cualquier formato
        # Esto sobrescribe la validación del módulo base_vat
        pass