# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError

class ResPartner(models.Model):
    _inherit = 'res.partner'

    # Campo específico para DNI (personas naturales)
    dni = fields.Char('DNI', size=8, help="Documento Nacional de Identidad", required=False)
    
    # Campo específico para RUC (empresas)
    ruc = fields.Char('RUC', size=11, help="Número de RUC", required=False)
    
    # Campo personalizado para el checkout
    ruc_custom = fields.Char('RUC', size=11, help="RUC personalizado para el checkout", required=False)
    
    # Campo para tipo de comprobante
    invoice_type = fields.Selection([
        ('boleta', 'Boleta'),
        ('factura', 'Factura')
    ], string='Tipo de Comprobante', default='boleta')
    
    # Campo VAT que se mapea automáticamente
    vat = fields.Char('NIF/VAT', readonly=True, help="Se mapea automáticamente desde DNI o RUC")

    def _check_dni(self):
        """
        Validación del DNI:
        - Debe tener exactamente 8 dígitos
        - Todos los caracteres deben ser números
        """
        for partner in self:
            if partner.dni:
                dni = partner.dni.strip()
                if len(dni) != 8 or not dni.isdigit():
                    raise ValidationError('El DNI debe tener exactamente 8 dígitos numéricos.')

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

    def _check_document_consistency(self):
        """
        Validación de consistencia entre tipo de comprobante y documento:
        - Boleta requiere DNI
        - Factura requiere RUC
        """
        for partner in self:
            if partner.invoice_type == 'boleta' and not partner.dni:
                raise ValidationError('Para boleta se requiere DNI.')
            elif partner.invoice_type == 'factura' and not (partner.ruc or partner.ruc_custom):
                raise ValidationError('Para factura se requiere RUC.')

    def _update_vat_field(self, vals):
        """
        Método auxiliar para actualizar el campo VAT según el tipo de comprobante
        """
        # Determinar el tipo de comprobante
        invoice_type = vals.get('invoice_type', getattr(self, 'invoice_type', 'boleta'))
        
        if invoice_type == 'factura':
            # Para factura, usar RUC
            if 'ruc' in vals and vals['ruc']:
                vals['vat'] = vals['ruc']
            elif 'ruc_custom' in vals and vals['ruc_custom']:
                vals['vat'] = vals['ruc_custom']
            elif hasattr(self, 'ruc') and self.ruc:
                vals['vat'] = self.ruc
            elif hasattr(self, 'ruc_custom') and self.ruc_custom:
                vals['vat'] = self.ruc_custom
        else:
            # Para boleta, usar DNI
            if 'dni' in vals and vals['dni']:
                vals['vat'] = vals['dni']
            elif hasattr(self, 'dni') and self.dni:
                vals['vat'] = self.dni

    @api.model
    def create(self, vals):
        """
        Al crear un partner, mapear DNI o RUC al campo VAT según el tipo de comprobante
        """
        # Crear un objeto temporal para usar el método auxiliar
        temp_partner = self.new(vals)
        temp_partner._update_vat_field(vals)
        return super(ResPartner, self).create(vals)

    def write(self, vals):
        """
        Al actualizar un partner, mapear DNI o RUC al campo VAT según el tipo de comprobante
        """
        for partner in self:
            partner._update_vat_field(vals)
        return super(ResPartner, self).write(vals)

    def _onchange_document_fields(self):
        """
        Actualizar el campo VAT cuando cambian los documentos o el tipo de comprobante
        """
        vals = {}
        self._update_vat_field(vals)
        if 'vat' in vals:
            self.vat = vals['vat']