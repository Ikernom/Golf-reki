import google.generativeai as genai
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import json
import re
import io
from src.maintenance import get_vehicle_info


def ai_analyze_csv(raw_csv_text: str) -> dict:
    """Analiza el log con la última versión de Gemini Flash."""
    info = get_vehicle_info()
    api_key = info.get("gemini_api_key")
    if not api_key: return {"error": "⚠️ Configura API Key en Configuración."}

    try:
        lines = raw_csv_text.splitlines()
        best_sep = "," if raw_csv_text.count(",") > raw_csv_text.count(";") else ";"
        h_idx = 0
        cols = []
        for i, line in enumerate(lines[:50]):
            parts = [p.strip() for p in line.split(best_sep)]
            if len(parts) > len(cols):
                cols = parts
                h_idx = i
        
        sample = "\n".join(lines[h_idx:h_idx+150])
        column_list = ", ".join(cols)
        
        genai.configure(api_key=api_key)
        # Usamos el alias 'latest' para evitar errores de versión hardcodeada
        model = genai.GenerativeModel('gemini-flash-latest')
        
        prompt = f"""ERES UN INGENIEIRO EXPERTO EN TELEMETRÍA DE VOLKSWAGEN (ESPECIALISTA EN VCDS / VAG-COM).
Analiza este log de un Golf MK4 TDI.

INSTRUCCIONES:
1. Identifica TODAS las columnas importantes.
2. Crea grupos lógicos para graficar (Ej: "Rendimiento del Turbo", "Ciclo de Inyección", "Masas de Aire (MAF)").
3. Para cada grupo, dime qué columnas exactas deben ir juntas en una gráfica de Plotly.
4. Realiza un análisis técnico del estado del coche.

COLUMNAS DISPONIBLES: {column_list}

MUESTRA DE DATOS:
{sample}

DEVUELVE ÚNICAMENTE UN OBJETO JSON:
{{
  "groups": [
    {{ "gid": "Turbo", "name": "Presión de Sobrealimentación", "columns": ["ColumnName1", "ColumnName2"] }}
  ],
  "analysis": "Markdown técnico",
  "detected_faults": []
}}"""

        response = model.generate_content(prompt)
        text = response.text.strip()
        if text.startswith("```"):
            text = re.sub(r'^```json\s*|\s*```$', '', text)
        return json.loads(text)
    except Exception as e:
        return {"error": f"Error IA: {str(e)}"}


def ai_build_charts(raw_csv_text: str, structure: dict) -> list:
    """Construye gráficas usando la estructura dictada por la IA."""
    try:
        lines = raw_csv_text.splitlines()
        best_sep = "," if raw_csv_text.count(",") > raw_csv_text.count(";") else ";"
        h_idx = 0
        for i, line in enumerate(lines[:50]):
            if line.count(best_sep) >= 3:
                h_idx = i
                break
                
        df = pd.read_csv(io.StringIO("\n".join(lines[h_idx:])), sep=best_sep, on_bad_lines='skip', engine='python')
        df.columns = [str(c).strip() for c in df.columns]
        numeric_df = df.apply(pd.to_numeric, errors='coerce')
        time_col = next((c for c in df.columns if 'TIME' in c.upper() or 'STAMP' in c.upper()), None)
        x_axis = df[time_col] if time_col else numeric_df.index

        figures = []
        groups = structure.get("groups", [])
        
        for g in groups:
            fig = go.Figure()
            target_cols = g.get("columns", [])
            added_count = 0
            for t_col in target_cols:
                found_col = t_col if t_col in numeric_df.columns else None
                if not found_col:
                    matches = [c for c in numeric_df.columns if t_col.lower() in c.lower()]
                    if matches: found_col = matches[0]
                
                if found_col and numeric_df[found_col].notna().sum() > 0:
                    fig.add_trace(go.Scatter(x=x_axis, y=numeric_df[found_col], name=found_col, mode='lines'))
                    added_count += 1
            
            if added_count > 0:
                fig.update_layout(
                    title=f"DIAGNÓSTICO: {g['name'].upper()}",
                    template="plotly_dark",
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0.3)",
                    hovermode="x unified",
                    font=dict(family="Share Tech Mono")
                )
                figures.append({"name": g["name"], "fig": fig})
        return figures
    except Exception as e:
        return []


def ai_chat_response(raw_csv_text: str, user_query: str, history: list = None) -> str:
    """Chat de log con Gemini Flash Latest."""
    info = get_vehicle_info()
    api_key = info.get("gemini_api_key")
    if not api_key: return "⚠️ Configura API Key."
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-flash-latest')
        sample = raw_csv_text[:4000] 
        prompt = f"Analiza telemetría Golf IV: {sample}. Pregunta: {user_query}"
        return model.generate_content(prompt).text
    except Exception as e:
        if "429" in str(e): return "⚠️ **SISTEMA SATURADO (CUOTA 429)**. Reintenta en 30s."
        return f"Error: {e}"


def ai_master_chat_response(user_query: str, history: list = None) -> str:
    """Chat maestro con Gemini Flash Latest."""
    from src.maintenance import (
        get_vehicle_info, list_entries, list_future_mods, 
        get_active_faults, get_reminders
    )
    info = get_vehicle_info()
    api_key = info.get("gemini_api_key")
    if not api_key: return "⚠️ Configura API Key."

    try:
        mantenimiento = list_entries()[:15]
        wishlist = list_future_mods()
        averias = get_active_faults()
        recordatorios = get_reminders()
        km_actual = info.get("odo_actual", "Desconocido")

        contexto = f"""CEREBRO PROYECTO GOLF MK4 (SISTEMA LATEST).
Info Coche: {info.get('engine_type', 'Desconocido')}, {km_actual} KM.
Historial: {json.dumps([e['description'] for e in mantenimiento])}
Mods Wishlist: {json.dumps([m['description'] for m in wishlist])}
Averías: {json.dumps([f['component'] for f in averias])}
"""
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-flash-latest')
        full_prompt = f"{contexto}\n\nPregunta: {user_query}"
        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        if "429" in str(e): return "⚠️ **ECU OVERLOAD (429)**. Espera 30 segundos para enfriar el bus de datos."
        return f"Error Master Chat: {str(e)}"
