from __future__ import annotations
from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import json
import io
from datetime import datetime

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
    update_log_chat,
    get_last_mileage_for_category,
    add_fault,
    get_active_faults,
    mark_fault_fixed,
    delete_log,
    delete_entry,
    update_entry,
    list_categories,
    add_category,
    list_future_mods,
    add_future_mod,
    delete_future_mod,
    update_future_mod
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

# --- SIDEBAR NAVIGATION ---
with st.sidebar:
    # Logo y Título
    col1, col2 = st.columns([1, 4])
    with col1:
        st.image("https://upload.wikimedia.org/wikipedia/commons/6/6d/Volkswagen_logo_2019.svg", width=50)
    with col2:
        st.markdown("<h2 style='margin:0; font-size:1.5rem; color:#ffffff;'>GOLF MK4</h2><p style='color:#1c39bb; margin:0; font-weight:bold; font-size:0.8rem;'>INDIGO EDITION</p>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # MFA Status Bar Dinámico
    active_faults = get_active_faults()
    if not active_faults:
        status_text = "MFA STATUS: OK | ALH 1.9 TDI"
        status_color = "#ff0000"
        glow_color = "rgba(255,0,0,0.2)"
    else:
        status_text = f"FAULT: {active_faults[0]['component']} | CHECK SYSTEM"
        status_color = "#ff4444"
        glow_color = "rgba(255,0,0,0.6)"

    st.markdown(f"""
        <div style="background-color: #000; border: 1px solid {status_color}; border-radius: 4px; padding: 8px; text-align: center; box-shadow: inset 0 0 15px {glow_color};">
            <span style="color: {status_color}; font-family: 'JetBrains Mono', monospace; font-weight: bold; font-size: 0.8rem; text-transform: uppercase;">
                {status_text}
            </span>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Lógica de persistencia de página (Callback para evitar el doble clic)
    menu_options = ["🏠 Dashboard", "🔧 Mantenimiento", "📈 Análisis de Logs", "⚙️ Configuración"]
    
    if "active_menu" not in st.session_state:
        st.session_state.active_menu = st.query_params.get("page", "🏠 Dashboard")
    
    def sync_menu():
        st.query_params["page"] = st.session_state.active_menu

    menu = st.radio(
        "SISTEMA CENTRAL", 
        menu_options, 
        key="active_menu", 
        on_change=sync_menu
    )

    st.markdown("---")
    
    # Odometer Section
    info = get_vehicle_info()
    current_km = int(info.get("current_mileage", 280000))
    st.markdown("<p style='color:#666; font-size:0.7rem; margin-bottom:0;'>TOTAL ODOMETER</p>", unsafe_allow_html=True)
    st.markdown(f"<h1 style='color:#ff0000; margin-top:0; font-size:1.8rem; text-shadow: 0 0 10px rgba(255,0,0,0.5);'>{current_km:,} KM</h1>", unsafe_allow_html=True)
    
    if st.button("⌨️ ACTUALIZAR KILOMETRAJE", use_container_width=True):
        st.query_params["page"] = "⚙️ Configuración"
        st.rerun()

    st.markdown("<div style='margin-top:20px; border-top:1px solid #222; padding-top:10px;'>", unsafe_allow_html=True)
    st.caption(f"PRÓXIMO SERVICIO: {current_km + (10000 - (current_km % 10000)) if (current_km % 10000) != 0 else current_km + 10000} KM")
    st.caption("ALH Care v3.5 • Indigo Edition")
    st.markdown("</div>", unsafe_allow_html=True)

# --- DASHBOARD ---
if menu == "🏠 Dashboard":
    st.title("Sistema de Diagnosis")
    
    # Header metrics
    info = get_vehicle_info()
    last_km = int(info.get("current_mileage", 280000))
    oil_interval = int(info.get("oil_interval", 10000))
    
    # Prioritize manual override from settings, fallback to DB search
    last_oil_km = int(info.get("last_oil_change_km", 0))
    if last_oil_km == 0:
        last_oil_km = get_last_mileage_for_category("Aceite") or 270000

    entries = list_entries()
    df_entries = pd.DataFrame(entries) if entries else pd.DataFrame()
    total_cost = df_entries["cost_eur"].sum() if not df_entries.empty else 0
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Kilometraje Actual", f"{last_km:,} km")
    c2.metric("Último Cambio Aceite", f"{last_oil_km:,} km", delta=f"{last_km - last_oil_km} km", delta_color="inverse")
    c3.metric("Próximo Aceite", f"{last_oil_km + oil_interval:,} km", delta=f"{(last_oil_km + oil_interval) - last_km} km")
    c4.metric("Inversión Total", f"{total_cost:,.2f} €")

    st.markdown("---")
    
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        # --- ESTADO DE SALUD ---
        st.subheader("🩺 Estado de Salud del Vehículo")
        active_faults = get_active_faults()
        if active_faults:
            for fault in active_faults:
                with st.container():
                    severity_color = "red" if fault["severity"] == "CRITICAL" else "orange"
                    st.markdown(f"""
                        <div style="border-left: 5px solid {severity_color}; background-color: #111; padding: 15px; border-radius: 5px; margin-bottom: 10px;">
                            <h4 style="margin:0; color:{severity_color};">{fault['component']} - {fault['severity']}</h4>
                            <p style="margin:5px 0; font-size:0.9rem;">{fault['description']}</p>
                            <small style="color:#666;">Detectado el: {fault['detected_at']}</small>
                        </div>
                    """, unsafe_allow_html=True)
                    if st.button(f"Marcar {fault['component']} como reparado", key=f"fix_{fault['id']}"):
                        mark_fault_fixed(fault['id'])
                        st.rerun()
        else:
            st.success("No se han detectado fallos activos. El coche está en perfecto estado.")

        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("📊 Histórico de Inversión")
        if not df_entries.empty:
            df_entries["date"] = pd.to_datetime(df_entries["date"])
            df_plot = df_entries.sort_values("date")
            fig = px.area(
                df_plot, 
                x="date", 
                y="cost_eur",
                title=f"Inversión Total: {total_cost:,.2f} €",
                line_shape="spline",
                color_discrete_sequence=["#1c47ff"],
                markers=True,
                hover_data={"description": True, "cost_eur": ":.2f €", "date": "|%d %b, %Y"}
            )
            fig.update_traces(marker=dict(size=8, color="#ff0000", line=dict(width=1, color="#fff")))
            fig.update_layout(
                plot_bgcolor="rgba(0,0,0,0)", 
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(family="JetBrains Mono, monospace", size=12, color="#00aaff")
            )
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
            st.w# --- MANTENIMIENTO ---
elif menu == "🔧 Mantenimiento":
    st.title("Gestión de Mantenimiento")
    db_categories = list_categories()
    
    # Estilo LCD Global para Mantenimiento y Pestañas
    st.markdown("""
        <style>
        /* Estilo para las Pestañas (Tabs) */
        div[data-testid="stTabs"] button {
            background-color: #000000 !important;
            color: #555555 !important;
            border: 1px solid #333333 !important;
            border-bottom: 2px solid #ff0000 !important;
            font-family: 'JetBrains Mono', monospace !important;
            font-weight: bold !important;
            text-transform: uppercase !important;
            letter-spacing: 1px !important;
            transition: all 0.3s ease !important;
        }
        
        div[data-testid="stTabs"] button[aria-selected="true"] {
            color: #1c47ff !important;
            border: 1px solid #1c47ff !important;
            border-bottom: 3px solid #1c47ff !important;
            box-shadow: 0 0 15px rgba(28, 71, 255, 0.4), inset 0 0 10px rgba(28, 71, 255, 0.2) !important;
            text-shadow: 0 0 10px rgba(28, 71, 255, 0.8) !important;
        }
        
        /* RECONSTRUCCIÓN TOTAL SELECTBOXES LCD */
        div[data-baseweb="select"] > div {
            background-color: #000000 !important;
            border: 1.5px solid #ff0000 !important;
            border-radius: 4px !important;
            box-shadow: inset 0 0 15px rgba(28, 71, 255, 0.2) !important;
            height: 45px !important;
        }
        
        /* Texto del valor seleccionado */
        div[data-baseweb="select"] [data-testid="stMarkdownContainer"] p,
        div[data-baseweb="select"] span {
            color: #1c47ff !important;
            text-shadow: 0 0 8px rgba(28, 71, 255, 0.8) !important;
            font-family: 'JetBrains Mono', monospace !important;
            font-weight: 800 !important;
            font-size: 1rem !important;
            text-transform: uppercase !important;
        }

        /* Icono de la flecha (dropdown) */
        div[data-baseweb="select"] svg {
            fill: #ff0000 !important;
        }

        /* Estilo para los inputs de registro/edición (Formularios) */
        div.stForm input, div.stForm textarea {
            background-color: #000000 !important;
            color: #1c47ff !important;
            border: 1.5px solid #ff0000 !important;
            box-shadow: inset 0 0 12px rgba(28, 71, 255, 0.25) !important;
            text-shadow: 0 0 5px rgba(28, 71, 255, 0.5) !important;
            font-family: 'JetBrains Mono', monospace !important;
            padding: 12px !important;
            border-radius: 4px !important;
        }

        /* TODAS las etiquetas (labels) de la sección */
        label p, .stMarkdown p {
            color: #1c47ff !important;
            text-shadow: 0 0 8px rgba(28, 71, 255, 0.6) !important;
            font-family: 'JetBrains Mono', monospace !important;
            font-weight: bold !important;
            text-transform: uppercase !important;
        }

        /* Botones de ordenación y otros botones de la sección */
        div.stButton button {
            background-color: #000000 !important;
            color: #1c47ff !important;
            border: 1.5px solid #ff0000 !important;
            box-shadow: 0 0 10px rgba(255, 0, 0, 0.2) !important;
            text-shadow: 0 0 8px rgba(28, 71, 255, 0.8) !important;
            font-family: 'JetBrains Mono', monospace !important;
            font-weight: 800 !important;
            text-transform: uppercase !important;
        }
        
        div.stButton button:hover {
            border-color: #1c47ff !important;
            color: #ffffff !important;
            box-shadow: 0 0 15px rgba(28, 71, 255, 0.5) !important;
        }
            color: #1c47ff !important;
            text-shadow: 0 0 8px rgba(28, 71, 255, 0.6) !important;
            font-family: 'JetBrains Mono', monospace !important;
            text-transform: uppercase !important;
            font-size: 0.8rem !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    tab_realized, tab_future = st.tabs(["🔧 Intervenciones Realizadas", "📅 Plan de Futuro (Wishlist)"])
    
    with tab_realized:
        col_new, col_cat = st.columns([2, 1])
        with col_new:
            with st.expander("➕ Registrar nueva intervención", expanded=False):
                with st.form("maintenance_form"):
                    st.markdown("<h4 style='color:#1c47ff; text-shadow:0 0 10px rgba(28,71,255,0.7);'>NUEVO REGISTRO LCD</h4>", unsafe_allow_html=True)
                    col1, col2 = st.columns(2)
                    with col1:
                        date = st.date_input("Fecha")
                        mileage = st.number_input("Kilometraje (km)", min_value=0, step=100, value=280000)
                        category = st.selectbox("Categoría", db_categories)
                    with col2:
                        description = st.text_input("Descripción", placeholder="Ej: Cambio aceite Motul 5W40")
                        cost = st.number_input("Coste (EUR)", min_value=0.0, step=5.0)
                        notes = st.text_area("Notas adicionales")

                    if st.form_submit_button("💾 GUARDAR EN MEMORIA"):
                        if description:
                            add_entry(str(date), int(mileage), category, description, float(cost), notes)
                            st.success("¡Registro guardado!")
                            st.rerun()
        
        with col_cat:
            with st.expander("📂 Gestionar Categorías"):
                new_cat_name = st.text_input("Nueva Categoría")
                if st.button("➕ Añadir Categoría", use_container_width=True):
                    if new_cat_name:
                        add_category(new_cat_name)
                        st.success(f"'{new_cat_name}' añadida")
                        st.rerun()
        
        st.divider()
        st.subheader("📋 Registro Histórico")
        
        all_entries = list_entries()
        filter_categories = ["Todas"] + db_categories
        
        col_f1, col_f2, col_f3 = st.columns([2, 2, 1])
        with col_f1:
            filter_cat = st.selectbox("Filtrar por categoría:", filter_categories)
        with col_f2:
            sort_by = st.selectbox("Ordenar por:", ["Fecha", "Kilometraje", "Coste", "Nombre"])
        with col_f3:
            st.markdown("<br>", unsafe_allow_html=True)
            if "sort_desc" not in st.session_state: st.session_state.sort_desc = True
            icon = "⬇️ Desc." if st.session_state.sort_desc else "⬆️ Asc."
            if st.button(icon, use_container_width=True):
                st.session_state.sort_desc = not st.session_state.sort_desc
                st.rerun()

        entries = all_entries
        if filter_cat != "Todas": entries = [e for e in all_entries if e["category"] == filter_cat]
        
        is_desc = st.session_state.sort_desc
        if sort_by == "Fecha": entries = sorted(entries, key=lambda x: x["date"], reverse=is_desc)
        elif sort_by == "Kilometraje": entries = sorted(entries, key=lambda x: x["mileage_km"], reverse=is_desc)
        elif sort_by == "Coste": entries = sorted(entries, key=lambda x: x.get("cost_eur", 0.0), reverse=is_desc)
        elif sort_by == "Nombre": entries = sorted(entries, key=lambda x: x["description"].lower(), reverse=is_desc)

        if not entries:
            st.info("No hay intervenciones registradas.")
        else:
            for entry in entries:
                # Estilo LCD para el historial (Borde Rojo)
                st.markdown(f"""
                    <div style="position: relative; height: 0px; margin-bottom: 0px;">
                        <div style="position: absolute; left: 50%; transform: translateX(-50%); top: 16px; z-index: 99; pointer-events: none;">
                            <span style="background: rgba(0, 0, 0, 0.95); color: #00d4ff; padding: 2px 12px; border-radius: 2px; font-size: 0.7rem; font-weight: 800; border: 1.5px solid #ff0000; box-shadow: 0 0 10px rgba(255, 0, 0, 0.4); text-transform: uppercase; font-family: 'JetBrains Mono', monospace;">
                                <span style="color: #ff0000;">●</span> {entry['category']}
                            </span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                with st.container():
                    st.markdown("""
                        <style>
                        div[data-testid="stExpander"] {
                            border: 2px solid #ff0000 !important;
                            box-shadow: inset 0 0 15px rgba(28, 71, 255, 0.1) !important;
                            background-color: #000 !important;
                        }
                        </style>
                    """, unsafe_allow_html=True)
                    with st.expander(f"🛠️ {entry['description']}"):
                        c_inf, c_btn = st.columns([3, 1])
                        edit_mode = st.session_state.get(f"edit_{entry['id']}", False)
                        with c_inf:
                            if not edit_mode:
                                st.markdown(f"<span style='color:#1c47ff; text-shadow:0 0 5px rgba(28,71,255,0.5); font-weight:bold;'>📅 {entry['date']} | 🛣️ {entry['mileage_km']:,} KM | 💰 {entry.get('cost_eur', 0.0)} €</span>", unsafe_allow_html=True)
                                if entry.get('notes'): st.markdown(f"*Notas:* {entry['notes']}")
                            else:
                                with st.form(f"edit_f_{entry['id']}"):
                                    n_date = st.date_input("Fecha", value=datetime.strptime(entry['date'], '%Y-%m-%d'))
                                    n_km = st.number_input("KM", value=entry['mileage_km'])
                                    n_desc = st.text_input("Desc.", value=entry['description'])
                                    n_cat = st.selectbox("Cat.", db_categories, index=db_categories.index(entry['category']) if entry['category'] in db_categories else 0)
                                    n_cost = st.number_input("Coste", value=float(entry.get('cost_eur', 0.0)))
                                    n_notes = st.text_area("Notas", value=entry.get('notes', ''))
                                    if st.form_submit_button("💾 ACTUALIZAR"):
                                        update_entry(entry['id'], n_date.strftime('%Y-%m-%d'), n_km, n_desc, n_cat, n_cost, n_notes)
                                        st.session_state[f"edit_{entry['id']}"] = False
                                        st.rerun()
                        with c_btn:
                            if not edit_mode:
                                if st.button("✏️", key=f"ed_{entry['id']}", use_container_width=True):
                                    st.session_state[f"edit_{entry['id']}"] = True
                                    st.rerun()
                                if st.button("🗑️", key=f"dl_{entry['id']}", use_container_width=True):
                                    delete_entry(entry['id'])
                                    st.rerun()

    with tab_future:
        st.subheader("📅 Plan de Futuro (Wishlist)")
        
        with st.expander("🚀 Añadir nueva idea de modificación", expanded=False):
            with st.form("future_mod_form"):
                st.markdown("<h4 style='color:#1c47ff; text-shadow:0 0 10px rgba(28,71,255,0.7);'>NUEVA MOD LCD</h4>", unsafe_allow_html=True)
                col_f1, col_f2 = st.columns(2)
                with col_f1:
                    f_desc = st.text_input("Descripción de la Mod")
                    f_cat = st.selectbox("Categoría", db_categories, key="future_cat")
                with col_f2:
                    f_cost = st.number_input("Coste Estimado (EUR)", min_value=0.0, step=10.0)
                    f_prio = st.select_slider("Prioridad", options=["Baja", "Media", "Alta"], value="Media")
                
                f_notes = st.text_area("Notas / Enlaces de piezas")
                if st.form_submit_button("➕ AÑADIR AL ROADMAP"):
                    if f_desc:
                        add_future_mod(f_desc, f_cost, f_cat, f_prio, f_notes)
                        st.success("¡Idea añadida!")
                        st.rerun()
        
        st.divider()
        f_mods = list_future_mods()
        if not f_mods:
            st.info("Aún no tienes planes registrados.")
        else:
            for mod in f_mods:
                prio_color = "#00ff00" if mod['priority'] == "Baja" else ("#ffff00" if mod['priority'] == "Media" else "#ff0000")
                
                # Burbuja Indigo - Posicionada más abajo para entrar en el recuadro
                st.markdown(f"""
                    <div style="position: relative; height: 0px; margin-bottom: 0px;">
                        <div style="position: absolute; left: 50%; transform: translateX(-50%); top: 16px; z-index: 99; pointer-events: none;">
                            <span style="background: rgba(0, 0, 0, 0.95); color: #00d4ff; padding: 2px 12px; border-radius: 2px; font-size: 0.7rem; font-weight: 800; border: 1.5px solid #2e5bff; box-shadow: 0 0 10px rgba(46, 91, 255, 0.4); text-transform: uppercase; font-family: 'JetBrains Mono', monospace;">
                                <span style="color: #2e5bff;">●</span> {mod['category']}
                            </span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                with st.container():
                    # CSS LCD para la Wishlist (Borde Azul)
                    st.markdown(f"""
                        <style>
                        div[data-testid="stExpander"]:has(p:contains("{mod['description']}")) {{
                            border: 2px solid #2e5bff !important;
                            box-shadow: inset 0 0 15px rgba(28, 71, 255, 0.15) !important;
                            background-color: #000 !important;
                        }}
                        </style>
                    """, unsafe_allow_html=True)
                    
                    with st.expander(f"🚀 {mod['description']}"):
                        c_inf, c_btn = st.columns([3, 1])
                        f_edit_mode = st.session_state.get(f"f_edit_{mod['id']}", False)
                        with c_inf:
                            if not f_edit_mode:
                                st.markdown(f"<span style='color:#1c47ff; text-shadow:0 0 5px rgba(28,71,255,0.5); font-weight:bold;'>💰 Est.: {mod['estimated_cost']} € | ⚡ Prioridad: <span style='color:{prio_color};'>{mod['priority']}</span></span>", unsafe_allow_html=True)
                                if mod.get('notes'): st.markdown(f"*Notas:* {mod['notes']}")
                            else:
                                with st.form(f"f_edit_form_{mod['id']}"):
                                    n_f_desc = st.text_input("Descripción", value=mod['description'])
                                    n_f_cat = st.selectbox("Categoría", db_categories, index=db_categories.index(mod['category']) if mod['category'] in db_categories else 0)
                                    n_f_cost = st.number_input("Coste Est. (€)", value=float(mod.get('estimated_cost', 0.0)))
                                    n_f_prio = st.select_slider("Prioridad", options=["Baja", "Media", "Alta"], value=mod['priority'])
                                    n_f_notes = st.text_area("Notas", value=mod.get('notes', ''))
                                    if st.form_submit_button("💾 ACTUALIZAR"):
                                        update_future_mod(mod['id'], n_f_desc, n_f_cost, n_f_cat, n_f_prio, n_f_notes)
                                        st.session_state[f"f_edit_{mod['id']}"] = False
                                        st.rerun()
                        with c_btn:
                            if not f_edit_mode:
                                if st.button("✏️", key=f"f_ed_btn_{mod['id']}", use_container_width=True):
                                    st.session_state[f"f_edit_{mod['id']}"] = True
                                    st.rerun()
                                if st.button("🗑️", key=f"f_dl_{mod['id']}", use_container_width=True):
                                    delete_future_mod(mod['id'])
                                    st.rerun()

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
                st.session_state["active_log_id"] = log_id
                st.session_state["raw_csv"] = log_data["content"]
                st.session_state["structure"] = json.loads(log_data["analysis_json"])
                # Cargar chat si existe
                if log_data.get("chat_history_json"):
                    st.session_state.ai_chat_history = json.loads(log_data["chat_history_json"])
                else:
                    st.session_state.ai_chat_history = []
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
            new_id = save_log(uploaded.name, raw_csv, json.dumps(structure))
            st.session_state["active_log_id"] = new_id
            st.session_state["raw_csv"] = raw_csv
            st.session_state["structure"] = structure
            st.session_state.ai_chat_history = []
            
            # Registrar fallos detectados con validación de tipo
            detected = structure.get("detected_faults", [])
            if isinstance(detected, list):
                for fault in detected:
                    if isinstance(fault, dict) and "component" in fault:
                        add_fault(
                            fault.get("component", "Desconocido"), 
                            fault.get("severity", "WARNING"), 
                            fault.get("description", "Sin descripción")
                        )
            
            st.success("Log analizado y guardado en el historial.")

    # --- MOSTRAR RESULTADOS (si hay un log cargado en state) ---
    if "raw_csv" in st.session_state and "structure" in st.session_state:
        raw_csv = st.session_state["raw_csv"]
        structure = st.session_state["structure"]
        active_log_id = st.session_state.get("active_log_id")

        # --- DEPURADOR DE LOGS (Solo visible si algo falla) ---
        with st.expander("🛠️ Depurador de Datos (Si no ves gráficas, abre esto)"):
            import io
            st.write("### Estructura detectada por IA")
            st.json(structure)
            
            try:
                # Intentamos leer las columnas reales
                lines = raw_csv.splitlines()
                best_sep = "," if raw_csv.count(",") > raw_csv.count(";") else ";"
                for i, line in enumerate(lines[:20]):
                    if len(line.split(best_sep)) > 3:
                        st.write(f"Columnas detectadas en fila {i}:")
                        st.code(line.split(best_sep))
                        break
            except Exception as e:
                st.error(f"Error en depurador: {e}")
        
        # Mostrar análisis del mecánico
        if structure.get("analysis"):
            col_a, col_b = st.columns([4, 1])
            with col_a:
                st.subheader("🔍 Análisis del Mecánico Virtual")
            with col_b:
                if st.button("🗑️ Eliminar Log", use_container_width=True, help="Borra este log del historial permanentemente"):
                    if active_log_id:
                        delete_log(active_log_id)
                        del st.session_state["raw_csv"]
                        del st.session_state["structure"]
                        if "active_log_id" in st.session_state: del st.session_state["active_log_id"]
                        st.success("Log eliminado correctamente.")
                        st.rerun()
            
            st.markdown(structure["analysis"])
        
        # Generar gráficas
        st.divider()
        st.subheader("📈 Gráficas del Log")
        
        charts = ai_build_charts(raw_csv, structure)
        
        if charts:
            tab_names = [f"{c['name']} ({c.get('gid', 'Auto')})" for c in charts]
            tabs = st.tabs(tab_names)
            
            for tab, chart in zip(tabs, charts):
                with tab:
                    st.plotly_chart(chart["fig"], use_container_width=True)
        else:
            st.warning("🤖 La IA no ha podido agrupar las columnas automáticamente.")
            
            # --- FUNCIÓN DE ESCANEO ROBUSTO ---
            def get_clean_df(text):
                lines = text.splitlines()
                # Detectar separador
                separators = [",", ";", "\t"]
                sep_counts = {s: text.count(s) for s in separators}
                best_sep = max(sep_counts, key=sep_counts.get)
                
                # Buscar la fila con más columnas (cabecera real)
                max_cols = 0
                header_idx = 0
                for i, line in enumerate(lines[:100]):
                    count = line.count(best_sep)
                    if count > max_cols:
                        max_cols = count
                        header_idx = i
                
                df = pd.read_csv(io.StringIO("\n".join(lines[header_idx:])), sep=best_sep, on_bad_lines='skip', engine='python')
                df.columns = [str(c).strip() for c in df.columns]
                return df, best_sep

            # --- BOTÓN DE FUERZA BRUTA ---
            if st.button("🚀 GENERAR GRÁFICAS DE TODO EL LOG", use_container_width=True):
                try:
                    df_all, _ = get_clean_df(raw_csv)
                    numeric_df = df_all.apply(pd.to_numeric, errors='coerce')
                    cols_to_plot = [c for c in numeric_df.columns if numeric_df[c].notna().sum() > 5 and 'TIME' not in c.upper()]
                    
                    if cols_to_plot:
                        t_col = next((c for c in df_all.columns if 'TIME' in c.upper()), df_all.columns[0])
                        for i in range(0, len(cols_to_plot), 4):
                            chunk = cols_to_plot[i:i+4]
                            fig_all = go.Figure()
                            for col in chunk:
                                fig_all.add_trace(go.Scatter(x=df_all[t_col], y=numeric_df[col], name=col, mode='lines'))
                            st.subheader(f"Bloque {i//4 + 1}")
                            st.plotly_chart(fig_all, use_container_width=True)
                    else:
                        st.error("No se detectaron columnas numéricas.")
                except Exception as e:
                    st.error(f"Error: {e}")

            # --- CONSTRUCTOR MANUAL ---
            with st.expander("🛠️ CONSTRUCTOR MANUAL"):
                try:
                    df_m, _ = get_clean_df(raw_csv)
                    t_col = next((c for c in df_m.columns if 'TIME' in c.upper()), df_m.columns[0])
                    all_cols = [c for c in df_m.columns if c != t_col]
                    selected = st.multiselect("Elige columnas:", all_cols)
                    if selected:
                        fig_m = go.Figure()
                        for s in selected:
                            fig_m.add_trace(go.Scatter(x=df_m[t_col], y=pd.to_numeric(df_m[s], errors='coerce'), name=s))
                        st.plotly_chart(fig_m, use_container_width=True)
                except:
                    st.write("No se pudo cargar el selector manual.")
        
        # Datos crudos (con salto de cabecera inteligente)
        with st.expander("📋 Datos crudos del CSV"):
            try:
                lines = raw_csv.splitlines()
                best_sep = "," if raw_csv.count(",") > raw_csv.count(";") else ";"
                h_idx = 0
                for i, line in enumerate(lines[:40]):
                    if line.count(best_sep) >= 3 and ("Group" in line or "TIME" in line.upper()):
                        h_idx = i
                        break
                
                df_raw = pd.read_csv(io.StringIO("\n".join(lines[h_idx:])), sep=best_sep, on_bad_lines='skip')
                st.dataframe(df_raw, use_container_width=True, hide_index=True)
            except Exception as e:
                st.code(raw_csv[:2000], language="csv")
                st.error(f"Error al visualizar tabla: {e}")

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
                    response = ai_chat_response(raw_csv, chat_prompt, st.session_state.ai_chat_history)
                    st.write(response)
            st.session_state.ai_chat_history.append({"role": "assistant", "content": response})
            
            # GUARDAR CHAT ACTUALIZADO EN DB
            if active_log_id:
                update_log_chat(active_log_id, json.dumps(st.session_state.ai_chat_history))

# --- CONFIGURACIÓN ---
elif menu == "⚙️ Configuración":
    st.title("Ajustes del Vehículo")
    info = get_vehicle_info()
    
    # Estilo MK4 LCD Pro para el formulario
    st.markdown("""
        <style>
        div[data-testid="stForm"] {
            border: 2px solid #ff0000 !important;
            background-color: #000000 !important;
            box-shadow: 0 0 30px rgba(255, 0, 0, 0.2) !important;
            padding: 2.5rem !important;
            border-radius: 4px !important;
        }
        
        /* Labels con Estilo Indigo Glow */
        div[data-testid="stForm"] label p {
            color: #1c47ff !important;
            text-shadow: 0 0 12px rgba(28, 71, 255, 0.8) !important;
            font-family: 'JetBrains Mono', monospace !important;
            font-weight: 800 !important;
            text-transform: uppercase !important;
            letter-spacing: 2px !important;
            font-size: 0.9rem !important;
        }
        
        /* Inputs con Estilo Caja LCD */
        div[data-testid="stForm"] input {
            background-color: #000000 !important;
            color: #1c47ff !important;
            border: 1px solid #ff0000 !important;
            border-radius: 4px !important;
            box-shadow: inset 0 0 15px rgba(28, 71, 255, 0.3) !important;
            text-shadow: 0 0 8px rgba(28, 71, 255, 0.6) !important;
            font-family: 'JetBrains Mono', monospace !important;
            font-weight: bold !important;
            padding: 10px !important;
        }
        
        /* Ajuste para inputs numéricos y selectores */
        div[data-testid="stForm"] div[data-baseweb="input"], 
        div[data-testid="stForm"] div[data-baseweb="select"] {
            background-color: transparent !important;
        }
        </style>
    """, unsafe_allow_html=True)

    with st.form("vehicle_info"):
        st.markdown("<h2 style='color:#1c47ff; text-shadow: 0 0 20px rgba(28,71,255,0.9); margin-bottom:25px; letter-spacing:4px;'>📊 SISTEMA CENTRAL</h2>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            vin = st.text_input("Bastidor (VIN)", value=info.get("vin", ""))
            engine_code = st.text_input("Código Motor", value=info.get("engine_code", "ALH"))
            plate = st.text_input("Matrícula", value=info.get("plate", ""))
        with col2:
            current_mileage_cfg = st.number_input("Kilometraje Actual (km)", value=int(info.get("current_mileage", 280000)), min_value=0)
            last_oil_cfg = st.number_input("Kilometraje Último Cambio Aceite (km)", value=int(info.get("last_oil_change_km", 270000)), min_value=0)
            oil_interval = st.number_input("Intervalo Cambio Aceite (km)", value=int(info.get("oil_interval", 10000)), min_value=1000, step=500)
        
        st.markdown("<br><h2 style='color:#1c47ff; text-shadow: 0 0 20px rgba(28,71,255,0.9); margin-bottom:25px; letter-spacing:4px;'>🤖 MECÁNICO IA</h2>", unsafe_allow_html=True)
        gemini_key = st.text_input("Gemini API Key", value=info.get("gemini_api_key", ""), type="password")

        st.markdown("<br>", unsafe_allow_html=True)
        if st.form_submit_button("💾 ACTUALIZAR SISTEMA"):
            update_vehicle_info("vin", vin)
            update_vehicle_info("engine_code", engine_code)
            update_vehicle_info("plate", plate)
            update_vehicle_info("current_mileage", str(current_mileage_cfg))
            update_vehicle_info("last_oil_change_km", str(last_oil_cfg))
            update_vehicle_info("oil_interval", str(oil_interval))
            update_vehicle_info("gemini_api_key", gemini_key)
            st.success("Configuración del sistema actualizada.")
            st.rerun()
