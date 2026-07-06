# -*- coding: utf-8 -*-
import streamlit as st
import pyodbc
import ollama
import json
import pandas as pd
from streamlit_lottie import st_lottie
import re

# --- 1. CONFIGURACIÓN DE LA PÁGINA Y ESTILOS ---
st.set_page_config(page_title="IA Concesionaria", page_icon="🚗", layout="wide")

st.markdown("""
<style>
    .stApp {
        background: linear-gradient(-45deg, #0e1117, #1a1c23, #151821, #262730);
        background-size: 400% 400%;
        animation: gradientBG 15s ease infinite;
    }
    @keyframes gradientBG {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    .stChatMessage {
        background-color: rgba(255, 255, 255, 0.03);
        border-radius: 15px;
        padding: 15px;
        margin-bottom: 10px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
</style>
""", unsafe_allow_html=True)

st.title("🚗 Automotora IA - Asistente Virtual")
st.markdown("**¡Hola!** Soy tu asistente virtual de la concesionaria. Pregúntame sobre nuestro catálogo, marcas, kilometraje o precios.")

# --- 2. FUNCIONES AUXILIARES ---
def load_lottiefile(filepath: str):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return None

@st.cache_resource
def iniciar_conexion():
    conexion = pyodbc.connect(
        'DRIVER={ODBC Driver 18 for SQL Server};'
        'SERVER=localhost;'
        'DATABASE=ConcesionariaReal;'
        'UID=sa;'
        'PWD=Kssplvda0916++;'
        'TrustServerCertificate=yes;',
        autocommit=True
    )
    conexion.setdecoding(pyodbc.SQL_CHAR, encoding='utf-8')
    conexion.setdecoding(pyodbc.SQL_WCHAR, encoding='utf-8')
    conexion.setencoding(encoding='utf-8')
    return conexion

try:
    conexion = iniciar_conexion()
    cursor = conexion.cursor()
except Exception as e:
    st.error(f"❌ Error al conectar a la base de datos: {e}")
    st.stop()

# --- 3. SIDEBAR ---
lottie_car = load_lottiefile("car.json")
with st.sidebar:
    if lottie_car:
        st_lottie(lottie_car, height=150, key="car_animation")
    
    st.header("⚙️ Panel de Control")
    st.markdown("""
    **Ejemplos de preguntas:**
    - ¿Qué vehículos vendió el vendedor Dealer?
    - Dame 5 autos que vendió el Dealer
    - Autos diésel con menos de 50.000 km
    """)
    st.divider()
    if st.button("🗑️ Limpiar chat", type="primary"):
        st.session_state.mensajes = []
        st.rerun()

# --- 4. HISTORIAL ---
if "mensajes" not in st.session_state:
    st.session_state.mensajes = []

for msg in st.session_state.mensajes:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- 5. ESQUEMA MEJORADO ---
esquema_bd = """
La base de datos tiene 4 tablas. USA SIEMPRE INNER JOIN:

1. Marcas(MarcaID, NombreMarca)
2. Modelos(ModeloID, MarcaID, NombreModelo, Combustible, Transmision)
3. Vendedores(VendedorID, TipoVendedor)     -- 'Dealer', 'Individual', etc.
4. Vehiculos(VehiculoID, ModeloID, VendedorID, Anio, Kilometraje, PrecioVenta, Dueno)

Columnas obligatorias a seleccionar:
Marcas.NombreMarca, Modelos.NombreModelo, Vehiculos.Anio, Vehiculos.PrecioVenta, 
Vehiculos.Kilometraje, Modelos.Combustible, Vehiculos.Dueno

REGLAS:
- Usa sintaxis SQL Server → SELECT TOP 30 (nunca LIMIT)
- Para "vendedor Dealer" usa: WHERE Vendedores.TipoVendedor = 'Dealer'
"""

few_shot = """
Ejemplos:

Pregunta: "dame 5 vehículos que vendió el vendedor Dealer"
SQL:
SELECT TOP 30 Marcas.NombreMarca, Modelos.NombreModelo, Vehiculos.Anio, Vehiculos.PrecioVenta, 
Vehiculos.Kilometraje, Modelos.Combustible, Vehiculos.Dueno
FROM Vehiculos 
INNER JOIN Modelos ON Vehiculos.ModeloID = Modelos.ModeloID
INNER JOIN Marcas ON Modelos.MarcaID = Marcas.MarcaID
INNER JOIN Vendedores ON Vehiculos.VendedorID = Vendedores.VendedorID
WHERE Vendedores.TipoVendedor = 'Dealer'
ORDER BY Vehiculos.PrecioVenta DESC
"""

# --- 6. LÓGICA PRINCIPAL MEJORADA ---
pregunta = st.chat_input("Ej: ¿Qué vehículos vendió el vendedor Dealer?")

if pregunta:
    st.session_state.mensajes.append({"role": "user", "content": pregunta})
    with st.chat_message("user"):
        st.markdown(pregunta)

    with st.chat_message("assistant"):
        with st.spinner("Analizando inventario..."):

            # Guardrail
            prompt_filtro = f"Responde SOLO 'SI' o 'NO': ¿La pregunta '{pregunta}' trata sobre vehículos o inventario?"
            filtro = ollama.chat(model='llama3', messages=[{'role': 'user', 'content': prompt_filtro}], options={"temperature": 0.0})['message']['content'].upper()

            if 'NO' in filtro:
                respuesta = "Solo puedo ayudarte con consultas sobre nuestro inventario de vehículos."
                st.markdown(respuesta)
                st.session_state.mensajes.append({"role": "assistant", "content": respuesta})
            else:
                # Generar SQL (mejorado con ejemplos)
                prompt_sql = f"""Eres experto en SQL Server.
{esquema_bd}

{few_shot}

Genera SOLO la consulta SQL Server (sin explicaciones) para: "{pregunta}"
"""
                sql_bruto = ollama.chat(model='llama3', messages=[{'role': 'user', 'content': prompt_sql}], options={"temperature": 0.0})['message']['content']
                sql_limpio = sql_bruto.replace("```sql", "").replace("```", "").strip()

                # Ejecutar SQL
                datos_dict = []
                error_msg = None
                try:
                    cursor.execute(sql_limpio)
                    resultados = cursor.fetchall()
                    if resultados:
                        columnas = [col[0] for col in cursor.description]
                        datos_dict = [dict(zip(columnas, fila)) for fila in resultados]
                except Exception as e:
                    error_msg = str(e)

                datos_json = json.dumps(datos_dict, ensure_ascii=False, default=str) if datos_dict else "[]"

                # === Prompt Final Mejorado ===
                prompt_final = f"""
Eres un asesor de ventas profesional y amable.

DATOS REALES DEL INVENTARIO: {datos_json}
PREGUNTA DEL CLIENTE: "{pregunta}"

REGLAS OBLIGATORIAS:
- Responde SIEMPRE en lenguaje natural y profesional en español.
- Si el cliente pidió una cantidad (ej: "dame 5", "muéstrame 8"), intenta entregar **al menos esa cantidad** si hay datos suficientes.
- Usa formato bonito: Precio con $ y puntos. Kilometraje con km.
- Traduce: First Owner → único dueño | Petrol → bencina | Diesel → diésel
- NUNCA inventes datos. Solo usa la información proporcionada.
- Si hay pocos resultados, dilo con naturalidad.
- No menciones SQL, JSON ni base de datos.
- Empieza de forma natural, por ejemplo:
  - "Los vehículos que vendió el vendedor Dealer son los siguientes:"
  - "Aquí te muestro algunos autos con único dueño:"
"""

                mensajes_ollama = [{"role": "system", "content": prompt_final}]
                for msg in st.session_state.mensajes[-4:]:
                    if msg["content"] != pregunta:
                        mensajes_ollama.append({"role": msg["role"], "content": msg["content"]})
                mensajes_ollama.append({"role": "user", "content": pregunta})

                respuesta_final = ollama.chat(
                    model='llama3',
                    messages=mensajes_ollama,
                    options={"temperature": 0.2, "num_ctx": 4096}
                )['message']['content']

                st.markdown(respuesta_final)
                st.session_state.mensajes.append({"role": "assistant", "content": respuesta_final})