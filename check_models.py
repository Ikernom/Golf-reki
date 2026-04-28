import google.generativeai as genai
import sqlite3

def get_api_key():
    try:
        conn = sqlite3.connect('data/maintenance.db')
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM vehicle_info WHERE key='gemini_api_key' LIMIT 1")
        res = cursor.fetchone()
        conn.close()
        return res[0] if res else None
    except:
        return None

api_key = get_api_key()
if not api_key:
    print("API Key no encontrada")
else:
    genai.configure(api_key=api_key)
    try:
        models = genai.list_models()
        for m in models:
            if 'generateContent' in m.supported_generation_methods:
                print(f"Name: {m.name}, Display: {m.display_name}")
    except Exception as e:
        print(f"Error: {e}")
