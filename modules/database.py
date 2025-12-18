"""
Sistema de Base de Datos Avanzado para Gestión de Cupos TD
Versión Profesional - Robusta y Optimizada
"""

import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
from contextlib import contextmanager
import json
from config import config

# ============================================================================
# MANEJO DE CONEXIONES CON CONTEXT MANAGER
# ============================================================================

@contextmanager
def get_connection():
    """Context manager para manejo seguro de conexiones"""
    conn = None
    try:
        conn = sqlite3.connect(config.DATABASE_PATH, timeout=30)
        conn.row_factory = sqlite3.Row  # Para acceder por nombre de columna
        yield conn
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        raise
    finally:
        if conn:
            conn.close()

# ============================================================================
# INICIALIZACIÓN DE BASE DE DATOS AVANZADA
# ============================================================================

def init_database():
    """Inicializa la base de datos con estructura avanzada"""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            
            # ===== TABLA CLIENTES (ESTRUCTURA AVANZADA) =====
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS clientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nit TEXT UNIQUE NOT NULL,
                nombre TEXT NOT NULL,
                total_cartera DECIMAL(15,2) DEFAULT 0,
                cupo_sugerido DECIMAL(15,2) DEFAULT 0,
                disponible DECIMAL(15,2) DEFAULT 0,
                porcentaje_uso DECIMAL(5,2) GENERATED ALWAYS AS (
                    CASE 
                        WHEN cupo_sugerido > 0 
                        THEN ROUND((total_cartera * 100.0 / cupo_sugerido), 2)
                        ELSE 0 
                    END
                ),
                estado_cupo TEXT GENERATED ALWAYS AS (
                    CASE 
                        WHEN total_cartera > cupo_sugerido THEN 'SOBREPASADO'
                        WHEN ROUND((total_cartera * 100.0 / cupo_sugerido), 2) > 90 THEN 'ALTO'
                        WHEN ROUND((total_cartera * 100.0 / cupo_sugerido), 2) > 70 THEN 'MEDIO'
                        ELSE 'NORMAL'
                    END
                ),
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                activo BOOLEAN DEFAULT 1,
                notas TEXT,
                contacto_email TEXT,
                contacto_telefono TEXT
            )
            ''')
            
            # ===== TABLA ÓRDENES DE COMPRA (OCS) - SISTEMA ROBUSTO =====
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS ocs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cliente_nit TEXT NOT NULL,
                numero_oc TEXT UNIQUE NOT NULL,
                proveedor TEXT,
                valor_total DECIMAL(15,2) NOT NULL,
                valor_autorizado DECIMAL(15,2) DEFAULT 0,
                valor_pendiente DECIMAL(15,2) GENERATED ALWAYS AS (valor_total - valor_autorizado),
                
                -- Estados del sistema
                estado_oc TEXT CHECK(estado_oc IN ('PENDIENTE', 'PARCIAL', 'AUTORIZADA', 'RECHAZADA', 'ANULADA')) DEFAULT 'PENDIENTE',
                tipo_oc TEXT CHECK(tipo_oc IN ('NORMAL', 'URGENTE', 'CUPO_NUEVO')) DEFAULT 'NORMAL',
                prioridad TEXT CHECK(prioridad IN ('BAJA', 'MEDIA', 'ALTA', 'CRITICA')) DEFAULT 'MEDIA',
                
                -- Información detallada
                descripcion TEXT,
                centro_costo TEXT,
                proyecto TEXT,
                area TEXT,
                
                -- Fechas importantes
                fecha_solicitud DATE,
                fecha_requerida DATE,
                fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                fecha_ultima_autorizacion TIMESTAMP,
                fecha_cierre TIMESTAMP,
                
                -- Control de cambios
                usuario_creacion TEXT DEFAULT 'Sistema',
                usuario_ultima_modificacion TEXT,
                version INTEGER DEFAULT 1,
                
                -- Campos adicionales
                adjuntos_url TEXT,
                referencia_cupo TEXT,
                observaciones TEXT,
                
                -- Índices para optimización
                FOREIGN KEY (cliente_nit) REFERENCES clientes(nit) ON DELETE CASCADE,
                CHECK (valor_total >= 0),
                CHECK (valor_autorizado >= 0 AND valor_autorizado <= valor_total)
            )
            ''')
            
            # ===== TABLA HISTORIAL DE AUTORIZACIONES =====
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS autorizaciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                oc_id INTEGER NOT NULL,
                tipo_autorizacion TEXT CHECK(tipo_autorizacion IN ('PARCIAL', 'TOTAL', 'RECHAZO')) NOT NULL,
                valor_autorizado DECIMAL(15,2) NOT NULL,
                nivel_autorizacion INTEGER DEFAULT 1,
                usuario_autorizador TEXT NOT NULL,
                departamento TEXT,
                fecha_autorizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                comentarios TEXT,
                estado_anterior TEXT,
                estado_nuevo TEXT,
                ip_address TEXT,
                dispositivo TEXT,
                
                FOREIGN KEY (oc_id) REFERENCES ocs(id) ON DELETE CASCADE
            )
            ''')
            
            # ===== TABLA SEGUIMIENTO DE CUPOS =====
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS seguimiento_cupos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cliente_nit TEXT NOT NULL,
                fecha_seguimiento DATE NOT NULL,
                total_cartera_inicial DECIMAL(15,2),
                cupo_sugerido_inicial DECIMAL(15,2),
                disponible_inicial DECIMAL(15,2),
                ocs_pendientes_count INTEGER DEFAULT 0,
                ocs_pendientes_valor DECIMAL(15,2) DEFAULT 0,
                ocs_autorizadas_count INTEGER DEFAULT 0,
                ocs_autorizadas_valor DECIMAL(15,2) DEFAULT 0,
                variacion_cartera DECIMAL(15,2) DEFAULT 0,
                tendencia TEXT,
                alertas_generadas TEXT,
                
                UNIQUE(cliente_nit, fecha_seguimiento),
                FOREIGN KEY (cliente_nit) REFERENCES clientes(nit) ON DELETE CASCADE
            )
            ''')
            
            # ===== TABLA PARÁMETROS DEL SISTEMA =====
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS parametros_sistema (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                clave TEXT UNIQUE NOT NULL,
                valor TEXT NOT NULL,
                tipo TEXT CHECK(tipo IN ('TEXTO', 'NUMERO', 'BOOLEAN', 'JSON', 'FECHA')),
                descripcion TEXT,
                categoria TEXT,
                editable BOOLEAN DEFAULT 1,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                usuario_modificacion TEXT
            )
            ''')
            
            # ===== TABLA LOG DE ACTIVIDAD =====
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS log_actividad (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                usuario TEXT,
                modulo TEXT,
                accion TEXT,
                entidad TEXT,
                entidad_id TEXT,
                detalles TEXT,
                ip_address TEXT,
                user_agent TEXT,
                nivel TEXT CHECK(nivel IN ('INFO', 'WARNING', 'ERROR', 'CRITICAL'))
            )
            ''')
            
            # ===== INSERTAR CLIENTES INICIALES =====
            cursor.execute("SELECT COUNT(*) FROM clientes")
            if cursor.fetchone()[0] == 0:
                for cliente in config.CLIENTES_INICIALES:
                    cursor.execute('''
                    INSERT INTO clientes (nit, nombre, total_cartera, cupo_sugerido, disponible)
                    VALUES (?, ?, ?, ?, ?)
                    ''', (
                        cliente['nit'],
                        cliente['nombre'],
                        cliente['total_cartera'],
                        cliente['cupo_sugerido'],
                        cliente['disponible']
                    ))
                
                # Insertar parámetros del sistema
                parametros = [
                    ('limite_alerta_cupo', '90', 'NUMERO', 'Porcentaje para alertas de cupo', 'SEGURIDAD'),
                    ('limite_critico_cupo', '100', 'NUMERO', 'Porcentaje crítico de cupo', 'SEGURIDAD'),
                    ('dias_retroactivo_ocs', '30', 'NUMERO', 'Días para mostrar OCs retroactivas', 'CONFIG'),
                    ('notificaciones_activas', 'true', 'BOOLEAN', 'Activar notificaciones', 'SISTEMA'),
                    ('version_sistema', config.APP_VERSION, 'TEXTO', 'Versión del sistema', 'SISTEMA'),
                ]
                
                cursor.executemany('''
                INSERT INTO parametros_sistema (clave, valor, tipo, descripcion, categoria)
                VALUES (?, ?, ?, ?, ?)
                ''', parametros)
            
            # ===== CREAR ÍNDICES PARA OPTIMIZACIÓN =====
            indices = [
                "CREATE INDEX IF NOT EXISTS idx_clientes_nit ON clientes(nit)",
                "CREATE INDEX IF NOT EXISTS idx_clientes_estado ON clientes(estado_cupo)",
                "CREATE INDEX IF NOT EXISTS idx_ocs_cliente ON ocs(cliente_nit)",
                "CREATE INDEX IF NOT EXISTS idx_ocs_estado ON ocs(estado_oc)",
                "CREATE INDEX IF NOT EXISTS idx_ocs_fecha ON ocs(fecha_registro)",
                "CREATE INDEX IF NOT EXISTS idx_ocs_numero ON ocs(numero_oc)",
                "CREATE INDEX IF NOT EXISTS idx_autorizaciones_oc ON autorizaciones(oc_id)",
                "CREATE INDEX IF NOT EXISTS idx_autorizaciones_fecha ON autorizaciones(fecha_autorizacion)",
                "CREATE INDEX IF NOT EXISTS idx_seguimiento_cliente ON seguimiento_cupos(cliente_nit)",
                "CREATE INDEX IF NOT EXISTS idx_seguimiento_fecha ON seguimiento_cupos(fecha_seguimiento)",
                "CREATE INDEX IF NOT EXISTS idx_log_fecha ON log_actividad(fecha)",
                "CREATE INDEX IF NOT EXISTS idx_log_usuario ON log_actividad(usuario)",
            ]
            
            for indice in indices:
                cursor.execute(indice)
            
            conn.commit()
            print("✅ Base de datos inicializada exitosamente")
            
    except Exception as e:
        print(f"❌ Error al inicializar base de datos: {e}")
        raise

# ============================================================================
# SISTEMA DE LOGGING AVANZADO
# ============================================================================

def log_actividad(usuario, modulo, accion, entidad, entidad_id=None, detalles="", nivel="INFO"):
    """Registra actividad en el sistema"""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
            INSERT INTO log_actividad 
            (usuario, modulo, accion, entidad, entidad_id, detalles, nivel)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (usuario, modulo, accion, entidad, entidad_id, detalles, nivel))
            conn.commit()
    except Exception as e:
        print(f"⚠️ Error en logging: {e}")

# ============================================================================
# CRUD AVANZADO PARA CLIENTES
# ============================================================================

def obtener_clientes(filtros=None):
    """Obtiene clientes con filtros avanzados"""
    try:
        with get_connection() as conn:
            query = '''
            SELECT 
                c.*,
                COUNT(o.id) as total_ocs,
                SUM(CASE WHEN o.estado_oc = 'PENDIENTE' THEN o.valor_pendiente ELSE 0 END) as valor_pendiente,
                SUM(CASE WHEN o.estado_oc = 'AUTORIZADA' THEN o.valor_autorizado ELSE 0 END) as valor_autorizado
            FROM clientes c
            LEFT JOIN ocs o ON c.nit = o.cliente_nit
            WHERE c.activo = 1
            '''
            
            params = []
            if filtros:
                condiciones = []
                if 'nit' in filtros and filtros['nit']:
                    condiciones.append("c.nit LIKE ?")
                    params.append(f"%{filtros['nit']}%")
                if 'nombre' in filtros and filtros['nombre']:
                    condiciones.append("c.nombre LIKE ?")
                    params.append(f"%{filtros['nombre']}%")
                if 'estado' in filtros and filtros['estado']:
                    condiciones.append("c.estado_cupo = ?")
                    params.append(filtros['estado'])
                
                if condiciones:
                    query += " AND " + " AND ".join(condiciones)
            
            query += " GROUP BY c.nit ORDER BY c.total_cartera DESC"
            
            df = pd.read_sql_query(query, conn, params=params)
            return df
            
    except Exception as e:
        print(f"❌ Error obteniendo clientes: {e}")
        return pd.DataFrame()

def crear_cliente(data):
    """Crea un nuevo cliente con validaciones"""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            
            # Validar NIT único
            cursor.execute("SELECT COUNT(*) FROM clientes WHERE nit = ?", (data['nit'],))
            if cursor.fetchone()[0] > 0:
                raise ValueError(f"Ya existe un cliente con NIT: {data['nit']}")
            
            # Calcular disponible
            disponible = data.get('cupo_sugerido', 0) - data.get('total_cartera', 0)
            
            cursor.execute('''
            INSERT INTO clientes 
            (nit, nombre, total_cartera, cupo_sugerido, disponible, contacto_email, contacto_telefono, notas)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data['nit'],
                data['nombre'],
                data.get('total_cartera', 0),
                data.get('cupo_sugerido', 0),
                disponible,
                data.get('contacto_email'),
                data.get('contacto_telefono'),
                data.get('notas')
            ))
            
            conn.commit()
            log_actividad(
                usuario=data.get('usuario', 'Sistema'),
                modulo='CLIENTES',
                accion='CREAR',
                entidad='CLIENTE',
                entidad_id=data['nit'],
                detalles=f"Cliente creado: {data['nombre']}"
            )
            
            return True
            
    except Exception as e:
        print(f"❌ Error creando cliente: {e}")
        raise

def actualizar_cliente(nit, data):
    """Actualiza un cliente existente"""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            
            # Verificar que el cliente existe
            cursor.execute("SELECT nombre FROM clientes WHERE nit = ?", (nit,))
            if not cursor.fetchone():
                raise ValueError(f"Cliente con NIT {nit} no encontrado")
            
            # Construir query dinámica
            campos = []
            params = []
            
            for campo in ['nombre', 'total_cartera', 'cupo_sugerido', 'contacto_email', 'contacto_telefono', 'notas']:
                if campo in data:
                    campos.append(f"{campo} = ?")
                    params.append(data[campo])
            
            if campos:
                # Calcular nuevo disponible
                if 'total_cartera' in data or 'cupo_sugerido' in data:
                    cursor.execute("SELECT total_cartera, cupo_sugerido FROM clientes WHERE nit = ?", (nit,))
                    row = cursor.fetchone()
                    
                    nueva_cartera = data.get('total_cartera', row['total_cartera'])
                    nuevo_cupo = data.get('cupo_sugerido', row['cupo_sugerido'])
                    nuevo_disponible = nuevo_cupo - nueva_cartera
                    
                    campos.append("disponible = ?")
                    params.append(nuevo_disponible)
                
                campos.append("fecha_actualizacion = CURRENT_TIMESTAMP")
                params.append(nit)
                
                query = f"UPDATE clientes SET {', '.join(campos)} WHERE nit = ?"
                cursor.execute(query, params)
                conn.commit()
                
                log_actividad(
                    usuario=data.get('usuario', 'Sistema'),
                    modulo='CLIENTES',
                    accion='ACTUALIZAR',
                    entidad='CLIENTE',
                    entidad_id=nit,
                    detalles="Cliente actualizado"
                )
                
                return True
                
    except Exception as e:
        print(f"❌ Error actualizando cliente: {e}")
        raise

# ============================================================================
# SISTEMA AVANZADO DE ÓRDENES DE COMPRA (OCs)
# ============================================================================

def crear_oc(data):
    """Crea una nueva Orden de Compra con validaciones avanzadas"""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            
            # Validaciones previas
            # 1. Verificar que el cliente existe y está activo
            cursor.execute('''
            SELECT disponible, estado_cupo FROM clientes 
            WHERE nit = ? AND activo = 1
            ''', (data['cliente_nit'],))
            
            cliente = cursor.fetchone()
            if not cliente:
                raise ValueError("Cliente no encontrado o inactivo")
            
            # 2. Validar cupo disponible
            disponible = cliente['disponible']
            valor_total = data['valor_total']
            
            if valor_total > disponible and data.get('tipo_oc') != 'CUPO_NUEVO':
                raise ValueError(f"Cupo insuficiente. Disponible: ${disponible:,.0f}, Solicitud: ${valor_total:,.0f}")
            
            # 3. Validar número de OC único
            cursor.execute("SELECT COUNT(*) FROM ocs WHERE numero_oc = ?", (data['numero_oc'],))
            if cursor.fetchone()[0] > 0:
                raise ValueError(f"Ya existe una OC con número: {data['numero_oc']}")
            
            # Crear la OC
            cursor.execute('''
            INSERT INTO ocs (
                cliente_nit, numero_oc, proveedor, valor_total, estado_oc,
                tipo_oc, prioridad, descripcion, centro_costo, proyecto,
                area, fecha_solicitud, fecha_requerida, usuario_creacion,
                referencia_cupo, observaciones
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data['cliente_nit'],
                data['numero_oc'],
                data.get('proveedor'),
                valor_total,
                data.get('estado_oc', 'PENDIENTE'),
                data.get('tipo_oc', 'NORMAL'),
                data.get('prioridad', 'MEDIA'),
                data.get('descripcion'),
                data.get('centro_costo'),
                data.get('proyecto'),
                data.get('area'),
                data.get('fecha_solicitud'),
                data.get('fecha_requerida'),
                data.get('usuario_creacion', 'Sistema'),
                data.get('referencia_cupo'),
                data.get('observaciones')
            ))
            
            oc_id = cursor.lastrowid
            
            # Si es OC autorizada completamente, actualizar cupo
            if data.get('estado_oc') == 'AUTORIZADA' and data.get('valor_autorizado', 0) > 0:
                cursor.execute('''
                UPDATE ocs 
                SET valor_autorizado = ?, fecha_ultima_autorizacion = CURRENT_TIMESTAMP
                WHERE id = ?
                ''', (data['valor_autorizado'], oc_id))
                
                # Actualizar cupo del cliente
                cursor.execute('''
                UPDATE clientes 
                SET total_cartera = total_cartera + ?,
                    disponible = disponible - ?,
                    fecha_actualizacion = CURRENT_TIMESTAMP
                WHERE nit = ?
                ''', (data['valor_autorizado'], data['valor_autorizado'], data['cliente_nit']))
            
            conn.commit()
            
            # Registrar actividad
            log_actividad(
                usuario=data.get('usuario_creacion', 'Sistema'),
                modulo='OCS',
                accion='CREAR',
                entidad='OC',
                entidad_id=oc_id,
                detalles=f"OC {data['numero_oc']} creada - Valor: ${valor_total:,.0f}"
            )
            
            return oc_id
            
    except Exception as e:
        print(f"❌ Error creando OC: {e}")
        raise

def autorizar_oc(oc_id, data):
    """Autoriza total o parcialmente una OC con sistema de niveles"""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            
            # Obtener información de la OC
            cursor.execute('''
            SELECT o.*, c.disponible 
            FROM ocs o
            JOIN clientes c ON o.cliente_nit = c.nit
            WHERE o.id = ?
            ''', (oc_id,))
            
            oc = cursor.fetchone()
            if not oc:
                raise ValueError("OC no encontrada")
            
            # Validar estado actual
            if oc['estado_oc'] == 'AUTORIZADA':
                raise ValueError("La OC ya está completamente autorizada")
            
            if oc['estado_oc'] == 'RECHAZADA':
                raise ValueError("La OC fue rechazada, no se puede autorizar")
            
            if oc['estado_oc'] == 'ANULADA':
                raise ValueError("La OC fue anulada")
            
            # Calcular nuevo estado
            valor_actual = oc['valor_autorizado'] or 0
            nuevo_valor = valor_actual + data['valor_autorizado']
            valor_total = oc['valor_total']
            
            # Determinar nuevo estado
            if nuevo_valor >= valor_total:
                estado_nuevo = 'AUTORIZADA'
                valor_autorizado = valor_total
            elif nuevo_valor > 0:
                estado_nuevo = 'PARCIAL'
                valor_autorizado = nuevo_valor
            else:
                estado_nuevo = 'PENDIENTE'
                valor_autorizado = 0
            
            # Validar cupo disponible para autorización
            if valor_autorizado > 0:
                cupo_disponible = oc['disponible']
                if cupo_disponible < data['valor_autorizado']:
                    raise ValueError(f"Cupo insuficiente. Disponible: ${cupo_disponible:,.0f}")
            
            # Actualizar OC
            cursor.execute('''
            UPDATE ocs 
            SET valor_autorizado = ?,
                estado_oc = ?,
                fecha_ultima_autorizacion = CURRENT_TIMESTAMP,
                usuario_ultima_modificacion = ?,
                version = version + 1
            WHERE id = ?
            ''', (valor_autorizado, estado_nuevo, data.get('usuario'), oc_id))
            
            # Registrar autorización
            cursor.execute('''
            INSERT INTO autorizaciones 
            (oc_id, tipo_autorizacion, valor_autorizado, nivel_autorizacion,
             usuario_autorizador, departamento, comentarios, estado_anterior,
             estado_nuevo, ip_address, dispositivo)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                oc_id,
                'PARCIAL' if estado_nuevo == 'PARCIAL' else 'TOTAL',
                data['valor_autorizado'],
                data.get('nivel_autorizacion', 1),
                data.get('usuario'),
                data.get('departamento'),
                data.get('comentarios'),
                oc['estado_oc'],
                estado_nuevo,
                data.get('ip_address'),
                data.get('dispositivo')
            ))
            
            # Actualizar cupo del cliente si se autorizó valor
            if data['valor_autorizado'] > 0:
                cursor.execute('''
                UPDATE clientes 
                SET total_cartera = total_cartera + ?,
                    disponible = disponible - ?,
                    fecha_actualizacion = CURRENT_TIMESTAMP
                WHERE nit = ?
                ''', (data['valor_autorizado'], data['valor_autorizado'], oc['cliente_nit']))
            
            conn.commit()
            
            # Log de actividad
            log_actividad(
                usuario=data.get('usuario', 'Sistema'),
                modulo='OCS',
                accion='AUTORIZAR',
                entidad='OC',
                entidad_id=oc_id,
                detalles=f"OC autorizada - Valor: ${data['valor_autorizado']:,.0f}, Estado: {estado_nuevo}"
            )
            
            return True
            
    except Exception as e:
        print(f"❌ Error autorizando OC: {e}")
        raise

def obtener_ocs(filtros=None):
    """Obtiene OCs con filtros avanzados"""
    try:
        with get_connection() as conn:
            query = '''
            SELECT 
                o.*,
                c.nombre as cliente_nombre,
                c.estado_cupo,
                (SELECT COUNT(*) FROM autorizaciones a WHERE a.oc_id = o.id) as total_autorizaciones,
                (SELECT MAX(fecha_autorizacion) FROM autorizaciones a WHERE a.oc_id = o.id) as ultima_autorizacion
            FROM ocs o
            JOIN clientes c ON o.cliente_nit = c.nit
            WHERE 1=1
            '''
            
            params = []
            
            if filtros:
                if 'cliente_nit' in filtros and filtros['cliente_nit']:
                    query += " AND o.cliente_nit = ?"
                    params.append(filtros['cliente_nit'])
                
                if 'estado_oc' in filtros and filtros['estado_oc']:
                    query += " AND o.estado_oc = ?"
                    params.append(filtros['estado_oc'])
                
                if 'numero_oc' in filtros and filtros['numero_oc']:
                    query += " AND o.numero_oc LIKE ?"
                    params.append(f"%{filtros['numero_oc']}%")
                
                if 'fecha_desde' in filtros and filtros['fecha_desde']:
                    query += " AND DATE(o.fecha_registro) >= ?"
                    params.append(filtros['fecha_desde'])
                
                if 'fecha_hasta' in filtros and filtros['fecha_hasta']:
                    query += " AND DATE(o.fecha_registro) <= ?"
                    params.append(filtros['fecha_hasta'])
                
                if 'prioridad' in filtros and filtros['prioridad']:
                    query += " AND o.prioridad = ?"
                    params.append(filtros['prioridad'])
            
            query += " ORDER BY o.fecha_registro DESC"
            
            df = pd.read_sql_query(query, conn, params=params)
            return df
            
    except Exception as e:
        print(f"❌ Error obteniendo OCs: {e}")
        return pd.DataFrame()

def obtener_historial_autorizaciones(oc_id):
    """Obtiene historial completo de autorizaciones de una OC"""
    try:
        with get_connection() as conn:
            query = '''
            SELECT * FROM autorizaciones 
            WHERE oc_id = ? 
            ORDER BY fecha_autorizacion DESC
            '''
            df = pd.read_sql_query(query, conn, params=(oc_id,))
            return df
    except Exception as e:
        print(f"❌ Error obteniendo historial: {e}")
        return pd.DataFrame()

# ============================================================================
# SISTEMA DE REPORTES Y ESTADÍSTICAS
# ============================================================================

def obtener_estadisticas_generales():
    """Obtiene estadísticas generales del sistema"""
    try:
        with get_connection() as conn:
            query = '''
            SELECT 
                -- Totales generales
                COUNT(DISTINCT c.nit) as total_clientes,
                SUM(c.total_cartera) as total_cartera_sistema,
                SUM(c.cupo_sugerido) as total_cupo_sistema,
                SUM(c.disponible) as total_disponible_sistema,
                
                -- Estados de cupo
                SUM(CASE WHEN c.estado_cupo = 'SOBREPASADO' THEN 1 ELSE 0 END) as clientes_sobrepasados,
                SUM(CASE WHEN c.estado_cupo = 'ALTO' THEN 1 ELSE 0 END) as clientes_alto,
                SUM(CASE WHEN c.estado_cupo = 'MEDIO' THEN 1 ELSE 0 END) as clientes_medio,
                SUM(CASE WHEN c.estado_cupo = 'NORMAL' THEN 1 ELSE 0 END) as clientes_normal,
                
                -- Estadísticas OCs
                COUNT(o.id) as total_ocs,
                SUM(CASE WHEN o.estado_oc = 'PENDIENTE' THEN o.valor_pendiente ELSE 0 END) as valor_pendiente,
                SUM(CASE WHEN o.estado_oc = 'AUTORIZADA' THEN o.valor_autorizado ELSE 0 END) as valor_autorizado,
                SUM(CASE WHEN o.estado_oc = 'PARCIAL' THEN o.valor_pendiente ELSE 0 END) as valor_parcial,
                
                -- Promedios
                AVG(c.porcentaje_uso) as promedio_uso,
                MAX(c.porcentaje_uso) as maximo_uso,
                MIN(c.porcentaje_uso) as minimo_uso
                
            FROM clientes c
            LEFT JOIN ocs o ON c.nit = o.cliente_nit
            WHERE c.activo = 1
            '''
            
            result = pd.read_sql_query(query, conn).iloc[0].to_dict()
            
            # Calcular porcentajes
            result['porcentaje_uso_promedio'] = round(result['promedio_uso'], 2)
            result['porcentaje_disponible'] = round((result['total_disponible_sistema'] / result['total_cupo_sistema'] * 100), 2) if result['total_cupo_sistema'] > 0 else 0
            
            return result
            
    except Exception as e:
        print(f"❌ Error obteniendo estadísticas: {e}")
        return {}

def obtener_tendencias_cupos(dias=30):
    """Obtiene tendencias de cupos en los últimos N días"""
    try:
        with get_connection() as conn:
            fecha_limite = (datetime.now() - timedelta(days=dias)).strftime('%Y-%m-%d')
            
            query = f'''
            SELECT 
                DATE(fecha_actualizacion) as fecha,
                COUNT(DISTINCT nit) as clientes_actualizados,
                SUM(total_cartera) as total_cartera_dia,
                SUM(cupo_sugerido) as total_cupo_dia,
                SUM(disponible) as total_disponible_dia,
                AVG(porcentaje_uso) as promedio_uso_dia
            FROM clientes
            WHERE fecha_actualizacion >= '{fecha_limite}'
            GROUP BY DATE(fecha_actualizacion)
            ORDER BY fecha DESC
            '''
            
            df = pd.read_sql_query(query, conn)
            return df
            
    except Exception as e:
        print(f"❌ Error obteniendo tendencias: {e}")
        return pd.DataFrame()

def generar_reporte_exportacion(formato='excel'):
    """Genera reporte completo para exportación"""
    try:
        with get_connection() as conn:
            # Obtener datos para el reporte
            data = {
                'clientes': pd.read_sql_query("SELECT * FROM clientes WHERE activo = 1", conn),
                'ocs': pd.read_sql_query("SELECT * FROM ocs", conn),
                'autorizaciones': pd.read_sql_query("SELECT * FROM autorizaciones", conn),
                'estadisticas': pd.DataFrame([obtener_estadisticas_generales()])
            }
            
            return data
            
    except Exception as e:
        print(f"❌ Error generando reporte: {e}")
        return {}

# ============================================================================
# SISTEMA DE SEGUIMIENTO Y ALERTAS
# ============================================================================

def verificar_alertas_cupos():
    """Verifica y genera alertas de cupos"""
    try:
        with get_connection() as conn:
            # Obtener parámetros del sistema
            cursor = conn.cursor()
            cursor.execute("SELECT valor FROM parametros_sistema WHERE clave = 'limite_alerta_cupo'")
            limite_alerta = float(cursor.fetchone()[0])
            
            cursor.execute("SELECT valor FROM parametros_sistema WHERE clave = 'limite_critico_cupo'")
            limite_critico = float(cursor.fetchone()[0])
            
            # Buscar clientes con alertas
            query = f'''
            SELECT 
                nit,
                nombre,
                total_cartera,
                cupo_sugerido,
                disponible,
                porcentaje_uso,
                estado_cupo,
                CASE 
                    WHEN porcentaje_uso >= {limite_critico} THEN 'CRITICO'
                    WHEN porcentaje_uso >= {limite_alerta} THEN 'ALERTA'
                    ELSE 'NORMAL'
                END as nivel_alerta
            FROM clientes
            WHERE activo = 1 AND porcentaje_uso >= {limite_alerta}
            ORDER BY porcentaje_uso DESC
            '''
            
            df = pd.read_sql_query(query, conn)
            return df
            
    except Exception as e:
        print(f"❌ Error verificando alertas: {e}")
        return pd.DataFrame()

def registrar_seguimiento_diario():
    """Registra seguimiento diario de cupos"""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            fecha_hoy = datetime.now().strftime('%Y-%m-%d')
            
            # Obtener datos de cada cliente
            cursor.execute('''
            SELECT 
                c.nit,
                c.total_cartera,
                c.cupo_sugerido,
                c.disponible,
                COUNT(o.id) as ocs_pendientes,
                SUM(CASE WHEN o.estado_oc = 'PENDIENTE' THEN o.valor_pendiente ELSE 0 END) as valor_pendiente
            FROM clientes c
            LEFT JOIN ocs o ON c.nit = o.cliente_nit AND o.estado_oc IN ('PENDIENTE', 'PARCIAL')
            WHERE c.activo = 1
            GROUP BY c.nit
            ''')
            
            for row in cursor.fetchall():
                # Verificar si ya existe seguimiento para hoy
                cursor.execute('''
                SELECT COUNT(*) FROM seguimiento_cupos 
                WHERE cliente_nit = ? AND fecha_seguimiento = ?
                ''', (row['nit'], fecha_hoy))
                
                if cursor.fetchone()[0] == 0:
                    cursor.execute('''
                    INSERT INTO seguimiento_cupos 
                    (cliente_nit, fecha_seguimiento, total_cartera_inicial, 
                     cupo_sugerido_inicial, disponible_inicial, ocs_pendientes_count,
                     ocs_pendientes_valor)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        row['nit'], fecha_hoy, row['total_cartera'], 
                        row['cupo_sugerido'], row['disponible'], 
                        row['ocs_pendientes'], row['valor_pendiente']
                    ))
            
            conn.commit()
            return True
            
    except Exception as e:
        print(f"❌ Error en seguimiento diario: {e}")
        return False

# ============================================================================
# INICIALIZACIÓN DEL SISTEMA
# ============================================================================

if __name__ == "__main__":
    # Verificar e inicializar la base de datos
    if not os.path.exists(config.DATABASE_PATH):
        print("🔧 Inicializando base de datos avanzada...")
        init_database()
        print("✅ Sistema listo para producción")
    else:
        print("✅ Base de datos ya existe")
        
    # Ejecutar seguimiento diario automático
    try:
        registrar_seguimiento_diario()
        print("📊 Seguimiento diario registrado")
    except:
        print("⚠️ Error en seguimiento diario")
