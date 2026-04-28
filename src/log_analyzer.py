from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


EXPECTED_COLUMNS = {"rpm", "maf_actual", "maf_requested", "map_actual", "coolant_temp"}


@dataclass
class AnalysisResult:
    alerts: list[str]
    metrics: dict[str, float]
    data: pd.DataFrame | None = None


def clean_vcds_log(uploaded_file) -> pd.DataFrame | str:
    """
    Lector universal para VCDS. Intenta extraer todos los canales disponibles.
    """
    import io
    import numpy as np
    
    content = uploaded_file.getvalue().decode("utf-8", errors="ignore").splitlines()
    if not content: return "El archivo está vacío."
    
    separator = ";" if any(";" in line for line in content[:10]) else ","
    
    try:
        # 1. Encontrar la línea de cabecera real (donde hay más texto/nombres de grupos)
        header_idx = -1
        for i, line in enumerate(content[:20]):
            up = line.upper()
            if "GROUP" in up or "RPM" in up or "TIME" in up or "STAMP" in up:
                header_idx = i
                break
        
        if header_idx == -1: header_idx = 0

        # 2. Leer desde esa línea
        df = pd.read_csv(io.StringIO("\n".join(content[header_idx:])), sep=separator, on_bad_lines='skip')
        
        # 3. Limpiar fila de unidades si existe
        if not df.empty:
            # Si la primera fila de datos tiene letras donde debería haber números, la quitamos
            first_val = str(df.iloc[0, 0])
            if any(c.isalpha() for c in first_val) and len(df) > 1:
                df = df.iloc[1:].reset_index(drop=True)

        # 4. Limpieza de nombres de columnas (quitar comillas, espacios y puntos)
        df.columns = [str(c).replace("'", "").replace('"', '').strip() for c in df.columns]
        
        # 5. Intentar identificar columnas para el análisis ALH
        # Creamos un mapeo interno para que analyze_log sepa qué es qué
        col_map = {}
        norm_cols = {c.upper(): c for c in df.columns}
        
        mapping = {
            "rpm": ["RPM", "ENGINE SPEED", "/MIN"],
            "maf_actual": ["MAF (ACTUAL)", "AIR FLOW (ACTUAL)", "MASS AIR"],
            "maf_requested": ["MAF (SPECIFIED)", "MAF (SPEC", "SPECIFIED"],
            "map_actual": ["MAP (ACTUAL)", "BOOST PRESSURE (ACTUAL)", "PRESSURE", "MAP"],
            "coolant_temp": ["COOLANT", "TEMP", "G62", "TEMPERATURE"]
        }

        for target, alts in mapping.items():
            for alt in alts:
                for norm_name, real_name in norm_cols.items():
                    if alt in norm_name:
                        col_map[target] = real_name
                        break
                if target in col_map: break
        
        # Guardamos el mapa de columnas en los metadatos del DF
        df.attrs["col_map"] = col_map
        return df

    except Exception as e:
        import traceback
        return f"Error al procesar el CSV: {str(e)}\n{traceback.format_exc()}"


def analyze_log(df: pd.DataFrame) -> AnalysisResult:
    if df.empty:
        return AnalysisResult(alerts=["El log está vacío."], metrics={}, data=None)

    col_map = df.attrs.get("col_map", {})
    
    # Intentar convertir todo a numérico
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    df = df.dropna(how='all').reset_index(drop=True)

    # Si faltan columnas básicas de motor, hacemos análisis genérico
    essential = ["rpm", "map_actual", "maf_actual"]
    is_motor_log = all(k in col_map for k in essential)

    if not is_motor_log:
        return AnalysisResult(
            alerts=["📊 Log genérico detectado. Mostrando datos sin análisis de motor específico."],
            metrics={"column_count": len(df.columns)},
            data=df
        )

    # Análisis específico ALH (si tenemos los datos necesarios)
    data = pd.DataFrame()
    data["rpm"] = df[col_map["rpm"]]
    data["map_actual"] = df[col_map["map_actual"]]
    data["maf_actual"] = df[col_map["maf_actual"]]
    
    # Columnas opcionales
    data["maf_requested"] = df[col_map["maf_requested"]] if "maf_requested" in col_map else data["maf_actual"]
    data["coolant_temp"] = df[col_map["coolant_temp"]] if "coolant_temp" in col_map else 90.0

    maf_diff_pct = ((data["maf_requested"] - data["maf_actual"]) / data["maf_requested"])
    map_peak = data["map_actual"].max()
    coolant_peak = data["coolant_temp"].max()
    rpm_peak = data["rpm"].max()

    alerts: list[str] = []
    
    if maf_diff_pct.mean() > 0.15:
        alerts.append("⚠️ MAF bajo: El caudalímetro mide menos de lo esperado.")
    if map_peak > 2350:
        alerts.append("⚠️ Overboost: Presión de turbo muy alta.")
    if rpm_peak > 3000 and data["map_actual"].max() < 1500:
        alerts.append("🚨 Limp Mode detectado.")
    if not alerts:
        alerts.append("✅ Parámetros de motor OK.")

    metrics = {
        "maf_error_pct_mean": float(maf_diff_pct.mean() * 100),
        "map_peak_mbar": float(map_peak),
        "coolant_peak_c": float(coolant_peak),
        "rpm_peak": float(rpm_peak),
        "score": max(0, 100 - (len(alerts) * 20))
    }
    
    return AnalysisResult(alerts=alerts, metrics=metrics, data=data)

    if data.empty:
        return AnalysisResult(
            alerts=["El log no contiene datos numericos validos tras limpiar valores vacios."],
            metrics={},
            data=None,
        )

    maf_diff_pct = ((data["maf_requested"] - data["maf_actual"]) / data["maf_requested"])
    map_peak = data["map_actual"].max()
    coolant_peak = data["coolant_temp"].max()
    rpm_peak = data["rpm"].max()

    alerts: list[str] = []
    
    # 1. MAF Health
    if maf_diff_pct.mean() > 0.20:
        alerts.append("⚠️ MAF muy bajo: El caudalímetro mide un 20% menos de lo solicitado. Posible fallo de MAF o fuga en admisión.")
    elif maf_diff_pct.mean() > 0.10:
        alerts.append("ℹ️ MAF algo perezoso: Lecturas ligeramente bajas. Limpiar caudalímetro podría ayudar.")

    # 2. Turbo Overshoot (ALH específico)
    # Buscamos si hay picos que superan por mucho la media cuando el acelerador está a fondo
    if map_peak > 2350:
        alerts.append("⚠️ Overboost detectado: Presión superior a 2.3 bar. ¡Cuidado con la culata! Revisar geometría del turbo o N75.")
    
    # 3. Limp Mode / Underboost
    if rpm_peak > 3000 and data["map_actual"].max() < 1500:
        alerts.append("🚨 Posible Limp Mode: El turbo no sopla a pesar de las altas RPM. El coche ha entrado en modo protección.")

    # 4. Temperatura
    if coolant_peak > 98:
        alerts.append("🔥 Temperatura crítica: Has superado los 98°C. Revisa el sensor G62 o el termostato.")
    elif coolant_peak < 75 and rpm_peak > 2500:
        alerts.append("❄️ Motor frío: Estás dándole carga con el motor por debajo de 75°C. No es recomendable para el turbo.")

    if not alerts:
        alerts.append("✅ Log impecable: Los parámetros están dentro de los rangos óptimos para un ALH.")

    metrics = {
        "maf_error_pct_mean": float(maf_diff_pct.mean() * 100),
        "map_peak_mbar": float(map_peak),
        "coolant_peak_c": float(coolant_peak),
        "rpm_peak": float(rpm_peak),
        "score": max(0, 100 - (len(alerts) * 15)) if "Log impecable" not in alerts[0] else 100
    }
    return AnalysisResult(alerts=alerts, metrics=metrics, data=data)
