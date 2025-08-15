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

    @api.constrains('dni')
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

    @api.constrains('dni', 'ruc', 'invoice_type')
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

    @api.multi
    def write(self, vals):
        """
        Al actualizar un partner, mapear DNI o RUC al campo VAT según el tipo de comprobante
        """
        for partner in self:
            partner._update_vat_field(vals)
        return super(ResPartner, self).write(vals)

    @api.onchange('invoice_type', 'dni', 'ruc', 'ruc_custom')
    def _onchange_document_fields(self):
        """
        Actualizar el campo VAT cuando cambian los documentos o el tipo de comprobante
        """
        vals = {}
        self._update_vat_field(vals)
        if 'vat' in vals:
            self.vat = vals['vat']

    def get_identification_number(self):
        """
        Helper method to get identification number with fallbacks.
        Returns the appropriate identification number based on invoice type and available fields.
        
        Returns:
            str: The identification number or empty string if none found
        """
        try:
            # First try based on invoice type
            if hasattr(self, 'invoice_type') and self.invoice_type == 'factura':
                # For factura, prefer RUC fields
                if hasattr(self, 'ruc') and self.ruc:
                    return self.ruc
                elif hasattr(self, 'ruc_custom') and self.ruc_custom:
                    return self.ruc_custom
            else:
                # For boleta or default, prefer DNI
                if hasattr(self, 'dni') and self.dni:
                    return self.dni
            
            # Fallback to standard Odoo VAT field
            if hasattr(self, 'vat') and self.vat:
                return self.vat
                
            # Check for Latin American identification if available
            if hasattr(self, 'l10n_latam_identification_type_id') and hasattr(self, 'vat'):
                if self.l10n_latam_identification_type_id and self.vat:
                    return self.vat
                    
            return ""
        except AttributeError:
            return ""

    def get_identification_type(self):
        """
        Helper method to get identification type.
        Returns the type of identification document.
        
        Returns:
            str: The identification type or 'unknown' if none found
        """
        try:
            # Check if we have invoice_type field
            if hasattr(self, 'invoice_type') and self.invoice_type:
                if self.invoice_type == 'factura':
                    return 'RUC'
                elif self.invoice_type == 'boleta':
                    return 'DNI'
            
            # Try to determine from available fields
            if hasattr(self, 'ruc') and self.ruc:
                return 'RUC'
            elif hasattr(self, 'ruc_custom') and self.ruc_custom:
                return 'RUC'
            elif hasattr(self, 'dni') and self.dni:
                return 'DNI'
            
            # Check for Latin American identification type if available
            if hasattr(self, 'l10n_latam_identification_type_id') and self.l10n_latam_identification_type_id:
                return self.l10n_latam_identification_type_id.name or 'VAT'
            
            # Fallback to VAT if available
            if hasattr(self, 'vat') and self.vat:
                return 'VAT'
                
            return 'unknown'
        except AttributeError:
            return 'unknown'

    def get_safe_identification_info(self):
        """
        Safe method to get identification information that handles missing attributes.
        Returns a formatted string with identification type and number.
        
        Returns:
            str: Formatted identification info or default message
        """
        try:
            identification_number = self.get_identification_number()
            identification_type = self.get_identification_type()
            
            if identification_number and identification_type != 'unknown':
                return f"{identification_type}: {identification_number}"
            elif identification_number:
                return f"ID: {identification_number}"
            else:
                return "No especificado"
        except Exception as e:
            # Log the error but don't raise it to avoid breaking the flow
            import logging
            _logger = logging.getLogger(__name__)
            _logger.warning(f"Error getting identification info for partner {self.id}: {e}")
            return "Error al obtener identificación"