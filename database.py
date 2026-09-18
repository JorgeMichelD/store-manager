import sqlite3


# =============================================
# CONEXIÓN CON SQLITE
# =============================================

conexion = sqlite3.connect("store_manager.db")

cursor = conexion.cursor()


# =============================================
# CREAR TABLA DE PRODUCTOS
# =============================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS productos(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    categoria TEXT NOT NULL,
    precio_compra REAL NOT NULL,
    precio_venta REAL NOT NULL,
    cantidad INTEGER NOT NULL,
    codigo_barras TEXT
)
""")


# =============================================
# CREAR TABLA DE VENTAS
# =============================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS ventas(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    producto_id INTEGER NOT NULL,
    producto_nombre TEXT NOT NULL,
    cantidad INTEGER NOT NULL,
    precio_compra REAL NOT NULL,
    precio_venta REAL NOT NULL,
    total REAL NOT NULL,
    ganancia REAL NOT NULL,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")


# =============================================
# GUARDAR CAMBIOS
# =============================================

conexion.commit()