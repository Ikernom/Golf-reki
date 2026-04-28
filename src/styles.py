import streamlit as st

def apply_styles():
    st.markdown("""
        <style>
        /* Main Container */
        .main {
            background-color: #0e1117;
            color: #ffffff;
        }
        
        /* Sidebar */
        [data-testid="stSidebar"] {
            background-image: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
            border-right: 1px solid #334155;
        }
        
        /* Cards */
        .stMetric {
            background-color: #1e293b;
            padding: 20px;
            border-radius: 15px;
            border: 1px solid #334155;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            transition: transform 0.2s;
        }
        .stMetric:hover {
            transform: translateY(-5px);
            border-color: #3b82f6;
        }
        
        /* Titles and Headers */
        h1, h2, h3 {
            font-family: 'Inter', sans-serif;
            font-weight: 800;
            letter-spacing: -0.025em;
            background: linear-gradient(90deg, #ffffff 0%, #94a3b8 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        /* Custom VW Blue accents */
        .stButton>button {
            background-color: #2563eb !important;
            color: white !important;
            border-radius: 8px !important;
            border: none !important;
            padding: 0.5rem 2rem !important;
            font-weight: 600 !important;
            transition: all 0.3s ease !important;
        }
        .stButton>button:hover {
            background-color: #1d4ed8 !important;
            box-shadow: 0 0 15px rgba(37, 99, 235, 0.4) !important;
            transform: scale(1.02);
        }
        
        /* Plotly charts backgrounds */
        .js-plotly-plot .plotly .main-svg {
            background: transparent !important;
        }
        
        /* Custom Garage Card */
        .garage-card {
            background: rgba(30, 41, 59, 0.7);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 25px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            margin-bottom: 20px;
        }
        
        /* Hidden menu */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        </style>
    """, unsafe_allow_html=True)
