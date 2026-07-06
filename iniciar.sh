#!/bin/bash
echo "🚀 Encendiendo la base de datos (SQL Server)..."
sudo docker start sqlserver

echo "🧠 Despertando el motor de IA (Ollama)..."
sudo systemctl start ollama

echo "⏳ Esperando 5 segundos para que los servicios arranquen..."
sleep 5

echo "🐍 Activando entorno virtual..."
# Asegúrate de que la ruta sea correcta. Asumo que el entorno se llama env_ia
source env_ia/bin/activate

echo "🌐 Levantando la interfaz de la IA..."
# Ya no necesitamos "python3 -m", al estar en el venv podemos usar streamlit directo
streamlit run web_ia.py
