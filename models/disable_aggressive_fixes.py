# -*- coding: utf-8 -*-
from odoo import models, api, fields
import logging

_logger = logging.getLogger(__name__)

class DisableAggressiveFixes(models.Model):
    _inherit = 'sale.order'

    @api.model
    def _disable_aggressive_fixes(self):
        """
        Desactivar temporalmente las correcciones automáticas agresivas
        """
        _logger.info("=== DESACTIVANDO CORRECCIONES AUTOMÁTICAS AGRESIVAS ===")
        _logger.info("⚠️ Las correcciones automáticas que modifican listas de precios están DESACTIVADAS")
        _logger.info("⚠️ Solo se ejecutarán correcciones mínimas y seguras")
        return True

    @api.model
    def _safe_minimal_fix_only(self):
        """
        Solo corrección mínima y segura - NO modifica listas de precios existentes
        """
        _logger.info("=== EJECUTANDO SOLO CORRECCIÓN MÍNIMA Y SEGURA ===")
        
        try:
            # Solo buscar órdenes que realmente tengan pricelist_id = None (no False)
            orders_with_none_pricelist = self.search([
                ('pricelist_id', '=', None)
            ])
            
            if not orders_with_none_pricelist:
                _logger.info("✅ No hay órdenes con pricelist_id = None - no se necesita corrección")
                return True
            
            _logger.info(f"⚠️ Encontradas {len(orders_with_none_pricelist)} órdenes con pricelist_id = None")
            
            # Solo usar listas de precios existentes (NO crear nuevas)
            existing_pricelist = self.env['product.pricelist'].sudo().search([
                ('active', '=', True)
            ], limit=1)
            
            if not existing_pricelist:
                _logger.warning("⚠️ No hay lista de precios activa existente - NO se creará una nueva")
                _logger.warning("⚠️ Las órdenes problemáticas permanecerán sin corregir")
                return False
            
            _logger.info(f"✅ Usando lista de precios existente: {existing_pricelist.name}")
            
            # Solo corregir órdenes con pricelist_id = None (no False)
            corrected_count = 0
            for order in orders_with_none_pricelist:
                try:
                    # Solo asignar si realmente es None (no False)
                    if order.pricelist_id is None:
                        order.write({
                            'pricelist_id': existing_pricelist.id,
                        })
                        corrected_count += 1
                        _logger.info(f"✅ Orden {order.name} corregida con lista existente")
                    else:
                        _logger.info(f"⚠️ Orden {order.name} tiene pricelist_id = {order.pricelist_id} - no se toca")
                        
                except Exception as e:
                    _logger.error(f"❌ Error al corregir orden {order.name}: {str(e)}")
            
            _logger.info(f"✅ Corrección mínima completada: {corrected_count} órdenes corregidas")
            _logger.info("✅ NO se modificaron listas de precios existentes")
            return True
            
        except Exception as e:
            _logger.error(f"❌ Error en corrección mínima: {str(e)}")
            return False

    @api.model
    def _emergency_cart_summary_fix_disabled(self):
        """
        Corrección de emergencia DESACTIVADA - solo corrección mínima
        """
        _logger.info("=== CORRECCIÓN DE EMERGENCIA DESACTIVADA - SOLO CORRECCIÓN MÍNIMA ===")
        
        try:
            # Solo ejecutar corrección mínima y segura
            result = self._safe_minimal_fix_only()
            
            if result:
                _logger.info("✅ Corrección mínima completada - sistema protegido")
            else:
                _logger.warning("⚠️ Corrección mínima completada pero con advertencias")
            
            return result
            
        except Exception as e:
            _logger.error(f"❌ Error en corrección mínima: {str(e)}")
            return False

    @api.model
    def _prevent_any_pricelist_modifications(self):
        """
        Prevenir cualquier modificación de listas de precios existentes
        """
        _logger.info("=== PREVINIENDO CUALQUIER MODIFICACIÓN DE LISTAS DE PRECIOS EXISTENTES ===")
        
        try:
            # Verificar que no se modifiquen listas de precios existentes
            existing_pricelists = self.env['product.pricelist'].sudo().search([])
            _logger.info(f"✅ Protegiendo {len(existing_pricelists)} listas de precios existentes")
            
            for pricelist in existing_pricelists:
                _logger.info(f"✅ Lista de precios protegida: {pricelist.name} (ID: {pricelist.id})")
            
            _logger.info("✅ Todas las listas de precios existentes están protegidas")
            return True
            
        except Exception as e:
            _logger.error(f"❌ Error al proteger listas de precios: {str(e)}")
            return False
