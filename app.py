from __future__ import annotations

from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st

from src.db import init_db
from src.log_analyzer import analyze_log
from src.maintenance import (
    MaintenanceEntry, 
    add_entry, 
    list_entries, 
    get_reminders, 
    get_vehicle_info, 
    update_vehicle_info,
    get_last_mileage_for_category
)
from src.styles import apply_styles

# Initialize
st.set_page_config(page_title="ALH Care Premium", page_icon="🏎️", layout="wide")
init_db()
apply_styles()

# Sidebar Navigation
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/6/6d/Volkswagen_logo_2019.svg/600px-Volkswagen_logo_2019.svg.png", width=60)
    st.markdown("### **Golf IV 1.9 TDI**")
    st.markdown('<p style="background-color: #0e1b40; color: #3b82f6; padding: 5px 12px; border-radius: 20px; font-weight: bold; border: 1px solid #3b82f6; display: inline-block; font-size: 0.8rem;">DEEP BLUE PEARL</p>', unsafe_allow_html=True)
    st.markdown("---")
    menu = st.radio(
        "MENÚ PRINCIPAL",
        ["🏠 Dashboard", "🔧 Mantenimiento", "📈 Análisis de Logs", "⚙️ Configuración"],
        label_visibility="collapsed"
    )
    st.markdown("---")
    st.info("🚗 **Kilometraje:** 280.000 km\n\n🕒 **Próximo Servicio:** 290.000 km")
    st.caption("ALH Care v2.1 • Premium Edition")

# --- DASHBOARD ---
if menu == "🏠 Dashboard":
    st.image("data/images/hero.png", use_container_width=True)
    st.title("Estado del Vehículo")
    
    # Header metrics
    entries = list_entries()
    df_entries = pd.DataFrame(entries) if entries else pd.DataFrame()
    
    total_cost = df_entries["cost_eur"].sum() if not df_entries.empty else 0
    last_km = df_entries["mileage_km"].max() if not df_entries.empty else 280000
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
    st.markdown("Sube tus logs de VCDS (CSV) para analizar el estado del turbo y el caudalímetro.")
    
    uploaded = st.file_uploader("Arrastra tu archivo .csv aquí", type=["csv"])
    if uploaded:
        df_log = pd.read_csv(uploaded)
        result = analyze_log(df_log)
        
        st.subheader("🔍 Resultados del Escaneo")
        
        # Alerts in a modern way
        for alert in result.alerts:
            if "Sin alertas" in alert: st.success(alert)
            else: st.warning(alert)
            
        if result.metrics:
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Error MAF medio", f"{result.metrics['maf_error_pct_mean']:.1f}%")
            m2.metric("Pico Turbo (MAP)", f"{result.metrics['map_peak_mbar']:.0f} mbar")
            m3.metric("Temp. Máxima", f"{result.metrics['coolant_peak_c']:.1f} °C")
            m4.metric("Health Score", f"{result.metrics['score']:.0f}/100")

        if result.data is not None:
            st.divider()
            tab_maf, tab_map = st.tabs(["Caudalímetro (MAF)", "Turbo (MAP)"])
            
            with tab_maf:
                fig_maf = px.line(result.data, x=result.data.index, y=["maf_requested", "maf_actual"],
                                title="Solicitado vs Real", color_discrete_map={"maf_requested": "#636EFA", "maf_actual": "#EF553B"})
                st.plotly_chart(fig_maf, use_container_width=True)
                
            with tab_map:
                fig_map = px.area(result.data, x="rpm", y="map_actual", title="Presión Turbo vs RPM", color_discrete_sequence=["#00CC96"])
                st.plotly_chart(fig_map, use_container_width=True)

# --- CONFIGURACIÓN ---
elif menu == "⚙️ Configuración":
    st.title("Ajustes del Vehículo")
    info = get_vehicle_info()
    
    with st.form("vehicle_info"):
        st.subheader("Información del Golf")
        vin = st.text_input("Bastidor (VIN)", value=info.get("vin", ""))
        engine_code = st.text_input("Código Motor", value=info.get("engine_code", "ALH"))
        plate = st.text_input("Matrícula", value=info.get("plate", ""))
        
        if st.form_submit_button("Actualizar Ficha"):
            update_vehicle_info("vin", vin)
            update_vehicle_info("engine_code", engine_code)
            update_vehicle_info("plate", plate)
            st.success("Ficha técnica actualizada.")
