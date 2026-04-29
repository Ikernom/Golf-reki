import google.generativeai as genai
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import json
import re
import io
import time
from src.maintenance import get_vehicle_info

def safe_generate_content(model, prompt, max_retries=3):
    """ECU RELAY: Gestión de peticiones con reintento automático."""
    for attempt in range(max_retries):
        try:
            return model.generate_content(prompt)
        except Exception as e:
            if "429" in str(e) and attempt < max_retries - 1:
                time.sleep((attempt + 1) * 2)
                continue
            raise e

def ai_analyze_csv(raw_csv_text: str) -> dict:
    info = get_vehicle_info()
    api_key = info.get("gemini_api_key")
    if not api_key: return {"error": "⚠️ Sin API Key."}
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-flash-latest')
        prompt = f"Analiza este log VCDS de Golf IV y devuelve solo JSON con gráficas. Log: {raw_csv_text[:4000]}"
        response = safe_generate_content(model, prompt)
        text = re.sub(r'^```json\s*|\s*```$', '', response.text.strip())
        return json.loads(text)
    except Exception as e: return {"error": f"Error IA: {e}"}

def ai_build_charts(raw_csv_text, structure):
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
                fig.update_layout(title=g['name'], template="plotly_dark")
                figures.append({"name": g["name"], "fig": fig})
        return figures
    except: return []

def ai_chat_response(raw_csv_text, user_query, history=None):
    info = get_vehicle_info()
    api_key = info.get("gemini_api_key")
    if not api_key: return "Falta API Key."
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-flash-latest')
        return safe_generate_content(model, f"Mecánico Golf IV. Log: {raw_csv_text[:4000]}. Pregunta: {user_query}").text
    except Exception as e: return f"Error: {e}"

@st.cache_data(ttl=600, show_spinner=False)
def ai_master_chat_response(user_query: str) -> str:
    """Master Chat con MEMORIA TOTAL del vehículo."""
    from src.maintenance import get_vehicle_info, list_entries, list_future_mods, get_active_faults
    info = get_vehicle_info()
    api_key = info.get("gemini_api_key")
    if not api_key: return "⚠️ Configura API Key."

    try:
        # Recuperamos ABSOLUTAMENTE TODO el historial y wishlist
        mantenimiento = [f"{e['date']} ({e['mileage_km']}km): {e['description']} - Coste: {e.get('cost_eur', 0)}€" for e in list_entries()]
        wishlist = [f"{m['description']} (Prioridad: {m['priority']})" for m in list_future_mods()]
        averias = [f"{f['component']}: {f['description']}" for f in get_active_faults()]
        
        contexto = f"""ERES EL CEREBRO DE UN PROYECTO VOLKSWAGEN GOLF MK4 TDI.
DATOS DEL VEHÍCULO:
- Motor: {info.get('engine_type')}
- Kilometraje Actual: {info.get('current_mileage')} KM

HISTORIAL COMPLETO DE MANTENIMIENTO:
{chr(10).join(mantenimiento)}

WISHLIST / MODS PENDIENTES:
{chr(10).join(wishlist)}

AVERÍAS Y FALLOS ACTIVOS:
{chr(10).join(averias)}

INSTRUCCIONES:
- Analiza toda la información para dar consejos coherentes.
- Si te preguntan por el futuro, ten en cuenta el pasado (ej: si ya cambió el turbo, no sugieras cambiarlo pronto).
- Mantén una actitud de ingeniero experto en VAG.
"""
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-flash-latest')
        full_prompt = f"{contexto}\n\nUSUARIO PREGUNTA: {user_query}"
        response = safe_generate_content(model, full_prompt)
        return response.text
    except Exception as e:
        if "429" in str(e):
            return "⚠️ **ECU OVERLOAD (429)**. Google sigue limitando las peticiones. Por favor, espera 20 segundos."
        return f"Error Master Chat: {str(e)}"
