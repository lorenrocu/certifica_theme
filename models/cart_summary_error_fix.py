# -*- coding: utf-8 -*-
from odoo import models, api, fields
import logging

_logger = logging.getLogger(__name__)

class CartSummaryErrorFix(models.Model):
    _inherit = 'sale.order'

    @api.model
    def _fix_cart_summary_template_error(self):
        """
        Corregir específicamente el error del template cart_summary
        """
        _logger.info("=== CORRIGIENDO ERROR ESPECÍFICO DE CART_SUMMARY TEMPLATE ===")
        
        try:
            # Buscar todas las órdenes sin lista de precios
            orders_without_pricelist = self.search([
                ('pricelist_id', '=', False)
            ])
            
            _logger.info(f"Encontradas {len(orders_without_pricelist)} órdenes sin lista de precios")
            
            # Obtener lista de precios por defecto
            default_pricelist = self.env['product.pricelist'].sudo().search([
                ('active', '=', True)
            ], limit=1)
            
            if not default_pricelist:
                _logger.warning("⚠️ No hay lista de precios activa, creando una por defecto")
                default_pricelist = self.env['product.pricelist'].sudo().create({
                    'name': 'Lista de Precios por Defecto',
                    'active': True,
                    'currency_id': self.env.ref('base.PEN').id if self.env.ref('base.PEN') else 1,
                })
                _logger.info(f"✅ Lista de precios por defecto creada: {default_pricelist.name}")
            
            # Corregir órdenes sin lista de precios
            for order in orders_without_pricelist:
                try:
                    order.write({
                        'pricelist_id': default_pricelist.id,
                    })
                    _logger.info(f"✅ Orden {order.name} corregida con lista de precios")
                except Exception as e:
                    _logger.error(f"❌ Error al corregir orden {order.name}: {str(e)}")
            
            # Buscar órdenes con lista de precios pero sin moneda
            orders_without_currency = self.search([
                ('pricelist_id', '!=', False),
                ('pricelist_id.currency_id', '=', False)
            ])
            
            _logger.info(f"Encontradas {len(orders_without_currency)} órdenes con lista de precios sin moneda")
            
            # Obtener moneda por defecto
            default_currency = self.env.ref('base.PEN') or self.env.ref('base.USD')
            if not default_currency:
                default_currency = self.env['res.currency'].sudo().search([], limit=1)
            
            if default_currency:
                # Corregir listas de precios sin moneda
                for order in orders_without_currency:
                    try:
                        order.pricelist_id.write({
                            'currency_id': default_currency.id,
                        })
                        _logger.info(f"✅ Lista de precios de orden {order.name} corregida con moneda")
                    except Exception as e:
                        _logger.error(f"❌ Error al corregir moneda de orden {order.name}: {str(e)}")
            
            _logger.info("✅ Corrección de cart_summary completada")
            return True
            
        except Exception as e:
            _logger.error(f"❌ Error general al corregir cart_summary: {str(e)}")
            return False

    @api.model
    def _ensure_cart_summary_safety(self):
        """
        Asegurar que todas las órdenes sean seguras para cart_summary
        """
        _logger.info("=== ASEGURANDO SEGURIDAD DE CART_SUMMARY ===")
        
        try:
            # Obtener todas las órdenes
            all_orders = self.search([])
            _logger.info(f"Verificando {len(all_orders)} órdenes")
            
            for order in all_orders:
                try:
                    # Verificar lista de precios
                    if not order.pricelist_id:
                        _logger.warning(f"⚠️ Orden {order.name} sin lista de precios")
                        default_pricelist = self.env['product.pricelist'].sudo().search([
                            ('active', '=', True)
                        ], limit=1)
                        if default_pricelist:
                            order.pricelist_id = default_pricelist.id
                            _logger.info(f"✅ Lista de precios asignada a {order.name}")
                    
                    # Verificar moneda de la lista de precios
                    if order.pricelist_id and not order.pricelist_id.currency_id:
                        _logger.warning(f"⚠️ Lista de precios de orden {order.name} sin moneda")
                        default_currency = self.env.ref('base.PEN') or self.env.ref('base.USD')
                        if default_currency:
                            order.pricelist_id.currency_id = default_currency.id
                            _logger.info(f"✅ Moneda asignada a lista de precios de {order.name}")
                    
                    # Verificar moneda de la orden
                    if not order.currency_id:
                        _logger.warning(f"⚠️ Orden {order.name} sin moneda")
                        if order.pricelist_id and order.pricelist_id.currency_id:
                            order.currency_id = order.pricelist_id.currency_id.id
                            _logger.info(f"✅ Moneda asignada a {order.name} desde lista de precios")
                        else:
                            default_currency = self.env.ref('base.PEN') or self.env.ref('base.USD')
                            if default_currency:
                                order.currency_id = default_currency.id
                                _logger.info(f"✅ Moneda por defecto asignada a {order.name}")
                    
                    # Verificar partner
                    if not order.partner_id:
                        _logger.warning(f"⚠️ Orden {order.name} sin partner")
                        default_partner = self.env['res.partner'].sudo().search([
                            ('customer', '=', True)
                        ], limit=1)
                        if default_partner:
                            order.partner_id = default_partner.id
                            _logger.info(f"✅ Partner asignado a {order.name}")
                    
                except Exception as e:
                    _logger.error(f"❌ Error al verificar orden {order.name}: {str(e)}")
            
            _logger.info("✅ Verificación de seguridad completada")
            return True
            
        except Exception as e:
            _logger.error(f"❌ Error general en verificación de seguridad: {str(e)}")
            return False

    @api.model
    def _create_safe_order_for_cart_summary(self):
        """
        Crear orden segura específicamente para cart_summary
        """
        _logger.info("=== CREANDO ORDEN SEGURA PARA CART_SUMMARY ===")
        
        try:
            # Obtener valores por defecto
            default_pricelist = self.env['product.pricelist'].sudo().search([
                ('active', '=', True)
            ], limit=1)
            
            if not default_pricelist:
                _logger.warning("⚠️ No hay lista de precios activa, creando una")
                default_pricelist = self.env['product.pricelist'].sudo().create({
                    'name': 'Lista de Precios para Cart Summary',
                    'active': True,
                    'currency_id': self.env.ref('base.PEN').id if self.env.ref('base.PEN') else 1,
                })
                _logger.info(f"✅ Lista de precios creada: {default_pricelist.name}")
            
            default_currency = self.env.ref('base.PEN') or self.env.ref('base.USD')
            if not default_currency:
                default_currency = self.env['res.currency'].sudo().search([], limit=1)
            
            default_partner = self.env['res.partner'].sudo().search([
                ('customer', '=', True)
            ], limit=1)
            
            if not default_partner:
                _logger.warning("⚠️ No hay partner cliente, creando uno")
                default_partner = self.env['res.partner'].sudo().create({
                    'name': 'Cliente por Defecto',
                    'customer': True,
                    'email': 'cliente@default.com',
                })
                _logger.info(f"✅ Partner creado: {default_partner.name}")
            
            # Crear orden segura
            safe_order_vals = {
                'name': 'Orden Segura para Cart Summary',
                'pricelist_id': default_pricelist.id,
                'currency_id': default_currency.id if default_currency else 1,
                'partner_id': default_partner.id,
                'website_id': self.env['website'].sudo().search([], limit=1).id if self.env['website'].sudo().search([]) else 1,
            }
            
            safe_order = self.create(safe_order_vals)
            _logger.info(f"✅ Orden segura creada: {safe_order.name}")
            
            return safe_order
            
        except Exception as e:
            _logger.error(f"❌ Error al crear orden segura: {str(e)}")
            return None

    @api.model
    def _get_cart_summary_safe_data(self):
        """
        Obtener datos seguros para cart_summary
        """
        _logger.info("=== OBTENIENDO DATOS SEGUROS PARA CART_SUMMARY ===")
        
        try:
            # Obtener orden actual
            current_order = self.env.context.get('website_sale_order')
            
            if not current_order:
                _logger.warning("⚠️ No hay orden en contexto, creando una segura")
                current_order = self._create_safe_order_for_cart_summary()
            
            if not current_order:
                _logger.error("❌ No se pudo crear orden segura")
                return self._get_dummy_cart_summary_data()
            
            # Verificar que la orden sea segura
            self._ensure_cart_summary_safety()
            
            # Preparar datos seguros
            safe_data = {
                'website_sale_order': current_order,
                'amount_total': current_order.amount_total or 0.0,
                'currency': current_order.pricelist_id.currency_id if current_order.pricelist_id and current_order.pricelist_id.currency_id else self.env.ref('base.PEN'),
                'pricelist': current_order.pricelist_id,
                'partner': current_order.partner_id,
            }
            
            _logger.info("✅ Datos seguros obtenidos para cart_summary")
            return safe_data
            
        except Exception as e:
            _logger.error(f"❌ Error al obtener datos seguros: {str(e)}")
            return self._get_dummy_cart_summary_data()

    @api.model
    def _get_dummy_cart_summary_data(self):
        """
        Obtener datos dummy para cart_summary
        """
        _logger.info("=== OBTENIENDO DATOS DUMMY PARA CART_SUMMARY ===")
        
        try:
            # Crear datos dummy
            dummy_data = {
                'website_sale_order': None,
                'amount_total': 0.0,
                'currency': self.env.ref('base.PEN') or self.env.ref('base.USD'),
                'pricelist': self.env['product.pricelist'].sudo().search([], limit=1),
                'partner': self.env['res.partner'].sudo().search([], limit=1),
            }
            
            _logger.info("✅ Datos dummy creados para cart_summary")
            return dummy_data
            
        except Exception as e:
            _logger.error(f"❌ Error al crear datos dummy: {str(e)}")
            # Retornar estructura mínima
            return {
                'website_sale_order': None,
                'amount_total': 0.0,
                'currency': None,
                'pricelist': None,
                'partner': None,
            }

    @api.model
    def _fix_cart_summary_immediately(self):
        """
        Corregir cart_summary inmediatamente cuando se detecta el error
        """
        _logger.info("=== CORRECCIÓN INMEDIATA DE CART_SUMMARY ===")
        
        try:
            # Ejecutar todas las correcciones
            self._fix_cart_summary_template_error()
            self._ensure_cart_summary_safety()
            
            # Crear orden segura si es necesario
            safe_order = self._create_safe_order_for_cart_summary()
            
            if safe_order:
                _logger.info("✅ Corrección inmediata completada exitosamente")
                return safe_order
            else:
                _logger.warning("⚠️ Corrección inmediata completada pero no se pudo crear orden segura")
                return None
                
        except Exception as e:
            _logger.error(f"❌ Error en corrección inmediata: {str(e)}")
            return None
