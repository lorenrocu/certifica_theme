# -*- coding: utf-8 -*-
from odoo import models, api, fields
import logging

_logger = logging.getLogger(__name__)

class WebsiteSaleErrorHandler(models.Model):
    _inherit = 'sale.order'

    @api.model
    def _get_default_pricelist(self):
        """
        Obtener lista de precios por defecto para evitar errores
        """
        _logger.info("=== OBTENIENDO LISTA DE PRECIOS POR DEFECTO ===")
        
        try:
            # Buscar lista de precios activa
            default_pricelist = self.env['product.pricelist'].sudo().search([
                ('active', '=', True)
            ], limit=1)
            
            if default_pricelist:
                _logger.info(f"✅ Lista de precios por defecto encontrada: {default_pricelist.name} (ID: {default_pricelist.id})")
                return default_pricelist
            
            # Si no hay lista activa, buscar cualquier lista
            any_pricelist = self.env['product.pricelist'].sudo().search([], limit=1)
            if any_pricelist:
                _logger.info(f"⚠️ Usando lista de precios disponible: {any_pricelist.name} (ID: {any_pricelist.id})")
                return any_pricelist
            
            # Crear lista de precios por defecto si no existe ninguna
            _logger.warning("⚠️ No se encontró ninguna lista de precios, creando una por defecto")
            default_pricelist = self.env['product.pricelist'].sudo().create({
                'name': 'Lista de Precios por Defecto',
                'active': True,
                'currency_id': self.env.ref('base.PEN').id,  # Moneda peruana por defecto
            })
            _logger.info(f"✅ Lista de precios por defecto creada: {default_pricelist.name} (ID: {default_pricelist.id})")
            return default_pricelist
            
        except Exception as e:
            _logger.error(f"❌ Error al obtener lista de precios por defecto: {str(e)}")
            # Retornar None y manejar el error en otro lugar
            return None

    @api.model
    def _get_default_currency(self):
        """
        Obtener moneda por defecto para evitar errores
        """
        _logger.info("=== OBTENIENDO MONEDA POR DEFECTO ===")
        
        try:
            # Buscar moneda peruana
            pen_currency = self.env.ref('base.PEN')
            if pen_currency:
                _logger.info(f"✅ Moneda PEN encontrada: {pen_currency.name}")
                return pen_currency
            
            # Si no hay PEN, buscar USD
            usd_currency = self.env.ref('base.USD')
            if usd_currency:
                _logger.info(f"⚠️ Usando moneda USD: {usd_currency.name}")
                return usd_currency
            
            # Si no hay ninguna, usar la primera disponible
            any_currency = self.env['res.currency'].sudo().search([], limit=1)
            if any_currency:
                _logger.info(f"⚠️ Usando moneda disponible: {any_currency.name}")
                return any_currency
            
            _logger.error("❌ No se encontró ninguna moneda en el sistema")
            return None
            
        except Exception as e:
            _logger.error(f"❌ Error al obtener moneda por defecto: {str(e)}")
            return None

    @api.model
    def create(self, vals):
        """
        Crear orden con valores por defecto para evitar errores
        """
        _logger.info("=== CREANDO ORDEN CON VALORES POR DEFECTO ===")
        _logger.info(f"Valores recibidos: {vals}")
        
        # Asignar lista de precios por defecto si no se proporciona
        if 'pricelist_id' not in vals or not vals['pricelist_id']:
            default_pricelist = self._get_default_pricelist()
            if default_pricelist:
                vals['pricelist_id'] = default_pricelist.id
                _logger.info(f"✅ Lista de precios asignada por defecto: {default_pricelist.name}")
            else:
                _logger.warning("⚠️ No se pudo asignar lista de precios por defecto")
        
        # Asignar moneda por defecto si no se proporciona
        if 'currency_id' not in vals or not vals['currency_id']:
            default_currency = self._get_default_currency()
            if default_currency:
                vals['currency_id'] = default_currency.id
                _logger.info(f"✅ Moneda asignada por defecto: {default_currency.name}")
            else:
                _logger.warning("⚠️ No se pudo asignar moneda por defecto")
        
        # Asignar partner por defecto si no se proporciona
        if 'partner_id' not in vals or not vals['partner_id']:
            default_partner = self.env['res.partner'].sudo().search([
                ('customer', '=', True)
            ], limit=1)
            if default_partner:
                vals['partner_id'] = default_partner.id
                _logger.info(f"✅ Partner asignado por defecto: {default_partner.name}")
            else:
                _logger.warning("⚠️ No se pudo asignar partner por defecto")
        
        _logger.info(f"Valores finales antes de crear: {vals}")
        
        # Crear la orden
        try:
            order = super().create(vals)
            _logger.info(f"✅ Orden creada exitosamente: {order.name}")
            return order
        except Exception as e:
            _logger.error(f"❌ Error al crear orden: {str(e)}")
            # Intentar con valores mínimos
            minimal_vals = {
                'name': 'Orden por Defecto',
                'pricelist_id': self._get_default_pricelist().id if self._get_default_pricelist() else 1,
                'currency_id': self._get_default_currency().id if self._get_default_currency() else 1,
                'partner_id': 1,  # Partner por defecto
            }
            _logger.info(f"⚠️ Intentando crear con valores mínimos: {minimal_vals}")
            return super().create(minimal_vals)

    def write(self, vals):
        """
        Actualizar orden con valores por defecto si es necesario
        """
        _logger.info("=== ACTUALIZANDO ORDEN CON VALORES POR DEFECTO ===")
        _logger.info(f"Valores recibidos: {vals}")
        
        # Asignar lista de precios por defecto si se está limpiando
        if 'pricelist_id' in vals and not vals['pricelist_id']:
            default_pricelist = self._get_default_pricelist()
            if default_pricelist:
                vals['pricelist_id'] = default_pricelist.id
                _logger.info(f"✅ Lista de precios restaurada por defecto: {default_pricelist.name}")
        
        # Asignar moneda por defecto si se está limpiando
        if 'currency_id' in vals and not vals['currency_id']:
            default_currency = self._get_default_currency()
            if default_currency:
                vals['currency_id'] = default_currency.id
                _logger.info(f"✅ Moneda restaurada por defecto: {default_currency.name}")
        
        _logger.info(f"Valores finales antes de actualizar: {vals}")
        
        # Actualizar la orden
        try:
            result = super().write(vals)
            _logger.info("✅ Orden actualizada exitosamente")
            return result
        except Exception as e:
            _logger.error(f"❌ Error al actualizar orden: {str(e)}")
            # Intentar con valores mínimos
            minimal_vals = {}
            if 'pricelist_id' in vals:
                minimal_vals['pricelist_id'] = self._get_default_pricelist().id if self._get_default_pricelist() else 1
            if 'currency_id' in vals:
                minimal_vals['currency_id'] = self._get_default_currency().id if self._get_default_currency() else 1
            
            if minimal_vals:
                _logger.info(f"⚠️ Intentando actualizar con valores mínimos: {minimal_vals}")
                return super().write(minimal_vals)
            return False

    @api.model
    def _ensure_pricelist_exists(self, order):
        """
        Asegurar que la orden tenga una lista de precios válida
        """
        _logger.info(f"=== VERIFICANDO LISTA DE PRECIOS PARA ORDEN {order.name} ===")
        
        if not order.pricelist_id:
            _logger.warning("⚠️ Orden sin lista de precios, asignando por defecto")
            default_pricelist = self._get_default_pricelist()
            if default_pricelist:
                order.pricelist_id = default_pricelist.id
                _logger.info(f"✅ Lista de precios asignada: {default_pricelist.name}")
            else:
                _logger.error("❌ No se pudo asignar lista de precios")
                return False
        
        if not order.pricelist_id.currency_id:
            _logger.warning("⚠️ Lista de precios sin moneda, asignando por defecto")
            default_currency = self._get_default_currency()
            if default_currency:
                order.pricelist_id.currency_id = default_currency.id
                _logger.info(f"✅ Moneda asignada: {default_currency.name}")
            else:
                _logger.error("❌ No se pudo asignar moneda")
                return False
        
        _logger.info("✅ Lista de precios verificada correctamente")
        return True

    @api.model
    def _ensure_order_validity(self, order):
        """
        Asegurar que la orden tenga todos los campos necesarios
        """
        _logger.info(f"=== VERIFICANDO VALIDEZ DE ORDEN {order.name} ===")
        
        # Verificar lista de precios
        if not self._ensure_pricelist_exists(order):
            return False
        
        # Verificar moneda
        if not order.currency_id:
            _logger.warning("⚠️ Orden sin moneda, asignando por defecto")
            default_currency = self._get_default_currency()
            if default_currency:
                order.currency_id = default_currency.id
                _logger.info(f"✅ Moneda asignada: {default_currency.name}")
            else:
                _logger.error("❌ No se pudo asignar moneda")
                return False
        
        # Verificar partner
        if not order.partner_id:
            _logger.warning("⚠️ Orden sin partner, asignando por defecto")
            default_partner = self.env['res.partner'].sudo().search([
                ('customer', '=', True)
            ], limit=1)
            if default_partner:
                order.partner_id = default_partner.id
                _logger.info(f"✅ Partner asignado: {default_partner.name}")
            else:
                _logger.error("❌ No se pudo asignar partner")
                return False
        
        _logger.info("✅ Orden verificada correctamente")
        return True

    @api.model
    def _get_order_for_display(self, order_id):
        """
        Obtener orden para mostrar en templates, asegurando que sea válida
        """
        _logger.info(f"=== OBTENIENDO ORDEN PARA MOSTRAR: {order_id} ===")
        
        try:
            order = self.browse(order_id)
            if order.exists():
                # Verificar y corregir la orden si es necesario
                self._ensure_order_validity(order)
                _logger.info(f"✅ Orden obtenida y validada: {order.name}")
                return order
            else:
                _logger.warning(f"⚠️ Orden {order_id} no existe")
                return None
        except Exception as e:
            _logger.error(f"❌ Error al obtener orden {order_id}: {str(e)}")
            return None

    @api.model
    def _create_dummy_order_for_display(self):
        """
        Crear orden dummy para mostrar en templates cuando no hay orden válida
        """
        _logger.info("=== CREANDO ORDEN DUMMY PARA MOSTRAR ===")
        
        try:
            # Crear orden con valores mínimos
            dummy_order = self.create({
                'name': 'Orden Temporal',
                'pricelist_id': self._get_default_pricelist().id if self._get_default_pricelist() else 1,
                'currency_id': self._get_default_currency().id if self._get_default_currency() else 1,
                'partner_id': 1,
            })
            
            _logger.info(f"✅ Orden dummy creada: {dummy_order.name}")
            return dummy_order
            
        except Exception as e:
            _logger.error(f"❌ Error al crear orden dummy: {str(e)}")
            return None

    @api.model
    def _get_safe_pricelist_currency(self, order):
        """
        Obtener moneda de la lista de precios de forma segura
        """
        _logger.info(f"=== OBTENIENDO MONEDA DE LISTA DE PRECIOS DE FORMA SEGURA ===")
        
        try:
            if order and order.pricelist_id and order.pricelist_id.currency_id:
                _logger.info(f"✅ Moneda obtenida: {order.pricelist_id.currency_id.name}")
                return order.pricelist_id.currency_id
            
            # Si no hay moneda válida, usar moneda por defecto
            default_currency = self._get_default_currency()
            if default_currency:
                _logger.info(f"⚠️ Usando moneda por defecto: {default_currency.name}")
                return default_currency
            
            _logger.error("❌ No se pudo obtener moneda válida")
            return None
            
        except Exception as e:
            _logger.error(f"❌ Error al obtener moneda: {str(e)}")
            return None

    @api.model
    def _get_safe_order_amount(self, order):
        """
        Obtener monto de la orden de forma segura
        """
        _logger.info(f"=== OBTENIENDO MONTO DE ORDEN DE FORMA SEGURA ===")
        
        try:
            if order and hasattr(order, 'amount_total') and order.amount_total is not None:
                _logger.info(f"✅ Monto obtenido: {order.amount_total}")
                return order.amount_total
            
            # Si no hay monto válido, usar 0
            _logger.warning("⚠️ Usando monto por defecto: 0.0")
            return 0.0
            
        except Exception as e:
            _logger.error(f"❌ Error al obtener monto: {str(e)}")
            return 0.0
