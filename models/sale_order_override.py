# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class SaleOrderOverride(models.Model):
    """
    Sobrescribe el modelo sale.order para manejar correctamente la asignación de partners
    """
    _inherit = 'sale.order'
    
    def _check_partner_assignment(self):
        """
        Verifica que el partner esté correctamente asignado
        """
        _logger.info(f"=== VERIFICANDO ASIGNACIÓN DE PARTNER EN PEDIDO {self.id} ===")
        
        if not self.partner_id:
            _logger.error(f"Pedido {self.id} sin partner asignado")
            return False
        
        # Verificar que el partner no sea el mismo que el website
        website = self.env['website'].get_current_website()
        if website and self.partner_id.id == website.partner_id.id:
            _logger.error(f"Pedido {self.id} tiene el mismo partner que el website")
            return False
        
        # Verificar campos mínimos del partner
        if not self.partner_id.name:
            _logger.error(f"Partner {self.partner_id.id} sin nombre")
            return False
        
        if not self.partner_id.email:
            _logger.error(f"Partner {self.partner_id.id} sin email")
            return False
        
        _logger.info(f"✅ Partner válido: {self.partner_id.name} (ID: {self.partner_id.id})")
        return True
    
    @api.model
    def create(self, vals):
        """
        Sobrescribimos create para asegurar que el partner se asigne correctamente
        """
        _logger.info("=== CREANDO PEDIDO ===")
        _logger.info(f"Vals: {vals}")
        
        # Si no hay partner_id, intentar obtenerlo de la sesión
        if 'partner_id' not in vals or not vals['partner_id']:
            session_partner_id = self.env.context.get('session_partner_id')
            if session_partner_id:
                vals['partner_id'] = session_partner_id
                _logger.info(f"Partner de sesión asignado: {session_partner_id}")
        
        # Crear el pedido
        order = super(SaleOrderOverride, self).create(vals)
        
        # Verificar que el partner esté correctamente asignado
        if not self._check_partner_assignment():
            _logger.warning(f"Pedido {order.id} creado con partner inválido")
        
        return order
    
    def write(self, vals):
        """
        Sobrescribimos write para asegurar que el partner se asigne correctamente
        """
        _logger.info(f"=== ACTUALIZANDO PEDIDO {self.id} ===")
        _logger.info(f"Vals: {vals}")
        
        # Si se está actualizando el partner_id, verificar que sea válido
        if 'partner_id' in vals and vals['partner_id']:
            # Verificar que el partner no sea el mismo que el website
            website = self.env['website'].get_current_website()
            if website and vals['partner_id'] == website.partner_id.id:
                _logger.warning(f"Intentando asignar partner del website al pedido {self.id}")
                # No permitir esta asignación
                vals.pop('partner_id')
                _logger.info("Partner_id removido de vals para evitar conflicto")
        
        # Actualizar el pedido
        result = super(SaleOrderOverride, self).write(vals)
        
        # Verificar que el partner esté correctamente asignado después de la actualización
        for order in self:
            if not order._check_partner_assignment():
                _logger.warning(f"Pedido {order.id} actualizado con partner inválido")
        
        return result
    
    def action_confirm(self):
        """
        Sobrescribimos action_confirm para verificar el partner antes de confirmar
        """
        _logger.info(f"=== CONFIRMANDO PEDIDO {self.id} ===")
        
        # Verificar que el partner esté correctamente asignado
        if not self._check_partner_assignment():
            raise ValidationError(_("El partner del pedido no es válido. Por favor, complete la información de envío."))
        
        # Llamar al método padre
        return super(SaleOrderOverride, self).action_confirm()
    
    def _create_payment_transaction(self, vals):
        """
        Sobrescribimos _create_payment_transaction para asegurar que el partner esté correctamente asignado
        """
        _logger.info(f"=== CREANDO TRANSACCIÓN DE PAGO PARA PEDIDO {self.id} ===")
        
        # Verificar que el partner esté correctamente asignado
        if not self._check_partner_assignment():
            raise ValidationError(_("El partner del pedido no es válido. Por favor, complete la información de envío."))
        
        # Asegurar que el partner_id esté en vals
        if 'partner_id' not in vals:
            vals['partner_id'] = self.partner_id.id
            _logger.info(f"Partner_id agregado a vals: {self.partner_id.id}")
        
        # Llamar al método padre
        return super(SaleOrderOverride, self)._create_payment_transaction(vals)
    
    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        """
        Sobrescribimos _onchange_partner_id para validar el partner seleccionado
        """
        _logger.info(f"=== ONCHANGE PARTNER_ID EN PEDIDO {self.id} ===")
        
        if self.partner_id:
            # Verificar que el partner no sea el mismo que el website
            website = self.env['website'].get_current_website()
            if website and self.partner_id.id == website.partner_id.id:
                _logger.warning("Seleccionado partner del website, esto puede causar problemas")
                # Mostrar advertencia al usuario
                return {
                    'warning': {
                        'title': _('Advertencia'),
                        'message': _('El partner seleccionado es el mismo que el website. Esto puede causar problemas en el proceso de pago.')
                    }
                }
        
        # Llamar al método padre
        return super(SaleOrderOverride, self)._onchange_partner_id()
