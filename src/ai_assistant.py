import google.generativeai as genai
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import json
import re
from src.maintenance import get_vehicle_info


def ai_analyze_csv(raw_csv_text: str) -> dict:
    """
    Envía el CSV crudo a Gemini y le pide que lo analice y devuelva
    instrucciones para generar las gráficas y detectar averías.
    """
    info = get_vehicle_info()
    api_key = info.get("gemini_api_key")

    if not api_key:
        return {"error": "⚠️ Configura tu Gemini API Key en Ajustes."}

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-flash-latest')

        # Limitamos el CSV para no saturar
        csv_sample = raw_csv_text[:8000]

        prompt = f"""Eres un experto en VCDS y motores VW TDI ALH.
Analiza este log CSV y devuelve SOLO un objeto JSON con:
1. "separator": "," o ";"
2. "header_rows": número de filas de cabecera.
3. "groups": lista de objetos con "gid", "name" y "columns" (lista de nombres de columnas).
4. "analysis": Resumen del estado mecánico (máx 100 palabras).
5. "detected_faults": Lista de fallos encontrados (si los hay), cada uno con:
   - "component": Nombre del componente (ej: "MAF", "Turbo", "Timing").
   - "severity": "CRITICAL" o "WARNING".
   - "description": Explicación técnica breve.

CSV:
{csv_sample}"""

        response = model.generate_content(prompt)
        text = response.text.strip()

        # Limpiar markdown
        text = re.sub(r'^```json\s*', '', text)
        text = re.sub(r'\s*```$', '', text)

        return json.loads(text)

    except Exception as e:
        return {"error": f"❌ Error con Gemini: {str(e)}"}


def ai_build_charts(raw_csv_text: str, structure: dict) -> list:
    """
    Usando la estructura que Gemini nos devolvió, construye las gráficas.
    """
    import io

    sep = structure.get("separator", ",")
    header_rows = structure.get("header_rows", 0)
    groups = structure.get("groups", [])

    if not groups:
        return []

    try:
        # Intentar leer el CSV
        df = pd.read_csv(io.StringIO(raw_csv_text), sep=sep, header=header_rows, on_bad_lines='skip')
        
        # Limpiar nombres de columnas (quitar espacios)
        df.columns = [c.strip() for c in df.columns]
        
        figures = []
        for g in groups:
            fig = go.Figure()
            
            # Buscar columna de tiempo (suele ser la primera del CSV o contener 'TIME')
            time_col = df.columns[0]
            for col in df.columns:
                if 'TIME' in col.upper():
                    time_col = col
                    break
            
            valid_cols = [c for c in g["columns"] if c in df.columns]
            
            if not valid_cols:
                continue

            for col in valid_cols:
                fig.add_trace(go.Scatter(
                    x=df[time_col],
                    y=df[col],
                    name=col,
                    mode='lines+markers' if len(df) < 50 else 'lines'
                ))
            
            fig.update_layout(
                title=f"Grupo {g['gid']}: {g['name']}",
                xaxis_title="Tiempo (s)",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#ffffff"),
                hovermode="x unified"
            )
            figures.append({"name": g["name"], "gid": g["gid"], "fig": fig})
            
        return figures
    except Exception as e:
        st.error(f"Error generando gráficas: {e}")
        return []


def ai_chat_response(raw_csv_text: str, user_query: str, history: list = None) -> str:
    """Chat con la IA sobre el log con memoria de conversación."""
    info = get_vehicle_info()
    api_key = info.get("gemini_api_key")

    if not api_key:
        return "⚠️ Configura tu Gemini API Key en Ajustes."

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-flash-latest')

        vehicle = f"Golf IV 1.9 TDI ALH, {info.get('current_mileage', '280000')} km"
        
        # Construir el contexto de la conversación
        history_text = ""
        if history:
            for msg in history[-10:]: # Enviamos los últimos 10 mensajes para no saturar
                role = "Mecánico" if msg["role"] == "assistant" else "Usuario"
                history_text += f"{role}: {msg['content']}\n"

        prompt = f"""Eres un mecánico experto en motores VW TDI ALH.
Vehículo: {vehicle}

Log VCDS (fragmento):
{raw_csv_text[:5000]}

Historial de conversación:
{history_text}

Usuario (pregunta actual): {user_query}

Responde en español, de forma profesional pero cercana. Mantén la continuidad de la charla anterior."""

        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"❌ Error: {str(e)}"
