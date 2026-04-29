# 🏎️ Golf-reki ALH Care 🛠️

**Golf-reki ALH Care** es una plataforma integral de gestión y diagnóstico diseñada específicamente para entusiastas del Volkswagen Golf MK4 (motor 1.9 TDI ALH). Combina la potencia de la Inteligencia Artificial con una interfaz inmersiva inspirada en el icónico cuadro de instrumentos *Indigo & Red*.

![Estilo MK4](https://img.shields.io/badge/UI-Retro_MK4_Indigo-blue?style=for-the-badge&logo=volkswagen)
![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)

---

## 🌟 Características Principales

### 🧠 Diagnóstico Inteligente (Mecánico Virtual)
- **Análisis de Logs VCDS**: Sube tus archivos `.csv` de telemetría y deja que **Gemini AI** analice el estado del turbo, el caudalímetro (MAF) y la inyección.
- **Detección Automática de Fallos**: El sistema identifica condiciones críticas y sugiere reparaciones.
- **Chat Interactivo**: Pregunta directamente a la IA sobre el comportamiento de tu motor (ej: "¿Por qué entra en limp mode?").

### 🔧 Gestión de Mantenimiento Avanzada
- **Registro de Intervenciones**: Control total sobre reparaciones, mantenimiento preventivo y costes.
- **Categorización Dinámica**: Crea tus propias categorías (Fluidos, Frenos, Mod, etc.) directamente desde la app.
- **Filtros y Ordenación**: Organiza tus registros por fecha, kilometraje o inversión.

### 📅 Plan de Futuro (Roadmap/Wishlist)
- **Pestaña de Proyectos**: Planifica tus futuras modificaciones y mejoras.
- **Priorización**: Clasifica tus ideas por urgencia (Alta, Media, Baja) y estima los costes para gestionar tu presupuesto.

### 📊 Análisis de Inversión
- **Gráficos Interactivos**: Visualiza el gasto acumulado en el tiempo con puntos interactivos para cada modificación.
- **Métricas del Dashboard**: Kilometraje actual, estado del aceite y total invertido de un solo vistazo.

---

## 🎨 Interfaz Inmersiva "Indigo & Red"
La aplicación ha sido rediseñada para replicar la atmósfera nocturna del **Golf MK4**:
- **Títulos Azul Índigo**: Resplandor neón idéntico a los relojes del cuadro.
- **Bordes Rojo Aguja**: Recuadros y alertas inspirados en las agujas y testigos del salpicadero.
- **Modo Oscuro Absoluto**: Optimizado para una visualización sin distracciones.

---

## 🛠️ Instalación y Configuración

### 1. Clonar y preparar entorno
```bash
# Clonar el repositorio
git clone <URL_DEL_REPO>
cd Golf-reki

# Crear y activar entorno virtual
python3 -m venv .venv
source .venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### 2. Configuración de IA
Para usar el Mecánico Virtual, necesitas una API Key de Google Gemini (gratuita):
1. Consíguela en [Google AI Studio](https://aistudio.google.com/).
2. Introdúcela en la sección de **⚙️ Configuración** dentro de la app.

---

## 🚀 Ejecución

```bash
streamlit run app.py
```
La aplicación se abrirá automáticamente en tu navegador (por defecto en `http://localhost:8501`).

---

## 📁 Estructura del Proyecto
- `app.py`: Núcleo de la interfaz y lógica de navegación.
- `src/maintenance.py`: Gestión de base de datos y CRUD de mantenimiento/roadmap.
- `src/ai_assistant.py`: Integración con Gemini para análisis de logs.
- `src/styles.py`: Motor de estilos CSS con temática MK4.
- `src/db.py`: Esquema de la base de datos SQLite3.

---

**Desarrollado para amantes del TDI • ALH Care v3.5 • Indigo Edition** 🏎️💨
