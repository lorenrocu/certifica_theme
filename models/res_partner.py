# -*- coding: utf-8 -*-
from odoo import models, api, fields
import logging

class ResPartner(models.Model):
    _inherit = 'res.partner'

    # Campo computado para el tipo de documento
    document_type = fields.Selection([
        ('dni', 'DNI'),
        ('ruc', 'RUC'),
        ('vat', 'VAT'),
        ('passport', 'Pasaporte'),
        ('foreign_id', 'Cédula Extranjera'),
        ('diplomatic', 'Carné de Identidad Diplomática'),
        ('non_domiciled', 'Documento de Identidad No Domiciliado')
    ], string='Tipo de Documento', compute='_compute_document_type', store=True, default='vat')

    # Campo computado para mostrar el tipo detectado
    document_type_detected = fields.Char(
        string='Tipo Detectado',
        compute='_compute_document_type_detected',
        store=False
    )

    @api.depends('vat')
    def _compute_document_type(self):
        """
        Computar automáticamente el tipo de documento basado en el VAT
        """
        for partner in self:
            if partner.vat:
                vat_clean = str(partner.vat).replace(' ', '').replace('-', '').replace('.', '')
                
                # Detectar DNI (8 dígitos)
                if len(vat_clean) == 8 and vat_clean.isdigit():
                    partner.document_type = 'dni'
                    _logger = logging.getLogger(__name__)
                    _logger.info(f"DNI detectado automáticamente: {vat_clean}")
                
                # Detectar RUC (11 dígitos)
                elif len(vat_clean) == 11 and vat_clean.isdigit():
                    partner.document_type = 'ruc'
                    _logger = logging.getLogger(__name__)
                    _logger.info(f"RUC detectado automáticamente: {vat_clean}")
                
                # Si no coincide con DNI o RUC, mantener VAT
                else:
                    partner.document_type = 'vat'
                    _logger = logging.getLogger(__name__)
                    _logger.info(f"Tipo de documento no reconocido, usando VAT: {vat_clean}")
            else:
                partner.document_type = 'vat'

    @api.depends('document_type')
    def _compute_document_type_detected(self):
        """
        Computar el texto del tipo detectado para mostrar en la interfaz
        """
        for partner in self:
            if partner.document_type == 'dni':
                partner.document_type_detected = 'DNI Detectado'
            elif partner.document_type == 'ruc':
                partner.document_type_detected = 'RUC Detectado'
            elif partner.document_type == 'vat':
                partner.document_type_detected = 'VAT Genérico'
            else:
                partner.document_type_detected = partner.document_type.title()

    @api.onchange('vat')
    def _onchange_vat_document_type(self):
        """
        Actualizar el tipo de documento cuando cambie el VAT
        """
        if self.vat:
            self._compute_document_type()

    def create(self, vals):
        """
        Al crear, mapear dni o ruc a vat y detectar tipo de documento
        """
        if 'dni' in vals and vals['dni']:
            # Formatear DNI para VAT (agregar prefijo 10)
            dni = str(vals['dni']).strip()
            if len(dni) == 8 and dni.isdigit():
                vals['vat'] = f"10{dni}"
                _logger = logging.getLogger(__name__)
                _logger.info(f"DNI {dni} mapeado a VAT: {vals['vat']}")
        
        elif 'ruc' in vals and vals['ruc']:
            # Formatear RUC para VAT
            ruc = str(vals['ruc']).strip()
            if len(ruc) == 11 and ruc.isdigit():
                # Verificar si ya tiene prefijo válido
                if ruc.startswith(('10', '20', '15', '16', '17')):
                    vals['vat'] = ruc
                else:
                    # Agregar prefijo 20 si no tiene uno válido
                    vals['vat'] = f"20{ruc[1:]}" if len(ruc) == 11 else ruc
                _logger = logging.getLogger(__name__)
                _logger.info(f"RUC {ruc} mapeado a VAT: {vals['vat']}")
        
        # Computar el tipo de documento
        if 'vat' in vals:
            # Crear un partner temporal para computar el tipo
            temp_partner = self.new({'vat': vals['vat']})
            temp_partner._compute_document_type()
            vals['document_type'] = temp_partner.document_type
        
        return super().create(vals)

    def write(self, vals):
        """
        Al escribir, mapear dni o ruc a vat y detectar tipo de documento
        """
        if 'dni' in vals and vals['dni']:
            # Formatear DNI para VAT (agregar prefijo 10)
            dni = str(vals['dni']).strip()
            if len(dni) == 8 and dni.isdigit():
                vals['vat'] = f"10{dni}"
                _logger = logging.getLogger(__name__)
                _logger.info(f"DNI {dni} mapeado a VAT: {vals['vat']}")
        
        elif 'ruc' in vals and vals['ruc']:
            # Formatear RUC para VAT
            ruc = str(vals['ruc']).strip()
            if len(ruc) == 11 and ruc.isdigit():
                # Verificar si ya tiene prefijo válido
                if ruc.startswith(('10', '20', '15', '16', '17')):
                    vals['vat'] = ruc
                else:
                    # Agregar prefijo 20 si no tiene uno válido
                    vals['vat'] = f"20{ruc[1:]}" if len(ruc) == 11 else ruc
                _logger = logging.getLogger(__name__)
                _logger.info(f"RUC {ruc} mapeado a VAT: {vals['vat']}")
        
        # Computar el tipo de documento si cambió el VAT
        if 'vat' in vals:
            # Crear un partner temporal para computar el tipo
            temp_partner = self.new({'vat': vals['vat']})
            temp_partner._compute_document_type()
            vals['document_type'] = temp_partner.document_type
        
        return super().write(vals)

    @api.constrains('vat')
    def _check_vat(self):
        """
        Deshabilitar la validación de VAT
        """
        _logger = logging.getLogger(__name__)
        _logger.info("=== VALIDACIÓN VAT DESHABILITADA ===")
        _logger.info("No se realizará ninguna validación de formato VAT")
        # No hacer absolutamente nada - permitir cualquier formato
        pass