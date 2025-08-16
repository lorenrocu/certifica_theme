# -*- coding: utf-8 -*-
from odoo import models, api
import logging

class VATMonkeyPatch(models.Model):
    _inherit = 'res.partner'

    @api.model
    def _patch_vat_validation(self):
        """
        Aplicar monkey patch para deshabilitar toda validación de VAT
        """
        _logger = logging.getLogger(__name__)
        _logger.info("=== APLICANDO MONKEY PATCH PARA VAT ===")
        
        # Monkey patch del método check_vat
        def patched_check_vat(self):
            _logger.info(f"=== MONKEY PATCH: check_vat deshabilitado para partner {self.id} ===")
            _logger.info(f"VAT: {self.vat}")
            return True
        
        # Aplicar el patch
        models.Model.check_vat = patched_check_vat
        _logger.info("=== MONKEY PATCH APLICADO EXITOSAMENTE ===")

    @api.model
    def create(self, vals):
        """
        Aplicar monkey patch antes de crear
        """
        if not hasattr(self, '_vat_patch_applied'):
            self._patch_vat_validation()
            self._vat_patch_applied = True
        
        return super().create(vals)

    def write(self, vals):
        """
        Aplicar monkey patch antes de escribir
        """
        if not hasattr(self, '_vat_patch_applied'):
            self._patch_vat_validation()
            self._vat_patch_applied = True
        
        return super().write(vals)

    def check_vat(self):
        """
        Método sobrescrito que siempre retorna True
        """
        _logger = logging.getLogger(__name__)
        _logger.info("=== MÉTODO CHECK_VAT SOBRESCRITO - DESHABILITADO ===")
        return True

    @api.constrains('vat')
    def _check_vat_constraint(self):
        """
        Constraint sobrescrito que no hace nada
        """
        _logger = logging.getLogger(__name__)
        _logger.info("=== CONSTRAINT VAT SOBRESCRITO - DESHABILITADO ===")
        pass
