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
    instrucciones para generar las gráficas.
    """
    info = get_vehicle_info()
    api_key = info.get("gemini_api_key")

    if not api_key:
        return {"error": "⚠️ Configura tu Gemini API Key en Ajustes."}

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-flash-latest')

        # Limitamos el CSV a los primeros 5000 caracteres para no saturar
        csv_sample = raw_csv_text[:8000]

        prompt = f"""Eres un experto en VCDS y motores VW TDI ALH.
Te paso un log de VCDS en formato CSV. Analiza su estructura y devuélveme un JSON con:

1. "groups": lista de grupos detectados, cada uno con:
   - "id": número del grupo (ej: "011")
   - "name": nombre descriptivo (ej: "Turbo Boost Analysis")
   - "columns": lista de objetos con "name" (nombre descriptivo) y "col_index" (índice de columna en el CSV original, 0-based)
   - "time_col_index": índice de la columna de tiempo para este grupo
   - "data_start_row": fila donde empiezan los datos numéricos (0-based)

2. "separator": el separador usado ("," o ";")

3. "analysis": texto con tu análisis mecánico del log (en español)

4. "header_rows": número de filas de cabecera antes de los datos

IMPORTANTE: Responde SOLO con el JSON, sin markdown ni explicaciones.

CSV:
{csv_sample}"""

        response = model.generate_content(prompt)
        text = response.text.strip()

        # Limpiar markdown si viene envuelto
        text = re.sub(r'^```json\s*', '', text)
        text = re.sub(r'\s*```$', '', text)

        return json.loads(text)

    except json.JSONDecodeError:
        # Si no devuelve JSON válido, devolvemos el texto como análisis
        return {"error": None, "analysis": response.text, "groups": []}
    except Exception as e:
        return {"error": f"❌ Error con Gemini: {str(e)}"}


def ai_build_charts(raw_csv_text: str, structure: dict) -> list:
    """
    Usando la estructura que Gemini nos devolvió, construye las gráficas.
    """
    import io

    sep = structure.get("separator", ",")
    header_rows = structure.get("header_rows", 0)
    groups = structure.get("groups", [])
    figures = []

    lines = raw_csv_text.splitlines()

    for group in groups:
        try:
            gid = group.get("id", "???")
            name = group.get("name", f"Group {gid}")
            columns = group.get("columns", [])
            time_idx = group.get("time_col_index")
            data_start = group.get("data_start_row", header_rows)

            if not columns:
                continue

            # Leer solo las filas de datos
            data_lines = lines[data_start:]
            rows = []
            for line in data_lines:
                parts = [p.strip().strip("'\"") for p in line.split(sep)]
                rows.append(parts)

            if not rows:
                continue

            # Construir la gráfica
            fig = go.Figure()

            # Eje X: tiempo si existe
            x_data = None
            if time_idx is not None:
                x_raw = [r[time_idx] if time_idx < len(r) else None for r in rows]
                x_data = pd.to_numeric(pd.Series(x_raw), errors='coerce')

            for col_info in columns:
                col_name = col_info.get("name", "???")
                col_idx = col_info.get("col_index")
                if col_idx is None:
                    continue

                y_raw = [r[col_idx] if col_idx < len(r) else None for r in rows]
                y_data = pd.to_numeric(pd.Series(y_raw), errors='coerce')

                fig.add_trace(go.Scatter(
                    x=x_data if x_data is not None else y_data.index,
                    y=y_data,
                    mode='lines',
                    name=col_name
                ))

            fig.update_layout(
                title=f"{name} (Group {gid})",
                xaxis_title="Tiempo (s)" if x_data is not None else "Muestra",
                yaxis_title="Valor",
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                hovermode="x unified"
            )

            figures.append({"name": name, "gid": gid, "fig": fig})

        except Exception:
            continue

    return figures


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
        
        # Construir el contexto de la conversación
        history_text = ""
        if history:
            for msg in history[-10:]: # Enviamos los últimos 10 mensajes para no saturar
                role = "Mecánico" if msg["role"] == "assistant" else "Usuario"
                history_text += f"{role}: {msg['content']}\n"

        prompt = f"""Eres un mecánico experto en motores VW TDI ALH.
Vehículo: {vehicle}

Log VCDS (fragmento):
{raw_csv_text[:5000]}

Historial de conversación:
{history_text}

Usuario (pregunta actual): {user_query}

Responde en español, de forma profesional pero cercana. Mantén la continuidad de la charla anterior."""

        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"❌ Error: {str(e)}"
