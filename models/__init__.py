# -*- coding: utf-8 -*-

# Importar todos los modelos personalizados
from . import res_partner
from . import base_vat_override
from . import l10n_latam_override
from . import vat_validation_override
from . import vat_monkey_patch
from . import website_sale_validation_override
from . import payment_validation_override
from . import sale_validation_override
from . import website_sale_error_handler
from . import website_sale_template_handler
from . import cart_summary_error_fix
from . import auto_cart_summary_fix
from . import safe_cart_summary_fix
from . import disable_aggressive_fixes

# Ejecutar SOLO corrección MÍNIMA y SEGURA al cargar el módulo
def _minimal_safe_fix_on_module_load():
    """
    Ejecutar SOLO corrección MÍNIMA y SEGURA - PROTEGIENDO LISTAS DE PRECIOS EXISTENTES
    """
    try:
        import logging
        _logger = logging.getLogger(__name__)
        _logger.info("=== MÓDULO CERTIFICA_THEME CARGADO - SOLO CORRECCIÓN MÍNIMA Y SEGURA ===")
        _logger.info("⚠️ CORRECCIONES AGRESIVAS DESACTIVADAS - LISTAS DE PRECIOS PROTEGIDAS")
        
        # Importar el modelo después de que esté disponible
        from odoo import api, SUPERUSER_ID
        env = api.Environment(cr, SUPERUSER_ID, {})
        
        # Desactivar correcciones agresivas
        sale_order_model = env['sale.order']
        if hasattr(sale_order_model, '_disable_aggressive_fixes'):
            sale_order_model._disable_aggressive_fixes()
            _logger.info("✅ Correcciones agresivas desactivadas")
        
        # Ejecutar SOLO corrección mínima y segura
        if hasattr(sale_order_model, '_emergency_cart_summary_fix_disabled'):
            result = sale_order_model._emergency_cart_summary_fix_disabled()
            if result:
                _logger.info("✅ Corrección MÍNIMA completada - LISTAS DE PRECIOS PROTEGIDAS")
            else:
                _logger.warning("⚠️ Corrección MÍNIMA completada pero con advertencias")
        else:
            _logger.warning("⚠️ Método de corrección MÍNIMA no disponible aún")
            
        # Proteger listas de precios existentes
        if hasattr(sale_order_model, '_prevent_any_pricelist_modifications'):
            sale_order_model._prevent_any_pricelist_modifications()
            _logger.info("✅ Listas de precios existentes protegidas")
            
    except Exception as e:
        _logger.error(f"❌ Error al ejecutar corrección MÍNIMA: {str(e)}")

# Ejecutar SOLO la corrección MÍNIMA cuando se importe el módulo
try:
    _minimal_safe_fix_on_module_load()
except Exception as e:
    # Si falla, no hacer nada - se ejecutará más tarde
    pass 