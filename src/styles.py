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

        /* --- UNIFICACIÓN UI: COMPONENTES GOLF MK4 VDO --- */
        
        /* MFA Status Bar (Pantalla Central VDO) */
        .mfa-status {
            background-color: #050505 !important;
            border-radius: 4px !important;
            padding: 12px !important;
            text-align: center !important;
            margin-bottom: 20px !important;
            border: 2px solid #ff0000 !important;
            box-shadow: inset 0 0 20px rgba(255, 0, 0, 0.3), 0 0 10px rgba(255, 0, 0, 0.2) !important;
            color: #ff0000 !important;
            font-family: 'Share Tech Mono', monospace !important;
            font-weight: bold !important;
            font-size: 1.1rem !important;
            text-transform: uppercase !important;
            letter-spacing: 2px !important;
        }

        .mfa-status.fault {
            background-color: #1a0000 !important;
            border-color: #ff0000 !important;
            box-shadow: inset 0 0 30px rgba(255, 0, 0, 0.8), 0 0 15px rgba(255, 0, 0, 0.5) !important;
            color: #ffffff !important;
            text-shadow: 0 0 10px #ff0000 !important;
            animation: pulse-fault 2s infinite;
        }

        @keyframes pulse-fault {
            0% { box-shadow: inset 0 0 30px rgba(255, 0, 0, 0.8); }
            50% { box-shadow: inset 0 0 50px rgba(255, 0, 0, 1); }
            100% { box-shadow: inset 0 0 30px rgba(255, 0, 0, 0.8); }
        }

        /* VDO Odometer (Pantallita de KM) */
        .vdo-odometer-label {
            color: #1c47ff !important;
            font-size: 0.8rem !important;
            margin-bottom: 0 !important;
            font-family: 'Michroma', sans-serif !important;
            letter-spacing: 1.5px !important;
            text-shadow: 0 0 5px rgba(28, 71, 255, 0.5) !important;
        }
        
        .vdo-odometer-value {
            background-color: #000000 !important;
            color: #1c47ff !important;
            padding: 10px !important;
            border: 1px solid #1c47ff !important;
            border-radius: 4px !important;
            margin-top: 5px !important;
            font-size: 2.2rem !important;
            text-shadow: 0 0 15px rgba(28, 71, 255, 0.8) !important;
            font-family: 'Share Tech Mono', monospace !important;
            letter-spacing: 3px !important;
            box-shadow: inset 0 0 15px rgba(28, 71, 255, 0.2) !important;
            display: inline-block !important;
        }

        /* Fault Cards (Estado de Salud) */
        .fault-card {
            background: linear-gradient(180deg, #0a0a0f 0%, #050505 100%) !important;
            padding: 15px !important;
            border-radius: 4px !important;
            margin-bottom: 15px !important;
            border: 1px solid #1c47ff !important;
            border-left: 6px solid #1c47ff !important;
            box-shadow: 0 0 15px rgba(28, 71, 255, 0.15) !important;
        }
        
        .fault-card.critical {
            border-color: #ff0000 !important;
            border-left-color: #ff0000 !important;
            box-shadow: 0 0 15px rgba(255, 0, 0, 0.3) !important;
        }

        .fault-card h4 {
            margin: 0 !important;
            font-family: 'Michroma', sans-serif !important;
            font-size: 1rem !important;
            color: #ffffff !important;
            letter-spacing: 1px !important;
            text-shadow: 0 0 8px rgba(255, 255, 255, 0.3) !important;
        }

        .fault-card p {
            margin: 10px 0 !important;
            color: #b0c4ff !important;
            font-family: 'Inter', sans-serif !important;
            font-size: 0.9rem !important;
        }

        .fault-card small {
            color: #ff0000 !important;
            font-family: 'Share Tech Mono', monospace !important;
            font-size: 0.75rem !important;
            letter-spacing: 1px !important;
        }

        /* LCD Bubbles (Historial y Wishlist) */
        .lcd-bubble-container {
            position: relative; 
            height: 0px; 
            margin-bottom: 0px;
        }

        .lcd-bubble {
            position: absolute; 
            left: 50%; 
            transform: translateX(-50%); 
            top: 16px; 
            z-index: 99; 
            pointer-events: none;
            background: #000000 !important;
            color: #ff0000 !important;
            padding: 4px 18px !important;
            border-radius: 2px !important;
            font-size: 0.75rem !important;
            border: 2px solid #ff0000 !important;
            box-shadow: inset 0 0 10px rgba(255, 0, 0, 0.5), 0 0 15px rgba(255, 0, 0, 0.4) !important;
            text-transform: uppercase !important;
            font-family: 'Share Tech Mono', monospace !important;
            letter-spacing: 2px !important;
            font-weight: bold !important;
        }
        
        .lcd-bubble.blue {
            color: #1c47ff !important;
            border-color: #1c47ff !important;
            box-shadow: inset 0 0 10px rgba(28, 71, 255, 0.5), 0 0 15px rgba(28, 71, 255, 0.4) !important;
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

