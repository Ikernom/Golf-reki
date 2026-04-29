import google.generativeai as genai
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import json
import re
import io
from src.maintenance import get_vehicle_info


def ai_analyze_csv(raw_csv_text: str) -> dict:
    """Analiza el log con Gemini enviándole solo la parte que contiene datos."""
    info = get_vehicle_info()
    api_key = info.get("gemini_api_key")
    if not api_key: return {"error": "⚠️ Configura API Key."}

    try:
        # Intentamos encontrar dónde empiezan los datos para ayudar a la IA
        lines = raw_csv_text.splitlines()
        data_start_idx = 0
        for i, line in enumerate(lines[:30]):
            if "Group" in line or "RPM" in line or "Speed" in line:
                data_start_idx = i
                break
        
        # Le pasamos a la IA un trozo de la cabecera y un trozo de los datos reales
        csv_sample = "\n".join(lines[data_start_idx:data_start_idx+50])

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-flash-latest')
        
        prompt = f"""Eres un experto en VCDS. Analiza este CSV.
Devuelve SOLO un JSON:
{{
  "groups": [{{ "gid": "001", "name": "Nombre", "columns": ["Col1", "Col2"] }}],
  "analysis": "resumen",
  "detected_faults": []
}}
CSV:
{csv_sample}"""

        response = model.generate_content(prompt)
        text = re.sub(r'^```json\s*|\s*```$', '', response.text.strip())
        return json.loads(text)
    except Exception as e:
        return {"error": f"Error IA: {e}"}


def ai_build_charts(raw_csv_text: str, structure: dict) -> list:
    """Lector de CSV especializado en logs de VCDS con cabeceras largas."""
    try:
        lines = raw_csv_text.splitlines()
        best_sep = "," if raw_csv_text.count(",") > raw_csv_text.count(";") else ";"
        
        # BUSCAMOS LA FILA DE CABECERA REAL (la que tiene los nombres de las columnas)
        header_idx = 0
        for i, line in enumerate(lines[:40]):
            # Una fila de datos real de VCDS suele tener muchos separadores
            if line.count(best_sep) >= 3 and ("Group" in line or "TIME" in line.upper() or "RPM" in line.upper()):
                header_idx = i
                break
        
        # Leer el CSV desde esa fila
        df = pd.read_csv(io.StringIO("\n".join(lines[header_idx:])), sep=best_sep, on_bad_lines='skip')
        
        # Limpiar columnas
        df.columns = [str(c).strip() for c in df.columns]
        
        # Eliminar filas que sean solo texto (VCDS a veces repite cabeceras)
        df = df[pd.to_numeric(df.iloc[:, 0], errors='coerce').notna() | pd.to_numeric(df.iloc[:, 1], errors='coerce').notna()]

        time_col = next((c for c in df.columns if 'TIME' in c.upper() or 'STAMP' in c.upper()), df.columns[0])
        figures = []
        
        for g in structure.get("groups", []):
            fig = go.Figure()
            json_cols = [c.strip().lower() for c in g.get("columns", [])]
            
            for dfc in df.columns:
                if any(jc in dfc.lower() for jc in json_cols):
                    y_data = pd.to_numeric(df[dfc], errors='coerce')
                    if y_data.notna().any():
                        fig.add_trace(go.Scatter(x=df[time_col], y=y_data, name=dfc, mode='lines'))
            
            if len(fig.data) > 0:
                fig.update_layout(
                    title=f"GRUPO {g.get('gid')}: {g['name']}",
                    xaxis_title="Tiempo (s)",
                    template="plotly_dark",
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    hovermode="x unified"
                )
                figures.append({"name": g["name"], "fig": fig})
        
        return figures
    except Exception:
        return []

def ai_chat_response(raw_csv_text: str, user_query: str, history: list = None) -> str:
    # Versión simplificada para mayor velocidad
    info = get_vehicle_info()
    api_key = info.get("gemini_api_key")
    if not api_key: return "⚠️ API Key."
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-flash-latest')
        prompt = f"Mecánico TDI ALH. Log: {raw_csv_text[:2000]}\nPregunta: {user_query}"
        return model.generate_content(prompt).text
    except: return "Error en chat."
