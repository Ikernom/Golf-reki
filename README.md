# ALH Care

App para llevar al dia el mantenimiento de un Golf IV 1.9 TDI ALH, registrar costes y analizar logs CSV de funcionamiento.

## Funcionalidades

- Registro de mantenimientos (fecha, km, categoria, descripcion, coste, notas).
- Historial completo con grafica de coste mensual.
- Subida de logs CSV y analisis basico (MAF, MAP, temperatura, RPM).
- Alertas automaticas de condiciones anormales.
- Base para crecer con recordatorios, comparativas y OBD-II.

## Requisitos

- Python 3.11+ (probado con 3.14)

## Instalacion con entorno virtual

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## Ejecucion

```bash
source .venv/bin/activate
streamlit run app.py
```

Se abrira en el navegador (normalmente `http://localhost:8501`).

## Formato recomendado de logs CSV

El analizador espera estas columnas (minusculas, separadas por coma):

- `rpm`
- `maf_actual`
- `maf_requested`
- `map_actual`
- `coolant_temp`

## Git

Inicializar repo:

```bash
git init
git add .
git commit -m "Initial ALH Care app"
```

Subir a GitHub (ejemplo):

```bash
git remote add origin <URL_DEL_REPO>
git branch -M main
git push -u origin main
```
