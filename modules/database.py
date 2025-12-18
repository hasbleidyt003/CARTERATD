# modules/databases.py
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import streamlit as st
import json
from pathlib import Path

class DatabaseManager:
    """Gestor robusto de base de datos con soporte para autorizaciones parciales"""
    
    def __init__(self, db_path="database.db"):
        self.db_path = db_path
        self.conn = None
        self.connect()
        self._backup_database()
    
    def connect(self):
        """Conectar a la base de datos con manejo de errores"""
        try:
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row
            self.conn.execute("PRAGMA foreign_keys = ON")
            self.conn.execute("PRAGMA journal_mode = WAL")
            self.conn.execute("PRAGMA synchronous = NORMAL")
            self.conn.execute("PRAGMA cache_size = -2000")
            
            # Crear todas las tablas
            self.create_tables()
            
            # Verificar integridad
            self._check_database_integrity()
            
            st.session_state.db_connected = True
            return True
            
        except sqlite3.Error as e:
            st.error(f"❌ Error conectando a la base de datos: {str(e)}")
            st.session_state.db_connected = False
            return False
    
    def _backup_database(self):
        """Crear backup de la base de datos"""
        try:
            backup_path = f"backups/db_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            Path("backups").mkdir(exist_ok=True)
            
            backup_conn = sqlite3.connect(backup_path)
            self.conn.backup(backup_conn)
            backup_conn.close()
            
            # Mantener solo los últimos 7 backups
            backups = sorted(Path("backups").glob("db_backup_*.db"))
            if len(backups) > 7:
                for old_backup in backups[:-7]:
                    old_backup.unlink()
                    
        except Exception as e:
            print(f"⚠️ No se pudo crear backup: {e}")
    
    def _check_database_integrity(self):
        """Verificar integridad de la base de datos"""
        try:
            result = self.conn.execute("PRAGMA integrity_check").fetchone()
            if result[0] != "ok":
                st.warning(f"⚠️ Problemas de integridad en la base de datos: {result[0]}")
                return False
            return True
        except Exception as e:
            print(f"⚠️ Error verificando integridad: {e}")
            return False
    
    def create_tables(self):
        """Crear todas las tablas del sistema"""
        cursor = self.conn.cursor()
        
        # Tabla de clientes
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo VARCHAR(20) UNIQUE NOT NULL,
            nombre VARCHAR(200) NOT NULL,
            nit VARCHAR(20) NOT NULL,
            direccion TEXT,
            telefono VARCHAR(20),
            email VARCHAR(100),
            contacto_principal VARCHAR(100),
            telefono_contacto VARCHAR(20),
            limite_credito DECIMAL(15,2) DEFAULT 0,
            saldo_actual DECIMAL(15,2) DEFAULT 0,
            dias_credito INTEGER DEFAULT 30,
            categoria VARCHAR(50),
            activo BOOLEAN DEFAULT 1,
            fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            notas TEXT,
            creado_por INTEGER,
            actualizado_por INTEGER,
            fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (creado_por) REFERENCES usuarios(id),
            FOREIGN KEY (actualizado_por) REFERENCES usuarios(id)
        )
        ''')
        
        # Tabla de Órdenes de Compra
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS ordenes_compra (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero_oc VARCHAR(50) UNIQUE NOT NULL,
            cliente_id INTEGER NOT NULL,
            tipo_oc VARCHAR(20) DEFAULT 'NORMAL', -- NORMAL, URGENTE, ESPECIAL
            valor_total DECIMAL(15,2) NOT NULL,
            valor_autorizado DECIMAL(15,2) DEFAULT 0,
            valor_pendiente DECIMAL(15,2) NOT NULL,
            valor_retenido DECIMAL(15,2) DEFAULT 0,
            valor_facturado DECIMAL(15,2) DEFAULT 0,
            valor_pagado DECIMAL(15,2) DEFAULT 0,
            estado VARCHAR(20) DEFAULT 'PENDIENTE', -- PENDIENTE, PARCIAL, COMPLETADA, ANULADA
            fecha_oc DATE NOT NULL,
            fecha_vencimiento DATE,
            fecha_entrega_estimada DATE,
            prioridad INTEGER DEFAULT 3, -- 1: Alta, 2: Media, 3: Baja
            moneda VARCHAR(3) DEFAULT 'COP',
            tasa_cambio DECIMAL(10,4) DEFAULT 1,
            plazo_entrega INTEGER,
            condiciones_pago TEXT,
            centro_costo VARCHAR(50),
            proyecto VARCHAR(100),
            motivo TEXT,
            observaciones TEXT,
            archivo_url TEXT,
            creado_por INTEGER,
            aprobado_por INTEGER,
            fecha_aprobacion TIMESTAMP,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (cliente_id) REFERENCES clientes(id),
            FOREIGN KEY (creado_por) REFERENCES usuarios(id),
            FOREIGN KEY (aprobado_por) REFERENCES usuarios(id),
            CHECK (valor_total >= 0),
            CHECK (valor_autorizado >= 0),
            CHECK (valor_pendiente >= 0),
            CHECK (valor_total = valor_autorizado + valor_pendiente)
        )
        ''')
        
        # Índices para ordenes_compra
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_oc_cliente ON ordenes_compra(cliente_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_oc_estado ON ordenes_compra(estado)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_oc_fecha ON ordenes_compra(fecha_oc)')
        
        # Tabla de autorizaciones parciales
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS autorizaciones_parciales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            oc_id INTEGER NOT NULL,
            numero_parcial VARCHAR(50) NOT NULL,
            valor_autorizado DECIMAL(15,2) NOT NULL,
            porcentaje_autorizado DECIMAL(5,2) NOT NULL,
            motivo TEXT,
            usuario_id INTEGER NOT NULL,
            fecha_autorizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            estado_anterior VARCHAR(20),
            estado_nuevo VARCHAR(20),
            ip_autorizacion VARCHAR(45),
            dispositivo TEXT,
            FOREIGN KEY (oc_id) REFERENCES ordenes_compra(id) ON DELETE CASCADE,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
            UNIQUE(oc_id, numero_parcial)
        )
        ''')
        
        # Tabla de historial de OCs
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS historial_ocs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            oc_id INTEGER NOT NULL,
            accion VARCHAR(50) NOT NULL, -- AUTORIZACION, MODIFICACION, ANULACION, ETC
            descripcion TEXT NOT NULL,
            valor_anterior DECIMAL(15,2),
            valor_nuevo DECIMAL(15,2),
            estado_anterior VARCHAR(20),
            estado_nuevo VARCHAR(20),
            usuario_id INTEGER,
            ip_address VARCHAR(45),
            dispositivo TEXT,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            metadata JSON,
            FOREIGN KEY (oc_id) REFERENCES ordenes_compra(id) ON DELETE CASCADE,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        )
        ''')
        
        # Tabla de items de OC
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS oc_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            oc_id INTEGER NOT NULL,
            item_numero INTEGER NOT NULL,
            codigo_producto VARCHAR(50),
            descripcion TEXT NOT NULL,
            unidad_medida VARCHAR(20),
            cantidad DECIMAL(10,3) NOT NULL,
            precio_unitario DECIMAL(15,2) NOT NULL,
            valor_total
