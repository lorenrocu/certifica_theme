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

# Ejecutar corrección automática de cart_summary al cargar el módulo
def _auto_fix_cart_summary_on_module_load():
    """
    Ejecutar corrección automática cuando se carga el módulo
    """
    try:
        import logging
        _logger = logging.getLogger(__name__)
        _logger.info("=== MÓDULO CERTIFICA_THEME CARGADO - EJECUTANDO CORRECCIÓN AUTOMÁTICA ===")
        
        # Importar el modelo después de que esté disponible
        from odoo import api, SUPERUSER_ID
        env = api.Environment(cr, SUPERUSER_ID, {})
        
        # Ejecutar corrección automática
        sale_order_model = env['sale.order']
        if hasattr(sale_order_model, '_emergency_cart_summary_fix'):
            result = sale_order_model._emergency_cart_summary_fix()
            if result:
                _logger.info("✅ Corrección automática ejecutada exitosamente al cargar el módulo")
            else:
                _logger.warning("⚠️ Corrección automática ejecutada pero con advertencias")
        else:
            _logger.warning("⚠️ Método de corrección no disponible aún")
            
    except Exception as e:
        _logger.error(f"❌ Error al ejecutar corrección automática: {str(e)}")

# Ejecutar la corrección cuando se importe el módulo
try:
    _auto_fix_cart_summary_on_module_load()
except Exception as e:
    # Si falla, no hacer nada - se ejecutará más tarde
    pass 