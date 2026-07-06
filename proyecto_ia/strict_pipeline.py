"""
Módulo de pipeline estricto - VERSIÓN FINAL PERFECCIONADA
Implementa Regex para fechas, intenciones flexibles y redacción natural con Ollama.
"""

import re
import ollama
from database import get_connection

OLLAMA_MODEL = "llama3:latest"

KEYWORDS_RELATED = ["vendedor","vendedora","ventas","venta","auto","modelo","marca","precio","caro","barato",
                    "enero","febrero","marzo","abril","mayo","junio","julio","agosto","septiembre","octubre","noviembre","diciembre",
                    "2023","2024","2025"]

def is_inventory_question(question: str) -> bool:
    """Verifica si la pregunta pertenece al dominio del concesionario."""
    q_lower = question.lower().strip()
    for kw in KEYWORDS_RELATED:
        if kw in q_lower:
            return True
    try:
        resp = ollama.chat(model=OLLAMA_MODEL, messages=[{"role": "user", "content": f'Responde SOLO "SI" o "NO": ¿Es sobre concesionario, autos o vendedores? "{question}"'}], options={"temperature": 0.0})
        return "SI" in resp["message"]["content"].strip().upper()
    except:
        return True

def extract_date_filter(question: str):
    """Extrae el año y el mes usando límites de palabra (Regex) para evitar falsos positivos."""
    q = question.lower()
    months = {
        "enero":"01", "febrero":"02", "marzo":"03", "abril":"04", 
        "mayo":"05", "junio":"06", "julio":"07", "agosto":"08", 
        "septiembre":"09", "octubre":"10", "noviembre":"11", "diciembre":"12"
    }
    
    year = next((y for y in ["2023","2024","2025"] if y in q), None)
    
    # Extraer el mes usando límites de palabra (\b)
    month_num = None
    for name, num in months.items():
        if re.search(rf"\b{name}\b", q):
            month_num = num
            break
            
    if month_num and year:
        return f"{year}-{month_num}"
    elif month_num:
        return f"2024-{month_num}" # Por defecto 2024 si no se especifica el año
    elif year:
        return year
    return None

def classify_intent(question: str) -> str:
    """Clasifica la intención del usuario de manera flexible mediante combinaciones de palabras clave."""
    q = question.strip().lower()
    has_date = extract_date_filter(question) is not None
    
    # Preguntas sobre vendedores
    vendedor_kws = ["vendedor", "vendedora", "quien", "quién"]
    ventas_kws = ["vendido", "ventas", "más", "mayor", "mejores", "top"]
    if any(v in q for v in vendedor_kws) and any(x in q for x in ventas_kws):
        if has_date:
            return "TOP_VENDEDOR_FECHA"
        return "TOP_VENDEDORES"
    
    # Preguntas sobre vehículos más vendidos
    vehiculo_kws = ["vehículo", "vehiculo", "modelo", "auto", "carro"]
    if any(v in q for v in vehiculo_kws) and any(x in q for x in ["vendido", "más", "popular"]):
        if has_date:
            return "MODELO_MAS_VENDIDO_FECHA"
    
    # Preguntas sobre cantidades o montos
    if any(x in q for x in ["cuántos", "cuántas", "cantidad", "se vendieron"]) and has_date:
        return "VENTAS_POR_FECHA"
    
    # Preguntas generales
    if any(x in q for x in ["caro", "caros"]):
        return "MODELOS_MAS_CAROS"
    if any(x in q for x in ["barato", "baratos"]):
        return "MODELOS_MAS_BARATOS"
    
    return "NORMAL"

def _format_money(val):
    """Formatea valores monetarios a dólares."""
    try:
        return f"${float(val):,.2f}"
    except:
        return str(val)

def generar_respuesta_natural(pregunta: str, datos_crudos: str) -> str:
    """Toma datos de SQLite y usa Llama 3 para redactar una respuesta fluida en lenguaje natural."""
    prompt_sistema = (
        "Eres AutoBot, el asistente experto y amable del Concesionario Nacional. "
        "Tu tarea es responder la pregunta del cliente utilizando ÚNICAMENTE los datos que te proveeremos. "
        "Redacta una respuesta natural, profesional y conversacional. No incluyas explicaciones de cómo obtuviste los datos. "
        "Nunca inventes información."
    )
    
    prompt_usuario = f"Pregunta del cliente: '{pregunta}'\nDatos de la base de datos a utilizar:\n{datos_crudos}"
    
    try:
        resp = ollama.chat(model=OLLAMA_MODEL, messages=[
            {"role": "system", "content": prompt_sistema},
            {"role": "user", "content": prompt_usuario}
        ], options={"temperature": 0.3})
        return resp["message"]["content"].strip()
    except Exception as e:
        # Fallback seguro en caso de que Llama 3 no responda
        return f"Aquí tienes la información solicitada: {datos_crudos}"

def handle_direct_query(intent: str, question: str) -> str | None:
    """Ejecuta consultas a SQLite y las envía a formatear con Llama 3."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        date_filter = extract_date_filter(question)
        pattern = f"{date_filter}%" if date_filter else None
        
        if intent == "TOP_VENDEDORES":
            cur.execute('''
                SELECT ve.nombre, COUNT(v.id) as num_ventas, ROUND(COALESCE(SUM(v.precio_final),0),2) as monto
                FROM vendedores ve LEFT JOIN ventas v ON ve.id = v.vendedor_id
                GROUP BY ve.id, ve.nombre 
                ORDER BY num_ventas DESC, monto DESC LIMIT 5
            ''')
            rows = cur.fetchall()
            datos_raw = ", ".join([f"{r[0]} ({r[1]} ventas, {_format_money(r[2])})" for r in rows])
            return generar_respuesta_natural(question, datos_raw)

        if intent == "TOP_VENDEDOR_FECHA" and pattern:
            cur.execute('''
                SELECT ve.nombre, COUNT(v.id) as num_ventas, ROUND(COALESCE(SUM(v.precio_final),0),2) as monto
                FROM vendedores ve JOIN ventas v ON ve.id = v.vendedor_id
                WHERE v.fecha_venta LIKE ? 
                GROUP BY ve.id, ve.nombre ORDER BY num_ventas DESC LIMIT 1
            ''', (pattern,))
            row = cur.fetchone()
            if row and row[1] > 0:
                datos_raw = f"Vendedor: {row[0]}, Ventas en {date_filter}: {row[1]}, Monto total: {_format_money(row[2])}"
                return generar_respuesta_natural(question, datos_raw)
            return f"No hay ventas registradas en {date_filter}."

        if intent == "MODELO_MAS_VENDIDO_FECHA" and pattern:
            cur.execute('''
                SELECT ma.nombre as marca, m.nombre as modelo, COUNT(v.id) as cantidad
                FROM ventas v
                JOIN modelos m ON v.modelo_id = m.id
                JOIN marcas ma ON m.marca_id = ma.id
                WHERE v.fecha_venta LIKE ?
                GROUP BY ma.nombre, m.nombre
                ORDER BY cantidad DESC LIMIT 1
            ''', (pattern,))
            row = cur.fetchone()
            if row and row[2] > 0:
                datos_raw = f"Vehículo más vendido en {date_filter}: {row[0]} {row[1]} con {row[2]} unidades."
                return generar_respuesta_natural(question, datos_raw)
            return f"No hay ventas registradas en {date_filter}."

        if intent == "VENTAS_POR_FECHA" and pattern:
            cur.execute("SELECT COUNT(*), ROUND(COALESCE(SUM(precio_final),0),2) FROM ventas WHERE fecha_venta LIKE ?", (pattern,))
            cant, monto = cur.fetchone()
            datos_raw = f"En {date_filter} se vendieron {cant} autos, con un ingreso de {_format_money(monto)}."
            return generar_respuesta_natural(question, datos_raw)

    finally:
        conn.close()
    return None

def process_question_strict(question: str, history: list = None) -> str:
    """Punto de entrada principal para el procesamiento estricto."""
    if not is_inventory_question(question):
        return "Lo siento, solo puedo ayudar con información del concesionario (marcas, modelos, vendedores y ventas)."
    
    intent = classify_intent(question)
    direct = handle_direct_query(intent, question)
    if direct:
        return direct
    
    # Fallback mejorado
    return "Disculpa, no logré entender bien tu solicitud. Por favor reformúlala, por ejemplo:\n• ¿Quién ha vendido más autos?\n• Vendedor que más vendió en octubre 2025\n• Vehículo más vendido en junio 2024"