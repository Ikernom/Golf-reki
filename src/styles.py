import streamlit as st

def apply_styles():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');

        /* Main App Reset */
        .main {
            background-color: #0a0a0a;
            color: #ffffff;
            font-family: 'JetBrains+Mono', monospace;
        }

        /* Sidebar - Center Console Style */
        [data-testid="stSidebar"] {
            background-color: #121212 !important;
            border-right: 2px solid #222;
            box-shadow: 10px 0 30px rgba(0,0,0,0.5);
        }
        
        [data-testid="stSidebar"] h3 {
            color: #ff0000 !important;
            text-shadow: 0 0 10px rgba(255, 0, 0, 0.5);
            font-family: 'JetBrains+Mono', monospace;
            text-transform: uppercase;
        }

        /* Navigation Radio - Red Backlit Feel */
        div[data-testid="stSidebarUserContent"] .st-emotion-cache-1647z6a {
            background-color: transparent !important;
            border-left: 4px solid transparent;
            transition: all 0.3s ease;
        }
        
        div[data-testid="stSidebarUserContent"] .st-emotion-cache-1647z6a:hover {
            background-color: rgba(255, 0, 0, 0.1) !important;
            border-left: 4px solid #ff0000;
        }

        /* Metrics - MFA (Multi-Function Display) Style */
        [data-testid="stMetric"] {
            background: #1a0000 !important;
            border: 2px solid #330000 !important;
            border-radius: 4px !important;
            padding: 15px !important;
            box-shadow: inset 0 0 15px rgba(255, 0, 0, 0.2);
        }
        
        [data-testid="stMetricLabel"] {
            color: #ff3333 !important;
            font-size: 0.8rem !important;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        [data-testid="stMetricValue"] {
            color: #ff0000 !important;
            font-family: 'JetBrains+Mono', monospace !important;
            text-shadow: 0 0 8px rgba(255, 0, 0, 0.8);
            font-weight: 700 !important;
        }

        /* Indigo Gauges Accents */
        h1, h2, h3 {
            color: #4d4dff !important;
            text-shadow: 0 0 15px rgba(77, 77, 255, 0.6);
            font-family: 'JetBrains+Mono', monospace;
        }

        /* Buttons - Red Switches */
        .stButton>button {
            background: #1a1a1a !important;
            color: #ff0000 !important;
            border: 1px solid #ff0000 !important;
            border-radius: 4px !important;
            font-family: 'JetBrains+Mono', monospace !important;
            text-transform: uppercase;
            box-shadow: 0 0 5px rgba(255, 0, 0, 0.2) !important;
            transition: all 0.2s !important;
        }
        
        .stButton>button:hover {
            background: #220000 !important;
            box-shadow: 0 0 15px rgba(255, 0, 0, 0.5) !important;
            color: #ff5555 !important;
        }

        /* Dataframes & Tables */
        .stDataFrame {
            border: 1px solid #333 !important;
            border-radius: 8px;
        }

        /* Custom Card for Garage Items */
        .garage-card {
            background: #111;
            border-left: 5px solid #4d4dff;
            padding: 20px;
            border-radius: 0 10px 10px 0;
            margin-bottom: 15px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.3);
        }

        /* Tabs Style */
        .stTabs [data-baseweb="tab-list"] {
            gap: 10px;
            background-color: transparent;
        }

        .stTabs [data-baseweb="tab"] {
            background-color: #1a1a1a !important;
            border: 1px solid #333 !important;
            color: #888 !important;
            border-radius: 4px 4px 0 0 !important;
            padding: 10px 20px !important;
        }

        .stTabs [aria-selected="true"] {
            background-color: #4d4dff !important;
            color: white !important;
            border-color: #4d4dff !important;
            box-shadow: 0 0 10px rgba(77, 77, 255, 0.5);
        }

        /* Chat Messages - Diagnostic Readout Style */
        [data-testid="stChatMessage"] {
            background-color: #1a1a1a !important;
            border-left: 3px solid #ff0000 !important;
            border-radius: 0 8px 8px 0 !important;
            margin-bottom: 10px !important;
        }
        
        [data-testid="stChatMessage"] p {
            font-family: 'JetBrains+Mono', monospace !important;
            color: #ccc !important;
        }

        /* Hide elements */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {background: transparent !important;}
        </style>
    """, unsafe_allow_html=True)
