#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de limpieza de emergencia para problemas de transacción de base de datos en Odoo
"""

import psycopg2
import sys
import os
from datetime import datetime

def cleanup_database(database_name, host='localhost', port=5432, user='odoo', password='odoo'):
    """
    Limpiar transacciones corruptas en la base de datos
    """
    print(f"🔧 Iniciando limpieza de emergencia para base de datos: {database_name}")
    print(f"⏰ Fecha y hora: {datetime.now()}")
    
    try:
        # Conectar a la base de datos
        conn = psycopg2.connect(
            host=host,
            port=port,
            database=database_name,
            user=user,
            password=password
        )
        
        # Crear cursor
        cur = conn.cursor()
        
        print("✅ Conexión a base de datos establecida")
        
        # 1. Terminar todas las transacciones activas
        print("🔄 Terminando transacciones activas...")
        cur.execute("""
            SELECT pid, usename, application_name, state, query_start, query
            FROM pg_stat_activity 
            WHERE state = 'active' 
            AND pid != pg_backend_pid()
            AND datname = %s
        """, (database_name,))
        
        active_transactions = cur.fetchall()
        print(f"📊 Transacciones activas encontradas: {len(active_transactions)}")
        
        for transaction in active_transactions:
            pid, username, app, state, start_time, query = transaction
            print(f"   - PID {pid}: {username} ({app}) - {state}")
            if query:
                print(f"     Query: {query[:100]}...")
        
        # 2. Terminar transacciones problemáticas (más de 5 minutos)
        print("⏰ Terminando transacciones antiguas...")
        cur.execute("""
            SELECT pid FROM pg_stat_activity 
            WHERE state = 'active' 
            AND pid != pg_backend_pid()
            AND datname = %s
            AND query_start < NOW() - INTERVAL '5 minutes'
        """, (database_name,))
        
        old_transactions = cur.fetchall()
        for old_tx in old_transactions:
            pid = old_tx[0]
            try:
                cur.execute("SELECT pg_terminate_backend(%s)", (pid,))
                print(f"   ✅ Transacción {pid} terminada")
            except Exception as e:
                print(f"   ❌ Error al terminar transacción {pid}: {e}")
        
        # 3. Verificar y limpiar locks
        print("🔒 Verificando locks de base de datos...")
        cur.execute("""
            SELECT locktype, database, relation::regclass, mode, granted
            FROM pg_locks l
            JOIN pg_database d ON l.database = d.oid
            WHERE d.datname = %s
        """, (database_name,))
        
        locks = cur.fetchall()
        print(f"📊 Locks encontrados: {len(locks)}")
        
        for lock in locks:
            locktype, db, relation, mode, granted = lock
            print(f"   - {locktype}: {relation} - {mode} ({'Granted' if granted else 'Waiting'})")
        
        # 4. Limpiar caché de vistas si es necesario
        print("🧹 Limpiando caché de vistas...")
        try:
            cur.execute("""
                DELETE FROM ir_ui_view WHERE active = false
            """)
            deleted_views = cur.fetchone()[0] if cur.rowcount > 0 else 0
            print(f"   ✅ {deleted_views} vistas inactivas eliminadas")
        except Exception as e:
            print(f"   ⚠️ No se pudieron limpiar vistas: {e}")
        
        # 5. Verificar integridad de la base de datos
        print("🔍 Verificando integridad de la base de datos...")
        cur.execute("""
            SELECT schemaname, tablename, attname, n_distinct, correlation
            FROM pg_stats 
            WHERE schemaname NOT IN ('information_schema', 'pg_catalog')
            AND tablename LIKE 'ir_%'
            LIMIT 10
        """)
        
        stats = cur.fetchall()
        print(f"📊 Estadísticas de tablas del sistema: {len(stats)}")
        
        # 6. Commit de la limpieza
        conn.commit()
        print("✅ Limpieza completada y commit realizado")
        
        # 7. Verificar estado final
        print("🔍 Verificando estado final...")
        cur.execute("""
            SELECT COUNT(*) as active_connections
            FROM pg_stat_activity 
            WHERE state = 'active' 
            AND datname = %s
        """, (database_name,))
        
        active_count = cur.fetchone()[0]
        print(f"📊 Conexiones activas restantes: {active_count}")
        
        # Cerrar conexión
        cur.close()
        conn.close()
        
        print("✅ Limpieza de emergencia completada exitosamente")
        return True
        
    except Exception as e:
        print(f"❌ Error durante la limpieza: {e}")
        return False

def main():
    """
    Función principal
    """
    print("🚨 SCRIPT DE LIMPIEZA DE EMERGENCIA PARA ODOO")
    print("=" * 50)
    
    # Configuración por defecto
    database_name = os.environ.get('ODOO_DB', 'tienda')
    host = os.environ.get('ODOO_HOST', 'localhost')
    port = int(os.environ.get('ODOO_PORT', 5432))
    user = os.environ.get('ODOO_USER', 'odoo')
    password = os.environ.get('ODOO_PASSWORD', 'odoo')
    
    print(f"📋 Configuración:")
    print(f"   - Base de datos: {database_name}")
    print(f"   - Host: {host}:{port}")
    print(f"   - Usuario: {user}")
    
    # Confirmar antes de proceder
    confirm = input("\n⚠️ ¿Estás seguro de que quieres proceder con la limpieza? (s/N): ")
    if confirm.lower() != 's':
        print("❌ Operación cancelada por el usuario")
        sys.exit(0)
    
    # Ejecutar limpieza
    success = cleanup_database(database_name, host, port, user, password)
    
    if success:
        print("\n🎉 LIMPIEZA COMPLETADA EXITOSAMENTE")
        print("💡 Recomendaciones:")
        print("   1. Reinicia el servicio de Odoo")
        print("   2. Verifica los logs del servidor")
        print("   3. Prueba el checkout nuevamente")
    else:
        print("\n💥 LA LIMPIEZA FALLÓ")
        print("💡 Acciones recomendadas:")
        print("   1. Verifica la conectividad a la base de datos")
        print("   2. Revisa los permisos del usuario")
        print("   3. Contacta al administrador de la base de datos")
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
