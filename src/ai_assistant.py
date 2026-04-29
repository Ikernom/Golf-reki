import google.generativeai as genai
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import json
import re
import io
from src.maintenance import get_vehicle_info


def ai_analyze_csv(raw_csv_text: str) -> dict:
    """Analiza el log con Gemini."""
    info = get_vehicle_info()
    api_key = info.get("gemini_api_key")
    if not api_key: return {"error": "⚠️ Configura API Key."}

    try:
        lines = raw_csv_text.splitlines()
        # Buscamos dónde empieza la acción (línea con más de 3 comas/puntos y coma)
        start_row = 0
        for i, line in enumerate(lines[:50]):
            if line.count(",") >= 3 or line.count(";") >= 3:
                start_row = i
                break
        
        sample = "\n".join(lines[start_row:start_row+100])
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-flash-latest')
        
        prompt = f"""Experto en VCDS. Analiza este CSV de un TDI. Devuelve SOLO JSON:
{{
  "groups": [{{ "gid": "001", "name": "Nombre", "columns": ["NombreExacto1"] }}],
  "analysis": "resumen técnico corto",
  "detected_faults": []
}}
CSV:
{sample}"""

        response = model.generate_content(prompt)
        text = re.sub(r'^```json\s*|\s*```$', '', response.text.strip())
        return json.loads(text)
    except Exception as e:
        return {"error": f"Error IA: {e}"}


def ai_build_charts(raw_csv_text: str, structure: dict) -> list:
    """Construye gráficas. Si falla la IA, usa lógica de detección automática."""
    lines = raw_csv_text.splitlines()
    best_sep = "," if raw_csv_text.count(",") > raw_csv_text.count(";") else ";"
    
    # 1. Encontrar la cabecera real
    h_idx = 0
    for i, line in enumerate(lines[:50]):
        if line.count(best_sep) >= 3:
            h_idx = i
            break
            
    # 2. Cargar DataFrame
    df = pd.read_csv(io.StringIO("\n".join(lines[h_idx:])), sep=best_sep, on_bad_lines='skip')
    df.columns = [str(c).strip() for c in df.columns]
    
    # 3. Identificar columnas numéricas
    numeric_df = df.apply(pd.to_numeric, errors='coerce')
    cols_con_datos = [c for c in numeric_df.columns if numeric_df[c].notna().sum() > 5]
    
    if not cols_con_datos:
        return []

    # 4. Eje X (Tiempo o índice)
    time_col = next((c for c in df.columns if 'TIME' in c.upper() or 'STAMP' in c.upper()), None)
    x_axis = df[time_col] if time_col else numeric_df.index

    figures = []
    groups = structure.get("groups", [])
    
    # --- SI HAY GRUPOS DE LA IA ---
    if groups:
        for g in groups:
            fig = go.Figure()
            target_cols = [c.lower() for c in g.get("columns", [])]
            
            for dfc in cols_con_datos:
                # Match flexible: ¿el nombre que pide la IA está dentro del nombre de la columna?
                if any(tc in dfc.lower() for tc in target_cols) or g["name"].lower() in dfc.lower():
                    fig.add_trace(go.Scatter(x=x_axis, y=numeric_df[dfc], name=dfc, mode='lines'))
            
            if len(fig.data) > 0:
                fig.update_layout(title=f"GRUPO {g.get('gid')}: {g['name']}", template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                figures.append({"name": g["name"], "fig": fig})

    # --- SI NO HAY GRUPOS O NO COINCIDEN, GRAFICAMOS TODO LO DETECTADO ---
    if not figures:
        # Agrupamos por 4 columnas para no saturar una sola gráfica
        for i in range(0, len(cols_con_datos), 4):
            chunk = cols_con_datos[i:i+4]
            fig = go.Figure()
            for col in chunk:
                fig.add_trace(go.Scatter(x=x_axis, y=numeric_df[col], name=col, mode='lines'))
            
            fig.update_layout(title=f"Datos Detectados (Automático) - Bloque {i//4 + 1}", template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            figures.append({"name": f"Auto {i//4 + 1}", "fig": fig})
            
    return figures

def ai_chat_response(raw_csv_text: str, user_query: str, history: list = None) -> str:
    info = get_vehicle_info()
    api_key = info.get("gemini_api_key")
    if not api_key: return "Falta API Key."
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-flash-latest')
        prompt = f"Mecánico TDI. Datos log: {raw_csv_text[:2000]}. Usuario: {user_query}"
        return model.generate_content(prompt).text
    except Exception as e: return f"Error: {e}"
