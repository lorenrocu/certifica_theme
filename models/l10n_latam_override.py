# -*- coding: utf-8 -*-
from odoo import models, api
import logging

class ResPartnerLatamOverride(models.Model):
    _inherit = 'res.partner'

    def check_vat(self):
        """
        Deshabilitar completamente la validación de VAT del módulo l10n_latam_base
        """
        _logger = logging.getLogger(__name__)
        _logger.info("=== VALIDACIÓN LATAM VAT DESHABILITADA ===")
        _logger.info(f"Partner {self.id}: No se realizará validación de VAT")
        _logger.info(f"VAT actual: {self.vat}")
        
        # No hacer ninguna validación - permitir cualquier formato
        return True

    @api.constrains('vat')
    def _check_vat_latam(self):
        """
        Deshabilitar la validación de VAT del módulo l10n_latam_base
        """
        _logger = logging.getLogger(__name__)
        _logger.info("=== CONSTRAINT LATAM VAT DESHABILITADA ===")
        _logger.info("No se realizará ninguna validación de formato VAT")
        # No hacer absolutamente nada - permitir cualquier formato
        pass

    def _check_vat_latam_base(self):
        """
        Deshabilitar la validación específica del módulo l10n_latam_base
        """
        _logger = logging.getLogger(__name__)
        _logger.info("=== VALIDACIÓN LATAM BASE DESHABILITADA ===")
        # No hacer ninguna validación
        return True

    def _check_vat_peru_latam(self):
        """
        Deshabilitar la validación específica para Perú del módulo l10n_latam_base
        """
        _logger = logging.getLogger(__name__)
        _logger.info("=== VALIDACIÓN LATAM PERÚ DESHABILITADA ===")
        # No hacer ninguna validación
        return True
