import google.generativeai as genai
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import json
import re
import io
import time
from src.maintenance import get_vehicle_info

# --- WRAPPER DE REINTENTO PARA EVITAR 429 ---
def safe_generate_content(model, prompt, max_retries=3):
    """Lanza la petición a Gemini con reintentos automáticos si hay saturación (429)."""
    for attempt in range(max_retries):
        try:
            return model.generate_content(prompt)
        except Exception as e:
            if "429" in str(e) and attempt < max_retries - 1:
                wait_time = (attempt + 1) * 5
                time.sleep(wait_time)
                continue
            raise e

def ai_analyze_csv(raw_csv_text: str) -> dict:
    """Analiza el log con reintentos automáticos."""
    info = get_vehicle_info()
    api_key = info.get("gemini_api_key")
    if not api_key: return {"error": "⚠️ Configura API Key."}

    try:
        lines = raw_csv_text.splitlines()
        best_sep = "," if raw_csv_text.count(",") > raw_csv_text.count(";") else ";"
        h_idx = 0
        cols = []
        for i, line in enumerate(lines[:30]):
            parts = [p.strip() for p in line.split(best_sep)]
            if len(parts) > len(cols):
                cols = parts
                h_idx = i
        
        sample = "\n".join(lines[h_idx:h_idx+80])
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-flash-latest')
        
        prompt = f"Analiza log VCDS Golf MK4. Devuelve SOLO JSON con grupos de gráficas y análisis. Columnas: {cols}. Muestra: {sample}"
        response = safe_generate_content(model, prompt)
        text = response.text.strip()
        if text.startswith("```"):
            text = re.sub(r'^```json\s*|\s*```$', '', text)
        return json.loads(text)
    except Exception as e:
        return {"error": f"Error IA: {str(e)}"}

def ai_build_charts(raw_csv_text: str, structure: dict) -> list:
    """Construye gráficas sin llamadas extra."""
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
    """Chat de log con auto-reintento."""
    info = get_vehicle_info()
    api_key = info.get("gemini_api_key")
    if not api_key: return "⚠️ Configura API Key."
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-flash-latest')
        prompt = f"Mecánico TDI. Log: {raw_csv_text[:1500]}. Pregunta: {user_query}. Sé breve."
        return safe_generate_content(model, prompt).text
    except Exception as e:
        return "⚠️ **ECU BUSY**. Reintentando..." if "429" in str(e) else f"Error: {e}"

@st.cache_data(ttl=300, show_spinner=False)
def ai_master_chat_response(user_query: str) -> str:
    """Chat maestro con visión TOTAL, CACHÉ y REINTENTOS."""
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
        
        contexto = f"Golf MK4 ({info.get('engine_type')}). KM: {info.get('current_mileage')}. Mant: {mantenimiento}. Mods: {wishlist}. Averías: {averias}."
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-flash-latest')
        response = safe_generate_content(model, f"{contexto}\nPregunta: {user_query}")
        return response.text
    except Exception as e:
        if "429" in str(e):
            return "⚠️ **CONEXIÓN ECU SATURADA**. El sistema de Google está limitando las peticiones. Por favor, espera unos segundos y pulsa Reset si persiste."
        return f"Error: {str(e)}"
