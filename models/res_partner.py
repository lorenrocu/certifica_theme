# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError
import logging

class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.onchange('vat')
    def _onchange_vat_auto_identification_type(self):
        """
        Detectar automáticamente el tipo de identificación basándose en el VAT
        y actualizar el campo l10n_latam_identification_type_id
        """
        if self.vat:
            vat_clean = str(self.vat).strip()
            _logger = logging.getLogger(__name__)
            _logger.info(f"=== DETECTANDO TIPO DE IDENTIFICACIÓN PARA: {vat_clean} ===")
            
            # Buscar el tipo de identificación correspondiente
            identification_type = self._get_identification_type_from_vat(vat_clean)
            
            if identification_type:
                self.l10n_latam_identification_type_id = identification_type
                _logger.info(f"Tipo de identificación detectado: {identification_type.name}")
            else:
                _logger.info("No se pudo detectar el tipo de identificación automáticamente")

    def _get_identification_type_from_vat(self, vat_number):
        """
        Obtener el tipo de identificación basándose en el número VAT
        """
        if not vat_number:
            return False
        
        vat_clean = str(vat_number).strip()
        _logger = logging.getLogger(__name__)
        
        try:
            # Buscar tipos de identificación disponibles
            identification_types = self.env['l10n_latam.identification.type'].search([
                ('active', '=', True)
            ])
            
            _logger.info(f"Tipos de identificación disponibles: {identification_types.mapped('name')}")
            
            # Detectar DNI (8 dígitos)
            if len(vat_clean) == 8 and vat_clean.isdigit():
                dni_type = identification_types.filtered(lambda x: x.name.lower() == 'dni')
                if dni_type:
                    _logger.info(f"DNI detectado: {vat_clean} -> {dni_type[0].name}")
                    return dni_type[0]
            
            # Detectar RUC (11 dígitos)
            elif len(vat_clean) == 11 and vat_clean.isdigit():
                ruc_type = identification_types.filtered(lambda x: x.name.lower() == 'ruc')
                if ruc_type:
                    _logger.info(f"RUC detectado: {vat_clean} -> {ruc_type[0].name}")
                    return ruc_type[0]
            
            # Detectar VAT con prefijos peruanos (10 dígitos)
            elif len(vat_clean) == 10 and vat_clean.startswith(('10', '20', '15', '16', '17')):
                ruc_type = identification_types.filtered(lambda x: x.name.lower() == 'ruc')
                if ruc_type:
                    _logger.info(f"RUC con prefijo detectado: {vat_clean} -> {ruc_type[0].name}")
                    return ruc_type[0]
            
            # Detectar DNI con prefijo 10 (10 dígitos)
            elif len(vat_clean) == 10 and vat_clean.startswith('10'):
                dni_type = identification_types.filtered(lambda x: x.name.lower() == 'dni')
                if dni_type:
                    _logger.info(f"DNI con prefijo 10 detectado: {vat_clean} -> {dni_type[0].name}")
                    return dni_type[0]
            
            # Buscar tipo de identificación fiscal por defecto
            default_type = identification_types.filtered(lambda x: x.is_vat)
            if default_type:
                _logger.info(f"Usando tipo de identificación fiscal por defecto: {default_type[0].name}")
                return default_type[0]
            
            _logger.info("No se pudo determinar el tipo de identificación")
            return False
            
        except Exception as e:
            _logger.error(f"Error al buscar tipos de identificación: {e}")
            return False

    @api.model
    def create(self, vals):
        """
        Al crear, detectar automáticamente el tipo de identificación
        """
        if 'vat' in vals and vals['vat']:
            # Detectar tipo de identificación
            identification_type = self._get_identification_type_from_vat(vals['vat'])
            if identification_type:
                vals['l10n_latam_identification_type_id'] = identification_type.id
        
        return super().create(vals)

    def write(self, vals):
        """
        Al escribir, detectar automáticamente el tipo de identificación
        """
        if 'vat' in vals and vals['vat']:
            # Detectar tipo de identificación
            identification_type = self._get_identification_type_from_vat(vals['vat'])
            if identification_type:
                vals['l10n_latam_identification_type_id'] = identification_type.id
        
        return super().write(vals)

    def get_identification_type_display(self):
        """
        Obtener el tipo de identificación para mostrar en la interfaz
        """
        if self.l10n_latam_identification_type_id:
            return self.l10n_latam_identification_type_id.name
        return 'VAT'

    @api.model
    def create(self, vals):
        """
        Al crear un partner, mapear DNI o RUC al campo VAT
        """
        
        _logger = logging.getLogger(__name__)
        _logger.info("=== CREATE PARTNER ===")
        _logger.info(f"Valores recibidos: {vals}")
        
        # Obtener valores de DNI y RUC si existen
        dni = vals.get('dni', '').strip() if vals.get('dni') else ''
        ruc = vals.get('ruc', '').strip() if vals.get('ruc') else ''
        
        _logger.info(f"DNI extraído: '{dni}'")
        _logger.info(f"RUC extraído: '{ruc}'")
        
        # Mapear DNI o RUC al campo VAT
        if dni:
            # Si es DNI de 8 dígitos, agregar prefijo 10
            if len(dni) == 8 and dni.isdigit():
                vals['vat'] = '10' + dni
                _logger.info(f"DNI mapeado a VAT con prefijo 10: {vals['vat']}")
            else:
                vals['vat'] = dni
                _logger.info(f"DNI mapeado a VAT: {vals['vat']}")
        
        elif ruc:
            # Verificar si el RUC ya tiene el prefijo correcto
            if len(ruc) == 11 and ruc.isdigit():
                # Si es RUC de 11 dígitos, verificar prefijos válidos
                valid_prefixes = ['10', '20', '15', '16', '17']
                if not any(ruc.startswith(prefix) for prefix in valid_prefixes):
                    # Si no tiene prefijo válido, agregar 20 por defecto
                    vals['vat'] = '20' + ruc
                    _logger.info(f"RUC mapeado a VAT con prefijo 20: {vals['vat']}")
                else:
                    vals['vat'] = ruc
                    _logger.info(f"RUC mapeado a VAT (ya tiene prefijo válido): {vals['vat']}")
            else:
                vals['vat'] = ruc
                _logger.info(f"RUC mapeado a VAT: {vals['vat']}")
        
        _logger.info(f"Valores finales antes de crear: {vals}")
        
        # Llamar al método create del modelo padre
        return super().create(vals)

    def write(self, vals):
        """
        Al escribir, mapear DNI o RUC al campo VAT
        """
        _logger = logging.getLogger(__name__)
        _logger.info("=== WRITE PARTNER ===")
        _logger.info(f"Valores recibidos: {vals}")
        _logger.info(f"Partner actual: {self}")
        _logger.info(f"VAT actual: {self.vat}")
        
        # Obtener valores de DNI y RUC si existen
        dni = vals.get('dni', '').strip() if vals.get('dni') else ''
        ruc = vals.get('ruc', '').strip() if vals.get('ruc') else ''
        
        _logger.info(f"DNI extraído: '{dni}'")
        _logger.info(f"RUC extraído: '{ruc}'")
        
        # Mapear DNI o RUC al campo VAT
        if dni:
            # Si es DNI de 8 dígitos, agregar prefijo 10
            if len(dni) == 8 and dni.isdigit():
                vals['vat'] = '10' + dni
                _logger.info(f"DNI mapeado a VAT con prefijo 10: {vals['vat']}")
            else:
                vals['vat'] = dni
                _logger.info(f"DNI mapeado a VAT: {vals['vat']}")
        
        elif ruc:
            # Verificar si el RUC ya tiene el prefijo correcto
            if len(ruc) == 11 and ruc.isdigit():
                # Si es RUC de 11 dígitos, verificar prefijos válidos
                valid_prefixes = ['10', '20', '15', '16', '17']
                if not any(ruc.startswith(prefix) for prefix in valid_prefixes):
                    # Si no tiene prefijo válido, agregar 20 por defecto
                    vals['vat'] = '20' + ruc
                    _logger.info(f"RUC mapeado a VAT con prefijo 20: {vals['vat']}")
                else:
                    vals['vat'] = ruc
                    _logger.info(f"RUC mapeado a VAT (ya tiene prefijo válido): {vals['vat']}")
            else:
                vals['vat'] = ruc
                _logger.info(f"RUC mapeado a VAT: {vals['vat']}")
        
        _logger.info(f"Valores finales antes de escribir: {vals}")
        
        # Llamar al método write del modelo padre
        return super().write(vals)