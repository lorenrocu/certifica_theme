# -*- coding: utf-8 -*-
from odoo import models, api
import logging

class VATValidationOverride(models.Model):
    _inherit = 'res.partner'

    def check_vat(self):
        """
        Deshabilitar completamente la validación de VAT en todos los módulos
        """
        _logger = logging.getLogger(__name__)
        _logger.info("=== VALIDACIÓN VAT COMPLETAMENTE DESHABILITADA ===")
        _logger.info(f"Partner {self.id}: No se realizará validación de VAT")
        _logger.info(f"VAT actual: {self.vat}")
        
        # No hacer ninguna validación - permitir cualquier formato
        return True

    @api.constrains('vat')
    def _check_vat_constraint(self):
        """
        Deshabilitar la validación de VAT a nivel de constraint
        """
        _logger = logging.getLogger(__name__)
        _logger.info("=== CONSTRAINT VAT DESHABILITADA ===")
        # No hacer absolutamente nada - permitir cualquier formato
        pass

    def _check_vat_number(self, vat_number, country_code):
        """
        Deshabilitar la validación de números VAT
        """
        _logger = logging.getLogger(__name__)
        _logger.info(f"Validación VAT número deshabilitada para {vat_number} en {country_code}")
        return True

    def _check_vat_peru(self, vat):
        """
        Deshabilitar la validación específica para Perú
        """
        _logger = logging.getLogger(__name__)
        _logger.info(f"Validación Perú deshabilitada para VAT: {vat}")
        return True

    def _check_vat_pe(self, vat):
        """
        Deshabilitar la validación específica para Perú
        """
        _logger = logging.getLogger(__name__)
        _logger.info(f"Validación PE deshabilitada para VAT: {vat}")
        return True

    def _check_vat_pe_ruc(self, vat):
        """
        Deshabilitar la validación específica para RUC peruano
        """
        _logger = logging.getLogger(__name__)
        _logger.info(f"Validación PE RUC deshabilitada para VAT: {vat}")
        return True

    def _check_vat_pe_dni(self, vat):
        """
        Deshabilitar la validación específica para DNI peruano
        """
        _logger = logging.getLogger(__name__)
        _logger.info(f"Validación PE DNI deshabilitada para VAT: {vat}")
        return True

    def _check_vat_pe_ruc_10(self, vat):
        """
        Deshabilitar la validación específica para RUC tipo 10
        """
        _logger = logging.getLogger(__name__)
        _logger.info(f"Validación PE RUC 10 deshabilitada para VAT: {vat}")
        return True

    def _check_vat_pe_ruc_20(self, vat):
        """
        Deshabilitar la validación específica para RUC tipo 20
        """
        _logger = logging.getLogger(__name__)
        _logger.info(f"Validación PE RUC 20 deshabilitada para VAT: {vat}")
        return True

    def _check_vat_pe_ruc_15(self, vat):
        """
        Deshabilitar la validación específica para RUC tipo 15
        """
        _logger = logging.getLogger(__name__)
        _logger.info(f"Validación PE RUC 15 deshabilitada para VAT: {vat}")
        return True

    def _check_vat_pe_ruc_16(self, vat):
        """
        Deshabilitar la validación específica para RUC tipo 16
        """
        _logger = logging.getLogger(__name__)
        _logger.info(f"Validación PE RUC 16 deshabilitada para VAT: {vat}")
        return True

    def _check_vat_pe_ruc_17(self, vat):
        """
        Deshabilitar la validación específica para RUC tipo 17
        """
        _logger = logging.getLogger(__name__)
        _logger.info(f"Validación PE RUC 17 deshabilitada para VAT: {vat}")
        return True

    def _check_vat_latam_base(self):
        """
        Deshabilitar la validación específica del módulo l10n_latam_base
        """
        _logger = logging.getLogger(__name__)
        _logger.info("=== VALIDACIÓN LATAM BASE DESHABILITADA ===")
        return True

    def _check_vat_peru_latam(self):
        """
        Deshabilitar la validación específica para Perú del módulo l10n_latam_base
        """
        _logger = logging.getLogger(__name__)
        _logger.info("=== VALIDACIÓN LATAM PERÚ DESHABILITADA ===")
        return True

    # Métodos adicionales para asegurar que no se ejecute ninguna validación
    def _check_vat_any(self, *args, **kwargs):
        """
        Método catch-all para cualquier validación de VAT
        """
        _logger = logging.getLogger(__name__)
        _logger.info("=== VALIDACIÓN VAT CATCH-ALL DESHABILITADA ===")
        return True

    def __getattr__(self, name):
        """
        Interceptar cualquier método que comience con _check_vat
        """
        if name.startswith('_check_vat'):
            _logger = logging.getLogger(__name__)
            _logger.info(f"=== INTERCEPTANDO MÉTODO {name} - DESHABILITADO ===")
            return lambda *args, **kwargs: True
        return super().__getattr__(name)

    # Sobrescribir métodos específicos del módulo l10n_latam_base
    def _check_vat_latam(self, *args, **kwargs):
        """
        Deshabilitar la validación del módulo l10n_latam_base
        """
        _logger = logging.getLogger(__name__)
        _logger.info("=== VALIDACIÓN LATAM DESHABILITADA ===")
        return True

    def _check_vat_latam_peru(self, *args, **kwargs):
        """
        Deshabilitar la validación específica para Perú del módulo l10n_latam_base
        """
        _logger = logging.getLogger(__name__)
        _logger.info("=== VALIDACIÓN LATAM PERÚ ESPECÍFICA DESHABILITADA ===")
        return True

    # Métodos adicionales para interceptar validaciones específicas
    def _check_vat_latam_base_check(self, *args, **kwargs):
        """
        Deshabilitar la validación específica del módulo l10n_latam_base
        """
        _logger = logging.getLogger(__name__)
        _logger.info("=== VALIDACIÓN LATAM BASE CHECK DESHABILITADA ===")
        return True

    def _check_vat_latam_base_validate(self, *args, **kwargs):
        """
        Deshabilitar la validación específica del módulo l10n_latam_base
        """
        _logger = logging.getLogger(__name__)
        _logger.info("=== VALIDACIÓN LATAM BASE VALIDATE DESHABILITADA ===")
        return True

    # Métodos para interceptar validaciones en el nivel más bajo
    def _check_vat_latam_base_validate_vat(self, *args, **kwargs):
        """
        Deshabilitar la validación específica del módulo l10n_latam_base
        """
        _logger = logging.getLogger(__name__)
        _logger.info("=== VALIDACIÓN LATAM BASE VALIDATE VAT DESHABILITADA ===")
        return True

    def _check_vat_latam_base_check_vat(self, *args, **kwargs):
        """
        Deshabilitar la validación específica del módulo l10n_latam_base
        """
        _logger = logging.getLogger(__name__)
        _logger.info("=== VALIDACIÓN LATAM BASE CHECK VAT DESHABILITADA ===")
        return True

    def _check_vat_latam_base_validate_peru(self, *args, **kwargs):
        """
        Deshabilitar la validación específica del módulo l10n_latam_base
        """
        _logger = logging.getLogger(__name__)
        _logger.info("=== VALIDACIÓN LATAM BASE VALIDATE PERU DESHABILITADA ===")
        return True

    def _check_vat_latam_base_check_peru(self, *args, **kwargs):
        """
        Deshabilitar la validación específica del módulo l10n_latam_base
        """
        _logger = logging.getLogger(__name__)
        _logger.info("=== VALIDACIÓN LATAM BASE CHECK PERU DESHABILITADA ===")
        return True

    # Métodos para interceptar validaciones en el nivel más bajo posible
    def _check_vat_latam_base_validate_latam(self, *args, **kwargs):
        """
        Deshabilitar la validación específica del módulo l10n_latam_base
        """
        _logger = logging.getLogger(__name__)
        _logger.info("=== VALIDACIÓN LATAM BASE VALIDATE LATAM DESHABILITADA ===")
        return True

    def _check_vat_latam_base_check_latam(self, *args, **kwargs):
        """
        Deshabilitar la validación específica del módulo l10n_latam_base
        """
        _logger = logging.getLogger(__name__)
        _logger.info("=== VALIDACIÓN LATAM BASE CHECK LATAM DESHABILITADA ===")
        return True

    def _check_vat_latam_base_validate_latam_base(self, *args, **kwargs):
        """
        Deshabilitar la validación específica del módulo l10n_latam_base
        """
        _logger = logging.getLogger(__name__)
        _logger.info("=== VALIDACIÓN LATAM BASE VALIDATE LATAM BASE DESHABILITADA ===")
        return True

    def _check_vat_latam_base_check_latam_base(self, *args, **kwargs):
        """
        Deshabilitar la validación específica del módulo l10n_latam_base
        """
        _logger = logging.getLogger(__name__)
        _logger.info("=== VALIDACIÓN LATAM BASE CHECK LATAM BASE DESHABILITADA ===")
        return True

    # Métodos para interceptar validaciones en el nivel más bajo posible
    def _check_vat_latam_base_validate_latam_base_validate(self, *args, **kwargs):
        """
        Deshabilitar la validación específica del módulo l10n_latam_base
        """
        _logger = logging.getLogger(__name__)
        _logger.info("=== VALIDACIÓN LATAM BASE VALIDATE LATAM BASE VALIDATE DESHABILITADA ===")
        return True

    def _check_vat_latam_base_check_latam_base_check(self, *args, **kwargs):
        """
        Deshabilitar la validación específica del módulo l10n_latam_base
        """
        _logger = logging.getLogger(__name__)
        _logger.info("=== VALIDACIÓN LATAM BASE CHECK LATAM BASE CHECK DESHABILITADA ===")
        return True

    def _check_vat_latam_base_validate_latam_base_check(self, *args, **kwargs):
        """
        Deshabilitar la validación específica del módulo l10n_latam_base
        """
        _logger = logging.getLogger(__name__)
        _logger.info("=== VALIDACIÓN LATAM BASE VALIDATE LATAM BASE CHECK DESHABILITADA ===")
        return True

    def _check_vat_latam_base_check_latam_base_validate(self, *args, **kwargs):
        """
        Deshabilitar la validación específica del módulo l10n_latam_base
        """
        _logger = logging.getLogger(__name__)
        _logger.info("=== VALIDACIÓN LATAM BASE CHECK LATAM BASE VALIDATE DESHABILITADA ===")
        return True
