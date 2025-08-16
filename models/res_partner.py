# -*- coding: utf-8 -*-
from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class ResPartner(models.Model):
    _inherit = 'res.partner'

    def _get_identification_type_from_vat(self, vat_number):
        """
        Obtener el ID del tipo de identificación basándose en el número VAT
        """
        if not vat_number:
            return False
        
        vat_clean = str(vat_number).strip()
        _logger.info(f"=== DETECTANDO TIPO DE IDENTIFICACIÓN PARA: {vat_clean} ===")
        
        try:
            # Verificar si el modelo está disponible
            if 'l10n.latam.identification.type' not in self.env.registry:
                _logger.warning("Modelo l10n.latam.identification.type no disponible")
                return False
            
            # Buscar el tipo de identificación en la base de datos
            identification_type_model = self.env['l10n.latam.identification.type']
            
            # Detectar DNI (8 dígitos) - ID 5 en tu base de datos
            if len(vat_clean) == 8 and vat_clean.isdigit():
                dni_type = identification_type_model.search([
                    ('name', '=', 'DNI'),
                    ('country_id', '=', 173)  # Perú
                ], limit=1)
                if dni_type:
                    _logger.info(f"DNI detectado: {vat_clean} -> Tipo ID: {dni_type.id}")
                    return dni_type.id
                else:
                    _logger.warning("No se encontró el tipo DNI en la base de datos")
                    return False
            
            # Detectar RUC (11 dígitos) - ID 4 en tu base de datos
            elif len(vat_clean) == 11 and vat_clean.isdigit():
                ruc_type = identification_type_model.search([
                    ('name', '=', 'RUC'),
                    ('country_id', '=', 173)  # Perú
                ], limit=1)
                if ruc_type:
                    _logger.info(f"RUC detectado: {vat_clean} -> Tipo ID: {ruc_type.id}")
                    return ruc_type.id
                else:
                    _logger.warning("No se encontró el tipo RUC en la base de datos")
                    return False
            
            # Detectar VAT con prefijos peruanos (10 dígitos)
            elif len(vat_clean) == 10 and vat_clean.startswith(('10', '20', '15', '16', '17')):
                ruc_type = identification_type_model.search([
                    ('name', '=', 'RUC'),
                    ('country_id', '=', 173)  # Perú
                ], limit=1)
                if ruc_type:
                    _logger.info(f"RUC con prefijo detectado: {vat_clean} -> Tipo ID: {ruc_type.id}")
                    return ruc_type.id
                else:
                    _logger.warning("No se encontró el tipo RUC en la base de datos")
                    return False
            
            # Detectar DNI con prefijo 10 (10 dígitos)
            elif len(vat_clean) == 10 and vat_clean.startswith('10'):
                dni_type = identification_type_model.search([
                    ('name', '=', 'DNI'),
                    ('country_id', '=', 173)  # Perú
                ], limit=1)
                if dni_type:
                    _logger.info(f"DNI con prefijo 10 detectado: {vat_clean} -> Tipo ID: {dni_type.id}")
                    return dni_type.id
                else:
                    _logger.warning("No se encontró el tipo DNI en la base de datos")
                    return False
            
            # Otros casos - usar VAT genérico
            else:
                vat_type = identification_type_model.search([
                    ('name', '=', 'VAT'),
                    ('country_id', '=', 173)  # Perú
                ], limit=1)
                if vat_type:
                    _logger.info(f"VAT genérico detectado: {vat_clean} -> Tipo ID: {vat_type.id}")
                    return vat_type.id
                else:
                    _logger.warning("No se encontró el tipo VAT en la base de datos")
                    return False
                    
        except Exception as e:
            _logger.error(f"Error al detectar tipo de identificación: {e}")
            return False

    @api.onchange('vat')
    def _onchange_vat_auto_identification_type(self):
        """
        Cambiar automáticamente el tipo de identificación cuando cambie el VAT
        """
        if self.vat:
            identification_type_id = self._get_identification_type_from_vat(self.vat)
            if identification_type_id:
                self.l10n_latam_identification_type_id = identification_type_id
                _logger.info(f"Tipo de identificación actualizado automáticamente a ID: {identification_type_id}")

    @api.model
    def create(self, vals):
        """
        Crear partner con detección automática del tipo de identificación
        """
        _logger.info("=== CREATE PARTNER ===")
        _logger.info(f"Valores recibidos: {vals}")
        
        # Extraer DNI y RUC si existen
        dni = vals.get('dni', '')
        ruc = vals.get('ruc', '')
        
        _logger.info(f"DNI extraído: '{dni}'")
        _logger.info(f"RUC extraído: '{ruc}'")
        
        # Si no hay VAT pero hay DNI o RUC, usar el que corresponda
        if 'vat' not in vals or not vals['vat']:
            if dni:
                vals['vat'] = dni
                _logger.info(f"DNI detectado: {dni}")
            elif ruc:
                vals['vat'] = ruc
                _logger.info(f"RUC detectado: {ruc}")
        
        # Detectar automáticamente el tipo de identificación
        if 'vat' in vals and vals['vat']:
            identification_type_id = self._get_identification_type_from_vat(vals['vat'])
            if identification_type_id:
                vals['l10n_latam_identification_type_id'] = identification_type_id
                _logger.info(f"Tipo de identificación detectado: {identification_type_id}")
        
        _logger.info(f"Valores finales antes de crear: {vals}")
        
        # Llamar al método original
        return super().create(vals)

    def write(self, vals):
        """
        Actualizar partner con detección automática del tipo de identificación
        """
        _logger.info("=== WRITE PARTNER ===")
        _logger.info(f"Valores recibidos: {vals}")
        
        # Si se está actualizando el VAT, detectar automáticamente el tipo
        if 'vat' in vals and vals['vat']:
            identification_type_id = self._get_identification_type_from_vat(vals['vat'])
            if identification_type_id:
                vals['l10n_latam_identification_type_id'] = identification_type_id
                _logger.info(f"Tipo de identificación detectado: {identification_type_id}")
        
        # Llamar al método original
        return super().write(vals)

    # Métodos para deshabilitar validación de VAT
    def check_vat(self, vat):
        """
        Sobrescribir validación de VAT para permitir cualquier formato
        """
        _logger.info(f"=== CHECK VAT OVERRIDE === {vat}")
        return True

    @api.constrains('vat')
    def _check_vat_constraint(self):
        """
        Sobrescribir constraint de VAT para no validar nada
        """
        _logger.info("=== VAT CONSTRAINT OVERRIDE ===")
        pass