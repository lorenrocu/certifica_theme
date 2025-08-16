# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError
import logging

class ResPartner(models.Model):
    _inherit = 'res.partner'

    # Campo personalizado para tipo de identificación
    identification_type = fields.Selection([
        ('dni', 'DNI'),
        ('ruc', 'RUC'),
        ('vat', 'VAT'),
        ('passport', 'Pasaporte'),
        ('foreign_id', 'Cédula Extranjera'),
        ('diplomatic', 'Carné Diplomático'),
        ('non_domiciled', 'Documento de No Domiciliado'),
    ], string='Tipo de Identificación', default='vat', help='Tipo de documento de identificación')

    @api.onchange('vat')
    def _onchange_vat_auto_identification_type(self):
        """
        Detectar automáticamente el tipo de identificación basándose en el VAT
        """
        if self.vat:
            vat_clean = str(self.vat).strip()
            _logger = logging.getLogger(__name__)
            _logger.info(f"=== DETECTANDO TIPO DE IDENTIFICACIÓN PARA: {vat_clean} ===")
            
            # Detectar automáticamente el tipo
            identification_type = self._get_identification_type_from_vat(vat_clean)
            
            if identification_type:
                self.identification_type = identification_type
                _logger.info(f"Tipo de identificación detectado: {identification_type}")
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
        
        # Detectar DNI (8 dígitos)
        if len(vat_clean) == 8 and vat_clean.isdigit():
            _logger.info(f"DNI detectado: {vat_clean}")
            return 'dni'
        
        # Detectar RUC (11 dígitos)
        elif len(vat_clean) == 11 and vat_clean.isdigit():
            _logger.info(f"RUC detectado: {vat_clean}")
            return 'ruc'
        
        # Detectar VAT con prefijos peruanos (10 dígitos)
        elif len(vat_clean) == 10 and vat_clean.startswith(('10', '20', '15', '16', '17')):
            _logger.info(f"RUC con prefijo detectado: {vat_clean}")
            return 'ruc'
        
        # Detectar DNI con prefijo 10 (10 dígitos)
        elif len(vat_clean) == 10 and vat_clean.startswith('10'):
            _logger.info(f"DNI con prefijo 10 detectado: {vat_clean}")
            return 'dni'
        
        # Otros casos
        else:
            _logger.info(f"VAT genérico detectado: {vat_clean}")
            return 'vat'

    @api.model
    def create(self, vals):
        """
        Al crear un partner, mapear DNI o RUC al campo VAT y detectar tipo automáticamente
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
        
        # Detectar tipo de identificación automáticamente si hay VAT
        if 'vat' in vals and vals['vat']:
            identification_type = self._get_identification_type_from_vat(vals['vat'])
            if identification_type:
                vals['identification_type'] = identification_type
                _logger.info(f"Tipo de identificación detectado: {identification_type}")
        
        _logger.info(f"Valores finales antes de crear: {vals}")
        
        # Llamar al método create del modelo padre
        return super().create(vals)

    def write(self, vals):
        """
        Al escribir, mapear DNI o RUC al campo VAT y detectar tipo automáticamente
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
        
        # Detectar tipo de identificación automáticamente si hay VAT
        if 'vat' in vals and vals['vat']:
            identification_type = self._get_identification_type_from_vat(vals['vat'])
            if identification_type:
                vals['identification_type'] = identification_type
                _logger.info(f"Tipo de identificación detectado: {identification_type}")
        
        _logger.info(f"Valores finales antes de escribir: {vals}")
        
        # Llamar al método write del modelo padre
        return super().write(vals)

    def get_identification_type_display(self):
        """
        Obtener el tipo de identificación para mostrar en la interfaz
        """
        type_mapping = {
            'dni': 'DNI',
            'ruc': 'RUC',
            'vat': 'VAT',
            'passport': 'Pasaporte',
            'foreign_id': 'Cédula Extranjera',
            'diplomatic': 'Carné Diplomático',
            'non_domiciled': 'Documento de No Domiciliado',
        }
        return type_mapping.get(self.identification_type, 'VAT')