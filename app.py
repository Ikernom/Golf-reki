from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from src.db import init_db
from src.log_analyzer import analyze_log
from src.maintenance import MaintenanceEntry, add_entry, list_entries


st.set_page_config(page_title="ALH Care", page_icon="🚗", layout="wide")
init_db()

st.title("ALH Care - Mantenimiento Golf IV 1.9 TDI (ALH)")
st.caption("Control de mantenimiento, costes y analisis automatico de logs.")

tab1, tab2, tab3 = st.tabs(["Mantenimiento", "Analisis logs", "Ideas avanzadas"])

with tab1:
    st.subheader("Nuevo mantenimiento")
    with st.form("maintenance_form"):
        col1, col2 = st.columns(2)
        with col1:
            date = st.date_input("Fecha")
            mileage = st.number_input("Kilometraje (km)", min_value=0, step=100, value=250000)
            category = st.selectbox(
                "Categoria",
                [
                    "Aceite",
                    "Filtros",
                    "Distribucion",
                    "Frenos",
                    "Suspension",
                    "Neumaticos",
                    "Electronica",
                    "Otro",
                ],
            )
        with col2:
            description = st.text_input("Descripcion", placeholder="Cambio aceite 5W40 + filtro")
            cost = st.number_input("Coste (EUR)", min_value=0.0, step=5.0)
            notes = st.text_area("Notas", placeholder="Marca, referencia, taller, observaciones")

        submitted = st.form_submit_button("Guardar mantenimiento")
        if submitted and description:
            entry = MaintenanceEntry(
                date=str(date),
                mileage_km=int(mileage),
                category=category,
                description=description,
                cost_eur=float(cost),
                notes=notes,
            )
            add_entry(entry)
            st.success("Mantenimiento guardado.")
        elif submitted:
            st.warning("La descripcion es obligatoria.")

    st.subheader("Historial")
    entries = list_entries()
    if entries:
        df_entries = pd.DataFrame(entries)
        st.dataframe(df_entries, use_container_width=True, hide_index=True)
        monthly_cost = (
            df_entries.assign(month=lambda d: pd.to_datetime(d["date"]).dt.to_period("M").astype(str))
            .groupby("month", as_index=False)["cost_eur"]
            .sum()
        )
        fig = px.bar(monthly_cost, x="month", y="cost_eur", title="Coste mensual de mantenimiento")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Aun no hay mantenimientos registrados.")

with tab2:
    st.subheader("Subir log CSV y analizar")
    st.markdown(
        "Columnas recomendadas: `rpm`, `maf_actual`, `maf_requested`, `map_actual`, `coolant_temp`."
    )
    uploaded = st.file_uploader("Sube tu log", type=["csv"])
    if uploaded is not None:
        logs_dir = Path("data/logs")
        logs_dir.mkdir(parents=True, exist_ok=True)
        target_file = logs_dir / uploaded.name
        target_file.write_bytes(uploaded.getbuffer())

        df_log = pd.read_csv(uploaded)
        st.write("Vista previa")
        st.dataframe(df_log.head(20), use_container_width=True)

        result = analyze_log(df_log)
        st.subheader("Resultado del analisis")
        for alert in result.alerts:
            if "Sin alertas" in alert:
                st.success(alert)
            else:
                st.warning(alert)

        if result.metrics:
            cols = st.columns(3)
            cols[0].metric("Error medio MAF (%)", f"{result.metrics['maf_error_pct_mean']:.2f}")
            cols[1].metric("MAP max (mbar)", f"{result.metrics['map_peak_mbar']:.0f}")
            cols[2].metric("Temperatura max (C)", f"{result.metrics['coolant_peak_c']:.1f}")

with tab3:
    st.subheader("Propuestas de evolucion")
    st.markdown(
        """
        - **Recordatorios inteligentes**: alertas por km/tiempo para aceite, filtros, distribucion y liquidos.
        - **Ficha tecnica del ALH**: referencias de piezas, pares de apriete y checklist de mantenimiento preventivo.
        - **Comparador de logs**: antes/despues de una reparacion para validar mejoras.
        - **Integracion OBD-II**: captura semiautomatica de datos con ELM327.
        - **Prediccion de averias**: modelos simples con historico para estimar riesgo de fallo.
        """
    )
