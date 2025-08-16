#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de prueba para verificar el mapeo automático de DNI/RUC al campo VAT
Este script simula la creación de partners con diferentes combinaciones de documentos
"""

import logging

# Configurar logging para ver los mensajes de depuración
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
_logger = logging.getLogger(__name__)

def test_vat_mapping():
    """
    Función de prueba para verificar el mapeo VAT
    Simula diferentes escenarios de creación de partners
    """
    print("=== INICIANDO PRUEBAS DE MAPEO VAT ===")
    print()
    
    # Escenarios de prueba
    test_cases = [
        {
            'name': 'Prueba 1: Solo DNI',
            'data': {
                'name': 'Juan Pérez',
                'dni': '12345678',
                'email': 'juan@test.com'
            },
            'expected_vat': '12345678'
        },
        {
            'name': 'Prueba 2: Solo RUC',
            'data': {
                'name': 'Empresa SAC',
                'ruc': '20123456789',
                'email': 'empresa@test.com'
            },
            'expected_vat': '20123456789'
        },
        {
            'name': 'Prueba 3: DNI y RUC (debe priorizar RUC)',
            'data': {
                'name': 'Cliente Mixto',
                'dni': '87654321',
                'ruc': '20987654321',
                'email': 'mixto@test.com'
            },
            'expected_vat': '20987654321'
        },
        {
            'name': 'Prueba 4: Solo RUC Custom',
            'data': {
                'name': 'Empresa Custom',
                'ruc_custom': '20555666777',
                'email': 'custom@test.com'
            },
            'expected_vat': '20555666777'
        },
        {
            'name': 'Prueba 5: DNI, RUC y RUC Custom (debe priorizar RUC)',
            'data': {
                'name': 'Cliente Completo',
                'dni': '11111111',
                'ruc': '20111111111',
                'ruc_custom': '20222222222',
                'email': 'completo@test.com'
            },
            'expected_vat': '20111111111'
        }
    ]
    
    # Simular la lógica de _update_vat_field
    for i, test_case in enumerate(test_cases, 1):
        print(f"--- {test_case['name']} ---")
        print(f"Datos de entrada: {test_case['data']}")
        
        # Simular el método _update_vat_field
        vals = test_case['data'].copy()
        vat_value = None
        
        # Lógica de priorización (igual que en el modelo)
        if 'ruc' in vals and vals['ruc'] and str(vals['ruc']).strip():
            vat_value = str(vals['ruc']).strip()
            print(f"✓ Capturando RUC '{vat_value}' para VAT")
        elif 'ruc_custom' in vals and vals['ruc_custom'] and str(vals['ruc_custom']).strip():
            vat_value = str(vals['ruc_custom']).strip()
            print(f"✓ Capturando RUC_CUSTOM '{vat_value}' para VAT")
        elif 'dni' in vals and vals['dni'] and str(vals['dni']).strip():
            vat_value = str(vals['dni']).strip()
            print(f"✓ Capturando DNI '{vat_value}' para VAT")
        
        # Asignar el valor capturado al VAT
        if vat_value:
            vals['vat'] = vat_value
            print(f"✓ VAT asignado: '{vat_value}'")
        else:
            print("✗ No se encontró ningún documento para mapear a VAT")
        
        # Verificar resultado
        expected = test_case['expected_vat']
        actual = vals.get('vat')
        
        if actual == expected:
            print(f"✅ ÉXITO: VAT = '{actual}' (esperado: '{expected}')")
        else:
            print(f"❌ ERROR: VAT = '{actual}' (esperado: '{expected}')")
        
        print(f"Datos finales: {vals}")
        print()
    
    print("=== PRUEBAS COMPLETADAS ===")

def test_checkout_scenarios():
    """
    Simula escenarios del checkout para verificar el flujo completo
    """
    print("\n=== SIMULANDO ESCENARIOS DE CHECKOUT ===")
    print()
    
    checkout_scenarios = [
        {
            'name': 'Checkout Boleta con DNI',
            'form_data': {
                'name': 'Cliente Boleta',
                'dni': '12345678',
                'email': 'boleta@test.com',
                'invoice_type_checkbox': 'off'
            }
        },
        {
            'name': 'Checkout Factura con RUC',
            'form_data': {
                'name': 'Empresa Factura',
                'ruc': '20123456789',
                'razon_social': 'Mi Empresa SAC',
                'email': 'factura@test.com',
                'invoice_type_checkbox': 'on'
            }
        }
    ]
    
    for scenario in checkout_scenarios:
        print(f"--- {scenario['name']} ---")
        form_data = scenario['form_data']
        print(f"Datos del formulario: {form_data}")
        
        # Simular values_preprocess
        new_values = {}
        is_invoice_requested = form_data.get('invoice_type_checkbox') == 'on'
        
        # Procesar DNI si está presente
        if 'dni' in form_data and form_data['dni']:
            new_values['dni'] = form_data['dni'].strip()
            print(f"✓ DNI procesado: {new_values['dni']}")
        
        # Procesar RUC si está presente
        if 'ruc' in form_data and form_data['ruc']:
            new_values['ruc'] = form_data['ruc'].strip()
            print(f"✓ RUC procesado: {new_values['ruc']}")
        
        # Procesar nombre/razón social
        if is_invoice_requested and 'razon_social' in form_data:
            new_values['name'] = form_data['razon_social'].strip()
            print(f"✓ Razón social como nombre: {new_values['name']}")
        else:
            new_values['name'] = form_data.get('name', '').strip()
            print(f"✓ Nombre: {new_values['name']}")
        
        new_values['email'] = form_data.get('email', '')
        new_values['invoice_type'] = 'factura' if is_invoice_requested else 'boleta'
        
        print(f"Valores procesados: {new_values}")
        
        # Simular _update_vat_field
        vat_value = None
        if 'ruc' in new_values and new_values['ruc']:
            vat_value = new_values['ruc']
        elif 'dni' in new_values and new_values['dni']:
            vat_value = new_values['dni']
        
        if vat_value:
            new_values['vat'] = vat_value
            print(f"✅ VAT final asignado: '{vat_value}'")
        else:
            print("❌ No se pudo asignar VAT")
        
        print(f"Datos finales del partner: {new_values}")
        print()

if __name__ == '__main__':
    test_vat_mapping()
    test_checkout_scenarios()
    print("\n🎉 Todas las pruebas completadas. Revise los resultados arriba.")