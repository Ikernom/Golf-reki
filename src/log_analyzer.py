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
    Limpia un archivo CSV de VCDS saltando encabezados y detectando el separador.
    """
    import io
    
    # Leer el contenido completo para analizarlo
    content = uploaded_file.getvalue().decode("utf-8", errors="ignore").splitlines()
    
    # Buscar la línea donde empiezan los datos (la que tiene 'RPM' o 'Group')
    header_idx = -1
    separator = ","
    
    for i, line in enumerate(content[:20]): # Miramos las primeras 20 líneas
        if "RPM" in line.upper() or "MARKER" in line.upper() or "GROUP" in line.upper():
            header_idx = i
            if ";" in line:
                separator = ";"
            break
            
    if header_idx == -1:
        return "No se ha encontrado el encabezado de datos (RPM, MAF, MAP) en las primeras 20 líneas."

    # Re-leer usando el índice encontrado
    try:
        # Saltamos las líneas de texto y leemos desde el header
        df = pd.read_csv(io.StringIO("\n".join(content[header_idx:])), sep=separator, on_bad_lines='skip')
        
        # VCDS suele poner una segunda línea de unidades (/min, mg/str) que hay que quitar
        # Si la primera fila tiene texto en la columna RPM, la quitamos
        if not df.empty and not str(df.iloc[0, 0]).replace('.','',1).isdigit():
            df = df.iloc[1:].reset_index(drop=True)
            
        return df
    except Exception as e:
        return f"Error al procesar el CSV: {str(e)}"


def analyze_log(df: pd.DataFrame) -> AnalysisResult:
    normalized = {col.lower().strip(): col for col in df.columns}
    
    # Mapeo inteligente de columnas (VCDS usa nombres largos como 'Engine Speed  (G28)')
    mapping = {
        "rpm": ["rpm", "engine speed", "engine speed  (g28)", "/min"],
        "maf_actual": ["maf (actual)", "maf_actual", "mass air flow (actual)", "maf - actual"],
        "maf_requested": ["maf (specified)", "maf_requested", "mass air flow (spec.)", "maf - specified"],
        "map_actual": ["map (actual)", "map_actual", "boost pressure (actual)", "map - actual"],
        "coolant_temp": ["coolant temp", "coolant_temp", "temperature", "coolant temperature (g62)"]
    }
    
    found_cols = {}
    for target, alternates in mapping.items():
        for alt in alternates:
            for norm_col in normalized:
                if alt in norm_col:
                    found_cols[target] = normalized[norm_col]
                    break
            if target in found_cols: break

    missing = [col for col in EXPECTED_COLUMNS if col not in found_cols]
    if missing:
        return AnalysisResult(
            alerts=[
                f"Faltan columnas críticas: {', '.join(missing)}. "
                "Asegúrate de que el log incluya RPM, MAF (Actual/Spec), MAP (Actual) y Temp."
            ],
            metrics={},
            data=None,
        )

    data = pd.DataFrame({
        "rpm": pd.to_numeric(df[found_cols["rpm"]], errors="coerce"),
        "maf_actual": pd.to_numeric(df[found_cols["maf_actual"]], errors="coerce"),
        "maf_requested": pd.to_numeric(df[found_cols["maf_requested"]], errors="coerce"),
        "map_actual": pd.to_numeric(df[found_cols["map_actual"]], errors="coerce"),
        "coolant_temp": pd.to_numeric(df[found_cols["coolant_temp"]], errors="coerce"),
    }).dropna()

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
