import streamlit as st

def apply_styles():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Michroma&family=Share+Tech+Mono&display=swap');

        /* ============================================
           TIPOGRAFÍA VW GOLF IV — SISTEMA GLOBAL
           Michroma + fallback emoji para no romper
           iconos de Streamlit
           ============================================ */

        /* Global — selectores seguros, con fallback emoji */
        html, body, [data-testid="stAppViewContainer"] {
            font-family: 'Michroma', 'Segoe UI Emoji', 'Apple Color Emoji', sans-serif !important;
        }

        /* Títulos */
        h1 {
            font-family: 'Michroma', sans-serif !important;
            font-size: 1.4rem !important;
            letter-spacing: 2px !important;
            line-height: 1.5 !important;
            color: #1c47ff !important;
            text-shadow: 0 0 12px rgba(28, 71, 255, 0.7), 0 0 25px rgba(28, 71, 255, 0.3) !important;
            text-transform: uppercase !important;
        }
        h2 {
            font-family: 'Michroma', sans-serif !important;
            font-size: 1.1rem !important;
            letter-spacing: 1.5px !important;
            line-height: 1.5 !important;
            color: #1c47ff !important;
            text-shadow: 0 0 10px rgba(28, 71, 255, 0.6) !important;
            text-transform: uppercase !important;
        }
        h3, h4 {
            font-family: 'Michroma', sans-serif !important;
            font-size: 0.9rem !important;
            letter-spacing: 1px !important;
            line-height: 1.5 !important;
            color: #1c47ff !important;
            text-shadow: 0 0 8px rgba(28, 71, 255, 0.5) !important;
            text-transform: uppercase !important;
        }

        /* Datos LCD: números, códigos, valores */
        code, .stNumberInput input, [data-testid="stMetricValue"],
        .stMarkdown code, [data-testid="stMetricValue"] div {
            font-family: 'Share Tech Mono', monospace !important;
        }

        .main {
            background-color: #050505 !important;
            color: #ffffff !important;
        }

        /* Sidebar */
        [data-testid="stSidebar"] {
            background-color: #0a0a0c !important;
            border-right: 1px solid #1c39bb !important;
            box-shadow: 5px 0 15px rgba(28, 57, 187, 0.1) !important;
        }
        
        [data-testid="stSidebarNav"] {
            background-color: transparent !important;
        }

        /* Menu Radio Buttons */
        div[data-testid="stSidebarUserContent"] .stRadio > label {
            color: #ffffff !important;
            font-family: 'Michroma', 'Segoe UI Emoji', sans-serif !important;
            font-size: 0.7rem !important;
            padding: 8px !important;
            border-radius: 5px !important;
            transition: all 0.3s !important;
        }

        div[data-testid="stSidebarUserContent"] .stRadio div[role="radiogroup"] > label[data-baseweb="radio"] {
            background-color: rgba(255, 255, 255, 0.03) !important;
            border: 1px solid rgba(28, 57, 187, 0.1) !important;
            margin-bottom: 4px !important;
            padding: 7px 10px !important;
            border-radius: 4px !important;
        }

        div[data-testid="stSidebarUserContent"] .stRadio div[role="radiogroup"] > label[data-baseweb="radio"]:hover {
            border-color: #1c39bb !important;
            background-color: rgba(28, 57, 187, 0.1) !important;
        }

        /* Active Menu Item */
        div[data-testid="stSidebarUserContent"] .stRadio div[role="radiogroup"] > label[data-baseweb="radio"]:has(input:checked) {
            background-color: #1c39bb !important;
            box-shadow: 0 0 15px rgba(28, 57, 187, 0.5) !important;
            border: 1px solid #2e5bff !important;
        }
        
        [data-testid="stSidebar"] h3 {
            color: #ffffff !important;
            text-shadow: 0 0 5px rgba(255, 255, 255, 0.5) !important;
            font-family: 'Michroma', sans-serif !important;
            font-size: 0.8rem !important;
            letter-spacing: 2px !important;
        }

        [data-testid="stSidebar"] p {
            font-size: 0.7rem !important;
            font-family: 'Michroma', 'Segoe UI Emoji', sans-serif !important;
        }

        /* Metrics */
        [data-testid="stMetric"] {
            background: #000000 !important;
            border: 1px solid #440000 !important;
            border-radius: 2px !important;
            padding: 0.8rem !important;
            box-shadow: inset 0 0 15px rgba(255, 0, 0, 0.1) !important;
        }
        
        [data-testid="stMetricLabel"] p {
            color: #ff4444 !important;
            font-family: 'Michroma', sans-serif !important;
            text-transform: uppercase !important;
            font-size: 0.6rem !important;
            letter-spacing: 1px !important;
        }
        
        [data-testid="stMetricValue"] div {
            color: #ff0000 !important;
            font-family: 'Share Tech Mono', monospace !important;
            text-shadow: 0 0 12px rgba(255, 0, 0, 0.9) !important;
            font-weight: 700 !important;
            font-size: 1.5rem !important;
        }

        /* Expanders */
        [data-testid="stExpander"] {
            border: 2px solid #ff0000 !important;
            background-color: #000000 !important;
            border-radius: 2px !important;
            box-shadow: 0 0 15px rgba(255, 0, 0, 0.3) !important;
            margin-bottom: 0.8rem !important;
        }
        
        [data-testid="stExpander"] summary p {
            color: #2e5bff !important;
            font-family: 'Michroma', 'Segoe UI Emoji', 'Apple Color Emoji', sans-serif !important;
            text-shadow: 0 0 10px rgba(46, 91, 255, 0.6) !important;
            font-size: 0.75rem !important;
            letter-spacing: 0.5px !important;
            line-height: 1.8 !important;
            word-spacing: 2px !important;
        }

        /* Buttons - MK4 Red Needles */
        div.stButton > button {
            background-color: #000000 !important;
            color: #ff0000 !important;
            border: 2px solid #ff0000 !important;
            border-radius: 2px !important;
            padding: 0.5rem 1rem !important;
            font-family: 'Michroma', 'Segoe UI Emoji', sans-serif !important;
            text-transform: uppercase !important;
            font-size: 0.65rem !important;
            letter-spacing: 1px !important;
            box-shadow: 0 0 10px rgba(255, 0, 0, 0.4) !important;
            transition: all 0.2s ease-in-out !important;
        }
        
        div.stButton > button:hover {
            background-color: #ff0000 !important;
            box-shadow: 0 0 25px rgba(255, 0, 0, 0.8) !important;
            color: #ffffff !important;
            transform: scale(1.02);
        }

        /* === ESTILOS LCD GLOBALES === */
        
        /* Pestañas (Tabs) */
        div[data-testid="stTabs"] button {
            background-color: #000000 !important;
            color: #555555 !important;
            border: 1px solid #333333 !important;
            border-bottom: 2px solid #ff0000 !important;
            font-family: 'Michroma', 'Segoe UI Emoji', sans-serif !important;
            font-size: 0.65rem !important;
            text-transform: uppercase !important;
            letter-spacing: 0.5px !important;
            transition: all 0.3s ease !important;
            padding: 8px 14px !important;
        }
        
        div[data-testid="stTabs"] button[aria-selected="true"] {
            color: #1c47ff !important;
            background-color: #000000 !important;
            border: 1px solid #1c47ff !important;
            border-bottom: 3px solid #1c47ff !important;
            box-shadow: 0 0 15px rgba(28, 71, 255, 0.4), inset 0 0 10px rgba(28, 71, 255, 0.2) !important;
            text-shadow: 0 0 10px rgba(28, 71, 255, 0.8) !important;
        }
        
        /* Selectboxes LCD */
        div[data-baseweb="select"] > div {
            background-color: #000000 !important;
            border: 1.5px solid #ff0000 !important;
            border-radius: 4px !important;
            box-shadow: inset 0 0 15px rgba(28, 71, 255, 0.2) !important;
            cursor: pointer !important;
        }
        
        /* Bloquear escritura y cursor en el selector - MODO FANTASMA */
        div[data-baseweb="select"] input {
            opacity: 0 !important;
            caret-color: transparent !important;
            cursor: pointer !important;
            position: absolute !important;
        }
        
        /* Forzar color Índigo en TODOS los niveles del texto seleccionado */
        div[data-baseweb="select"] * {
            color: #1c47ff !important;
            text-shadow: 0 0 10px rgba(28, 71, 255, 0.9) !important;
            font-family: 'Michroma', sans-serif !important;
        }
        
        div[data-baseweb="select"] span, 
        div[data-baseweb="select"] div,
        div[data-baseweb="select"] p {
            color: #1c47ff !important;
            font-size: 0.7rem !important;
            text-transform: uppercase !important;
            letter-spacing: 1px !important;
        }

        div[data-baseweb="select"] svg {
            fill: #ff0000 !important;
        }

        /* --- ESTILO PARA EL MENÚ DESPLEGABLE (DROPDOWN LIST) --- */
        [data-baseweb="popover"] ul {
            background-color: #000000 !important;
            border: 1px solid #ff0000 !important;
            box-shadow: 0 0 20px rgba(255, 0, 0, 0.4) !important;
        }

        [data-baseweb="popover"] li {
            background-color: #000000 !important;
            color: #1c47ff !important;
            font-family: 'Michroma', sans-serif !important;
            text-transform: uppercase !important;
            font-size: 0.7rem !important;
            transition: all 0.2s !important;
        }

        [data-baseweb="popover"] li:hover {
            background-color: #1c47ff !important;
            color: #ffffff !important;
            text-shadow: 0 0 10px rgba(255, 255, 255, 0.8) !important;
        }

        /* Inputs y Textareas */
        input, textarea, [data-testid="stTextInput"] input, [data-testid="stTextArea"] textarea {
            background-color: #000000 !important;
            color: #1c47ff !important;
            border: 1.5px solid #ff0000 !important;
            box-shadow: inset 0 0 12px rgba(28, 71, 255, 0.25) !important;
            text-shadow: 0 0 5px rgba(28, 71, 255, 0.5) !important;
            font-family: 'Share Tech Mono', monospace !important;
            font-size: 0.85rem !important;
            border-radius: 4px !important;
        }

        /* Etiquetas (Labels) */
        label p {
            color: #1c47ff !important;
            text-shadow: 0 0 8px rgba(28, 71, 255, 0.6) !important;
            font-family: 'Michroma', sans-serif !important;
            text-transform: uppercase !important;
            font-size: 0.65rem !important;
            line-height: 1.6 !important;
        }
        
        /* Párrafos generales - NO forzar tamaño para no romper layouts */
        .stMarkdown p {
            color: #1c47ff !important;
            text-shadow: 0 0 6px rgba(28, 71, 255, 0.4) !important;
            font-family: 'Michroma', 'Segoe UI Emoji', 'Apple Color Emoji', sans-serif !important;
            font-size: 0.8rem !important;
            line-height: 1.8 !important;
            word-spacing: 2px !important;
        }

        /* Botones Globales LCD */
        div.stButton button {
            background-color: #000000 !important;
            color: #1c47ff !important;
            border: 1.5px solid #ff0000 !important;
            box-shadow: 0 0 10px rgba(255, 0, 0, 0.2) !important;
            text-shadow: 0 0 8px rgba(28, 71, 255, 0.8) !important;
            font-family: 'Michroma', 'Segoe UI Emoji', sans-serif !important;
            font-size: 0.65rem !important;
            text-transform: uppercase !important;
            letter-spacing: 0.5px !important;
        }
        
        div.stButton button:hover {
            border-color: #1c47ff !important;
            color: #ffffff !important;
            box-shadow: 0 0 15px rgba(28, 71, 255, 0.5) !important;
        }

        /* Chat Messages */
        [data-testid="stChatMessage"] {
            background-color: #0a0a0a !important;
            border-left: 4px solid #ff0000 !important;
            margin-bottom: 0.5rem !important;
            border-radius: 0 10px 10px 0 !important;
        }
        
        [data-testid="stChatMessageContent"] p {
            color: #00ff00 !important;
            font-family: 'Share Tech Mono', monospace !important;
            font-size: 0.85rem !important;
            text-shadow: 0 0 5px rgba(0, 255, 0, 0.3);
        }

        /* File Uploader - Unidad de Diagnóstico */
        [data-testid="stFileUploader"] {
            background-color: #000000 !important;
            border: 1.5px solid #ff0000 !important;
            border-radius: 4px !important;
            padding: 1rem !important;
            box-shadow: 0 0 20px rgba(255, 0, 0, 0.2), inset 0 0 15px rgba(28, 71, 255, 0.1) !important;
        }

        [data-testid="stFileUploader"] section {
            background-color: transparent !important;
            border: 1px dashed rgba(28, 71, 255, 0.4) !important;
        }

        [data-testid="stFileUploader"] label p {
            color: #1c47ff !important;
            text-shadow: 0 0 8px rgba(28, 71, 255, 0.6) !important;
            font-family: 'Michroma', sans-serif !important;
            text-transform: uppercase !important;
            font-size: 0.7rem !important;
        }

        [data-testid="stFileUploader"] small {
            color: #2e5bff !important;
            font-family: 'Share Tech Mono', monospace !important;
        }

        /* Botón de Upload interno */
        [data-testid="stFileUploader"] button {
            background-color: #000000 !important;
            color: #ff0000 !important;
            border: 1px solid #ff0000 !important;
            font-family: 'Michroma', sans-serif !important;
            text-transform: uppercase !important;
            font-size: 0.6rem !important;
            letter-spacing: 1px !important;
            transition: all 0.3s !important;
        }

        [data-testid="stFileUploader"] button:hover {
            background-color: #ff0000 !important;
            color: #ffffff !important;
            box-shadow: 0 0 15px #ff0000 !important;
        }

        /* Hide Streamlit elements */
        #MainMenu, footer { visibility: hidden; }
        </style>
    """, unsafe_allow_html=True)
