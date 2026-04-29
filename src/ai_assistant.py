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
Analiza este log CSV y devuelve SOLO un objeto JSON con esta estructura exacta:
{{
  "separator": "," o ";",
  "header_rows": número de filas de cabecera hasta que empiezan los nombres de las columnas,
  "groups": [
    {{
      "gid": "número del grupo",
      "name": "nombre descriptivo",
      "columns": ["Nombre Exacto Columna 1", "Nombre Exacto Columna 2"]
    }}
  ],
  "analysis": "resumen técnico",
  "detected_faults": [
    {{
      "component": "Nombre",
      "severity": "CRITICAL/WARNING",
      "description": "Explicación"
    }}
  ]
}}

IMPORTANTE: Los nombres en "columns" deben ser EXACTAMENTE iguales a los que aparecen en el CSV.
Si no hay fallos, "detected_faults" debe ser [].

CSV:
{csv_sample}"""

        response = model.generate_content(prompt)
        text = response.text.strip()

        # Limpiar markdown si viene envuelto
        text = re.sub(r'^```json\s*', '', text)
        text = re.sub(r'\s*```$', '', text)

        return json.loads(text)

    except Exception as e:
        return {"error": f"❌ Error con Gemini: {str(e)}"}


def ai_build_charts(raw_csv_text: str, structure: dict) -> list:
    """
    Construye gráficas usando Plotly basándose en el JSON de estructura.
    """
    import io

    sep = structure.get("separator", ",")
    header_rows = structure.get("header_rows", 0)
    groups = structure.get("groups", [])

    if not groups:
        return []

    try:
        # Leer el CSV con el separador y cabecera detectados
        df = pd.read_csv(io.StringIO(raw_csv_text), sep=sep, header=header_rows, on_bad_lines='skip')
        
        # Limpiar nombres de columnas
        df.columns = [str(c).strip() for c in df.columns]
        
        figures = []
        for g in groups:
            fig = go.Figure()
            
            # Detectar columna de tiempo
            time_col = None
            for col in df.columns:
                if 'TIME' in col.upper() or 'STAMP' in col.upper():
                    time_col = col
                    break
            
            if not time_col:
                time_col = df.columns[0] # Fallback a la primera columna

            # Filtrar columnas que realmente existen en el DF
            valid_cols = [c.strip() for c in g.get("columns", []) if c.strip() in df.columns]
            
            if not valid_cols:
                continue

            for col in valid_cols:
                # Asegurarse de que los datos son numéricos
                y_data = pd.to_numeric(df[col], errors='coerce')
                if y_data.isna().all():
                    continue
                    
                fig.add_trace(go.Scatter(
                    x=df[time_col],
                    y=y_data,
                    name=col,
                    mode='lines'
                ))
            
            if len(fig.data) == 0:
                continue

            fig.update_layout(
                title=f"GRUPO {g.get('gid', '???')}: {g.get('name', 'Análisis')}",
                xaxis_title="Tiempo (s)",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#ffffff"),
                hovermode="x unified",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            figures.append({"name": g.get("name"), "gid": g.get("gid"), "fig": fig})
            
        return figures
    except Exception:
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
        
        history_text = ""
        if history:
            for msg in history[-8:]:
                role = "Mecánico" if msg["role"] == "assistant" else "Usuario"
                history_text += f"{role}: {msg['content']}\n"

        prompt = f"""Eres un mecánico experto en motores VW TDI ALH.
Vehículo: {vehicle}
Log VCDS: {raw_csv_text[:4000]}
Historial: {history_text}
Usuario: {user_query}

Responde en español, breve y directo. Si te preguntan por gráficas, recuerda que TÚ YA HAS ANALIZADO los datos y el sistema las está dibujando, no digas que no puedes verlas."""

        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"❌ Error: {str(e)}"
