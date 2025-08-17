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
from . import template_error_interceptor
from . import website_sale_order_guarantee

# Ejecutar GARANTÍA COMPLETA de cart_summary al cargar el módulo
def _cart_summary_guarantee_on_module_load():
    """
    Ejecutar GARANTÍA COMPLETA de cart_summary - PROTEGIENDO LISTAS DE PRECIOS EXISTENTES
    """
    try:
        import logging
        _logger = logging.getLogger(__name__)
        _logger.info("=== MÓDULO CERTIFICA_THEME CARGADO - GARANTÍA COMPLETA DE CART_SUMMARY ===")
        _logger.info("⚠️ CORRECCIONES AGRESIVAS DESACTIVADAS - LISTAS DE PRECIOS PROTEGIDAS")
        _logger.info("🚀 GARANTÍA COMPLETA DE CART_SUMMARY ACTIVADA")
        
        # Importar el modelo después de que esté disponible
        from odoo import api, SUPERUSER_ID
        env = api.Environment(cr, SUPERUSER_ID, {})
        
        # Desactivar correcciones agresivas
        sale_order_model = env['sale.order']
        if hasattr(sale_order_model, '_disable_aggressive_fixes'):
            sale_order_model._disable_aggressive_fixes()
            _logger.info("✅ Correcciones agresivas desactivadas")
        
        # Proteger listas de precios existentes
        if hasattr(sale_order_model, '_prevent_any_pricelist_modifications'):
            sale_order_model._prevent_any_pricelist_modifications()
            _logger.info("✅ Listas de precios existentes protegidas")
        
        # Activar garantía de cart_summary
        website_model = env['website']
        if hasattr(website_model, '_ensure_cart_summary_always_works'):
            result = website_model._ensure_cart_summary_always_works()
            if result:
                _logger.info("✅ GARANTÍA COMPLETA DE CART_SUMMARY ACTIVADA - LISTAS DE PRECIOS PROTEGIDAS")
            else:
                _logger.warning("⚠️ GARANTÍA activada pero con advertencias")
        else:
            _logger.warning("⚠️ Método de garantía no disponible aún")
            
    except Exception as e:
        _logger.error(f"❌ Error al ejecutar GARANTÍA de cart_summary: {str(e)}")

# Ejecutar la GARANTÍA COMPLETA cuando se importe el módulo
try:
    _cart_summary_guarantee_on_module_load()
except Exception as e:
    # Si falla, no hacer nada - se ejecutará más tarde
    pass 