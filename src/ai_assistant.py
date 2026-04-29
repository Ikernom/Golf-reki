import google.generativeai as genai
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import json
import re
import io
from src.maintenance import get_vehicle_info


def ai_analyze_csv(raw_csv_text: str) -> dict:
    """Analiza el log con Gemini para extraer estructura y fallos."""
    info = get_vehicle_info()
    api_key = info.get("gemini_api_key")

    if not api_key:
        return {"error": "⚠️ Configura tu Gemini API Key en Ajustes."}

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-flash-latest')
        csv_sample = raw_csv_text[:8000]

        prompt = f"""Eres un experto en VCDS. Analiza este CSV de un VW TDI.
Devuelve SOLO un JSON con esta estructura:
{{
  "groups": [
    {{
      "gid": "001",
      "name": "Nombre Grupo",
      "columns": ["NombreExacto1", "NombreExacto2"]
    }}
  ],
  "analysis": "resumen corto",
  "detected_faults": []
}}
Usa los nombres de columna tal cual aparecen en el CSV. No inventes nombres.
CSV:
{csv_sample}"""

        response = model.generate_content(prompt)
        text = response.text.strip()
        text = re.sub(r'^```json\s*', '', text)
        text = re.sub(r'\s*```$', '', text)

        return json.loads(text)
    except Exception as e:
        return {"error": f"Error IA: {str(e)}"}


def ai_build_charts(raw_csv_text: str, structure: dict) -> list:
    """Construye gráficas con una lógica de lectura de CSV ultra-robusta."""
    try:
        # 1. Detectar Separador y Cabecera REAL
        # Buscamos la fila que tiene más separadores (esa suele ser la de columnas)
        lines = raw_csv_text.splitlines()
        best_sep = "," if raw_csv_text.count(",") > raw_csv_text.count(";") else ";"
        
        header_idx = 0
        max_cols = 0
        for i, line in enumerate(lines[:20]): # Miramos las primeras 20 filas
            cols = len(line.split(best_sep))
            if cols > max_cols:
                max_cols = cols
                header_idx = i
        
        # 2. Leer el CSV saltando la basura inicial
        df = pd.read_csv(
            io.StringIO(raw_csv_text), 
            sep=best_sep, 
            header=header_idx, 
            on_bad_lines='skip',
            engine='python'
        )
        
        # 3. Limpiar columnas (quitar espacios y puntos)
        df.columns = [str(c).strip() for c in df.columns]
        
        # 4. Detectar Tiempo
        time_col = next((c for c in df.columns if 'TIME' in c.upper() or 'STAMP' in c.upper()), df.columns[0])

        figures = []
        groups = structure.get("groups", [])
        
        for g in groups:
            fig = go.Figure()
            # Buscamos columnas del JSON que coincidan con el DF (ignorando mayúsculas/minúsculas)
            json_cols = [c.strip() for c in g.get("columns", [])]
            valid_cols = []
            
            for jc in json_cols:
                for dfc in df.columns:
                    if jc.lower() in dfc.lower(): # Match flexible
                        valid_cols.append(dfc)
            
            # Si no hay matches, intentamos buscar por palabras clave del nombre del grupo
            if not valid_cols:
                keywords = g["name"].lower().split()
                for dfc in df.columns:
                    if any(k in dfc.lower() for k in keywords if len(k) > 3):
                        valid_cols.append(dfc)

            valid_cols = list(set(valid_cols)) # Quitar duplicados

            for col in valid_cols:
                y_data = pd.to_numeric(df[col], errors='coerce')
                if y_data.notna().any():
                    fig.add_trace(go.Scatter(x=df[time_col], y=y_data, name=col, mode='lines'))
            
            if len(fig.data) > 0:
                fig.update_layout(
                    title=f"GRUPO {g.get('gid', '???')}: {g['name']}",
                    xaxis_title="Tiempo (s)",
                    template="plotly_dark",
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    hovermode="x unified"
                )
                figures.append({"name": g["name"], "gid": g.get("gid"), "fig": fig})
        
        return figures
    except Exception:
        return []


def ai_chat_response(raw_csv_text: str, user_query: str, history: list = None) -> str:
    """Chat con memoria."""
    info = get_vehicle_info()
    api_key = info.get("gemini_api_key")
    if not api_key: return "⚠️ Configura API Key."

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-flash-latest')
        history_text = "\n".join([f"{'Mecánico' if m['role']=='assistant' else 'Usuario'}: {m['content']}" for m in (history or [])[-6:]])
        
        prompt = f"""Experto TDI ALH. Log: {raw_csv_text[:3000]}\nHistorial: {history_text}\nUsuario: {user_query}\nResponde directo y técnico en español."""
        return model.generate_content(prompt).text
    except Exception as e:
        return f"Error: {e}"
