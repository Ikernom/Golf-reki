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
        data_start_idx = 0
        for i, line in enumerate(lines[:40]):
            if line.count(",") >= 3 or line.count(";") >= 3:
                if "Group" in line or "RPM" in line or "TIME" in line.upper():
                    data_start_idx = i
                    break
        
        csv_sample = "\n".join(lines[data_start_idx:data_start_idx+60])
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-flash-latest')
        
        prompt = f"""Analiza este log de VCDS. Devuelve SOLO JSON:
{{
  "groups": [{{ "gid": "011", "name": "Turbo", "columns": ["Engine Speed", "Boost Pressure"] }}],
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
    """Construye gráficas con lógica de 'Smart Match'."""
    try:
        lines = raw_csv_text.splitlines()
        best_sep = "," if raw_csv_text.count(",") > raw_csv_text.count(";") else ";"
        header_idx = 0
        for i, line in enumerate(lines[:50]):
            if line.count(best_sep) >= 3 and ("Group" in line or "TIME" in line.upper()):
                header_idx = i
                break
        
        df = pd.read_csv(io.StringIO("\n".join(lines[header_idx:])), sep=best_sep, on_bad_lines='skip')
        df.columns = [str(c).strip() for c in df.columns]
        
        # Quedarse solo con columnas numéricas
        numeric_df = df.apply(pd.to_numeric, errors='coerce')
        valid_cols = [c for c in numeric_df.columns if numeric_df[c].notna().any()]
        
        time_col = next((c for c in df.columns if 'TIME' in c.upper() or 'STAMP' in c.upper()), df.columns[0])
        figures = []
        
        groups = structure.get("groups", [])
        
        # Si la IA no devolvió grupos, creamos uno genérico con todo lo que sea numérico
        if not groups:
            groups = [{"gid": "ALL", "name": "Datos Detectados", "columns": valid_cols}]

        for g in groups:
            fig = go.Figure()
            target_cols = [c.lower() for c in g.get("columns", [])]
            
            added_any = False
            for dfc in valid_cols:
                # Match si el nombre está en el JSON O si el nombre del grupo está en la columna
                match_json = any(tc in dfc.lower() for tc in target_cols)
                match_group = g["name"].lower() in dfc.lower()
                
                if match_json or match_group:
                    fig.add_trace(go.Scatter(x=df[time_col], y=numeric_df[dfc], name=dfc, mode='lines'))
                    added_any = True
            
            if added_any:
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
    except Exception as e:
        st.error(f"Error gráfico: {e}")
        return []

def ai_chat_response(raw_csv_text: str, user_query: str, history: list = None) -> str:
    info = get_vehicle_info()
    api_key = info.get("gemini_api_key")
    if not api_key: return "API Key faltante."
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-flash-latest')
        prompt = f"Mecánico TDI. Pregunta: {user_query}. Datos: {raw_csv_text[:2000]}"
        return model.generate_content(prompt).text
    except: return "Error."
