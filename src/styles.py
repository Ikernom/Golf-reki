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

        /* Sidebar - Mk4 Center Console */
        [data-testid="stSidebar"] {
            background-color: #111111 !important;
            border-right: 2px solid #222 !important;
        }
        
        [data-testid="stSidebar"] h3 {
            color: #ff0000 !important;
            text-shadow: 0 0 10px rgba(255, 0, 0, 0.7) !important;
            font-family: 'JetBrains Mono', monospace !important;
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
            color: #2e5bff !important;
            text-shadow: 0 0 20px rgba(46, 91, 255, 0.8) !important;
            font-family: 'JetBrains Mono', monospace !important;
            text-transform: uppercase !important;
        }

        /* Buttons - Backlit Switches */
        div.stButton > button {
            background-color: #1a1a1a !important;
            color: #ff0000 !important;
            border: 1.5px solid #ff0000 !important;
            border-radius: 4px !important;
            padding: 0.5rem 1rem !important;
            font-family: 'JetBrains Mono', monospace !important;
            box-shadow: 0 0 8px rgba(255, 0, 0, 0.3) !important;
            transition: all 0.2s ease-in-out !important;
        }
        
        div.stButton > button:hover {
            background-color: #2a0000 !important;
            box-shadow: 0 0 20px rgba(255, 0, 0, 0.6) !important;
            color: #ff4444 !important;
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
