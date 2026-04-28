import streamlit as st

def apply_styles():
    st.markdown("""
        <style>
        /* Main Container */
        .main {
            background-color: #050a14;
            color: #ffffff;
        }
        
        /* Sidebar - Deep Blue Pearl Style */
        [data-testid="stSidebar"] {
            background-image: linear-gradient(180deg, #0e1b40 0%, #050a14 100%);
            border-right: 1px solid #1e293b;
        }
        
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
            color: #cbd5e1;
            font-size: 0.9rem;
        }

        /* Highlighted Sidebar Radio */
        .st-emotion-cache-1647z6a {
            background-color: rgba(37, 99, 235, 0.1) !important;
            border-radius: 10px;
        }
        
        /* Cards */
        .stMetric {
            background: linear-gradient(145deg, #0f172a, #1e293b);
            padding: 20px;
            border-radius: 15px;
            border: 1px solid rgba(255, 255, 255, 0.05);
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
        }
        
        /* Custom VW Blue accents */
        .stButton>button {
            background: linear-gradient(90deg, #1e40af 0%, #3b82f6 100%) !important;
            color: white !important;
            border-radius: 12px !important;
            border: none !important;
            padding: 0.6rem 2rem !important;
            font-weight: 700 !important;
            text-transform: uppercase;
            letter-spacing: 0.5px;
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
