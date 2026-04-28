from __future__ import annotations

from dataclasses import dataclass, field
import io
import re

import pandas as pd


@dataclass
class GroupData:
    """Datos de un grupo individual de VCDS."""
    group_id: str          # ej: "011"
    group_label: str       # ej: "Group A"
    column_names: list[str]
    units: list[str]
    data: pd.DataFrame


@dataclass
class AnalysisResult:
    alerts: list[str]
    metrics: dict[str, float]
    groups: list[GroupData] = field(default_factory=list)
    data: pd.DataFrame | None = None


def clean_vcds_log(uploaded_file) -> list[GroupData] | str:
    """
    Parser avanzado para logs de VCDS multicanal.
    Detecta cada bloque 'Group X:' y extrae sus columnas y datos por separado.
    Devuelve una lista de GroupData, uno por cada grupo encontrado.
    """
    content = uploaded_file.getvalue().decode("utf-8", errors="ignore").splitlines()
    if not content:
        return "El archivo está vacío."

    separator = ";" if any(";" in line for line in content[:10]) else ","

    groups: list[GroupData] = []

    # 1. Localizar todas las líneas que empiezan con "Group X:"
    group_starts: list[tuple[int, str, str, list[str]]] = []  # (line_idx, label, group_id, col_names)

    for i, line in enumerate(content):
        # Detectar líneas como: "Group A:,011,Boost Pressure (Specified),..."
        # o "Group A:;011;Boost Pressure (Specified);..."
        parts = [p.strip().strip("'\"") for p in re.split(r'[,;]', line)]
        if parts and re.match(r'Group\s+[A-Z]:', parts[0], re.IGNORECASE):
            label = parts[0].rstrip(":")   # "Group A"
            group_id = parts[1] if len(parts) > 1 else "???"
            col_names = parts[2:] if len(parts) > 2 else []
            # Filtrar columnas vacías
            col_names = [c for c in col_names if c]
            group_starts.append((i, label, group_id, col_names))

    # Si no encontramos formato de grupos, intentar lectura plana como fallback
    if not group_starts:
        return _fallback_flat_read(content, separator)

    # 2. Para cada grupo, extraer la fila de unidades y los datos
    for idx, (line_idx, label, group_id, col_names) in enumerate(group_starts):
        # Determinar dónde terminan los datos de este grupo
        # (siguiente grupo o fin del archivo)
        if idx + 1 < len(group_starts):
            end_idx = group_starts[idx + 1][0]
        else:
            end_idx = len(content)

        # La línea siguiente al grupo suele ser la de unidades
        # Luego "Marker,Time Stamp,..." o directamente datos numéricos
        block_lines = content[line_idx + 1 : end_idx]
        if not block_lines:
            continue

        # Intentar detectar la fila de unidades (suele tener solo texto corto como "mbar", "/min", "%")
        units_line = block_lines[0]
        units_parts = [p.strip().strip("'\"") for p in re.split(r'[,;]', units_line)]
        # Heurística: si la mayoría de los campos tienen letras o /, es una fila de unidades
        non_empty = [u for u in units_parts if u]
        is_units = len(non_empty) > 0 and sum(1 for u in non_empty if any(c.isalpha() or c == '/' for c in u)) > len(non_empty) * 0.5

        if is_units:
            units = units_parts[2:]  # Saltar Marker y Time Stamp
            data_lines = block_lines[1:]
        else:
            units = [""] * len(col_names)
            data_lines = block_lines

        # Construir los nombres completos de las columnas: "Boost Pressure (Specified) [mbar]"
        full_col_names = []
        for j, name in enumerate(col_names):
            unit = units[j] if j < len(units) and units[j] else ""
            if unit:
                full_col_names.append(f"{name} [{unit}]")
            else:
                full_col_names.append(name)

        # 3. Parsear las filas de datos
        all_cols = ["Marker", "Time Stamp"] + full_col_names
        rows = []
        for dl in data_lines:
            parts = [p.strip().strip("'\"") for p in re.split(r'[,;]', dl)]
            if not parts or not parts[0]:
                continue
            # Verificar que la primera columna (Marker) es numérica o vacía
            try:
                float(parts[0])
            except ValueError:
                # Puede ser la cabecera "Marker,Time Stamp,..." -> saltar
                if "MARKER" in parts[0].upper() or "TIME" in parts[0].upper():
                    continue
                continue
            rows.append(parts[:len(all_cols)])

        if not rows:
            continue

        df = pd.DataFrame(rows, columns=all_cols[:len(rows[0])])
        # Convertir a numérico
        for col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        groups.append(GroupData(
            group_id=group_id,
            group_label=label,
            column_names=full_col_names,
            units=units,
            data=df
        ))

    if not groups:
        return "No se han podido extraer datos de los grupos del log."

    return groups


def _fallback_flat_read(content: list[str], separator: str) -> list[GroupData] | str:
    """Lectura plana para CSVs simples que no tengan formato de grupos VCDS."""
    try:
        # Buscar dónde empiezan los datos
        header_idx = 0
        for i, line in enumerate(content[:20]):
            up = line.upper()
            if "RPM" in up or "TIME" in up or "STAMP" in up or "MARKER" in up:
                header_idx = i
                break

        df = pd.read_csv(io.StringIO("\n".join(content[header_idx:])), sep=separator, on_bad_lines='skip')

        # Limpiar fila de unidades si la primera fila tiene texto
        if not df.empty:
            first_val = str(df.iloc[0, 0])
            if any(c.isalpha() for c in first_val) and len(df) > 1:
                df = df.iloc[1:].reset_index(drop=True)

        df.columns = [str(c).replace("'", "").replace('"', '').strip() for c in df.columns]

        for col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        return [GroupData(
            group_id="---",
            group_label="Datos",
            column_names=list(df.columns),
            units=[],
            data=df
        )]
    except Exception as e:
        return f"Error al procesar el CSV: {str(e)}"


def analyze_groups(groups: list[GroupData]) -> AnalysisResult:
    """
    Analiza los grupos extraídos. Si detecta grupos conocidos (011, 003),
    realiza análisis específico ALH. Si no, devuelve los datos tal cual.
    """
    alerts: list[str] = []
    metrics: dict[str, float] = {}

    # Buscar grupos conocidos del motor ALH
    group_map = {g.group_id: g for g in groups}

    # Grupo 011 - Turbo
    g011 = group_map.get("011")
    if g011 is not None and not g011.data.empty:
        df = g011.data
        # Las columnas de datos (sin Marker y Time Stamp) típicamente son:
        # Boost Specified, Boost Actual, Engine Speed, Charge Pressure Dev
        data_cols = [c for c in df.columns if c not in ("Marker", "Time Stamp")]
        if len(data_cols) >= 2:
            boost_spec = df[data_cols[0]]
            boost_actual = df[data_cols[1]]
            peak_boost = boost_actual.max()
            metrics["map_peak_mbar"] = float(peak_boost) if pd.notna(peak_boost) else 0

            if peak_boost > 2350:
                alerts.append("⚠️ **Overboost detectado** en Grupo 011: Presión de turbo superior a 2350 mbar.")
        if len(data_cols) >= 3:
            rpm_col = df[data_cols[2]]
            rpm_peak = rpm_col.max()
            metrics["rpm_peak"] = float(rpm_peak) if pd.notna(rpm_peak) else 0

    # Grupo 003 - MAF
    g003 = group_map.get("003")
    if g003 is not None and not g003.data.empty:
        df = g003.data
        data_cols = [c for c in df.columns if c not in ("Marker", "Time Stamp")]
        if len(data_cols) >= 2:
            maf_spec = df[data_cols[0]]
            maf_actual = df[data_cols[1]]
            maf_diff = ((maf_spec - maf_actual) / maf_spec).mean()
            metrics["maf_error_pct_mean"] = float(maf_diff * 100) if pd.notna(maf_diff) else 0

            if maf_diff > 0.15:
                alerts.append("⚠️ **MAF bajo** en Grupo 003: El caudalímetro mide un {:.0f}% menos de lo solicitado.".format(maf_diff * 100))

    # Grupo 008 - Inyección
    g008 = group_map.get("008")
    if g008 is not None and not g008.data.empty:
        alerts.append("📊 Grupo 008 (Inyección/Torque) detectado con {} muestras.".format(len(g008.data)))

    if not alerts:
        alerts.append("✅ Todos los parámetros dentro de rangos normales para un ALH.")

    # Health Score
    warning_count = sum(1 for a in alerts if "⚠️" in a or "🚨" in a)
    metrics["score"] = max(0, 100 - (warning_count * 25))

    return AnalysisResult(
        alerts=alerts,
        metrics=metrics,
        groups=groups,
        data=None
    )
