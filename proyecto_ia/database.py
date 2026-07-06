"""
Módulo de base de datos para el Concesionario.
Maneja SQLite con 4 tablas interconectadas + datos de prueba realistas.
"""

import sqlite3
import os
from datetime import datetime, timedelta
import random

DB_PATH = os.path.join(os.path.dirname(__file__), "concesionario.db")

def get_connection():
    """Obtiene conexión a la base de datos."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    """Crea las tablas si no existen."""
    conn = get_connection()
    cursor = conn.cursor()

    # Tabla 1: MARCAS
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS marcas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL UNIQUE,
            pais_origen TEXT,
            año_fundacion INTEGER
        )
    """)

    # Tabla 2: MODELOS (relacionada con marcas)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS modelos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            marca_id INTEGER NOT NULL,
            nombre TEXT NOT NULL,
            año INTEGER,
            precio_base REAL,
            tipo TEXT,
            FOREIGN KEY (marca_id) REFERENCES marcas(id)
        )
    """)

    # Tabla 3: VENDEDORES
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vendedores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            email TEXT,
            telefono TEXT,
            fecha_contratacion DATE,
            comision_porcentaje REAL DEFAULT 5.0
        )
    """)

    # Tabla 4: VENTAS (relacionada con modelos y vendedores)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ventas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            modelo_id INTEGER NOT NULL,
            vendedor_id INTEGER NOT NULL,
            cliente_nombre TEXT NOT NULL,
            fecha_venta DATE NOT NULL,
            precio_final REAL NOT NULL,
            FOREIGN KEY (modelo_id) REFERENCES modelos(id),
            FOREIGN KEY (vendedor_id) REFERENCES vendedores(id)
        )
    """)

    conn.commit()
    conn.close()

def populate_sample_data():
    """
    Genera exactamente 1000 registros en CADA tabla (marcas, modelos, vendedores, ventas).
    Si ya existen muchos datos, no vuelve a generar.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Verificar cuántos datos hay actualmente
    cursor.execute("SELECT COUNT(*) FROM marcas")
    current_marcas = cursor.fetchone()[0]

    # Si ya tenemos cerca de 1000 o más, no regeneramos
    if current_marcas >= 900:
        conn.close()
        return

    print("🔄 Generando base de datos grande (1000 registros por tabla)... Esto puede tardar unos segundos.")

    # ===== LIMPIAR DATOS ANTERIORES =====
    cursor.execute("DELETE FROM ventas")
    cursor.execute("DELETE FROM modelos")
    cursor.execute("DELETE FROM vendedores")
    cursor.execute("DELETE FROM marcas")
    conn.commit()

    # ===== NOMBRES PARA GENERACIÓN =====
    nombres_hombre = [
        "Carlos", "José", "Miguel", "Juan", "Luis", "Alejandro", "Roberto", "Fernando",
        "Ricardo", "Daniel", "Eduardo", "Francisco", "Antonio", "Manuel", "Javier",
        "Pedro", "Óscar", "Sergio", "Andrés", "Rafael", "Mario", "Héctor", "Raúl",
        "Alberto", "Jorge", "Enrique", "Gabriel", "Martín", "Pablo", "Diego", "Víctor"
    ]
    nombres_mujer = [
        "María", "Ana", "Laura", "Sofía", "Isabel", "Patricia", "Claudia", "Gabriela",
        "Verónica", "Mónica", "Silvia", "Adriana", "Carmen", "Rosa", "Elena", "Lucía",
        "Beatriz", "Raquel", "Diana", "Martha", "Gloria", "Teresa", "Alicia", "Sara",
        "Paula", "Andrea", "Natalia", "Lorena", "Valeria", "Camila", "Daniela", "Fernanda"
    ]
    apellidos = [
        "García", "Rodríguez", "Martínez", "López", "González", "Hernández", "Pérez",
        "Sánchez", "Ramírez", "Torres", "Flores", "Rivera", "Gómez", "Díaz", "Morales",
        "Reyes", "Cruz", "Ortiz", "Vargas", "Mendoza", "Ruiz", "Aguilar", "Medina",
        "Castro", "Vega", "Delgado", "Rojas", "Navarro", "Rivas", "Campos", "Molina",
        "Contreras", "Silva", "Núñez", "Valdez", "Jiménez", "Chávez", "Romero", "Álvarez",
        "Méndez", "Domínguez", "Cortes", "Guerrero", "Ibarra", "Soto", "Luna", "Ríos"
    ]

    tipos_vehiculo = ["Sedán", "SUV", "Hatchback", "Pickup", "Deportivo", "Minivan", "Coupé", "Convertible"]

    # ===== 1. GENERAR 1000 MARCAS =====
    paises = [
        "Japón", "Estados Unidos", "Alemania", "Corea del Sur", "Francia", "Italia",
        "Reino Unido", "España", "Suecia", "China", "India", "México", "Brasil",
        "Argentina", "Canadá", "Australia", "Rusia", "Turquía", "Tailandia", "Malasia"
    ]

    prefijos_marca = [
        "Aether", "Lumina", "Velox", "Forge", "Nexus", "Pulse", "Horizon", "Apex",
        "Quantum", "Vortex", "Eclipse", "Nova", "Stellar", "Fusion", "Zenith", "Atlas",
        "Prime", "Helix", "Orion", "Titan", "Phoenix", "Spectra", "Vertex", "Ignis",
        "Astral", "Catalyst", "Dynasty", "Empire", "Genesis", "Legacy", "Momentum",
        "Noble", "Pinnacle", "Radiant", "Summit", "Valor", "Zephyr"
    ]

    marcas_data = []
    usados = set()

    # Primero marcas más "reales" / conocidas
    marcas_base = [
        ("Toyota", "Japón", 1937), ("Ford", "Estados Unidos", 1903), ("BMW", "Alemania", 1916),
        ("Mercedes-Benz", "Alemania", 1926), ("Audi", "Alemania", 1909), ("Hyundai", "Corea del Sur", 1967),
        ("Kia", "Corea del Sur", 1944), ("Chevrolet", "Estados Unidos", 1911), ("Volkswagen", "Alemania", 1937),
        ("Nissan", "Japón", 1933), ("Renault", "Francia", 1899), ("Peugeot", "Francia", 1810),
        ("Honda", "Japón", 1948), ("Mazda", "Japón", 1920), ("Subaru", "Japón", 1953),
        ("Mitsubishi", "Japón", 1870), ("Suzuki", "Japón", 1909), ("Lexus", "Japón", 1989),
        ("Acura", "Japón", 1986), ("Infiniti", "Japón", 1989), ("Volvo", "Suecia", 1927),
        ("Saab", "Suecia", 1945), ("Jaguar", "Reino Unido", 1922), ("Land Rover", "Reino Unido", 1948),
        ("Mini", "Reino Unido", 1969), ("Bentley", "Reino Unido", 1919), ("Rolls-Royce", "Reino Unido", 1906),
        ("Ferrari", "Italia", 1947), ("Lamborghini", "Italia", 1963), ("Maserati", "Italia", 1914),
        ("Alfa Romeo", "Italia", 1910), ("Fiat", "Italia", 1899), ("Porsche", "Alemania", 1931),
        ("Opel", "Alemania", 1862), ("Skoda", "República Checa", 1895), ("Seat", "España", 1950),
        ("Citroën", "Francia", 1919), ("DS Automobiles", "Francia", 2014), ("Alpine", "Francia", 1955),
        ("Tesla", "Estados Unidos", 2003), ("Rivian", "Estados Unidos", 2009), ("Lucid", "Estados Unidos", 2007),
        ("Cadillac", "Estados Unidos", 1902), ("Lincoln", "Estados Unidos", 1917), ("GMC", "Estados Unidos", 1902),
        ("Dodge", "Estados Unidos", 1900), ("Jeep", "Estados Unidos", 1941), ("Ram", "Estados Unidos", 2010),
        ("Chrysler", "Estados Unidos", 1925), ("Buick", "Estados Unidos", 1903), ("Pontiac", "Estados Unidos", 1926),
    ]

    for nombre, pais, año in marcas_base:
        marcas_data.append((nombre, pais, año))
        usados.add(nombre)

    # Generar las restantes hasta llegar a 1000
    idx = 1
    while len(marcas_data) < 1000:
        base = random.choice(prefijos_marca)
        sufijo = random.choice(["Motors", "Auto", "Cars", "Vehicles", "Automotive", "Drive", ""])
        nombre = f"{base} {sufijo}".strip()
        if nombre in usados:
            nombre = f"{base} {idx}"
            idx += 1
        usados.add(nombre)

        pais = random.choice(paises)
        año = random.randint(1950, 2022)
        marcas_data.append((nombre, pais, año))

    cursor.executemany(
        "INSERT INTO marcas (nombre, pais_origen, año_fundacion) VALUES (?, ?, ?)",
        marcas_data
    )
    conn.commit()

    # Obtener todos los IDs de marcas
    cursor.execute("SELECT id FROM marcas ORDER BY id")
    marca_ids = [row[0] for row in cursor.fetchall()]

    # Las primeras 350 marcas (las más realistas) recibirán más modelos
    marcas_populares = marca_ids[:350]

    print(f"   → 1000 marcas generadas")

    # ===== 2. GENERAR 1000 MODELOS (con buena distribución) =====
    modelos_data = []
    sufijos_modelo = ["X", "GT", "Pro", "Sport", "Prime", "Elite", "Max", "Turbo", "Hybrid", "EV", "Plus", "Limited"]
    nombres_modelo_base = [
        "Nova", "Strada", "Pulse", "Vortex", "Aether", "Helix", "Zenith", "Atlas", "Forge",
        "Ranger", "Summit", "Cruiser", "Phantom", "Eclipse", "Falcon", "Hawk", "Viper",
        "Titan", "Orion", "Spectra", "Legacy", "Pinnacle", "Valor", "Zephyr", "Horizon"
    ]

    # Primero: aseguramos que las 400 primeras marcas tengan al menos 1 modelo
    marcas_con_modelo = set()
    for marca_id in marca_ids[:400]:
        base = random.choice(nombres_modelo_base)
        sufijo = random.choice(sufijos_modelo)
        año = random.randint(2020, 2025)
        nombre = f"{base} {sufijo}"
        tipo = random.choice(tipos_vehiculo)
        precio = round(random.uniform(18500, 78000), 2)
        modelos_data.append((marca_id, nombre, año, precio, tipo))
        marcas_con_modelo.add(marca_id)

    # Luego completamos hasta 1000 modelos (dando preferencia fuerte a marcas populares)
    while len(modelos_data) < 1000:
        if random.random() < 0.78:
            marca_id = random.choice(marcas_populares)
        else:
            marca_id = random.choice(marca_ids)

        base = random.choice(nombres_modelo_base)
        sufijo = random.choice(sufijos_modelo)
        año = random.randint(2020, 2025)
        nombre = f"{base} {sufijo}"

        tipo = random.choice(tipos_vehiculo)
        if tipo == "Deportivo":
            precio = round(random.uniform(45000, 145000), 2)
        elif tipo == "SUV":
            precio = round(random.uniform(22000, 85000), 2)
        elif tipo == "Pickup":
            precio = round(random.uniform(28000, 72000), 2)
        elif tipo in ["Convertible", "Coupé"]:
            precio = round(random.uniform(38000, 125000), 2)
        else:
            precio = round(random.uniform(14500, 48000), 2)

        modelos_data.append((marca_id, nombre, año, precio, tipo))
        marcas_con_modelo.add(marca_id)

    random.shuffle(modelos_data)  # para que no estén ordenados por marca

    cursor.executemany(
        "INSERT INTO modelos (marca_id, nombre, año, precio_base, tipo) VALUES (?, ?, ?, ?, ?)",
        modelos_data
    )
    conn.commit()

    cursor.execute("SELECT id FROM modelos")
    modelo_ids = [row[0] for row in cursor.fetchall()]

    print(f"   → 1000 modelos generados")

    # ===== 3. GENERAR 1000 VENDEDORES =====
    vendedores_data = []
    dominios = ["concesionario.com", "autonacional.mx", "ventas.com", "grupoauto.com"]

    for i in range(1000):
        if random.random() > 0.48:
            nombre = f"{random.choice(nombres_hombre)} {random.choice(apellidos)}"
        else:
            nombre = f"{random.choice(nombres_mujer)} {random.choice(apellidos)}"
            if random.random() > 0.6:
                nombre += f" de {random.choice(apellidos)}"

        email = f"{nombre.lower().replace(' ', '.').replace('á','a').replace('é','e').replace('í','i').replace('ó','o').replace('ú','u')[:30]}@{random.choice(dominios)}"
        telefono = f"+52 {random.randint(55, 99)} {random.randint(1000, 9999)} {random.randint(1000, 9999)}"

        # Fecha contratación entre 2015 y 2025
        dias = random.randint(0, 3650)
        fecha = (datetime(2025, 1, 1) - timedelta(days=dias)).strftime("%Y-%m-%d")
        comision = round(random.uniform(3.5, 8.5), 1)

        vendedores_data.append((nombre, email, telefono, fecha, comision))

    cursor.executemany(
        "INSERT INTO vendedores (nombre, email, telefono, fecha_contratacion, comision_porcentaje) VALUES (?, ?, ?, ?, ?)",
        vendedores_data
    )
    conn.commit()

    cursor.execute("SELECT id FROM vendedores")
    vendedor_ids = [row[0] for row in cursor.fetchall()]

    print(f"   → 1000 vendedores generados")

    # ===== 4. GENERAR 1000 VENTAS =====
    clientes_base = nombres_hombre + nombres_mujer

    ventas_data = []
    start_date = datetime(2023, 1, 10)

    for i in range(1000):
        modelo_id = random.choice(modelo_ids)
        vendedor_id = random.choice(vendedor_ids)

        # Nombre de cliente
        cliente = f"{random.choice(clientes_base)} {random.choice(apellidos)}"

        # Fecha entre 2023 y hoy
        dias_offset = random.randint(0, 820)
        fecha = (start_date + timedelta(days=dias_offset)).strftime("%Y-%m-%d")

        # Precio final con variación realista
        cursor.execute("SELECT precio_base FROM modelos WHERE id = ?", (modelo_id,))
        precio_base = cursor.fetchone()[0]
        variacion = random.uniform(-0.08, 0.18)  # -8% a +18%
        precio_final = round(precio_base * (1 + variacion), 2)

        ventas_data.append((modelo_id, vendedor_id, cliente, fecha, precio_final))

    cursor.executemany(
        "INSERT INTO ventas (modelo_id, vendedor_id, cliente_nombre, fecha_venta, precio_final) VALUES (?, ?, ?, ?, ?)",
        ventas_data
    )
    conn.commit()
    conn.close()

    print("✅ ¡Base de datos generada exitosamente!")
    print("   1000 marcas | 1000 modelos | 1000 vendedores | 1000 ventas")

def get_schema_description():
    """Devuelve una descripción clara del esquema para el LLM."""
    return """
TABLAS DE LA BASE DE DATOS DEL CONCESIONARIO:

1. marcas
   - id (INTEGER, PRIMARY KEY)
   - nombre (TEXT, ej: Toyota, BMW, Ford)
   - pais_origen (TEXT)
   - año_fundacion (INTEGER)

2. modelos
   - id (INTEGER, PRIMARY KEY)
   - marca_id (INTEGER, FOREIGN KEY → marcas.id)
   - nombre (TEXT, ej: Corolla, X5, Mustang)
   - año (INTEGER)
   - precio_base (REAL)
   - tipo (TEXT: Sedán, SUV, Deportivo, Pickup, Hatchback)

3. vendedores
   - id (INTEGER, PRIMARY KEY)
   - nombre (TEXT)
   - email (TEXT)
   - telefono (TEXT)
   - fecha_contratacion (DATE)
   - comision_porcentaje (REAL)

4. ventas
   - id (INTEGER, PRIMARY KEY)
   - modelo_id (INTEGER, FOREIGN KEY → modelos.id)
   - vendedor_id (INTEGER, FOREIGN KEY → vendedores.id)
   - cliente_nombre (TEXT)
   - fecha_venta (DATE)
   - precio_final (REAL)

RELACIONES:
- Un modelo pertenece a UNA marca.
- Una venta corresponde a UN modelo y UN vendedor.
"""

def execute_safe_query(sql: str):
    """
    Ejecuta una consulta SQL de forma segura.
    Solo permite SELECT. Rechaza cualquier cosa peligrosa.
    """
    forbidden = ["INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "CREATE", "TRUNCATE", 
                 "REPLACE", "ATTACH", "DETACH", "PRAGMA", "--", "/*"]
    
    sql_upper = sql.upper().strip()
    
    # Validaciones de seguridad
    if not sql_upper.startswith("SELECT"):
        raise ValueError("Solo se permiten consultas SELECT.")
    
    for word in forbidden:
        if word in sql_upper:
            raise ValueError(f"Operación no permitida: {word}")
    
    # Limitar resultados para no saturar
    if "LIMIT" not in sql_upper:
        sql = sql.rstrip(";") + " LIMIT 100;"
    
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(sql)
        rows = cursor.fetchall()
        # Convertir a lista de diccionarios
        result = [dict(row) for row in rows]
        return result
    except Exception as e:
        raise e
    finally:
        conn.close()

def get_table_stats():
    """Devuelve estadísticas rápidas de las tablas."""
    conn = get_connection()
    cursor = conn.cursor()
    stats = {}
    for table in ["marcas", "modelos", "vendedores", "ventas"]:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        stats[table] = cursor.fetchone()[0]
    conn.close()
    return stats