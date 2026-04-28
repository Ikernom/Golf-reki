from __future__ import annotations

from dataclasses import dataclass, field
import io
import re

import pandas as pd


@dataclass
class GroupData:
    group_id: str
    group_label: str
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
    Parser para logs VCDS multicanal horizontales.
    Los grupos van lado a lado: Group A (011) | Group B (003) | Group C (008)
    """
    raw = uploaded_file.getvalue().decode("utf-8", errors="ignore")
    lines = raw.splitlines()
    if not lines:
        return "El archivo está vacío."

    sep = ";" if any(";" in l for l in lines[:5]) else ","

    # 1. Parsear todas las líneas del header (primeras 30)
    header_parts = []
    for i, line in enumerate(lines[:30]):
        header_parts.append([p.strip().strip("'\"") for p in line.split(sep)])

    # 2. Encontrar filas clave
    group_row_idx = -1
    marker_row_idx = -1
    for i, parts in enumerate(header_parts):
        if any(re.match(r'Group\s+[A-Z]', p, re.I) for p in parts):
            group_row_idx = i
        if any(p.upper() in ('MARKER', 'MARK') for p in parts):
            marker_row_idx = i
            break

    if marker_row_idx == -1:
        # Buscar primera fila con datos numéricos
        for i, line in enumerate(lines):
            parts = [p.strip() for p in line.split(sep)]
            if parts and re.match(r'^\d+$', parts[0]):
                marker_row_idx = i - 1
                break

    if marker_row_idx == -1:
        return "No se pudo encontrar el inicio de los datos."

    # 3. Extraer IDs de grupo y posiciones
    group_ids = []
    group_col_positions = []
    if group_row_idx >= 0:
        gparts = header_parts[group_row_idx]
        for j, p in enumerate(gparts):
            if re.match(r'^\d{2,3}$', p):
                group_ids.append(p.zfill(3))
                group_col_positions.append(j)

    # 4. Extraer filas descriptivas (entre group_row y marker_row)
    desc_rows = []
    start_desc = (group_row_idx + 1) if group_row_idx >= 0 else 0
    for r in range(start_desc, marker_row_idx):
        if r < len(header_parts):
            desc_rows.append(header_parts[r])

    # 5. Leer los datos desde marker_row
    data_text = "\n".join(lines[marker_row_idx:])
    df = pd.read_csv(io.StringIO(data_text), sep=sep, on_bad_lines='skip')

    # Quitar fila de unidades si la primera fila tiene texto
    if not df.empty:
        first = str(df.iloc[0, 1]) if len(df.columns) > 1 else str(df.iloc[0, 0])
        if any(c.isalpha() for c in first):
            df = df.iloc[1:].reset_index(drop=True)

    # Convertir a numérico
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # 6. Detectar grupos por columnas TIME repetidas
    cols = list(df.columns)
    time_indices = [i for i, c in enumerate(cols) if 'TIME' in str(c).upper()]

    if not time_indices:
        # Sin TIME -> un solo grupo con todo
        df_clean = df.dropna(how='all', axis=1).dropna(how='all')
        return [GroupData("---", "Datos", list(df_clean.columns), [], df_clean)]

    # 7. Dividir columnas en grupos
    groups: list[GroupData] = []
    for g_idx, t_start in enumerate(time_indices):
        # Fin del grupo: siguiente TIME o fin de columnas
        if g_idx + 1 < len(time_indices):
            t_end = time_indices[g_idx + 1]
            # Quitar columnas Unnamed separadoras
            while t_end > t_start and 'unnamed' in str(cols[t_end - 1]).lower():
                t_end -= 1
        else:
            t_end = len(cols)
            while t_end > t_start and 'unnamed' in str(cols[t_end - 1]).lower():
                t_end -= 1

        group_cols = cols[t_start:t_end]
        group_df = df[group_cols].copy().dropna(how='all')

        # Renombrar TIME.1 -> TIME, (G28).1 -> (G28)
        rename = {}
        for c in group_cols:
            base = re.sub(r'\.\d+$', '', c)
            if base != c:
                rename[c] = base
        group_df = group_df.rename(columns=rename)

        # Construir nombres descriptivos desde las filas de cabecera
        final_names = list(group_df.columns)
        if desc_rows and group_col_positions and g_idx < len(group_col_positions):
            gpos = group_col_positions[g_idx]
            for col_i, col_name in enumerate(final_names):
                abs_pos = t_start + col_i
                combined = []
                for dr in desc_rows:
                    if abs_pos < len(dr) and dr[abs_pos]:
                        combined.append(dr[abs_pos])
                if combined:
                    full_name = " ".join(combined)
                    final_names[col_i] = full_name

        # Aplicar nombres descriptivos
        group_df.columns = final_names

        gid = group_ids[g_idx] if g_idx < len(group_ids) else f"{g_idx + 1:03d}"
        label = f"Group {chr(65 + g_idx)}"

        groups.append(GroupData(
            group_id=gid,
            group_label=label,
            column_names=final_names,
            units=[],
            data=group_df
        ))

    return groups if groups else "No se pudieron extraer datos."


def analyze_groups(groups: list[GroupData]) -> AnalysisResult:
    alerts: list[str] = []
    metrics: dict[str, float] = {}

    group_map = {g.group_id: g for g in groups}

    # Grupo 011 - Turbo
    g011 = group_map.get("011")
    if g011 is not None and not g011.data.empty:
        data_cols = [c for c in g011.data.columns if 'TIME' not in c.upper()]
        if len(data_cols) >= 2:
            peak = g011.data[data_cols[1]].max()
            metrics["map_peak_mbar"] = float(peak) if pd.notna(peak) else 0
            if peak > 2350:
                alerts.append("⚠️ **Overboost** en Grupo 011: Presión > 2350 mbar.")

    # Grupo 003 - MAF
    g003 = group_map.get("003")
    if g003 is not None and not g003.data.empty:
        data_cols = [c for c in g003.data.columns if 'TIME' not in c.upper()]
        if len(data_cols) >= 2:
            spec = g003.data[data_cols[0]]
            actual = g003.data[data_cols[1]]
            diff = ((spec - actual) / spec).mean()
            metrics["maf_error_pct_mean"] = float(diff * 100) if pd.notna(diff) else 0
            if diff > 0.15:
                alerts.append(f"⚠️ **MAF bajo** en Grupo 003: {diff*100:.0f}% menos de lo solicitado.")

    if not alerts:
        alerts.append("✅ Todos los parámetros dentro de rangos normales para un ALH.")

    warning_count = sum(1 for a in alerts if "⚠️" in a or "🚨" in a)
    metrics["score"] = max(0, 100 - (warning_count * 25))

    return AnalysisResult(alerts=alerts, metrics=metrics, groups=groups)
