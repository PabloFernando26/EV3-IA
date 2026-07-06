#!/bin/bash
echo "🧹 Cerrando la interfaz web (Streamlit)..."
pkill -f "streamlit run web_ia.py" 2>/dev/null || true
pkill -f "streamlit run app_presentacion.py" 2>/dev/null || true

echo "🧠 Deteniendo Ollama (opcional)..."
read -p "¿Quieres apagar también Ollama? (s/N): " confirm
if [[ "$confirm" =~ ^[sS]$ ]]; then
    sudo systemctl stop ollama 2>/dev/null || pkill -f "ollama" 2>/dev/null || true
    echo "Ollama detenido."
else
    echo "Ollama sigue corriendo (recomendado para uso rápido)."
fi

echo "✅ ¡Chatbot cerrado correctamente!"
