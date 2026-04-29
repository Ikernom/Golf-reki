import google.generativeai as genai
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import json
import re
import io
from src.maintenance import get_vehicle_info


def ai_analyze_csv(raw_csv_text: str) -> dict:
    """Analiza el log con la última versión de Gemini Flash (Optimizado)."""
    info = get_vehicle_info()
    api_key = info.get("gemini_api_key")
    if not api_key: return {"error": "⚠️ Configura API Key."}

    try:
        lines = raw_csv_text.splitlines()
        best_sep = "," if raw_csv_text.count(",") > raw_csv_text.count(";") else ";"
        h_idx = 0
        cols = []
        for i, line in enumerate(lines[:30]): # Escaneo más corto
            parts = [p.strip() for p in line.split(best_sep)]
            if len(parts) > len(cols):
                cols = parts
                h_idx = i
        
        sample = "\n".join(lines[h_idx:h_idx+80]) # Muestra reducida para ahorrar tokens
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-flash-latest')
        
        prompt = f"Analiza este log de VCDS (VW Golf MK4). Devuelve SOLO JSON con grupos de gráficas (nombre y columnas) y un breve análisis técnico. Columnas: {cols}. Muestra: {sample}"
        response = model.generate_content(prompt)
        text = response.text.strip()
        if text.startswith("```"):
            text = re.sub(r'^```json\s*|\s*```$', '', text)
        return json.loads(text)
    except Exception as e:
        return {"error": f"Error IA: {str(e)}"}


def ai_build_charts(raw_csv_text: str, structure: dict) -> list:
    """Construye gráficas sin llamadas extra a la IA."""
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
        for g in structure.get("groups", []):
            fig = go.Figure()
            for t_col in g.get("columns", []):
                if t_col in numeric_df.columns:
                    fig.add_trace(go.Scatter(x=x_axis, y=numeric_df[t_col], name=t_col, mode='lines'))
            if len(fig.data) > 0:
                fig.update_layout(title=g['name'], template="plotly_dark", font=dict(family="Share Tech Mono"))
                figures.append({"name": g["name"], "fig": fig})
        return figures
    except: return []


def ai_chat_response(raw_csv_text: str, user_query: str, history: list = None) -> str:
    """Chat de log optimizado."""
    info = get_vehicle_info()
    api_key = info.get("gemini_api_key")
    if not api_key: return "⚠️ Configura API Key."
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-flash-latest')
        prompt = f"Mecánico TDI. Log: {raw_csv_text[:1500]}. Pregunta: {user_query}. Sé breve."
        return model.generate_content(prompt).text
    except Exception as e:
        if "429" in str(e): return "⚠️ **SISTEMA SATURADO**. Espera 20s."
        return f"Error: {e}"


@st.cache_data(ttl=60, show_spinner=False)
def ai_master_chat_response(user_query: str) -> str:
    """Chat maestro con visión TOTAL y CACHÉ para evitar 429."""
    from src.maintenance import (
        get_vehicle_info, list_entries, list_future_mods, 
        get_active_faults
    )
    info = get_vehicle_info()
    api_key = info.get("gemini_api_key")
    if not api_key: return "⚠️ Configura API Key."

    try:
        mantenimiento = [f"{e['date']}: {e['description']}" for e in list_entries()]
        wishlist = [f"{m['description']} ({m['priority']})" for m in list_future_mods()]
        averias = [f['component'] for f in get_active_faults()]
        
        contexto = f"Golf MK4. KM: {info.get('current_mileage')}. Mant: {mantenimiento}. Mods: {wishlist}. Averías: {averias}."
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-flash-latest')
        response = model.generate_content(f"{contexto}\nPregunta: {user_query}")
        return response.text
    except Exception as e:
        if "429" in str(e): return "⚠️ **SISTEMA SATURADO**. Espera 10s."
        return f"Error: {str(e)}"
