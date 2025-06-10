# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError

class ResPartner(models.Model):
    _inherit = 'res.partner'

    # Campo específico para RUC
    ruc = fields.Char('RUC', size=11, help="Número de RUC", required=False)
    
    # Campo personalizado para el checkout
    ruc_custom = fields.Char('RUC', size=11, help="RUC personalizado para el checkout", required=False)
    
    # Deshabilitar el campo VAT
    vat = fields.Char('NIF/VAT', readonly=True)

    @api.constrains('ruc', 'ruc_custom')
    def _check_ruc(self):
        """
        Validación del RUC:
        - Debe tener exactamente 11 dígitos
        - Todos los caracteres deben ser números
        """
        for partner in self:
            for field in ['ruc', 'ruc_custom']:
                value = getattr(partner, field)
                if value:
                    ruc = value.strip()
                    if len(ruc) != 11 or not ruc.isdigit():
                        raise ValidationError('El RUC debe tener exactamente 11 dígitos numéricos.')

    @api.model
    def create(self, vals):
        """
        Al crear un partner, copiar el RUC al campo vat si está presente
        """
        if 'ruc' in vals and vals['ruc']:
            vals['vat'] = vals['ruc']
        elif 'ruc_custom' in vals and vals['ruc_custom']:
            vals['vat'] = vals['ruc_custom']
        return super(ResPartner, self).create(vals)

    @api.multi
    def write(self, vals):
        """
        Al actualizar un partner, copiar el RUC al campo vat si está presente
        """
        if 'ruc' in vals and vals['ruc']:
            vals['vat'] = vals['ruc']
        elif 'ruc_custom' in vals and vals['ruc_custom']:
            vals['vat'] = vals['ruc_custom']
        return super(ResPartner, self).write(vals) 