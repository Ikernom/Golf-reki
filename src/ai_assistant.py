import google.generativeai as genai
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import json
import re
import io
from src.maintenance import get_vehicle_info


def ai_analyze_csv(raw_csv_text: str) -> dict:
    """Analiza el log con Gemini, pidiéndole explícitamente la estructura de gráficas."""
    info = get_vehicle_info()
    api_key = info.get("gemini_api_key")
    if not api_key: return {"error": "⚠️ Configura API Key en Configuración."}

    try:
        # 1. Detección de separador y columnas
        lines = raw_csv_text.splitlines()
        best_sep = "," if raw_csv_text.count(",") > raw_csv_text.count(";") else ";"
        
        # Encontrar cabecera real (la que tiene más columnas)
        h_idx = 0
        cols = []
        for i, line in enumerate(lines[:50]):
            parts = [p.strip() for p in line.split(best_sep)]
            if len(parts) > len(cols):
                cols = parts
                h_idx = i
        
        # 2. Preparar muestra y nombres de columnas
        sample = "\n".join(lines[h_idx:h_idx+150]) # Muestra más amplia
        column_list = ", ".join(cols)
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-flash-latest')
        
        prompt = f"""ERES UN INGENIEIRO EXPERTO EN TELEMETRÍA DE VOLKSWAGEN (ESPECIALISTA EN VCDS / VAG-COM).
Analiza este log de un Golf MK4 TDI.

INSTRUCCIONES:
1. Identifica TODAS las columnas importantes.
2. Crea grupos lógicos para graficar (Ej: "Rendimiento del Turbo", "Ciclo de Inyección", "Masas de Aire (MAF)").
3. Para cada grupo, dime qué columnas exactas deben ir juntas en una gráfica de Plotly.
4. Realiza un análisis técnico del estado del coche: ¿Hay lag en el turbo? ¿El MAF mide bien? ¿La inyección es estable?

COLUMNAS DISPONIBLES: {column_list}

MUESTRA DE DATOS:
{sample}

DEVUELVE ÚNICAMENTE UN OBJETO JSON CON ESTE FORMATO:
{{
  "groups": [
    {{ "gid": "Turbo", "name": "Presión de Sobrealimentación", "columns": ["ColumnName1", "ColumnName2"] }},
    {{ "gid": "MAF", "name": "Masa de Aire y Admisión", "columns": ["..."] }}
  ],
  "analysis": "Markdown con análisis técnico detallado, problemas detectados y consejos.",
  "detected_faults": [
    {{ "component": "Turbo", "severity": "CRITICAL/WARNING", "description": "..." }}
  ]
}}"""

        response = model.generate_content(prompt)
        # Limpiar posible markdown del JSON
        text = response.text.strip()
        if text.startswith("```"):
            text = re.sub(r'^```json\s*|\s*```$', '', text)
        
        return json.loads(text)
    except Exception as e:
        return {"error": f"Error de comunicación con Gemini: {str(e)}"}


def ai_build_charts(raw_csv_text: str, structure: dict) -> list:
    """Construye gráficas profesionales usando la estructura dictada por Gemini."""
    try:
        lines = raw_csv_text.splitlines()
        best_sep = "," if raw_csv_text.count(",") > raw_csv_text.count(";") else ";"
        
        # Localizar cabecera
        h_idx = 0
        for i, line in enumerate(lines[:50]):
            if line.count(best_sep) >= 3:
                h_idx = i
                break
                
        df = pd.read_csv(io.StringIO("\n".join(lines[h_idx:])), sep=best_sep, on_bad_lines='skip', engine='python')
        df.columns = [str(c).strip() for c in df.columns]
        
        # Convertir a numérico
        numeric_df = df.apply(pd.to_numeric, errors='coerce')
        
        # Eje X: Tiempo
        time_col = next((c for c in df.columns if 'TIME' in c.upper() or 'STAMP' in c.upper()), None)
        x_axis = df[time_col] if time_col else numeric_df.index

        figures = []
        groups = structure.get("groups", [])
        
        # Usar las agrupaciones sugeridas por Gemini
        for g in groups:
            fig = go.Figure()
            target_cols = g.get("columns", [])
            
            added_count = 0
            for t_col in target_cols:
                # Búsqueda exacta y flexible
                found_col = None
                if t_col in numeric_df.columns:
                    found_col = t_col
                else:
                    # Intento de match parcial por si Gemini acorta nombres
                    matches = [c for c in numeric_df.columns if t_col.lower() in c.lower()]
                    if matches: found_col = matches[0]
                
                if found_col and numeric_df[found_col].notna().sum() > 0:
                    fig.add_trace(go.Scatter(
                        x=x_axis, 
                        y=numeric_df[found_col], 
                        name=found_col,
                        mode='lines',
                        line=dict(width=2),
                        hovertemplate='%{y:.2f}'
                    ))
                    added_count += 1
            
            if added_count > 0:
                fig.update_layout(
                    title=f"DIAGNÓSTICO: {g['name'].upper()}",
                    template="plotly_dark",
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0.3)",
                    hovermode="x unified",
                    xaxis_title="Tiempo / Muestra",
                    margin=dict(l=20, r=20, t=50, b=20),
                    font=dict(family="Share Tech Mono")
                )
                figures.append({"name": g["name"], "fig": fig})

        # Fallback si Gemini no devolvió grupos válidos
        if not figures:
            cols_con_datos = [c for c in numeric_df.columns if numeric_df[c].notna().sum() > 5 and 'TIME' not in c.upper()]
            for i in range(0, len(cols_con_datos), 4):
                chunk = cols_con_datos[i:i+4]
                fig = go.Figure()
                for col in chunk:
                    fig.add_trace(go.Scatter(x=x_axis, y=numeric_df[col], name=col))
                fig.update_layout(title=f"Auto-Agrupación - Bloque {i//4 + 1}", template="plotly_dark")
                figures.append({"name": f"Auto {i//4 + 1}", "fig": fig})
                
        return figures
    except Exception as e:
        st.error(f"Error construyendo gráficas: {e}")
        return []

def ai_chat_response(raw_csv_text: str, user_query: str, history: list = None) -> str:
    info = get_vehicle_info()
    api_key = info.get("gemini_api_key")
    if not api_key: return "⚠️ Configura API Key."
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-flash-latest')
        # Enviar una muestra más representativa al chat
        sample = raw_csv_text[:4000] 
        prompt = f"""Eres el Ingeniero de Telemetría de un Golf MK4 TDI. 
Analiza estos datos de log y responde a la consulta del usuario.
DATOS DEL LOG (CSV):
{sample}

USUARIO PREGUNTA: {user_query}"""
        return model.generate_content(prompt).text
    except Exception as e: return f"Error en Chat: {e}"


def ai_master_chat_response(user_query: str, history: list = None) -> str:
    """Chat maestro con visión global de todo el vehículo."""
    from src.maintenance import (
        get_vehicle_info, list_entries, list_future_mods, 
        get_active_faults, get_reminders
    )
    
    info = get_vehicle_info()
    api_key = info.get("gemini_api_key")
    if not api_key: return "⚠️ Configura API Key en Configuración."

    # Recopilar contexto global
    try:
        mantenimiento = list_entries()[:15] # Últimos 15 registros
        wishlist = list_future_mods()
        averias = get_active_faults()
        recordatorios = get_reminders()
        km_actual = info.get("odo_actual", "Desconocido")

        contexto = f"""ESTÁS ACTUANDO COMO EL 'CEREBRO' DE UN PROYECTO VOLKSWAGEN GOLF MK4.
Tienes acceso a TODA la información del vehículo del usuario.

INFORMACIÓN DEL COCHE:
- Motor/Modelo: {info.get('engine_type', 'Desconocido')} {info.get('horse_power', '')} CV
- Kilometraje Actual: {km_actual} KM

HISTORIAL RECIENTE:
{json.dumps([{'fecha': e['date'], 'km': e['mileage_km'], 'desc': e['description']} for e in mantenimiento], indent=2)}

MODS PENDIENTES (WISHLIST):
{json.dumps([{'mod': m['description'], 'prioridad': m['priority']} for m in wishlist], indent=2)}

AVERÍAS / ALERTAS ACTIVAS:
{json.dumps([{'componente': f['component'], 'desc': f['description']} for f in averias], indent=2)}

PRÓXIMOS RECORDATORIOS:
{json.dumps([{'titulo': r['title'], 'km_limite': r['due_mileage']} for r in recordatorios], indent=2)}

INSTRUCCIONES:
- Responde de forma técnica pero motivadora.
- Si el usuario pregunta por mantenimiento, cruza datos (ej: 'Viendo que ya hiciste X, te recomiendo Y').
- Si el usuario pregunta por mods, opina basándote en su motor y las averías que tenga.
- Usa un tono de experto en Golf IV (VAG).
"""
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-flash-latest')
        full_prompt = f"{contexto}\n\nUSUARIO PREGUNTA: {user_query}"
        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        return f"Error en Master Chat: {str(e)}"
