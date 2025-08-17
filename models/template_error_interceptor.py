# -*- coding: utf-8 -*-
from odoo import models, api, fields
import logging

_logger = logging.getLogger(__name__)

class TemplateErrorInterceptor(models.Model):
    _inherit = 'website'

    def _get_safe_website_sale_order_for_template(self):
        """
        Obtener orden segura para templates sin causar errores
        """
        _logger.info("=== OBTENIENDO ORDEN SEGURA PARA TEMPLATES ===")
        
        try:
            # Intentar obtener la orden del website
            order = self.sale_get_order(force_create=False)
            
            if not order:
                _logger.warning("⚠️ No hay orden en el website - creando orden segura")
                order = self._create_safe_order_for_template()
            
            if order and (not order.pricelist_id or not order.pricelist_id.currency_id):
                _logger.warning(f"⚠️ Orden {order.name} sin lista de precios válida - corrigiendo")
                self._fix_order_for_template_safety(order)
            
            _logger.info(f"✅ Orden segura obtenida: {order.name if order else 'None'}")
            return order
            
        except Exception as e:
            _logger.error(f"❌ Error al obtener orden segura: {str(e)}")
            return self._create_safe_order_for_template()

    def _create_safe_order_for_template(self):
        """
        Crear orden segura para templates cuando no hay ninguna
        """
        _logger.info("=== CREANDO ORDEN SEGURA PARA TEMPLATES ===")
        
        try:
            # Buscar lista de precios existente (NO crear nueva)
            existing_pricelist = self.env['product.pricelist'].sudo().search([
                ('active', '=', True)
            ], limit=1)
            
            if not existing_pricelist:
                _logger.error("❌ No hay lista de precios existente - no se puede crear orden segura")
                return None
            
            # Buscar partner existente (NO crear nuevo)
            existing_partner = self.env['res.partner'].sudo().search([
                ('customer', '=', True)
            ], limit=1)
            
            if not existing_partner:
                _logger.error("❌ No hay partner cliente existente - no se puede crear orden segura")
                return None
            
            # Crear orden segura con datos existentes
            safe_order_vals = {
                'name': 'Orden Segura para Template',
                'pricelist_id': existing_pricelist.id,
                'partner_id': existing_partner.id,
                'website_id': self.id,
            }
            
            order = self.env['sale.order'].sudo().create(safe_order_vals)
            _logger.info(f"✅ Orden segura creada: {order.name}")
            
            return order
            
        except Exception as e:
            _logger.error(f"❌ Error al crear orden segura: {str(e)}")
            return None

    def _fix_order_for_template_safety(self, order):
        """
        Corregir orden para que sea segura en templates
        """
        _logger.info(f"=== CORRIGIENDO ORDEN {order.name} PARA TEMPLATES ===")
        
        try:
            # Verificar lista de precios
            if not order.pricelist_id:
                _logger.warning(f"⚠️ Orden {order.name} sin lista de precios")
                existing_pricelist = self.env['product.pricelist'].sudo().search([
                    ('active', '=', True)
                ], limit=1)
                
                if existing_pricelist:
                    order.pricelist_id = existing_pricelist.id
                    _logger.info(f"✅ Lista de precios existente asignada a {order.name}")
                else:
                    _logger.error(f"❌ No hay lista de precios disponible para {order.name}")
                    return False
            
            # Verificar moneda de la lista de precios
            if order.pricelist_id and not order.pricelist_id.currency_id:
                _logger.warning(f"⚠️ Lista de precios de {order.name} sin moneda")
                # NO modificar la lista de precios existente
                _logger.info(f"⚠️ Lista de precios {order.pricelist_id.name} no se modificará")
                return False
            
            # Verificar partner
            if not order.partner_id:
                _logger.warning(f"⚠️ Orden {order.name} sin partner")
                existing_partner = self.env['res.partner'].sudo().search([
                    ('customer', '=', True)
                ], limit=1)
                
                if existing_partner:
                    order.partner_id = existing_partner.id
                    _logger.info(f"✅ Partner existente asignado a {order.name}")
                else:
                    _logger.error(f"❌ No hay partner disponible para {order.name}")
                    return False
            
            _logger.info(f"✅ Orden {order.name} corregida para templates")
            return True
            
        except Exception as e:
            _logger.error(f"❌ Error al corregir orden {order.name}: {str(e)}")
            return False

    def _get_template_safe_data(self, template_name):
        """
        Obtener datos seguros para cualquier template
        """
        _logger.info(f"=== OBTENIENDO DATOS SEGUROS PARA TEMPLATE: {template_name} ===")
        
        try:
            if template_name == 'website_sale.cart_summary':
                return self._get_cart_summary_safe_data()
            else:
                _logger.warning(f"⚠️ Template {template_name} no tiene manejador específico")
                return None
                
        except Exception as e:
            _logger.error(f"❌ Error al obtener datos seguros para {template_name}: {str(e)}")
            return None

    def _get_cart_summary_safe_data(self):
        """
        Obtener datos específicamente seguros para cart_summary
        """
        _logger.info("=== OBTENIENDO DATOS SEGUROS PARA CART_SUMMARY ===")
        
        try:
            # Obtener orden segura
            order = self._get_safe_website_sale_order_for_template()
            
            if not order:
                _logger.error("❌ No se pudo obtener orden segura para cart_summary")
                return self._get_dummy_cart_summary_data()
            
            # Verificar que la orden sea completamente segura
            if not self._verify_order_template_safety(order):
                _logger.warning("⚠️ Orden no es completamente segura, usando datos dummy")
                return self._get_dummy_cart_summary_data()
            
            # Preparar datos seguros
            safe_data = {
                'website_sale_order': order,
                'amount_total': order.amount_total or 0.0,
                'currency': order.pricelist_id.currency_id if order.pricelist_id and order.pricelist_id.currency_id else None,
                'pricelist': order.pricelist_id,
                'partner': order.partner_id,
            }
            
            _logger.info("✅ Datos seguros obtenidos para cart_summary")
            return safe_data
            
        except Exception as e:
            _logger.error(f"❌ Error al obtener datos seguros para cart_summary: {str(e)}")
            return self._get_dummy_cart_summary_data()

    def _verify_order_template_safety(self, order):
        """
        Verificar que la orden sea completamente segura para templates
        """
        _logger.info(f"=== VERIFICANDO SEGURIDAD COMPLETA DE ORDEN {order.name} ===")
        
        try:
            # Verificar lista de precios
            if not order.pricelist_id:
                _logger.warning(f"❌ Orden {order.name} sin lista de precios")
                return False
            
            # Verificar moneda de la lista de precios
            if not order.pricelist_id.currency_id:
                _logger.warning(f"❌ Lista de precios de {order.name} sin moneda")
                return False
            
            # Verificar partner
            if not order.partner_id:
                _logger.warning(f"❌ Orden {order.name} sin partner")
                return False
            
            _logger.info(f"✅ Orden {order.name} es completamente segura para templates")
            return True
            
        except Exception as e:
            _logger.error(f"❌ Error al verificar seguridad de orden {order.name}: {str(e)}")
            return False

    def _get_dummy_cart_summary_data(self):
        """
        Obtener datos dummy para cart_summary cuando no hay datos seguros
        """
        _logger.info("=== OBTENIENDO DATOS DUMMY PARA CART_SUMMARY ===")
        
        try:
            # Crear datos dummy mínimos
            dummy_data = {
                'website_sale_order': None,
                'amount_total': 0.0,
                'currency': None,
                'pricelist': None,
                'partner': None,
            }
            
            _logger.info("✅ Datos dummy creados para cart_summary")
            return dummy_data
            
        except Exception as e:
            _logger.error(f"❌ Error al crear datos dummy: {str(e)}")
            # Retornar estructura mínima absoluta
            return {
                'website_sale_order': None,
                'amount_total': 0.0,
                'currency': None,
                'pricelist': None,
                'partner': None,
            }

    def _intercept_template_error(self, template_name, error):
        """
        Interceptar errores de template y aplicar corrección automática
        """
        _logger.error(f"=== ERROR INTERCEPTADO EN TEMPLATE {template_name}: {str(error)} ===")
        
        try:
            if template_name == 'website_sale.cart_summary':
                _logger.info("⚠️ Error en cart_summary - aplicando corrección automática")
                
                # Obtener datos seguros
                safe_data = self._get_cart_summary_safe_data()
                
                if safe_data:
                    _logger.info("✅ Corrección automática aplicada para cart_summary")
                    return safe_data
                else:
                    _logger.warning("⚠️ No se pudieron obtener datos seguros para cart_summary")
                    return None
            else:
                _logger.warning(f"⚠️ Template {template_name} no tiene interceptor específico")
                return None
                
        except Exception as e:
            _logger.error(f"❌ Error al interceptar template {template_name}: {str(e)}")
            return None
