# 🚗 AutoBot - Asistente IA del Concesionario

Chatbot inteligente en lenguaje natural que **únicamente** responde preguntas sobre la base de datos del concesionario de vehículos. Desarrollado con **Ollama + Llama 3 + Streamlit + SQLite**.

## ✨ Características

- **4 tablas interconectadas** con **1000 registros cada una**:
  - `marcas` (1000 marcas, mezcla de reales y generadas)
  - `modelos` (1000 modelos con precios y tipos variados)
  - `vendedores` (1000 vendedores con comisiones)
  - `ventas` (1000 ventas con relaciones correctas)

- **Guardrails estrictos**: La IA rechaza cualquier pregunta ajena al concesionario (deportes, recetas, programación, etc.)

- **Chatbot en lenguaje natural**: Pregunta como hablarías con una persona. La IA convierte tu pregunta a SQL, ejecuta y responde de forma natural.

- **Totalmente local**: Usa Ollama (sin enviar datos a la nube).

## 📋 Requisitos

- Python 3.9+
- Ollama instalado y con el modelo `llama3:latest`
- Streamlit y ollama-python

## 🚀 Instalación y Uso

### 1. Verifica que Ollama esté instalado y corriendo

```bash
ollama list
# Debe mostrar: llama3:latest
```

Si no tienes el modelo:

```bash
ollama pull llama3:latest
```

### 2. Instala dependencias (si hace falta)

```bash
pip install -r requirements.txt
```

### 3. Inicia el sistema

```bash
./iniciar_IA.sh
```

Abre tu navegador en: **http://localhost:8501**

### 4. Para detener

```bash
./apagar_IA.sh
```

## 💬 Ejemplos de Preguntas que Puedes Hacer

### Sobre marcas y modelos:
- ¿Qué marcas tenemos disponibles?
- ¿Cuántos modelos de Toyota hay?
- Muéstrame los SUV de BMW y Audi con su precio base
- ¿Cuál es el auto más barato de la marca Kia?

### Sobre ventas y estadísticas:
- ¿Cuántas ventas se han realizado este año?
- ¿Cuál es el vendedor que más ha vendido?
- ¿Cuánto dinero se ha vendido en total del modelo RAV4?
- Top 5 modelos más vendidos

### Sobre vendedores:
- Lista todos los vendedores con su porcentaje de comisión
- ¿Quiénes son los vendedores contratados en 2022?
- ¿Cuál es el promedio de ventas por vendedor?

### Preguntas que serán rechazadas (correctamente):
- ¿Quién ganó el mundial?
- ¿Cómo hago una torta?
- Explícame qué es Python
- Cuéntame un chiste

## 🗄️ Estructura del Proyecto

```
proyecto_ia/
├── database.py           # Lógica de SQLite + seeding de 1000 registros por tabla
├── strict_pipeline.py    # Motor de IA estricto y preciso (handlers directos + LLM controlado)
├── web_ia.py             # App Streamlit principal (UI completa + sidebar)
├── app_presentacion.py   # Versión minimalista para demos/presentaciones
├── iniciar_IA.sh         # Script de inicio (recomendado)
├── apagar_IA.sh          # Script de apagado
├── requirements.txt
├── concesionario.db      # Base de datos SQLite (generada automáticamente)
└── README.md
```

## 🔒 Cómo Funcionan los Guardrails

El sistema usa **dos llamadas al LLM** por pregunta:

1. **Clasificación**: "¿Esta pregunta es sobre el concesionario?" → Solo SI/NO
2. Si es NO → Respuesta de rechazo inmediata
3. Si es SI → Genera SQL seguro → Ejecuta → Responde naturalmente

Además, la ejecución de SQL está protegida contra cualquier comando destructivo.

## 🛠️ Personalización

- Cambia el modelo en `web_ia.py` (línea `OLLAMA_MODEL`)
- Los datos se generan en `database.py` → `populate_sample_data()` (actualmente 1000 por tabla)
- Ajusta los prompts del sistema para cambiar el tono de las respuestas

## 📝 Notas Técnicas

- La base de datos se crea automáticamente en `concesionario.db` la primera vez (1000 registros por tabla)
- **Pipeline de precisión**: Para consultas amplias ("todos los vendedores", "top ventas", listas grandes, etc.) se usan handlers directos sobre SQLite (0 alucinaciones). El LLM solo se usa para consultas específicas y para redactar la respuesta final de forma natural.
- Todas las respuestas están en español
- El sistema es 100% local y privado
- Funciona excelente con llama3 (4.7GB). Modelos más pequeños pueden dar peores resultados en SQL.

---

Desarrollado como demostración de IA local con restricciones fuertes de dominio.