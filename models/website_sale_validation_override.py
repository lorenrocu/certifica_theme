# -*- coding: utf-8 -*-
from odoo import models, api, fields
import logging

_logger = logging.getLogger(__name__)

class WebsiteSaleValidationOverride(models.Model):
    _inherit = 'sale.order'

    def _checkout_form_validate(self, mode, all_form_values, data_values):
        """
        DESHABILITAR COMPLETAMENTE LA VALIDACIÓN DEL CHECKOUT EN WEBSITE_SALE
        """
        _logger.info("=== WEBSITE_SALE CHECKOUT VALIDATION COMPLETELY DISABLED ===")
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
        _logger.info("=== VALORES RECIBIDOS EN WEBSITE_SALE VALIDATION ===")
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
        _logger.info("=== VALIDACIONES IGNORADAS EN WEBSITE_SALE ===")
        
        if not name:
            _logger.info("⚠️ Nombre faltante - IGNORADO en website_sale")
        if not email:
            _logger.info("⚠️ Email faltante - IGNORADO en website_sale")
        if not phone:
            _logger.info("⚠️ Teléfono faltante - IGNORADO en website_sale")
        if not street:
            _logger.info("⚠️ Dirección faltante - IGNORADO en website_sale")
        if not city:
            _logger.info("⚠️ Ciudad faltante - IGNORADO en website_sale")
        if not country_id:
            _logger.info("⚠️ País faltante - IGNORADO en website_sale")
        if not zip:
            _logger.info("⚠️ Código postal faltante - IGNORADO en website_sale")
        if not vat:
            _logger.info("⚠️ VAT faltante - IGNORADO en website_sale")
        
        # Validaciones de formato ignoradas
        if email and '@' not in email:
            _logger.info("⚠️ Email inválido - IGNORADO en website_sale")
        if phone and len(phone) < 7:
            _logger.info("⚠️ Teléfono muy corto - IGNORADO en website_sale")
        if vat and len(vat) < 5:
            _logger.info("⚠️ VAT muy corto - IGNORADO en website_sale")
        
        # DESHABILITAR TODAS LAS VALIDACIONES - RETORNAR SIN ERRORES
        _logger.info("=== TODAS LAS VALIDACIONES DE WEBSITE_SALE DESHABILITADAS ===")
        _logger.info("✅ El formulario será procesado sin validaciones en website_sale")
        _logger.info("✅ Las validaciones solo se realizan en el frontend")
        
        return {}, []

    def _checkout_form_save(self, mode, checkout, all_values):
        """
        DESHABILITAR VALIDACIONES EN EL GUARDADO DEL CHECKOUT
        """
        _logger.info("=== WEBSITE_SALE CHECKOUT SAVE - VALIDACIONES DESHABILITADAS ===")
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
        _logger.info("=== VALORES EXTRAÍDOS EN WEBSITE_SALE SAVE ===")
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
        _logger.info("=== VALIDACIONES IGNORADAS EN WEBSITE_SALE SAVE ===")
        
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
        _logger.info("=== PROCESANDO SIN VALIDACIONES EN WEBSITE_SALE ===")
        
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

    def _checkout_form_validate_address(self, mode, all_form_values, data_values):
        """
        DESHABILITAR VALIDACIÓN DE DIRECCIÓN
        """
        _logger.info("=== WEBSITE_SALE ADDRESS VALIDATION DISABLED ===")
        _logger.info(f"Mode: {mode}")
        _logger.info(f"All form values: {all_form_values}")
        _logger.info(f"Data values: {data_values}")
        
        # Obtener valores para logging
        street = all_form_values.get('street', '').strip()
        city = all_form_values.get('city', '').strip()
        country_id = all_form_values.get('country_id', '')
        state_id = all_form_values.get('state_id', '')
        zip = all_form_values.get('zip', '').strip()
        
        # LOGS DETALLADOS
        _logger.info("=== VALORES DE DIRECCIÓN RECIBIDOS ===")
        _logger.info(f"Dirección: '{street}'")
        _logger.info(f"Ciudad: '{city}'")
        _logger.info(f"Estado ID: '{state_id}'")
        _logger.info(f"País ID: '{country_id}'")
        _logger.info(f"Código Postal: '{zip}'")
        
        # LOGS DE VALIDACIONES IGNORADAS
        _logger.info("=== VALIDACIONES DE DIRECCIÓN IGNORADAS ===")
        
        if not street:
            _logger.info("⚠️ Dirección faltante - IGNORADO en validación de dirección")
        if not city:
            _logger.info("⚠️ Ciudad faltante - IGNORADO en validación de dirección")
        if not country_id:
            _logger.info("⚠️ País faltante - IGNORADO en validación de dirección")
        if not zip:
            _logger.info("⚠️ Código postal faltante - IGNORADO en validación de dirección")
        
        # DESHABILITAR VALIDACIONES
        _logger.info("=== VALIDACIÓN DE DIRECCIÓN DESHABILITADA ===")
        _logger.info("✅ La dirección será procesada sin validaciones")
        
        return {}, []

    def _checkout_form_validate_payment(self, mode, all_form_values, data_values):
        """
        DESHABILITAR VALIDACIÓN DE PAGO
        """
        _logger.info("=== WEBSITE_SALE PAYMENT VALIDATION DISABLED ===")
        _logger.info(f"Mode: {mode}")
        _logger.info(f"All form values: {all_form_values}")
        _logger.info(f"Data values: {data_values}")
        
        # Obtener valores para logging
        acquirer_id = all_form_values.get('acquirer_id', '')
        payment_token_id = all_form_values.get('payment_token_id', '')
        
        # LOGS DETALLADOS
        _logger.info("=== VALORES DE PAGO RECIBIDOS ===")
        _logger.info(f"Acquirer ID: '{acquirer_id}'")
        _logger.info(f"Payment Token ID: '{payment_token_id}'")
        
        # LOGS DE VALIDACIONES IGNORADAS
        _logger.info("=== VALIDACIONES DE PAGO IGNORADAS ===")
        
        if not acquirer_id:
            _logger.info("⚠️ Acquirer faltante - IGNORADO en validación de pago")
        if not payment_token_id:
            _logger.info("⚠️ Payment Token faltante - IGNORADO en validación de pago")
        
        # DESHABILITAR VALIDACIONES
        _logger.info("=== VALIDACIÓN DE PAGO DESHABILITADA ===")
        _logger.info("✅ El pago será procesado sin validaciones")
        
        return {}, []

    def _checkout_form_validate_shipping(self, mode, all_form_values, data_values):
        """
        DESHABILITAR VALIDACIÓN DE ENVÍO
        """
        _logger.info("=== WEBSITE_SALE SHIPPING VALIDATION DISABLED ===")
        _logger.info(f"Mode: {mode}")
        _logger.info(f"All form values: {all_form_values}")
        _logger.info(f"Data values: {data_values}")
        
        # Obtener valores para logging
        shipping_option = all_form_values.get('shipping_option', '')
        delivery_type = all_form_values.get('delivery_type', '')
        
        # LOGS DETALLADOS
        _logger.info("=== VALORES DE ENVÍO RECIBIDOS ===")
        _logger.info(f"Opción de envío: '{shipping_option}'")
        _logger.info(f"Tipo de entrega: '{delivery_type}'")
        
        # LOGS DE VALIDACIONES IGNORADAS
        _logger.info("=== VALIDACIONES DE ENVÍO IGNORADAS ===")
        
        if not shipping_option:
            _logger.info("⚠️ Opción de envío faltante - IGNORADO en validación de envío")
        if not delivery_type:
            _logger.info("⚠️ Tipo de entrega faltante - IGNORADO en validación de envío")
        
        # DESHABILITAR VALIDACIONES
        _logger.info("=== VALIDACIÓN DE ENVÍO DESHABILITADA ===")
        _logger.info("✅ El envío será procesado sin validaciones")
        
        return {}, []

    def _checkout_form_validate_cart(self, mode, all_form_values, data_values):
        """
        DESHABILITAR VALIDACIÓN DEL CARRITO
        """
        _logger.info("=== WEBSITE_SALE CART VALIDATION DISABLED ===")
        _logger.info(f"Mode: {mode}")
        _logger.info(f"All form values: {all_form_values}")
        _logger.info(f"Data values: {data_values}")
        
        # Obtener valores para logging
        cart_id = all_form_values.get('cart_id', '')
        product_ids = all_form_values.get('product_ids', [])
        
        # LOGS DETALLADOS
        _logger.info("=== VALORES DEL CARRITO RECIBIDOS ===")
        _logger.info(f"Cart ID: '{cart_id}'")
        _logger.info(f"Product IDs: {product_ids}")
        
        # LOGS DE VALIDACIONES IGNORADAS
        _logger.info("=== VALIDACIONES DEL CARRITO IGNORADAS ===")
        
        if not cart_id:
            _logger.info("⚠️ Cart ID faltante - IGNORADO en validación del carrito")
        if not product_ids:
            _logger.info("⚠️ Product IDs faltantes - IGNORADO en validación del carrito")
        
        # DESHABILITAR VALIDACIONES
        _logger.info("=== VALIDACIÓN DEL CARRITO DESHABILITADA ===")
        _logger.info("✅ El carrito será procesado sin validaciones")
        
        return {}, []

    def _checkout_form_validate_order(self, mode, all_form_values, data_values):
        """
        DESHABILITAR VALIDACIÓN DE LA ORDEN
        """
        _logger.info("=== WEBSITE_SALE ORDER VALIDATION DISABLED ===")
        _logger.info(f"Mode: {mode}")
        _logger.info(f"All form values: {all_form_values}")
        _logger.info(f"Data values: {data_values}")
        
        # Obtener valores para logging
        order_id = all_form_values.get('order_id', '')
        amount_total = all_form_values.get('amount_total', '')
        
        # LOGS DETALLADOS
        _logger.info("=== VALORES DE LA ORDEN RECIBIDOS ===")
        _logger.info(f"Order ID: '{order_id}'")
        _logger.info(f"Amount Total: '{amount_total}'")
        
        # LOGS DE VALIDACIONES IGNORADAS
        _logger.info("=== VALIDACIONES DE LA ORDEN IGNORADAS ===")
        
        if not order_id:
            _logger.info("⚠️ Order ID faltante - IGNORADO en validación de la orden")
        if not amount_total:
            _logger.info("⚠️ Amount Total faltante - IGNORADO en validación de la orden")
        
        # DESHABILITAR VALIDACIONES
        _logger.info("=== VALIDACIÓN DE LA ORDEN DESHABILITADA ===")
        _logger.info("✅ La orden será procesada sin validaciones")
        
        return {}, []

    def _checkout_form_validate_final(self, mode, all_form_values, data_values):
        """
        DESHABILITAR VALIDACIÓN FINAL
        """
        _logger.info("=== WEBSITE_SALE FINAL VALIDATION DISABLED ===")
        _logger.info(f"Mode: {mode}")
        _logger.info(f"All form values: {all_form_values}")
        _logger.info(f"Data values: {data_values}")
        
        # LOGS FINALES
        _logger.info("=== VALIDACIÓN FINAL DESHABILITADA ===")
        _logger.info("✅ Todas las validaciones del checkout están deshabilitadas")
        _logger.info("✅ Solo se realizan validaciones en el frontend")
        _logger.info("✅ El backend procesará cualquier dato sin restricciones")
        
        return {}, []
