# -*- coding: utf-8 -*-
from odoo import models, api, fields
import logging

_logger = logging.getLogger(__name__)

class SaleValidationOverride(models.Model):
    _inherit = 'sale.order'

    def _checkout_form_validate(self, mode, all_form_values, data_values):
        """
        DESHABILITAR COMPLETAMENTE LA VALIDACIÓN DEL CHECKOUT EN SALE
        """
        _logger.info("=== SALE CHECKOUT VALIDATION COMPLETELY DISABLED ===")
        _logger.info(f"Mode: {mode}")
        _logger.info(f"All form values: {all_form_values}")
        _logger.info(f"Data values: {data_values}")
        
        # Obtener todos los valores para logging
        name = all_form_values.get('name', '').strip()
        email = all_form_values.get('email', '').strip()
        phone = all_form_values.get('phone', '').strip()
        street = all_form_values.get('street', '').strip()
        city = all_form_values.get('city', '').strip()
        country_id = all_form_values.get('country_id', '')
        state_id = all_form_values.get('state_id', '')
        zip = all_form_values.get('zip', '').strip()
        vat = all_form_values.get('vat', '').strip()
        
        # LOGS DETALLADOS DE TODOS LOS VALORES
        _logger.info("=== VALORES RECIBIDOS EN SALE VALIDATION ===")
        _logger.info(f"Nombre: '{name}'")
        _logger.info(f"Email: '{email}'")
        _logger.info(f"Teléfono: '{phone}'")
        _logger.info(f"Dirección: '{street}'")
        _logger.info(f"Ciudad: '{city}'")
        _logger.info(f"Estado ID: '{state_id}'")
        _logger.info(f"País ID: '{country_id}'")
        _logger.info(f"Código Postal: '{zip}'")
        _logger.info(f"VAT: '{vat}'")
        
        # LOGS DE VALIDACIONES IGNORADAS
        _logger.info("=== VALIDACIONES IGNORADAS EN SALE ===")
        
        if not name:
            _logger.info("⚠️ Nombre faltante - IGNORADO en sale")
        if not email:
            _logger.info("⚠️ Email faltante - IGNORADO en sale")
        if not phone:
            _logger.info("⚠️ Teléfono faltante - IGNORADO en sale")
        if not street:
            _logger.info("⚠️ Dirección faltante - IGNORADO en sale")
        if not city:
            _logger.info("⚠️ Ciudad faltante - IGNORADO en sale")
        if not country_id:
            _logger.info("⚠️ País faltante - IGNORADO en sale")
        if not zip:
            _logger.info("⚠️ Código postal faltante - IGNORADO en sale")
        if not vat:
            _logger.info("⚠️ VAT faltante - IGNORADO en sale")
        
        # Validaciones de formato ignoradas
        if email and '@' not in email:
            _logger.info("⚠️ Email inválido - IGNORADO en sale")
        if phone and len(phone) < 7:
            _logger.info("⚠️ Teléfono muy corto - IGNORADO en sale")
        if vat and len(vat) < 5:
            _logger.info("⚠️ VAT muy corto - IGNORADO en sale")
        
        # DESHABILITAR TODAS LAS VALIDACIONES - RETORNAR SIN ERRORES
        _logger.info("=== TODAS LAS VALIDACIONES DE SALE DESHABILITADAS ===")
        _logger.info("✅ El formulario será procesado sin validaciones en sale")
        _logger.info("✅ Las validaciones solo se realizan en el frontend")
        
        return {}, []

    def _checkout_form_save(self, mode, checkout, all_values):
        """
        DESHABILITAR VALIDACIONES EN EL GUARDADO DEL CHECKOUT EN SALE
        """
        _logger.info("=== SALE CHECKOUT SAVE - VALIDACIONES DESHABILITADAS ===")
        _logger.info(f"Mode: {mode}")
        _logger.info(f"Checkout: {checkout}")
        _logger.info(f"All values: {all_values}")
        
        # Obtener todos los valores para logging
        name = all_values.get('name', '').strip()
        email = all_values.get('email', '').strip()
        phone = all_values.get('phone', '').strip()
        street = all_values.get('street', '').strip()
        city = all_values.get('city', '').strip()
        country_id = all_values.get('country_id', '')
        state_id = all_values.get('state_id', '')
        zip = all_values.get('zip', '').strip()
        vat = all_values.get('vat', '').strip()
        
        # LOGS DETALLADOS
        _logger.info("=== VALORES EXTRAÍDOS EN SALE SAVE ===")
        _logger.info(f"Nombre: '{name}'")
        _logger.info(f"Email: '{email}'")
        _logger.info(f"Teléfono: '{phone}'")
        _logger.info(f"Dirección: '{street}'")
        _logger.info(f"Ciudad: '{city}'")
        _logger.info(f"Estado ID: '{state_id}'")
        _logger.info(f"País ID: '{country_id}'")
        _logger.info(f"Código Postal: '{zip}'")
        _logger.info(f"VAT: '{vat}'")
        
        # LOGS DE VALIDACIONES IGNORADAS
        _logger.info("=== VALIDACIONES IGNORADAS EN SALE SAVE ===")
        
        if not name:
            _logger.info("⚠️ Nombre faltante - IGNORADO en save")
        if not email:
            _logger.info("⚠️ Email faltante - IGNORADO en save")
        if not phone:
            _logger.info("⚠️ Teléfono faltante - IGNORADO en save")
        if not street:
            _logger.info("⚠️ Dirección faltante - IGNORADO en save")
        if not city:
            _logger.info("⚠️ Ciudad faltante - IGNORADO en save")
        if not country_id:
            _logger.info("⚠️ País faltante - IGNORADO en save")
        
        # PROCESAR SIN VALIDACIONES
        _logger.info("=== PROCESANDO SIN VALIDACIONES EN SALE ===")
        
        # Asignar valores por defecto si faltan
        if not checkout.get('name'):
            checkout['name'] = name or 'Cliente'
            _logger.info(f"Nombre por defecto: '{checkout['name']}' (sin validación)")
        
        if not checkout.get('email'):
            checkout['email'] = email or 'cliente@example.com'
            _logger.info(f"Email por defecto: '{checkout['email']}' (sin validación)")
        
        if not checkout.get('phone'):
            checkout['phone'] = phone or '000000000'
            _logger.info(f"Teléfono por defecto: '{checkout['phone']}' (sin validación)")
        
        if not checkout.get('street'):
            checkout['street'] = street or 'Sin dirección'
            _logger.info(f"Dirección por defecto: '{checkout['street']}' (sin validación)")
        
        if not checkout.get('city'):
            checkout['city'] = city or 'Sin ciudad'
            _logger.info(f"Ciudad por defecto: '{checkout['city']}' (sin validación)")
        
        if not checkout.get('country_id'):
            checkout['country_id'] = country_id or 173  # Perú por defecto
            _logger.info(f"País por defecto: {checkout['country_id']} (sin validación)")
        
        if not checkout.get('state_id') and state_id:
            checkout['state_id'] = state_id
            _logger.info(f"Estado asignado: {state_id} (sin validación)")
        
        if not checkout.get('zip'):
            checkout['zip'] = zip or '00000'
            _logger.info(f"Código postal por defecto: '{checkout['zip']}' (sin validación)")
        
        if not checkout.get('vat'):
            checkout['vat'] = vat or '00000000'
            _logger.info(f"VAT por defecto: '{checkout['vat']}' (sin validación)")
        
        _logger.info(f"Checkout final (sin validaciones): {checkout}")
        
        # Llamar al método original sin validaciones
        try:
            _logger.info("=== LLAMANDO MÉTODO ORIGINAL SIN VALIDACIONES ===")
            result = super()._checkout_form_save(mode, checkout, all_values)
            _logger.info("✅ Método original ejecutado sin validaciones")
            return result
        except Exception as e:
            _logger.error(f"❌ Error en método original: {str(e)}")
            _logger.info("⚠️ Error ignorado - continuando sin validaciones")
            # Retornar ID por defecto
            return 1

    def _validate_order_data(self, order_data):
        """
        DESHABILITAR VALIDACIÓN DE DATOS DE ORDEN
        """
        _logger.info("=== SALE ORDER DATA VALIDATION DISABLED ===")
        _logger.info(f"Datos de orden: {order_data}")
        
        # Obtener valores para logging
        partner_id = order_data.get('partner_id', '')
        date_order = order_data.get('date_order', '')
        payment_term_id = order_data.get('payment_term_id', '')
        pricelist_id = order_data.get('pricelist_id', '')
        
        # LOGS DETALLADOS
        _logger.info("=== VALORES DE ORDEN RECIBIDOS ===")
        _logger.info(f"Partner ID: '{partner_id}'")
        _logger.info(f"Fecha de orden: '{date_order}'")
        _logger.info(f"Término de pago ID: '{payment_term_id}'")
        _logger.info(f"Lista de precios ID: '{pricelist_id}'")
        
        # LOGS DE VALIDACIONES IGNORADAS
        _logger.info("=== VALIDACIONES DE ORDEN IGNORADAS ===")
        
        if not partner_id:
            _logger.info("⚠️ Partner ID faltante - IGNORADO en validación de orden")
        if not date_order:
            _logger.info("⚠️ Fecha de orden faltante - IGNORADO en validación de orden")
        if not payment_term_id:
            _logger.info("⚠️ Término de pago faltante - IGNORADO en validación de orden")
        if not pricelist_id:
            _logger.info("⚠️ Lista de precios faltante - IGNORADO en validación de orden")
        
        # DESHABILITAR VALIDACIONES
        _logger.info("=== VALIDACIÓN DE ORDEN DESHABILITADA ===")
        _logger.info("✅ La orden será procesada sin validaciones")
        
        return True

    def _validate_order_line_data(self, line_data):
        """
        DESHABILITAR VALIDACIÓN DE DATOS DE LÍNEA DE ORDEN
        """
        _logger.info("=== SALE ORDER LINE DATA VALIDATION DISABLED ===")
        _logger.info(f"Datos de línea: {line_data}")
        
        # Obtener valores para logging
        product_id = line_data.get('product_id', '')
        name = line_data.get('name', '')
        product_uom_qty = line_data.get('product_uom_qty', '')
        product_uom = line_data.get('product_uom', '')
        price_unit = line_data.get('price_unit', '')
        
        # LOGS DETALLADOS
        _logger.info("=== VALORES DE LÍNEA RECIBIDOS ===")
        _logger.info(f"Producto ID: '{product_id}'")
        _logger.info(f"Nombre: '{name}'")
        _logger.info(f"Cantidad: '{product_uom_qty}'")
        _logger.info(f"UOM: '{product_uom}'")
        _logger.info(f"Precio unitario: '{price_unit}'")
        
        # LOGS DE VALIDACIONES IGNORADAS
        _logger.info("=== VALIDACIONES DE LÍNEA IGNORADAS ===")
        
        if not product_id:
            _logger.info("⚠️ Producto ID faltante - IGNORADO en validación de línea")
        if not name:
            _logger.info("⚠️ Nombre faltante - IGNORADO en validación de línea")
        if not product_uom_qty:
            _logger.info("⚠️ Cantidad faltante - IGNORADO en validación de línea")
        if not product_uom:
            _logger.info("⚠️ UOM faltante - IGNORADO en validación de línea")
        if not price_unit:
            _logger.info("⚠️ Precio unitario faltante - IGNORADO en validación de línea")
        
        # Validaciones de formato ignoradas
        if product_uom_qty and float(product_uom_qty) <= 0:
            _logger.info("⚠️ Cantidad inválida (<= 0) - IGNORADO en validación de línea")
        if price_unit and float(price_unit) < 0:
            _logger.info("⚠️ Precio unitario inválido (< 0) - IGNORADO en validación de línea")
        
        # DESHABILITAR VALIDACIONES
        _logger.info("=== VALIDACIÓN DE LÍNEA DESHABILITADA ===")
        _logger.info("✅ La línea será procesada sin validaciones")
        
        return True

    def _validate_order_partner(self, partner):
        """
        DESHABILITAR VALIDACIÓN DE PARTNER DE ORDEN
        """
        _logger.info("=== SALE ORDER PARTNER VALIDATION DISABLED ===")
        _logger.info(f"Partner: {partner}")
        
        # LOGS DE VALIDACIONES IGNORADAS
        _logger.info("=== VALIDACIONES DE PARTNER IGNORADAS ===")
        
        if not partner:
            _logger.info("⚠️ Partner faltante - IGNORADO en validación")
        if partner and not str(partner).isdigit():
            _logger.info("⚠️ Partner ID inválido - IGNORADO en validación")
        
        # DESHABILITAR VALIDACIONES
        _logger.info("=== VALIDACIÓN DE PARTNER DESHABILITADA ===")
        _logger.info("✅ El partner será procesado sin validaciones")
        
        return True

    def _validate_order_amount(self, amount):
        """
        DESHABILITAR VALIDACIÓN DE MONTO DE ORDEN
        """
        _logger.info("=== SALE ORDER AMOUNT VALIDATION DISABLED ===")
        _logger.info(f"Monto: {amount}")
        
        # LOGS DE VALIDACIONES IGNORADAS
        _logger.info("=== VALIDACIONES DE MONTO IGNORADAS ===")
        
        if not amount:
            _logger.info("⚠️ Monto faltante - IGNORADO en validación")
        if amount and float(amount) <= 0:
            _logger.info("⚠️ Monto inválido (<= 0) - IGNORADO en validación")
        if amount and float(amount) > 999999999:
            _logger.info("⚠️ Monto muy alto - IGNORADO en validación")
        
        # DESHABILITAR VALIDACIONES
        _logger.info("=== VALIDACIÓN DE MONTO DESHABILITADA ===")
        _logger.info("✅ El monto será procesado sin validaciones")
        
        return True

    def _validate_order_final(self, order_data):
        """
        DESHABILITAR VALIDACIÓN FINAL DE ORDEN
        """
        _logger.info("=== SALE ORDER FINAL VALIDATION DISABLED ===")
        _logger.info(f"Datos de orden: {order_data}")
        
        # LOGS FINALES
        _logger.info("=== VALIDACIÓN FINAL DE ORDEN DESHABILITADA ===")
        _logger.info("✅ Todas las validaciones de orden están deshabilitadas")
        _logger.info("✅ Solo se realizan validaciones en el frontend")
        _logger.info("✅ El backend procesará cualquier dato de orden sin restricciones")
        
        return True
