#!/bin/bash
echo "🛑 Apagando la base de datos (SQL Server)..."
sudo docker stop sqlserver

echo "🧠 Apagando el motor de IA (Ollama)..."
sudo systemctl stop ollama

echo "🧹 Cerrando la interfaz web (Streamlit)..."
# Usamos pkill para buscar el proceso de streamlit asociado a tu archivo
pkill -f "streamlit run web_ia.py"

echo "✅ ¡Todo apagado de forma segura! Memoria RAM liberada. ¡Ve a descansar!"
