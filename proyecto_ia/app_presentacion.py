"""
pipeline estricto (strict_pipeline.py) como cerebro principal.
"""

import streamlit as st
from database import init_database, populate_sample_data, get_table_stats
from strict_pipeline import process_question_strict

st.set_page_config(page_title="AutoBot - Concesionario Nacional", page_icon="🚗", layout="centered")

st.title("🚗 AutoBot")
st.caption("Asistente Inteligente del Concesionario Nacional • Precisión garantizada")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "¡Hola! Soy AutoBot. Puedo ayudarte con información precisa sobre nuestro inventario, vendedores y ventas. ¿Qué necesitas saber?"}
    ]

if "db_ready" not in st.session_state:
    with st.spinner("Preparando base de datos..."):
        init_database()
        populate_sample_data()
    st.session_state.db_ready = True
    try:
        stats = get_table_stats()
        st.caption(f"✅ {stats['marcas']} marcas • {stats['modelos']} modelos • {stats['ventas']} ventas")
    except Exception:
        pass

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Escribe tu pregunta sobre el concesionario..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Consultando nuestro inventario con precisión..."):
            try:
                respuesta = process_question_strict(prompt, st.session_state.messages)
            except Exception as e:
                respuesta = "Disculpa, tuve un problema técnico. Por favor intenta de nuevo."
            st.markdown(respuesta)
            st.session_state.messages.append({"role": "assistant", "content": respuesta})
