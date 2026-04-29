from __future__ import annotations
from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st
import json
import io

from src.db import init_db
from src.ai_assistant import ai_analyze_csv, ai_build_charts, ai_chat_response
from src.maintenance import (
    MaintenanceEntry, 
    add_entry, 
    list_entries, 
    get_reminders, 
    get_vehicle_info, 
    update_vehicle_info,
    save_log,
    list_logs,
    get_log,
    get_last_mileage_for_category
)
from src.styles import apply_styles

# Initialize Page Config (MUST BE FIRST)
st.set_page_config(
    page_title="Golf-reki ALH Care",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Global styles for sidebar visibility
st.markdown("""
    <style>
    button[kind="headerNoPadding"] {
        background-color: rgba(37, 99, 235, 0.3) !important;
        border-radius: 5px !important;
        color: #2563eb !important;
        padding: 5px !important;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize DB
init_db()
apply_styles()

# Sidebar Navigation
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/6/6d/Volkswagen_logo_2019.svg/600px-Volkswagen_logo_2019.svg.png", width=60)
    st.markdown("### **GOLF MK4 TDI**")
    st.markdown('<p style="background-color: #1a0000; color: #ff0000; padding: 5px 12px; border-radius: 4px; font-weight: bold; border: 1px solid #ff0000; display: inline-block; font-size: 0.7rem; font-family: monospace; box-shadow: 0 0 10px rgba(255,0,0,0.3);">MFA ACTIVE | ALH 1.9</p>', unsafe_allow_html=True)
    st.markdown("---")
    menu = st.radio(
        "MENÚ PRINCIPAL",
        ["🏠 Dashboard", "🔧 Mantenimiento", "📈 Análisis de Logs", "⚙️ Configuración"],
        label_visibility="collapsed"
    )
    st.markdown("---")
    
    # KM Management in Sidebar
    info = get_vehicle_info()
    current_km = int(info.get("current_mileage", 280000))
    
    # Fetch last maintenance km to ensure we don't go below that either
    entries = list_entries()
    last_maint_km = max([e["mileage_km"] for e in entries]) if entries else 0
    min_allowed_km = max(current_km, last_maint_km)
    
    st.markdown(f'<h3 style="color: #4d4dff; text-align: center;">{min_allowed_km:,} KM</h3>', unsafe_allow_html=True)
    
    with st.expander("ACTUALIZAR ODOMETRO"):
        new_km = st.number_input("Kilómetros", value=min_allowed_km, step=100, min_value=min_allowed_km)
        if st.button("SET KM", use_container_width=True):
            if new_km > current_km:
                update_vehicle_info("current_mileage", str(new_km))
                st.success("OK")
                st.rerun()

    st.caption(f"PRÓXIMO SERVICIO: {min_allowed_km + (10000 - (min_allowed_km % 10000)) if (min_allowed_km % 10000) != 0 else min_allowed_km + 10000} KM")
    st.caption("ALH Care v3.0 • Indigo Edition")

# --- DASHBOARD ---
if menu == "🏠 Dashboard":
    # Placeholder para la imagen del salpicadero
    st.image("dashboard_final.jpg", use_container_width=True)

    st.title("Sistema de Diagnosis")
    
    # Header metrics
    info = get_vehicle_info()
    last_km = int(info.get("current_mileage", 280000))
    entries = list_entries()
    df_entries = pd.DataFrame(entries) if entries else pd.DataFrame()
    total_cost = df_entries["cost_eur"].sum() if not df_entries.empty else 0
    last_oil_km = get_last_mileage_for_category("Aceite") or 270000
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Kilometraje Actual", f"{last_km:,} km")
    c2.metric("Último Cambio Aceite", f"{last_oil_km:,} km", delta=f"{last_km - last_oil_km} km", delta_color="inverse")
    c3.metric("Próximo Aceite", f"{last_oil_km + 10000:,} km", delta=f"{(last_oil_km + 10000) - last_km} km")
    c4.metric("Inversión Total", f"{total_cost:,.2f} €")

    st.markdown("---")
    
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        st.subheader("📊 Histórico de Inversión")
        if not df_entries.empty:
            df_entries["date"] = pd.to_datetime(df_entries["date"])
            fig = px.area(
                df_entries.sort_values("date"), 
                x="date", 
                y="cost_eur",
                title="Gasto acumulado en el tiempo",
                line_shape="spline",
                color_discrete_sequence=["#2563eb"]
            )
            fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No hay datos suficientes para mostrar gráficas.")

    with col_right:
        st.subheader("🔔 Recordatorios")
        reminders = get_reminders()
        if reminders:
            for r in reminders:
                st.info(f"**{r['title']}**\n\nLímite: {r['due_mileage']} km")
        else:
            st.success("✅ Todo al día. ¡A disfrutar del TDI!")
            st.write("No tienes tareas pendientes urgentes.")

# --- MANTENIMIENTO ---
elif menu == "🔧 Mantenimiento":
    st.title("Gestión de Mantenimiento")
    
    with st.expander("➕ Registrar nueva intervención", expanded=False):
        with st.form("maintenance_form"):
            col1, col2 = st.columns(2)
            with col1:
                date = st.date_input("Fecha")
                mileage = st.number_input("Kilometraje (km)", min_value=0, step=100, value=280000)
                category = st.selectbox("Categoría", ["Aceite", "Filtros", "Distribución", "Frenos", "Suspensión", "Neumáticos", "Electrónica", "Otro"])
            with col2:
                description = st.text_input("Descripción", placeholder="Ej: Cambio aceite Motul 5W40")
                cost = st.number_input("Coste (EUR)", min_value=0.0, step=5.0)
                notes = st.text_area("Notas adicionales")

            if st.form_submit_button("Guardar Registro"):
                if description:
                    add_entry(MaintenanceEntry(str(date), int(mileage), category, description, float(cost), notes))
                    st.success("¡Registro guardado con éxito!")
                    st.rerun()
                else:
                    st.error("La descripción es obligatoria.")

    st.subheader("Historial Completo")
    entries = list_entries()
    if entries:
        st.dataframe(pd.DataFrame(entries), use_container_width=True, hide_index=True)
    else:
        st.info("Aún no has registrado ningún mantenimiento.")

# --- ANÁLISIS DE LOGS ---
elif menu == "📈 Análisis de Logs":
    st.title("Telemetría y Diagnóstico")
    st.markdown("Sube tus logs de VCDS (CSV). **Gemini AI** analizará la estructura y generará las gráficas automáticamente.")
    
    # --- HISTORIAL DE LOGS ---
    saved_logs = list_logs()
    if saved_logs:
        log_options = {f"{l['filename']} ({l['timestamp']})": l['id'] for l in saved_logs}
        selected_log_name = st.selectbox("📂 Cargar log del historial", ["-- Selecciona un log --"] + list(log_options.keys()))
        
        if selected_log_name != "-- Selecciona un log --":
            log_id = log_options[selected_log_name]
            log_data = get_log(log_id)
            if log_data:
                st.session_state["raw_csv"] = log_data["content"]
                st.session_state["structure"] = json.loads(log_data["analysis_json"])
                st.info(f"Cargado: {log_data['filename']}")

    st.divider()
    
    uploaded = st.file_uploader("Arrastra tu archivo .csv aquí para un nuevo análisis", type=["csv"])
    if uploaded:
        raw_csv = uploaded.getvalue().decode("utf-8", errors="ignore")
        
        with st.spinner("🤖 Gemini está analizando la estructura del log..."):
            structure = ai_analyze_csv(raw_csv)
        
        if "error" in structure and structure["error"]:
            st.error(structure["error"])
        else:
            # Guardar en DB para siempre
            save_log(uploaded.name, raw_csv, json.dumps(structure))
            st.session_state["raw_csv"] = raw_csv
            st.session_state["structure"] = structure
            st.success("Log analizado y guardado en el historial.")

    # --- MOSTRAR RESULTADOS (si hay un log cargado en state) ---
    if "raw_csv" in st.session_state and "structure" in st.session_state:
        raw_csv = st.session_state["raw_csv"]
        structure = st.session_state["structure"]
        
        # Mostrar análisis del mecánico
        if structure.get("analysis"):
            st.subheader("🔍 Análisis del Mecánico Virtual")
            st.markdown(structure["analysis"])
        
        # Generar gráficas
        st.divider()
        st.subheader("📈 Gráficas por Grupo")
        
        charts = ai_build_charts(raw_csv, structure)
        
        if charts:
            tab_names = [f"{c['name']} ({c['gid']})" for c in charts]
            tabs = st.tabs(tab_names)
            
            for tab, chart in zip(tabs, charts):
                with tab:
                    st.plotly_chart(chart["fig"], use_container_width=True)
        else:
            st.warning("No se pudieron generar gráficas. Prueba a preguntar en el chat.")
        
        # Datos crudos
        with st.expander("📋 Datos crudos del CSV"):
            try:
                sep = structure.get("separator", ",")
                header = structure.get("header_rows", 0)
                import io
                df_raw = pd.read_csv(io.StringIO(raw_csv), sep=sep, header=header, on_bad_lines='skip')
                st.dataframe(df_raw, use_container_width=True, hide_index=True)
            except Exception:
                st.code(raw_csv[:3000], language="csv")

        # --- CHAT IA ---
        st.divider()
        st.subheader("🤖 Mecánico Virtual (Chat)")
        
        if "ai_chat_history" not in st.session_state:
            st.session_state.ai_chat_history = []

        for msg in st.session_state.ai_chat_history:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

        if chat_prompt := st.chat_input("Pregunta sobre el log (ej: ¿El turbo va bien?)"):
            with st.chat_message("user"):
                st.write(chat_prompt)
            st.session_state.ai_chat_history.append({"role": "user", "content": chat_prompt})
            
            with st.chat_message("assistant", avatar="🏎️"):
                with st.spinner("Analizando..."):
                    response = ai_chat_response(raw_csv, chat_prompt)
                    st.write(response)
            st.session_state.ai_chat_history.append({"role": "assistant", "content": response})

# --- CONFIGURACIÓN ---
elif menu == "⚙️ Configuración":
    st.title("Ajustes del Vehículo")
    info = get_vehicle_info()
    
    with st.form("vehicle_info"):
        st.subheader("Información del Golf")
        vin = st.text_input("Bastidor (VIN)", value=info.get("vin", ""))
        engine_code = st.text_input("Código Motor", value=info.get("engine_code", "ALH"))
        plate = st.text_input("Matrícula", value=info.get("plate", ""))
        current_mileage_cfg = st.number_input("Kilometraje Actual (km)", value=min_allowed_km, min_value=min_allowed_km)
        
        st.markdown("---")
        st.subheader("IA y Conectividad")
        gemini_key = st.text_input("Gemini API Key", value=info.get("gemini_api_key", ""), type="password", help="Obtenla en aistudio.google.com")

        if st.form_submit_button("Actualizar Ficha"):
            update_vehicle_info("vin", vin)
            update_vehicle_info("engine_code", engine_code)
            update_vehicle_info("plate", plate)
            update_vehicle_info("current_mileage", str(current_mileage_cfg))
            update_vehicle_info("gemini_api_key", gemini_key)
            st.success("Ficha técnica actualizada.")
            st.rerun()
