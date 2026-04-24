from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


EXPECTED_COLUMNS = {"rpm", "maf_actual", "maf_requested", "map_actual", "coolant_temp"}


@dataclass
class AnalysisResult:
    alerts: list[str]
    metrics: dict[str, float]


def analyze_log(df: pd.DataFrame) -> AnalysisResult:
    normalized = {col.lower().strip(): col for col in df.columns}
    missing = [col for col in EXPECTED_COLUMNS if col not in normalized]
    if missing:
        return AnalysisResult(
            alerts=[
                "Faltan columnas en el log: "
                + ", ".join(sorted(missing))
                + ". Columnas esperadas: rpm, maf_actual, maf_requested, map_actual, coolant_temp."
            ],
            metrics={},
        )

    data = pd.DataFrame(
        {
            "rpm": pd.to_numeric(df[normalized["rpm"]], errors="coerce"),
            "maf_actual": pd.to_numeric(df[normalized["maf_actual"]], errors="coerce"),
            "maf_requested": pd.to_numeric(df[normalized["maf_requested"]], errors="coerce"),
            "map_actual": pd.to_numeric(df[normalized["map_actual"]], errors="coerce"),
            "coolant_temp": pd.to_numeric(df[normalized["coolant_temp"]], errors="coerce"),
        }
    ).dropna()

    if data.empty:
        return AnalysisResult(
            alerts=["El log no contiene datos numericos validos tras limpiar valores vacios."],
            metrics={},
        )

    maf_diff_pct = ((data["maf_requested"] - data["maf_actual"]) / data["maf_requested"]).clip(
        lower=-2, upper=2
    )
    map_peak = data["map_actual"].max()
    coolant_peak = data["coolant_temp"].max()
    rpm_peak = data["rpm"].max()

    alerts: list[str] = []
    if maf_diff_pct.mean() > 0.15:
        alerts.append(
            "MAF por debajo de lo solicitado de forma sostenida (>15%). Revisar caudalimetro, admision o fugas."
        )
    if coolant_peak > 100:
        alerts.append("Temperatura refrigerante alta (>100C). Revisar termostato, radiador o ventiladores.")
    if map_peak > 2600:
        alerts.append("Pico de MAP alto (>2600 mbar). Posible overboost o control N75 a revisar.")
    if not alerts:
        alerts.append("Sin alertas criticas en este log.")

    metrics = {
        "maf_error_pct_mean": float(maf_diff_pct.mean() * 100),
        "maf_actual_mean": float(data["maf_actual"].mean()),
        "maf_requested_mean": float(data["maf_requested"].mean()),
        "map_peak_mbar": float(map_peak),
        "coolant_peak_c": float(coolant_peak),
        "rpm_peak": float(rpm_peak),
    }
    return AnalysisResult(alerts=alerts, metrics=metrics)
