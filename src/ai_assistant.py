import google.generativeai as genai
import pandas as pd
import streamlit as st
from src.maintenance import get_vehicle_info

def get_ai_response(df: pd.DataFrame, user_query: str = "Analiza este log de mi Golf IV 1.9 TDI ALH y dime si ves algo raro o qué gráfica debería hacer.") -> str:
    """
    Envía el log a Gemini y devuelve un análisis o respuesta a la consulta.
    """
    info = get_vehicle_info()
    api_key = info.get("gemini_api_key")
    
    if not api_key:
        return "⚠️ Configura tu Gemini API Key en la pestaña de Ajustes para activar el asistente IA."

    try:
        genai.configure(api_key=api_key)
        # Usamos el modelo insignia Gemini 3.1 Pro para el máximo nivel de razonamiento
        model = genai.GenerativeModel('gemini-3.1-pro')
        
        # Resumen del log para no saturar el contexto si es muy largo
        # Tomamos una muestra representativa o los estadísticos
        stats = df.describe().to_string()
        sample = df.head(20).to_string()
        tail = df.tail(20).to_string()
        
        vehicle_context = f"Coche: Golf IV 1.9 TDI (Motor ALH), Color: Deep Blue Pearl, KM: {info.get('current_mileage', '280000')}"
        
        prompt = f"""
        Eres un experto mecánico especializado en motores Volkswagen TDI (especialmente el 1.9 ALH).
        Datos del vehículo: {vehicle_context}
        
        Tengo un log de VCDS con las siguientes columnas: {', '.join(df.columns)}
        
        Estadísticas del log:
        {stats}
        
        Muestra de datos (inicio):
        {sample}
        
        Muestra de datos (final):
        {tail}
        
        Consulta del usuario: {user_query}
        
        Responde de forma profesional pero cercana, como un mecánico que conoce bien estos motores. 
        Si el usuario te pide una gráfica, sugiere qué columnas cruzar.
        Si ves problemas de turbo (overboost/limp mode) o MAF basándote en los números, coméntalo.
        """
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"❌ Error al contactar con la IA: {str(e)}"
