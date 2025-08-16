# -*- coding: utf-8 -*-
from odoo import models, api
import logging

class ResPartnerVATOverride(models.Model):
    _inherit = 'res.partner'

    @api.constrains('vat')
    def _check_vat(self):
        """
        Completamente deshabilitar la validación de VAT
        """
        _logger = logging.getLogger(__name__)
        _logger.info("=== VALIDACIÓN VAT DESHABILITADA ===")
        _logger.info("No se realizará ninguna validación de formato VAT")
        # No hacer absolutamente nada - permitir cualquier formato
        pass

    def check_vat(self):
        """
        Deshabilitar completamente la validación de VAT del módulo base_vat
        """
        _logger = logging.getLogger(__name__)
        _logger.info("=== MÉTODO CHECK_VAT DESHABILITADO ===")
        _logger.info(f"Partner {self.id}: No se realizará validación de VAT")
        _logger.info(f"VAT actual: {self.vat}")
        
        # No hacer ninguna validación - permitir cualquier formato
        return True

    def _check_vat_number(self, vat_number, country_code):
        """
        Sobrescribir el método de validación de números VAT
        """
        _logger = logging.getLogger(__name__)
        _logger.info(f"Validación VAT deshabilitada para {vat_number} en {country_code}")
        # Siempre retornar True - no validar nada
        return True

    def _check_vat_peru(self, vat):
        """
        Validación personalizada para Perú que permite cualquier formato
        """
        _logger = logging.getLogger(__name__)
        _logger.info(f"Validación Perú deshabilitada para VAT: {vat}")
        # Permitir cualquier formato
        return True

    def _check_vat_pe(self, vat):
        """
        Validación específica para Perú - permitir cualquier formato
        """
        _logger = logging.getLogger(__name__)
        _logger.info(f"Validación PE deshabilitada para VAT: {vat}")
        # Permitir cualquier formato
        return True

    def _check_vat_pe_ruc(self, vat):
        """
        Validación específica para RUC peruano - permitir cualquier formato
        """
        _logger = logging.getLogger(__name__)
        _logger.info(f"Validación PE RUC deshabilitada para VAT: {vat}")
        # Permitir cualquier formato
        return True

    def _check_vat_pe_dni(self, vat):
        """
        Validación específica para DNI peruano - permitir cualquier formato
        """
        _logger = logging.getLogger(__name__)
        _logger.info(f"Validación PE DNI deshabilitada para VAT: {vat}")
        # Permitir cualquier formato
        return True

    def _check_vat_pe_ruc_10(self, vat):
        """
        Validación específica para RUC tipo 10 - permitir cualquier formato
        """
        _logger = logging.getLogger(__name__)
        _logger.info(f"Validación PE RUC 10 deshabilitada para VAT: {vat}")
        # Permitir cualquier formato
        return True

    def _check_vat_pe_ruc_20(self, vat):
        """
        Validación específica para RUC tipo 20 - permitir cualquier formato
        """
        _logger = logging.getLogger(__name__)
        _logger.info(f"Validación PE RUC 20 deshabilitada para VAT: {vat}")
        # Permitir cualquier formato
        return True

    def _check_vat_pe_ruc_15(self, vat):
        """
        Validación específica para RUC tipo 15 - permitir cualquier formato
        """
        _logger = logging.getLogger(__name__)
        _logger.info(f"Validación PE RUC 15 deshabilitada para VAT: {vat}")
        # Permitir cualquier formato
        return True

    def _check_vat_pe_ruc_16(self, vat):
        """
        Validación específica para RUC tipo 16 - permitir cualquier formato
        """
        _logger = logging.getLogger(__name__)
        _logger.info(f"Validación PE RUC 16 deshabilitada para VAT: {vat}")
        # Permitir cualquier formato
        return True

    def _check_vat_pe_ruc_17(self, vat):
        """
        Validación específica para RUC tipo 17 - permitir cualquier formato
        """
        _logger = logging.getLogger(__name__)
        _logger.info(f"Validación PE RUC 17 deshabilitada para VAT: {vat}")
        # Permitir cualquier formato
        return True
