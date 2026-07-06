"""
Asistente IA del Concesionario - Chatbot con Ollama + Streamlit
Pipeline estricto para máxima precisión y cero alucinaciones.
Solo responde preguntas relacionadas con la base de datos del concesionario.
"""

import streamlit as st
from database import init_database, populate_sample_data, get_table_stats
from strict_pipeline import process_question_strict

# ============================================================
# INICIALIZACIÓN Y UI
# ============================================================

def init_session_state():
    """Inicializa el estado de la sesión de forma segura."""
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "¡Hola! Soy AutoBot, el asistente oficial del Concesionario Nacional. Puedo ayudarte con información precisa sobre nuestras marcas, modelos, vendedores y ventas. ¿Qué necesitas saber?"
            }
        ]
    if "db_ready" not in st.session_state:
        st.session_state.db_ready = False


def ensure_database():
    """Inicializa la BD una sola vez por sesión (o si está vacía)."""
    if not st.session_state.db_ready:
        with st.spinner("Verificando base de datos del concesionario..."):
            init_database()
            populate_sample_data()
            st.session_state.db_ready = True
        stats = get_table_stats()
        st.success(f"✅ Base de datos lista: {stats['marcas']} marcas, {stats['modelos']} modelos, {stats['vendedores']} vendedores, {stats['ventas']} ventas.")


def render_sidebar():
    """Barra lateral informativa y útil."""
    st.sidebar.title("🚗 Concesionario Nacional")
    st.sidebar.markdown("### Asistente IA con Ollama + Llama 3")
    
    try:
        stats = get_table_stats()
    except Exception:
        stats = {"marcas": "?", "modelos": "?", "vendedores": "?", "ventas": "?"}
    
    st.sidebar.markdown("#### 📊 Estadísticas actuales")
    st.sidebar.metric("Marcas", stats["marcas"])
    st.sidebar.metric("Modelos", stats["modelos"])
    st.sidebar.metric("Vendedores", stats["vendedores"])
    st.sidebar.metric("Ventas registradas", stats["ventas"])
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("#### 🔒 Restricciones estrictas")
    st.sidebar.info(
        "Este asistente **solo** responde preguntas sobre:\n\n"
        "• Marcas y modelos de vehículos\n"
        "• Vendedores y su desempeño\n"
        "• Ventas y estadísticas\n"
        "• Precios y disponibilidad\n\n"
        "Cualquier otro tema (deportes, recetas, programación, etc.) será rechazado automáticamente."
    )
    
    if st.sidebar.button("🗑️ Limpiar conversación", use_container_width=True):
        st.session_state.messages = st.session_state.messages[:1]
        st.rerun()
    
    st.sidebar.markdown("---")
    st.sidebar.caption("Modelo: llama3:latest | Motor: pipeline estricto + SQLite\n100% local y privado")


def display_chat():
    """Renderiza el historial de chat."""
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def handle_user_question(question: str):
    """Procesa la pregunta con el pipeline estricto y muestra respuesta."""
    # Echo del usuario
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)
    
    # Respuesta del asistente
    with st.chat_message("assistant"):
        with st.spinner("Consultando nuestro inventario con precisión..."):
            try:
                respuesta = process_question_strict(question, st.session_state.messages)
            except Exception as e:
                respuesta = "Disculpa, tuve un problema técnico procesando tu consulta. Por favor intenta de nuevo."
        st.markdown(respuesta)
    
    st.session_state.messages.append({"role": "assistant", "content": respuesta})


def main():
    st.set_page_config(
        page_title="AutoBot - Asistente del Concesionario",
        page_icon="🚗",
        layout="centered"
    )
    
    init_session_state()
    ensure_database()
    render_sidebar()
    
    st.title("🚗 AutoBot")
    st.caption("Asistente Inteligente del Concesionario Nacional • Respuestas 100% basadas en datos reales")
    
    display_chat()
    
    # Input
    if question := st.chat_input("Escribe tu pregunta sobre el concesionario (marcas, modelos, vendedores, ventas, precios)..."):
        handle_user_question(question)


if __name__ == "__main__":
    main()
