# -*- coding: utf-8 -*-
"""
Modelo para deshabilitar completamente todas las validaciones de backend
Asegura que todas las validaciones se manejen exclusivamente en el frontend
"""

from odoo import models, api, fields
import logging

_logger = logging.getLogger(__name__)

class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    @api.constrains('vat')
    def check_vat(self):
        """
        Override para deshabilitar completamente la validación de VAT/RUC
        """
        _logger.info("🚫 VALIDACIÓN VAT DESHABILITADA - Frontend maneja validación")
        return True
    
    @api.constrains('email')
    def _check_email(self):
        """
        Override para deshabilitar validación de email
        """
        _logger.info("🚫 VALIDACIÓN EMAIL DESHABILITADA - Frontend maneja validación")
        return True
    
    @api.constrains('phone')
    def _check_phone(self):
        """
        Override para deshabilitar validación de teléfono
        """
        _logger.info("🚫 VALIDACIÓN TELÉFONO DESHABILITADA - Frontend maneja validación")
        return True
    
    def _validate_fields(self, field_names, excluded=None):
        """
        Override para deshabilitar todas las validaciones de campos
        """
        _logger.info(f"🚫 VALIDACIONES DE CAMPOS DESHABILITADAS: {field_names}")
        _logger.info("✅ Frontend maneja todas las validaciones")
        return True
    
    @api.model
    def _check_vat_pe(self, vat):
        """
        Override para deshabilitar validación específica de RUC peruano
        """
        _logger.info(f"🚫 VALIDACIÓN RUC PERUANO DESHABILITADA: {vat}")
        return True
    
    def _run_vat_test(self, vat_country, vat_number, vat_no):
        """
        Override para deshabilitar todas las pruebas de VAT
        """
        _logger.info(f"🚫 PRUEBAS VAT DESHABILITADAS: {vat_country}-{vat_number}")
        return True

class L10nLatamIdentificationType(models.Model):
    _inherit = 'l10n_latam.identification.type'
    
    @api.constrains('name')
    def _check_name(self):
        """
        Deshabilitar validaciones de tipo de identificación
        """
        _logger.info("🚫 VALIDACIÓN TIPO IDENTIFICACIÓN DESHABILITADA")
        return True

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    def _check_cart_access(self):
        """
        Override para deshabilitar validaciones de acceso al carrito
        """
        _logger.info("🚫 VALIDACIONES DE CARRITO DESHABILITADAS")
        return True
    
    @api.constrains('partner_id')
    def _check_partner_id(self):
        """
        Deshabilitar validaciones de partner en órdenes de venta
        """
        _logger.info("🚫 VALIDACIÓN PARTNER EN SALE ORDER DESHABILITADA")
        return True

class WebsiteSaleController(models.AbstractModel):
    _name = 'website.sale.validation.disable'
    _description = 'Deshabilita validaciones de Website Sale'
    
    @api.model
    def disable_all_validations(self):
        """
        Método para confirmar que todas las validaciones están deshabilitadas
        """
        disabled_validations = [
            'VAT/RUC validation',
            'Email format validation', 
            'Phone format validation',
            'Required fields validation',
            'Address completeness validation',
            'Country/State validation',
            'Postal code validation',
            'Partner access validation',
            'Cart access validation',
            'L10n Peru identification validation'
        ]
        
        _logger.info("🚫 TODAS LAS VALIDACIONES DE BACKEND DESHABILITADAS:")
        for validation in disabled_validations:
            _logger.info(f"  - ❌ {validation}")
        
        _logger.info("✅ FRONTEND MANEJA TODAS LAS VALIDACIONES EXCLUSIVAMENTE")
        return True
