import streamlit as st

def apply_styles():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Michroma&family=Share+Tech+Mono&family=Inter:wght@300;400&display=swap');

        /* ============================================
           ESTÉTICA GOLF MK4 2026 — AIRY INDIGO RED
           ============================================ */

        /* Global — Estética Glassmorphism */
        html, body, [data-testid="stAppViewContainer"] {
            font-family: 'Michroma', sans-serif !important;
            background: radial-gradient(circle at top right, #0a0a15 0%, #050505 100%) !important;
            color: #e0e0e0 !important;
        }

        /* Títulos Modernizados */
        h1, h2, h3 {
            font-family: 'Michroma', sans-serif !important;
            letter-spacing: 3px !important;
            line-height: 1.6 !important;
            text-transform: uppercase !important;
            color: #1c47ff !important;
            text-shadow: 0 0 15px rgba(28, 71, 255, 0.4) !important;
        }

        h1 { font-size: 1.6rem !important; margin-bottom: 1.5rem !important; }
        h2 { font-size: 1.2rem !important; }

        /* Contenedores con Aura Roja (Glassmorphism) */
        [data-testid="stExpander"], [data-testid="stMetric"], .stChatMessage, [data-testid="stFileUploader"] {
            background: rgba(10, 10, 10, 0.6) !important;
            backdrop-filter: blur(10px) !important;
            border: 1px solid rgba(255, 0, 0, 0.3) !important;
            border-radius: 8px !important;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5), 0 0 10px rgba(255, 0, 0, 0.1) !important;
            transition: all 0.3s ease !important;
        }

        [data-testid="stExpander"]:hover {
            border-color: rgba(255, 0, 0, 0.6) !important;
            box-shadow: 0 0 20px rgba(255, 0, 0, 0.2) !important;
        }

        /* Tipografía Airy para párrafos */
        .stMarkdown p, label p {
            font-family: 'Michroma', sans-serif !important;
            font-size: 0.75rem !important;
            line-height: 2.0 !important; /* Espaciado generoso */
            letter-spacing: 0.8px !important;
            color: #b0c4ff !important; /* Indigo suave para lectura */
            text-shadow: none !important;
        }

        /* Inputs y Escritura - Más cómodos */
        input, textarea, [data-testid="stTextInput"] input, [data-testid="stTextArea"] textarea {
            background-color: rgba(0, 0, 0, 0.4) !important;
            color: #ffffff !important;
            border: 1px solid rgba(255, 0, 0, 0.3) !important;
            border-radius: 6px !important;
            padding: 12px !important;
            font-family: 'Inter', sans-serif !important; /* Fuente más legible para escribir */
            font-size: 0.9rem !important;
            line-height: 1.6 !important;
            transition: border 0.3s !important;
        }

        input:focus, textarea:focus {
            border-color: #ff0000 !important;
            box-shadow: 0 0 10px rgba(255, 0, 0, 0.3) !important;
            outline: none !important;
        }

        /* Botones - Estilo Aguja de Cuadro */
        div.stButton > button {
            background: linear-gradient(135deg, #000 0%, #111 100%) !important;
            color: #ff0000 !important;
            border: 1px solid #ff0000 !important;
            border-radius: 4px !important;
            padding: 0.6rem 1.2rem !important;
            font-family: 'Michroma', sans-serif !important;
            font-size: 0.65rem !important;
            letter-spacing: 2px !important;
            box-shadow: 0 0 8px rgba(255, 0, 0, 0.2) !important;
            transition: all 0.3s !important;
        }

        div.stButton > button:hover {
            background: #ff0000 !important;
            color: #fff !important;
            box-shadow: 0 0 20px rgba(255, 0, 0, 0.6) !important;
            transform: translateY(-2px);
        }

        /* Sidebar Persistente */
        [data-testid="stSidebar"] {
            background-color: rgba(5, 5, 7, 0.95) !important;
            border-right: 1px solid rgba(28, 71, 255, 0.2) !important;
        }

        /* Selectboxes - Estilo LCD */
        div[data-baseweb="select"] > div {
            background-color: rgba(0,0,0,0.5) !important;
            border: 1px solid rgba(255, 0, 0, 0.4) !important;
            border-radius: 6px !important;
        }

        div[data-baseweb="select"] * {
            color: #1c47ff !important;
            font-family: 'Michroma', sans-serif !important;
            font-size: 0.75rem !important;
        }

        /* Metrics LCD Red */
        [data-testid="stMetricValue"] div {
            color: #ff0000 !important;
            font-family: 'Share Tech Mono', monospace !important;
            text-shadow: 0 0 15px rgba(255, 0, 0, 0.8) !important;
            font-size: 1.8rem !important;
        }

        /* Chat Messages Modernos */
        [data-testid="stChatMessage"] {
            margin-bottom: 1rem !important;
            padding: 1rem !important;
        }

        [data-testid="stChatMessageContent"] p {
            color: #00ffcc !important; /* Un verde cian más legible que el puro */
            font-family: 'Share Tech Mono', monospace !important;
            line-height: 1.6 !important;
        }

        /* Scrollbar Personalizada */
        ::-webkit-scrollbar { width: 8px; }
        ::-webkit-scrollbar-track { background: #050505; }
        ::-webkit-scrollbar-thumb { 
            background: #1c47ff; 
            border-radius: 10px;
            box-shadow: 0 0 5px rgba(28, 71, 255, 0.5);
        }

        /* Hide Streamlit elements */
        #MainMenu, footer { visibility: hidden; }
        </style>
    """, unsafe_allow_html=True)
