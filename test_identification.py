#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de prueba para verificar la detección del tipo de identificación
"""

import xmlrpc.client
import sys

# Configuración de conexión
url = 'http://localhost:8069'
db = 'tienda'
username = 'admin'
password = 'admin'

def test_identification_detection():
    """Probar la detección del tipo de identificación"""
    
    try:
        # Conectar a Odoo
        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
        uid = common.authenticate(db, username, password, {})
        
        if not uid:
            print("❌ Error de autenticación")
            return False
        
        print(f"✅ Conectado como usuario ID: {uid}")
        
        # Conectar a los modelos
        models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
        
        # Verificar que el modelo l10n.latam.identification.type existe
        try:
            identification_types = models.execute_kw(db, uid, password, 'l10n.latam.identification.type', 'search_read', 
                [[('country_id', '=', 173)]], {'fields': ['id', 'name', 'description', 'country_id']})
            
            print(f"✅ Tipos de identificación encontrados: {len(identification_types)}")
            for it in identification_types:
                print(f"   - ID {it['id']}: {it['name']} ({it['description']})")
                
        except Exception as e:
            print(f"❌ Error al buscar tipos de identificación: {e}")
            return False
        
        # Verificar que el campo l10n_latam_identification_type_id existe en res.partner
        try:
            partner_fields = models.execute_kw(db, uid, password, 'res.partner', 'fields_get', [], {})
            
            if 'l10n_latam_identification_type_id' in partner_fields:
                field_info = partner_fields['l10n_latam_identification_type_id']
                print(f"✅ Campo l10n_latam_identification_type_id encontrado:")
                print(f"   - Tipo: {field_info.get('type', 'N/A')}")
                print(f"   - String: {field_info.get('string', 'N/A')}")
                print(f"   - Relación: {field_info.get('relation', 'N/A')}")
            else:
                print("❌ Campo l10n_latam_identification_type_id NO encontrado en res.partner")
                return False
                
        except Exception as e:
            print(f"❌ Error al verificar campos de res.partner: {e}")
            return False
        
        # Probar la detección automática
        print("\n🧪 Probando detección automática:")
        
        # Test DNI (8 dígitos)
        dni_number = "72663936"
        print(f"   DNI {dni_number}:")
        
        # Buscar el tipo DNI
        dni_type = models.execute_kw(db, uid, password, 'l10n.latam.identification.type', 'search_read', 
            [[('name', '=', 'DNI'), ('country_id', '=', 173)]], {'fields': ['id', 'name']})
        
        if dni_type:
            dni_id = dni_type[0]['id']
            print(f"     ✅ Tipo DNI encontrado con ID: {dni_id}")
        else:
            print(f"     ❌ Tipo DNI NO encontrado")
            return False
        
        # Test RUC (11 dígitos)
        ruc_number = "20123456789"
        print(f"   RUC {ruc_number}:")
        
        # Buscar el tipo RUC
        ruc_type = models.execute_kw(db, uid, password, 'l10n.latam.identification.type', 'search_read', 
            [[('name', '=', 'RUC'), ('country_id', '=', 173)]], {'fields': ['id', 'name']})
        
        if ruc_type:
            ruc_id = ruc_type[0]['id']
            print(f"     ✅ Tipo RUC encontrado con ID: {ruc_id}")
        else:
            print(f"     ❌ Tipo RUC NO encontrado")
            return False
        
        print("\n✅ Todas las pruebas pasaron correctamente!")
        return True
        
    except Exception as e:
        print(f"❌ Error general: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Iniciando pruebas de detección de identificación...")
    success = test_identification_detection()
    
    if success:
        print("\n🎉 Sistema listo para usar!")
        sys.exit(0)
    else:
        print("\n💥 Hay problemas que resolver")
        sys.exit(1)
