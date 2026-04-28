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
    Lector avanzado para logs multicanal de VCDS.
    Busca los marcadores de grupo y mapea por posición.
    """
    import io
    import numpy as np
    
    content = uploaded_file.getvalue().decode("utf-8", errors="ignore").splitlines()
    separator = ";" if any(";" in line for line in content[:10]) else ","
    
    try:
        # Leer todo sin cabeceras para analizar la estructura
        raw_df = pd.read_csv(io.StringIO("\n".join(content)), sep=separator, header=None, on_bad_lines='skip')
        
        # Diccionario para los nuevos datos
        extracted = {}
        
        # 1. Buscar el bloque 011 (Turbo)
        # Normalmente: [Col con '011'] -> [RPM] -> [MAP Spec] -> [MAP Actual] -> [N75]
        for col in raw_df.columns:
            matches = raw_df[raw_df[col].astype(str).str.contains('011', na=False)]
            if not matches.empty:
                idx = matches.index[0]
                extracted["rpm"] = pd.to_numeric(raw_df.iloc[idx+2:, col], errors='coerce')
                extracted["map_actual"] = pd.to_numeric(raw_df.iloc[idx+2:, col+2], errors='coerce')
                break
        
        # 2. Buscar el bloque 003 (MAF)
        # Normalmente: [Col con '003'] -> [RPM] -> [MAF Spec] -> [MAF Actual] -> [EGR]
        for col in raw_df.columns:
            matches = raw_df[raw_df[col].astype(str).str.contains('003', na=False)]
            if not matches.empty:
                idx = matches.index[0]
                if "rpm" not in extracted: # Por si no estaba el 011
                    extracted["rpm"] = pd.to_numeric(raw_df.iloc[idx+2:, col], errors='coerce')
                extracted["maf_requested"] = pd.to_numeric(raw_df.iloc[idx+2:, col+1], errors='coerce')
                extracted["maf_actual"] = pd.to_numeric(raw_df.iloc[idx+2:, col+2], errors='coerce')
                break
                
        # 3. Buscar Temperatura (Bloque 001 o 007 habitualmente)
        # Buscamos la palabra 'Temperature' en cualquier parte de las primeras filas
        for col in raw_df.columns:
            header_sample = raw_df.iloc[:10, col].astype(str).str.upper()
            if any("TEMP" in s for s in header_sample):
                extracted["coolant_temp"] = pd.to_numeric(raw_df.iloc[2:, col], errors='coerce')
                break

        if not extracted:
            return "No he podido encontrar los bloques 003 o 011 en el archivo."
            
        final_df = pd.DataFrame(extracted).dropna(subset=['rpm']).reset_index(drop=True)
        
        # Si falta la temperatura, ponemos 90 por defecto para no romper el análisis
        if "coolant_temp" not in final_df:
            final_df["coolant_temp"] = 90.0
            
        return final_df

    except Exception as e:
        return f"Error crítico al parsear el log: {str(e)}"


def analyze_log(df: pd.DataFrame) -> AnalysisResult:
    # Como el nuevo clean_vcds_log ya devuelve las columnas normalizadas, 
    # el análisis es directo.
    data = df.copy()

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
