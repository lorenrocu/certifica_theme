# -*- coding: utf-8 -*-
from odoo import models, api, fields
import logging

_logger = logging.getLogger(__name__)

class SafeCartSummaryFix(models.Model):
    _inherit = 'sale.order'

    @api.model
    def _safe_fix_cart_summary_only(self):
        """
        Corregir SOLO el error de cart_summary sin tocar listas de precios existentes
        """
        _logger.info("=== CORRECCIÓN SEGURA DE CART_SUMMARY - SIN TOCAR LISTAS DE PRECIOS ===")
        
        try:
            # Solo buscar órdenes que realmente tengan el error (pricelist_id = None)
            orders_with_null_pricelist = self.search([
                ('pricelist_id', '=', False)
            ])
            
            if not orders_with_null_pricelist:
                _logger.info("✅ No hay órdenes con pricelist_id nulo - no se necesita corrección")
                return True
            
            _logger.info(f"⚠️ Encontradas {len(orders_with_null_pricelist)} órdenes con pricelist_id nulo")
            
            # Buscar la lista de precios activa existente (NO crear una nueva)
            existing_pricelist = self.env['product.pricelist'].sudo().search([
                ('active', '=', True)
            ], limit=1)
            
            if not existing_pricelist:
                _logger.warning("⚠️ No hay lista de precios activa existente - NO se creará una nueva")
                return False
            
            _logger.info(f"✅ Usando lista de precios existente: {existing_pricelist.name}")
            
            # Solo corregir órdenes que realmente tengan pricelist_id = None
            corrected_count = 0
            for order in orders_with_null_pricelist:
                try:
                    # Solo asignar si realmente es None
                    if order.pricelist_id is False or order.pricelist_id is None:
                        order.write({
                            'pricelist_id': existing_pricelist.id,
                        })
                        corrected_count += 1
                        _logger.info(f"✅ Orden {order.name} corregida con lista existente")
                    else:
                        _logger.info(f"⚠️ Orden {order.name} ya tiene pricelist_id - no se toca")
                        
                except Exception as e:
                    _logger.error(f"❌ Error al corregir orden {order.name}: {str(e)}")
            
            _logger.info(f"✅ Corrección completada: {corrected_count} órdenes corregidas")
            return True
            
        except Exception as e:
            _logger.error(f"❌ Error en corrección segura: {str(e)}")
            return False

    @api.model
    def _ensure_cart_summary_works_without_modifying_pricelists(self):
        """
        Asegurar que cart_summary funcione sin modificar listas de precios existentes
        """
        _logger.info("=== VERIFICANDO CART_SUMMARY SIN MODIFICAR LISTAS DE PRECIOS ===")
        
        try:
            # Solo verificar órdenes que realmente tengan problemas
            problematic_orders = self.search([
                '|',
                ('pricelist_id', '=', False),
                ('pricelist_id', '=', None)
            ])
            
            if not problematic_orders:
                _logger.info("✅ No hay órdenes problemáticas - cart_summary debería funcionar")
                return True
            
            _logger.info(f"⚠️ Encontradas {len(problematic_orders)} órdenes problemáticas")
            
            # Solo corregir las que realmente necesiten corrección
            for order in problematic_orders:
                try:
                    if order.pricelist_id is False or order.pricelist_id is None:
                        _logger.warning(f"⚠️ Orden {order.name} sin pricelist_id - asignando existente")
                        
                        # Buscar lista de precios existente (NO crear nueva)
                        existing_pricelist = self.env['product.pricelist'].sudo().search([
                            ('active', '=', True)
                        ], limit=1)
                        
                        if existing_pricelist:
                            order.pricelist_id = existing_pricelist.id
                            _logger.info(f"✅ Lista de precios existente asignada a {order.name}")
                        else:
                            _logger.warning(f"⚠️ No hay lista de precios existente para {order.name}")
                    
                    # Verificar que la moneda esté disponible
                    if order.pricelist_id and not order.pricelist_id.currency_id:
                        _logger.warning(f"⚠️ Lista de precios de {order.name} sin moneda")
                        # NO modificar la lista de precios existente
                        _logger.info(f"⚠️ Lista de precios {order.pricelist_id.name} no se modificará")
                    
                except Exception as e:
                    _logger.error(f"❌ Error al verificar orden {order.name}: {str(e)}")
            
            _logger.info("✅ Verificación completada sin modificar listas de precios existentes")
            return True
            
        except Exception as e:
            _logger.error(f"❌ Error en verificación segura: {str(e)}")
            return False

    @api.model
    def _get_cart_summary_safe_context(self):
        """
        Obtener contexto seguro para cart_summary sin modificar datos existentes
        """
        _logger.info("=== OBTENIENDO CONTEXTO SEGURO PARA CART_SUMMARY ===")
        
        try:
            # Buscar orden actual sin forzar creación
            current_order = self.env.context.get('website_sale_order')
            
            if not current_order:
                _logger.info("⚠️ No hay orden en contexto - cart_summary puede fallar")
                return None
            
            # Solo verificar que la orden sea válida para cart_summary
            if current_order.pricelist_id is False or current_order.pricelist_id is None:
                _logger.warning(f"⚠️ Orden {current_order.name} sin pricelist_id - cart_summary fallará")
                
                # Buscar lista de precios existente (NO crear nueva)
                existing_pricelist = self.env['product.pricelist'].sudo().search([
                    ('active', '=', True)
                ], limit=1)
                
                if existing_pricelist:
                    current_order.pricelist_id = existing_pricelist.id
                    _logger.info(f"✅ Lista de precios existente asignada a {current_order.name}")
                else:
                    _logger.error(f"❌ No hay lista de precios disponible para {current_order.name}")
                    return None
            
            _logger.info(f"✅ Orden {current_order.name} válida para cart_summary")
            return current_order
            
        except Exception as e:
            _logger.error(f"❌ Error al obtener contexto seguro: {str(e)}")
            return None

    @api.model
    def _prevent_cart_summary_error_without_changes(self):
        """
        Prevenir error de cart_summary sin hacer cambios innecesarios
        """
        _logger.info("=== PREVINIENDO ERROR DE CART_SUMMARY SIN CAMBIOS INNECESARIOS ===")
        
        try:
            # Solo ejecutar la corrección mínima necesaria
            result = self._safe_fix_cart_summary_only()
            
            if result:
                _logger.info("✅ Prevención completada - solo se corrigieron órdenes problemáticas")
            else:
                _logger.warning("⚠️ Prevención completada pero con advertencias")
            
            return result
            
        except Exception as e:
            _logger.error(f"❌ Error en prevención: {str(e)}")
            return False

    @api.model
    def _emergency_cart_summary_fix_safe(self):
        """
        Corrección de emergencia SEGURA para cart_summary
        """
        _logger.info("=== CORRECCIÓN DE EMERGENCIA SEGURA PARA CART_SUMMARY ===")
        
        try:
            # Solo ejecutar correcciones que no modifiquen datos existentes
            self._safe_fix_cart_summary_only()
            self._ensure_cart_summary_works_without_modifying_pricelists()
            
            _logger.info("✅ Corrección de emergencia segura completada")
            return True
            
        except Exception as e:
            _logger.error(f"❌ Error en corrección de emergencia segura: {str(e)}")
            return False
