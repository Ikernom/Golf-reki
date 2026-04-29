import streamlit as st

def apply_styles():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');

        /* Global Reset */
        .main {
            background-color: #050505 !important;
            color: #ffffff !important;
        }

        /* Sidebar - Mk4 Cockpit Style */
        [data-testid="stSidebar"] {
            background-color: #0a0a0c !important;
            border-right: 1px solid #1c39bb !important;
            box-shadow: 5px 0 15px rgba(28, 57, 187, 0.1) !important;
        }
        
        [data-testid="stSidebarNav"] {
            background-color: transparent !important;
        }

        /* Menu Radio Buttons - Indigo Glow */
        div[data-testid="stSidebarUserContent"] .stRadio > label {
            color: #ffffff !important;
            font-family: 'JetBrains Mono', monospace !important;
            font-size: 0.9rem !important;
            padding: 10px !important;
            border-radius: 5px !important;
            transition: all 0.3s !important;
        }

        div[data-testid="stSidebarUserContent"] .stRadio div[role="radiogroup"] > label[data-baseweb="radio"] {
            background-color: rgba(255, 255, 255, 0.03) !important;
            border: 1px solid rgba(28, 57, 187, 0.1) !important;
            margin-bottom: 5px !important;
            padding: 8px 12px !important;
            border-radius: 4px !important;
        }

        div[data-testid="stSidebarUserContent"] .stRadio div[role="radiogroup"] > label[data-baseweb="radio"]:hover {
            border-color: #1c39bb !important;
            background-color: rgba(28, 57, 187, 0.1) !important;
        }

        /* Active Menu Item - Pure Indigo */
        div[data-testid="stSidebarUserContent"] .stRadio div[role="radiogroup"] > label[data-baseweb="radio"]:has(input:checked) {
            background-color: #1c39bb !important;
            box-shadow: 0 0 15px rgba(28, 57, 187, 0.5) !important;
            border: 1px solid #2e5bff !important;
        }
        
        [data-testid="stSidebar"] h3 {
            color: #ffffff !important;
            text-shadow: 0 0 5px rgba(255, 255, 255, 0.5) !important;
            font-family: 'JetBrains Mono', monospace !important;
            letter-spacing: 2px !important;
        }

        /* Metrics - Iconic Indigo and Red LCD */
        [data-testid="stMetric"] {
            background: #000000 !important;
            border: 1px solid #440000 !important;
            border-radius: 2px !important;
            padding: 1rem !important;
            box-shadow: inset 0 0 15px rgba(255, 0, 0, 0.1) !important;
        }
        
        [data-testid="stMetricLabel"] p {
            color: #ff4444 !important;
            font-family: 'JetBrains Mono', monospace !important;
            text-transform: uppercase !important;
            font-size: 0.75rem !important;
        }
        
        [data-testid="stMetricValue"] div {
            color: #ff0000 !important;
            font-family: 'JetBrains Mono', monospace !important;
            text-shadow: 0 0 12px rgba(255, 0, 0, 0.9) !important;
            font-weight: 700 !important;
        }

        /* Titles - MK4 Deep Indigo Display */
        h1, h2, h3, .stSubheader {
            color: #1c47ff !important;
            text-shadow: 0 0 12px rgba(28, 71, 255, 0.7), 0 0 25px rgba(28, 71, 255, 0.3) !important;
            font-family: 'JetBrains Mono', monospace !important;
            text-transform: uppercase !important;
            letter-spacing: 3px !important;
            font-weight: 800 !important;
        }

        /* Expanders - Dashboard Units */
        [data-testid="stExpander"] {
            border: 2px solid #ff0000 !important;
            background-color: #000000 !important;
            border-radius: 2px !important;
            box-shadow: 0 0 15px rgba(255, 0, 0, 0.3) !important;
            margin-bottom: 1rem !important;
        }
        
        [data-testid="stExpander"] summary p {
            color: #2e5bff !important;
            font-family: 'JetBrains Mono', monospace !important;
            font-weight: 700 !important;
            text-shadow: 0 0 10px rgba(46, 91, 255, 0.6) !important;
            font-size: 1.1rem !important;
        }

        /* Buttons - MK4 Red Needles */
        div.stButton > button {
            background-color: #000000 !important;
            color: #ff0000 !important;
            border: 2px solid #ff0000 !important;
            border-radius: 2px !important;
            padding: 0.6rem 1.2rem !important;
            font-family: 'JetBrains Mono', monospace !important;
            text-transform: uppercase !important;
            font-weight: bold !important;
            letter-spacing: 1.5px !important;
            box-shadow: 0 0 10px rgba(255, 0, 0, 0.4) !important;
            transition: all 0.2s ease-in-out !important;
        }
        
        div.stButton > button:hover {
            background-color: #ff0000 !important;
            box-shadow: 0 0 25px rgba(255, 0, 0, 0.8) !important;
            color: #ffffff !important;
            transform: scale(1.02);
        }

        /* Tabs - Blue Selection */
        button[data-baseweb="tab"] {
            color: #666 !important;
            font-family: 'JetBrains Mono', monospace !important;
        }
        
        button[aria-selected="true"] {
            background-color: #2e5bff !important;
            color: #ffffff !important;
            box-shadow: 0 0 15px rgba(46, 91, 255, 0.5) !important;
        }

        /* Chat Messages - Diagnostic Log Style */
        [data-testid="stChatMessage"] {
            background-color: #0a0a0a !important;
            border-left: 4px solid #ff0000 !important;
            margin-bottom: 0.5rem !important;
            border-radius: 0 10px 10px 0 !important;
        }
        
        [data-testid="stChatMessageContent"] p {
            color: #00ff00 !important;
            font-family: 'JetBrains Mono', monospace !important;
            font-size: 0.9rem !important;
            text-shadow: 0 0 5px rgba(0, 255, 0, 0.3);
        }

        /* Hide Streamlit elements */
        #MainMenu, footer { visibility: hidden; }
        </style>
    """, unsafe_allow_html=True)
