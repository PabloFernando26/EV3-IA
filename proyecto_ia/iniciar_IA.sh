#!/bin/bash
set -e

echo "🧠 Verificando Ollama..."
if ! ollama list >/dev/null 2>&1; then
    echo "⚠️  Ollama no responde. Asegúrate de que esté corriendo (ollama serve o systemctl)."
    echo "   Intentando arrancar con systemd (puede requerir sudo)..."
    sudo systemctl start ollama 2>/dev/null || true
    sleep 2
fi

echo "📦 Verificando modelo llama3:latest..."
ollama pull llama3:latest 2>/dev/null || echo "   (Si falla, ejecuta manualmente: ollama pull llama3:latest)"

echo ""
echo "🌐 Levantando AutoBot (Streamlit)..."
echo ""
echo "════════════════════════════════════════════════════════════"
echo "   🚗 AutoBot - Asistente del Concesionario Nacional"
echo "   Abre tu navegador en: http://localhost:8501"
echo "════════════════════════════════════════════════════════════"
echo ""

# Preferir web_ia.py (UI completa). Si no existe usa app_presentacion.py
APP="web_ia.py"
if [ ! -f "$APP" ]; then
    APP="app_presentacion.py"
fi

python3 -m streamlit run "$APP" --server.headless true --server.port 8501
