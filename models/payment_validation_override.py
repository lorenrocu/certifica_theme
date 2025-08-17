# -*- coding: utf-8 -*-
from odoo import models, api, fields
import logging

_logger = logging.getLogger(__name__)

class PaymentValidationOverride(models.Model):
    _inherit = 'payment.acquirer'

    def _validate_payment_data(self, data):
        """
        DESHABILITAR VALIDACIÓN DE DATOS DE PAGO
        """
        _logger.info("=== PAYMENT DATA VALIDATION DISABLED ===")
        _logger.info(f"Data recibida: {data}")
        
        # Obtener valores para logging
        amount = data.get('amount', '')
        currency_id = data.get('currency_id', '')
        partner_id = data.get('partner_id', '')
        reference = data.get('reference', '')
        
        # LOGS DETALLADOS
        _logger.info("=== VALORES DE PAGO RECIBIDOS ===")
        _logger.info(f"Monto: '{amount}'")
        _logger.info(f"Moneda ID: '{currency_id}'")
        _logger.info(f"Partner ID: '{partner_id}'")
        _logger.info(f"Referencia: '{reference}'")
        
        # LOGS DE VALIDACIONES IGNORADAS
        _logger.info("=== VALIDACIONES DE PAGO IGNORADAS ===")
        
        if not amount:
            _logger.info("⚠️ Monto faltante - IGNORADO en validación de pago")
        if not currency_id:
            _logger.info("⚠️ Moneda faltante - IGNORADO en validación de pago")
        if not partner_id:
            _logger.info("⚠️ Partner faltante - IGNORADO en validación de pago")
        if not reference:
            _logger.info("⚠️ Referencia faltante - IGNORADO en validación de pago")
        
        # Validaciones de formato ignoradas
        if amount and float(amount) <= 0:
            _logger.info("⚠️ Monto inválido (<= 0) - IGNORADO en validación de pago")
        if currency_id and not str(currency_id).isdigit():
            _logger.info("⚠️ Moneda ID inválido - IGNORADO en validación de pago")
        if partner_id and not str(partner_id).isdigit():
            _logger.info("⚠️ Partner ID inválido - IGNORADO en validación de pago")
        
        # DESHABILITAR VALIDACIONES
        _logger.info("=== VALIDACIÓN DE PAGO DESHABILITADA ===")
        _logger.info("✅ El pago será procesado sin validaciones")
        
        return True

    def _validate_transaction_data(self, data):
        """
        DESHABILITAR VALIDACIÓN DE DATOS DE TRANSACCIÓN
        """
        _logger.info("=== PAYMENT TRANSACTION VALIDATION DISABLED ===")
        _logger.info(f"Data de transacción: {data}")
        
        # Obtener valores para logging
        acquirer_id = data.get('acquirer_id', '')
        amount = data.get('amount', '')
        currency_id = data.get('currency_id', '')
        partner_id = data.get('partner_id', '')
        reference = data.get('reference', '')
        
        # LOGS DETALLADOS
        _logger.info("=== VALORES DE TRANSACCIÓN RECIBIDOS ===")
        _logger.info(f"Acquirer ID: '{acquirer_id}'")
        _logger.info(f"Monto: '{amount}'")
        _logger.info(f"Moneda ID: '{currency_id}'")
        _logger.info(f"Partner ID: '{partner_id}'")
        _logger.info(f"Referencia: '{reference}'")
        
        # LOGS DE VALIDACIONES IGNORADAS
        _logger.info("=== VALIDACIONES DE TRANSACCIÓN IGNORADAS ===")
        
        if not acquirer_id:
            _logger.info("⚠️ Acquirer ID faltante - IGNORADO en validación de transacción")
        if not amount:
            _logger.info("⚠️ Monto faltante - IGNORADO en validación de transacción")
        if not currency_id:
            _logger.info("⚠️ Moneda faltante - IGNORADO en validación de transacción")
        if not partner_id:
            _logger.info("⚠️ Partner faltante - IGNORADO en validación de transacción")
        if not reference:
            _logger.info("⚠️ Referencia faltante - IGNORADO en validación de transacción")
        
        # DESHABILITAR VALIDACIONES
        _logger.info("=== VALIDACIÓN DE TRANSACCIÓN DESHABILITADA ===")
        _logger.info("✅ La transacción será procesada sin validaciones")
        
        return True

    def _validate_payment_method(self, payment_method):
        """
        DESHABILITAR VALIDACIÓN DE MÉTODO DE PAGO
        """
        _logger.info("=== PAYMENT METHOD VALIDATION DISABLED ===")
        _logger.info(f"Método de pago: {payment_method}")
        
        # LOGS DE VALIDACIONES IGNORADAS
        _logger.info("=== VALIDACIONES DE MÉTODO DE PAGO IGNORADAS ===")
        
        if not payment_method:
            _logger.info("⚠️ Método de pago faltante - IGNORADO en validación")
        if payment_method and payment_method not in ['card', 'bank', 'cash', 'transfer']:
            _logger.info(f"⚠️ Método de pago inválido '{payment_method}' - IGNORADO en validación")
        
        # DESHABILITAR VALIDACIONES
        _logger.info("=== VALIDACIÓN DE MÉTODO DE PAGO DESHABILITADA ===")
        _logger.info("✅ El método de pago será procesado sin validaciones")
        
        return True

    def _validate_card_data(self, card_data):
        """
        DESHABILITAR VALIDACIÓN DE DATOS DE TARJETA
        """
        _logger.info("=== CARD DATA VALIDATION DISABLED ===")
        _logger.info(f"Datos de tarjeta: {card_data}")
        
        # Obtener valores para logging
        card_number = card_data.get('card_number', '')
        expiry_month = card_data.get('expiry_month', '')
        expiry_year = card_data.get('expiry_year', '')
        cvv = card_data.get('cvv', '')
        holder_name = card_data.get('holder_name', '')
        
        # LOGS DETALLADOS
        _logger.info("=== VALORES DE TARJETA RECIBIDOS ===")
        _logger.info(f"Número: '{card_number}'")
        _logger.info(f"Mes expiración: '{expiry_month}'")
        _logger.info(f"Año expiración: '{expiry_year}'")
        _logger.info(f"CVV: '{cvv}'")
        _logger.info(f"Nombre titular: '{holder_name}'")
        
        # LOGS DE VALIDACIONES IGNORADAS
        _logger.info("=== VALIDACIONES DE TARJETA IGNORADAS ===")
        
        if not card_number:
            _logger.info("⚠️ Número de tarjeta faltante - IGNORADO en validación")
        if not expiry_month:
            _logger.info("⚠️ Mes de expiración faltante - IGNORADO en validación")
        if not expiry_year:
            _logger.info("⚠️ Año de expiración faltante - IGNORADO en validación")
        if not cvv:
            _logger.info("⚠️ CVV faltante - IGNORADO en validación")
        if not holder_name:
            _logger.info("⚠️ Nombre del titular faltante - IGNORADO en validación")
        
        # Validaciones de formato ignoradas
        if card_number and len(card_number) < 13:
            _logger.info("⚠️ Número de tarjeta muy corto - IGNORADO en validación")
        if expiry_month and (int(expiry_month) < 1 or int(expiry_month) > 12):
            _logger.info("⚠️ Mes de expiración inválido - IGNORADO en validación")
        if expiry_year and int(expiry_year) < 2020:
            _logger.info("⚠️ Año de expiración inválido - IGNORADO en validación")
        if cvv and len(cvv) < 3:
            _logger.info("⚠️ CVV muy corto - IGNORADO en validación")
        
        # DESHABILITAR VALIDACIONES
        _logger.info("=== VALIDACIÓN DE TARJETA DESHABILITADA ===")
        _logger.info("✅ Los datos de tarjeta serán procesados sin validaciones")
        
        return True

    def _validate_bank_data(self, bank_data):
        """
        DESHABILITAR VALIDACIÓN DE DATOS BANCARIOS
        """
        _logger.info("=== BANK DATA VALIDATION DISABLED ===")
        _logger.info(f"Datos bancarios: {bank_data}")
        
        # Obtener valores para logging
        account_number = bank_data.get('account_number', '')
        routing_number = bank_data.get('routing_number', '')
        account_type = bank_data.get('account_type', '')
        holder_name = bank_data.get('holder_name', '')
        
        # LOGS DETALLADOS
        _logger.info("=== VALORES BANCARIOS RECIBIDOS ===")
        _logger.info(f"Número de cuenta: '{account_number}'")
        _logger.info(f"Número de routing: '{routing_number}'")
        _logger.info(f"Tipo de cuenta: '{account_type}'")
        _logger.info(f"Nombre del titular: '{holder_name}'")
        
        # LOGS DE VALIDACIONES IGNORADAS
        _logger.info("=== VALIDACIONES BANCARIAS IGNORADAS ===")
        
        if not account_number:
            _logger.info("⚠️ Número de cuenta faltante - IGNORADO en validación")
        if not routing_number:
            _logger.info("⚠️ Número de routing faltante - IGNORADO en validación")
        if not account_type:
            _logger.info("⚠️ Tipo de cuenta faltante - IGNORADO en validación")
        if not holder_name:
            _logger.info("⚠️ Nombre del titular faltante - IGNORADO en validación")
        
        # DESHABILITAR VALIDACIONES
        _logger.info("=== VALIDACIÓN BANCARIA DESHABILITADA ===")
        _logger.info("✅ Los datos bancarios serán procesados sin validaciones")
        
        return True

    def _validate_payment_amount(self, amount, currency):
        """
        DESHABILITAR VALIDACIÓN DE MONTO DE PAGO
        """
        _logger.info("=== PAYMENT AMOUNT VALIDATION DISABLED ===")
        _logger.info(f"Monto: {amount}, Moneda: {currency}")
        
        # LOGS DE VALIDACIONES IGNORADAS
        _logger.info("=== VALIDACIONES DE MONTO IGNORADAS ===")
        
        if not amount:
            _logger.info("⚠️ Monto faltante - IGNORADO en validación")
        if amount and float(amount) <= 0:
            _logger.info("⚠️ Monto inválido (<= 0) - IGNORADO en validación")
        if amount and float(amount) > 999999999:
            _logger.info("⚠️ Monto muy alto - IGNORADO en validación")
        if not currency:
            _logger.info("⚠️ Moneda faltante - IGNORADO en validación")
        
        # DESHABILITAR VALIDACIONES
        _logger.info("=== VALIDACIÓN DE MONTO DESHABILITADA ===")
        _logger.info("✅ El monto será procesado sin validaciones")
        
        return True

    def _validate_payment_currency(self, currency):
        """
        DESHABILITAR VALIDACIÓN DE MONEDA DE PAGO
        """
        _logger.info("=== PAYMENT CURRENCY VALIDATION DISABLED ===")
        _logger.info(f"Moneda: {currency}")
        
        # LOGS DE VALIDACIONES IGNORADAS
        _logger.info("=== VALIDACIONES DE MONEDA IGNORADAS ===")
        
        if not currency:
            _logger.info("⚠️ Moneda faltante - IGNORADO en validación")
        if currency and not str(currency).isdigit():
            _logger.info("⚠️ Moneda ID inválido - IGNORADO en validación")
        
        # DESHABILITAR VALIDACIONES
        _logger.info("=== VALIDACIÓN DE MONEDA DESHABILITADA ===")
        _logger.info("✅ La moneda será procesada sin validaciones")
        
        return True

    def _validate_payment_partner(self, partner):
        """
        DESHABILITAR VALIDACIÓN DE PARTNER DE PAGO
        """
        _logger.info("=== PAYMENT PARTNER VALIDATION DISABLED ===")
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

    def _validate_payment_reference(self, reference):
        """
        DESHABILITAR VALIDACIÓN DE REFERENCIA DE PAGO
        """
        _logger.info("=== PAYMENT REFERENCE VALIDATION DISABLED ===")
        _logger.info(f"Referencia: {reference}")
        
        # LOGS DE VALIDACIONES IGNORADAS
        _logger.info("=== VALIDACIONES DE REFERENCIA IGNORADAS ===")
        
        if not reference:
            _logger.info("⚠️ Referencia faltante - IGNORADO en validación")
        if reference and len(reference) < 3:
            _logger.info("⚠️ Referencia muy corta - IGNORADO en validación")
        if reference and len(reference) > 100:
            _logger.info("⚠️ Referencia muy larga - IGNORADO en validación")
        
        # DESHABILITAR VALIDACIONES
        _logger.info("=== VALIDACIÓN DE REFERENCIA DESHABILITADA ===")
        _logger.info("✅ La referencia será procesada sin validaciones")
        
        return True

    def _validate_payment_final(self, payment_data):
        """
        DESHABILITAR VALIDACIÓN FINAL DE PAGO
        """
        _logger.info("=== PAYMENT FINAL VALIDATION DISABLED ===")
        _logger.info(f"Datos de pago: {payment_data}")
        
        # LOGS FINALES
        _logger.info("=== VALIDACIÓN FINAL DE PAGO DESHABILITADA ===")
        _logger.info("✅ Todas las validaciones de pago están deshabilitadas")
        _logger.info("✅ Solo se realizan validaciones en el frontend")
        _logger.info("✅ El backend procesará cualquier dato de pago sin restricciones")
        
        return True
