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

        /* Titles - Indigo Gauge Glow */
        h1, h2, h3, .stSubheader {
            color: #4338ca !important;
            text-shadow: 0 0 15px rgba(67, 56, 202, 0.6) !important;
            font-family: 'JetBrains Mono', monospace !important;
            text-transform: uppercase !important;
            letter-spacing: 2px !important;
        }

        /* Expanders - Dashboard Units */
        [data-testid="stExpander"] {
            border: 1.5px solid #ef4444 !important;
            background-color: #0c0c0e !important;
            border-radius: 4px !important;
            box-shadow: 0 0 10px rgba(239, 68, 68, 0.1) !important;
        }
        
        [data-testid="stExpander"] summary p {
            color: #6366f1 !important;
            font-family: 'JetBrains Mono', monospace !important;
            font-weight: 700 !important;
            text-shadow: 0 0 10px rgba(99, 102, 241, 0.5) !important;
        }

        /* Buttons - Backlit Switches */
        div.stButton > button {
            background-color: #0f172a !important;
            color: #ef4444 !important;
            border: 1.5px solid #ef4444 !important;
            border-radius: 4px !important;
            padding: 0.5rem 1rem !important;
            font-family: 'JetBrains Mono', monospace !important;
            text-transform: uppercase !important;
            letter-spacing: 1px !important;
            box-shadow: 0 0 8px rgba(239, 68, 68, 0.2) !important;
            transition: all 0.2s ease-in-out !important;
        }
        
        div.stButton > button:hover {
            background-color: #ef4444 !important;
            box-shadow: 0 0 20px rgba(239, 68, 68, 0.6) !important;
            color: #ffffff !important;
            transform: translateY(-1px);
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
