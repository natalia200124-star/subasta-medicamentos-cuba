import streamlit as st
import pandas as pd
from streamlit_autorefresh import st_autorefresh
import base64
from datetime import datetime

# ==============================
# CONFIGURACIÓN PRINCIPAL
# ==============================
st.set_page_config(
    page_title="Subasta Solidaria - Medicamentos para Cuba",
    page_icon="💊",
    layout="wide"
)

st_autorefresh(interval=2000, key="autorefresh")

# ==============================
# LINKS CSV
# ==============================
CSV_DONACIONES = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT2zRpYc-c3ZznxlPo51_k-5W3mNMzsxl8zlUzxCtugfc2ONIK_C-ht1DzKCR6vy2f1YSnwBx8umQxs/pub?gid=1533440022&single=true&output=csv"
CSV_METAS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT2zRpYc-c3ZznxlPo51_k-5W3mNMzsxl8zlUzxCtugfc2ONIK_C-ht1DzKCR6vy2f1YSnwBx8umQxs/pub?gid=199575778&single=true&output=csv"

# ==============================
# ESTILO PROYECTOR PREMIUM (UNA SOLA VISTA)
# ==============================
st.markdown("""
<style>

html, body, [class*="css"]  {
    background: #f2f2f2;
    font-family: Arial, sans-serif;
}

.block-container {
    padding-top: 0.5rem;
    padding-bottom: 0.5rem;
    max-width: 100%;
}

header {visibility: hidden;}
footer {visibility: hidden;}

.top-header {
    width: 100%;
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: white;
    border-radius: 14px;
    padding: 14px 20px;
    box-shadow: 0px 4px 14px rgba(0,0,0,0.10);
    margin-bottom: 14px;
}

.header-left {
    display: flex;
    align-items: center;
    gap: 14px;
}

.logo-box {
    width: 120px;
    height: 70px;
    background: #2b4c8a;
    border-radius: 10px;
    display: flex;
    justify-content: center;
    align-items: center;
    color: white;
    font-weight: 900;
    font-size: 14px;
    text-align: center;
    padding: 8px;
}

.header-title {
    font-size: 30px;
    font-weight: 900;
    color: #1c2f57;
    margin: 0;
}

.header-date {
    font-size: 13px;
    font-weight: 700;
    color: #555;
    margin-top: 4px;
}

.header-right {
    font-size: 30px;
    font-weight: 900;
    color: #d19a00;
}

.summary-row {
    width: 100%;
    display: flex;
    gap: 12px;
    margin-bottom: 12px;
}

.summary-card {
    flex: 1;
    background: white;
    border-radius: 14px;
    padding: 12px 14px;
    box-shadow: 0px 4px 12px rgba(0,0,0,0.10);
    text-align: center;
}

.summary-title {
    font-size: 13px;
    font-weight: 700;
    color: #555;
    margin-bottom: 5px;
}

.summary-value {
    font-size: 38px;
    font-weight: 900;
    color: #1c2f57;
}

.progress-global {
    flex: 2;
    background: white;
    border-radius: 14px;
    padding: 12px 14px;
    box-shadow: 0px 4px 12px rgba(0,0,0,0.10);
}

.progress-title {
    font-size: 13px;
    font-weight: 800;
    color: #555;
    margin-bottom: 8px;
    text-align: center;
}

.progress-bar-outer {
    width: 100%;
    height: 22px;
    background: #d9d9d9;
    border-radius: 14px;
    overflow: hidden;
    border: 1px solid rgba(0,0,0,0.10);
}

.progress-bar-inner {
    height: 100%;
    background: linear-gradient(90deg, #2b4c8a, #1c2f57);
    width: 0%;
    transition: width 0.8s ease-in-out;
}

.progress-label {
    text-align: right;
    font-weight: 900;
    font-size: 14px;
    color: #111;
    margin-top: 4px;
}

.grid-meds {
    width: 100%;
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 12px;
}

.med-card {
    background: white;
    border-radius: 14px;
    padding: 14px;
    box-shadow: 0px 4px 12px rgba(0,0,0,0.10);
    min-height: 440px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}

.med-name {
    font-size: 22px;
    font-weight: 900;
    color: #1c2f57;
    text-align: center;
    margin-bottom: 10px;
}

.med-meta {
    font-size: 14px;
    font-weight: 700;
    color: #333;
    margin-top: 8px;
    text-align: center;
}

.med-progress-outer {
    width: 100%;
    height: 20px;
    background: #d9d9d9;
    border-radius: 12px;
    overflow: hidden;
    margin-top: 8px;
    border: 1px solid rgba(0,0,0,0.10);
}

.med-progress-inner {
    height: 100%;
    background: #2b4c8a;
    width: 0%;
    transition: width 0.8s ease-in-out;
}

.med-percent {
    font-size: 15px;
    font-weight: 900;
    color: #111;
    text-align: right;
    margin-top: 4px;
}

.med-img-box {
    width: 100%;
    height: 160px;
    display: flex;
    justify-content: center;
    align-items: center;
    margin-top: 12px;
}

.med-img-box svg {
    width: 110px;
    height: 150px;
}

.med-status {
    margin-top: 10px;
    text-align: center;
    font-size: 13px;
    font-weight: 800;
    padding: 6px;
    border-radius: 10px;
    background: #f3f3f3;
    border: 1px solid rgba(0,0,0,0.08);
}

</style>
""", unsafe_allow_html=True)

# ==============================
# FUNCIONES
# ==============================
@st.cache_data(ttl=2)
def cargar_datos():
    donaciones = pd.read_csv(CSV_DONACIONES)
    metas = pd.read_csv(CSV_METAS)
    return donaciones, metas

def formatear_numero(x):
    try:
        return f"{int(float(x)):,}".replace(",", ".")
    except:
        return "0"

def obtener_svg_fraco(porcentaje):
    # frasco con "relleno" según porcentaje
    porcentaje = max(0, min(float(porcentaje), 100))
    altura = int(120 * (porcentaje / 100))
    y = 140 - altura

    return f"""
    <svg viewBox="0 0 120 180">
        <rect x="35" y="20" width="50" height="20" rx="5" fill="#cfcfcf" stroke="#777" stroke-width="2"/>
        <rect x="30" y="40" width="60" height="120" rx="18" fill="none" stroke="#1c2f57" stroke-width="4"/>

        <clipPath id="clip">
            <rect x="30" y="40" width="60" height="120" rx="18"/>
        </clipPath>

        <rect x="30" y="{y}" width="60" height="{altura}" fill="#2b4c8a" clip-path="url(#clip)"/>

        <rect x="30" y="40" width="60" height="120" rx="18" fill="none" stroke="#1c2f57" stroke-width="4"/>
    </svg>
    """

# ==============================
# CARGA DE DATOS
# ==============================
try:
    donaciones, metas = cargar_datos()
except:
    st.error("No se pudieron cargar los datos. Revisa los links CSV.")
    st.stop()

donaciones.columns = [c.strip().lower() for c in donaciones.columns]
metas.columns = [c.strip().lower() for c in metas.columns]

# Timestamp
if "timestamp" in donaciones.columns:
    donaciones.rename(columns={"timestamp": "fecha_hora"}, inplace=True)

# Donante público
for col in donaciones.columns:
    if "nombre" in col and "dashboard" in col:
        donaciones.rename(columns={col: "donante_publico"}, inplace=True)

if "donante_publico" not in donaciones.columns:
    donaciones["donante_publico"] = "Anónimo"

donaciones["donante_publico"] = donaciones["donante_publico"].fillna("").astype(str).str.strip()
donaciones.loc[donaciones["donante_publico"] == "", "donante_publico"] = "Anónimo"

# Validación metas
if "medicamento" not in metas.columns or "meta" not in metas.columns:
    st.error("El archivo METAS debe tener columnas: medicamento, meta")
    st.stop()

metas["medicamento"] = metas["medicamento"].astype(str).str.strip()
metas["meta"] = pd.to_numeric(metas["meta"], errors="coerce").fillna(0)

lista_medicamentos = metas["medicamento"].tolist()

# Crear columnas medicamentos si no existen
for med in lista_medicamentos:
    col = med.lower()
    if col not in donaciones.columns:
        donaciones[col] = 0

# Convertir a numérico
for med in lista_medicamentos:
    donaciones[med.lower()] = pd.to_numeric(donaciones[med.lower()], errors="coerce").fillna(0)

# Melt formato largo
donaciones_largo = donaciones.melt(
    id_vars=[c for c in donaciones.columns if c not in [m.lower() for m in lista_medicamentos]],
    value_vars=[m.lower() for m in lista_medicamentos],
    var_name="medicamento",
    value_name="cantidad"
)

donaciones_largo = donaciones_largo[donaciones_largo["cantidad"] > 0]

# Avance completo (incluye medicamentos sin donaciones)
donado_por_med = donaciones_largo.groupby("medicamento", as_index=False)["cantidad"].sum()

metas_temp = metas.copy()
metas_temp["medicamento"] = metas_temp["medicamento"].str.lower()

avance = metas_temp.merge(donado_por_med, on="medicamento", how="left")
avance["cantidad"] = avance["cantidad"].fillna(0)

avance["porcentaje"] = avance.apply(
    lambda r: (r["cantidad"] / r["meta"] * 100) if r["meta"] > 0 else 0,
    axis=1
)

# Global
total_recaudado = avance["cantidad"].sum()
total_meta = avance["meta"].sum()
porcentaje_total = (total_recaudado / total_meta * 100) if total_meta > 0 else 0

# Para mostrar nombres originales
map_nombre_original = dict(zip(metas_temp["medicamento"], metas["medicamento"]))

# Fecha actual
fecha_hoy = datetime.now().strftime("%d de %B de %Y")

# ==============================
# HEADER
# ==============================
st.markdown(f"""
<div class="top-header">
    <div class="header-left">
        <div class="logo-box">
            GENEROSIDAD<br>COLOMBIA<br>2025
        </div>
        <div>
            <div class="header-title">Círculo de Generosidad</div>
            <div class="header-date">{fecha_hoy}</div>
        </div>
    </div>

    <div class="header-right">
        Córdoba nos necesita
    </div>
</div>
""", unsafe_allow_html=True)

# ==============================
# RESUMEN SUPERIOR
# ==============================
porcentaje_total_barra = max(0, min(porcentaje_total, 100))

st.markdown(f"""
<div class="summary-row">

    <div class="summary-card">
        <div class="summary-title">Total meta</div>
        <div class="summary-value">{formatear_numero(total_meta)}</div>
    </div>

    <div class="summary-card">
        <div class="summary-title">Total recolectado</div>
        <div class="summary-value">{formatear_numero(total_recaudado)}</div>
    </div>

    <div class="progress-global">
        <div class="progress-title">Avance global</div>
        <div class="progress-bar-outer">
            <div class="progress-bar-inner" style="width:{porcentaje_total_barra}%;"></div>
        </div>
        <div class="progress-label">{porcentaje_total:.1f}%</div>
    </div>

</div>
""", unsafe_allow_html=True)

# ==============================
# TARJETAS HORIZONTALES (5 COLUMNAS)
# ==============================
st.markdown("<div class='grid-meds'>", unsafe_allow_html=True)

for _, row in avance.iterrows():
    med_key = row["medicamento"]
    nombre_original = map_nombre_original.get(med_key, med_key)

    cantidad = float(row["cantidad"])
    meta = float(row["meta"])
    porcentaje = float(row["porcentaje"])

    porcentaje_barra = max(0, min(porcentaje, 100))

    if porcentaje >= 100:
        estado = "Meta alcanzada"
    elif porcentaje >= 70:
        estado = "Avance alto"
    elif porcentaje >= 40:
        estado = "Avance medio"
    else:
        estado = "Avance bajo"

    svg = obtener_svg_fraco(porcentaje)

    st.markdown(f"""
    <div class="med-card">

        <div class="med-name">{nombre_original}</div>

        <div class="med-img-box">
            {svg}
        </div>

        <div class="med-meta">
            Donado: <b>{formatear_numero(cantidad)}</b><br>
            Meta: <b>{formatear_numero(meta)}</b>
        </div>

        <div class="med-progress-outer">
            <div class="med-progress-inner" style="width:{porcentaje_barra}%;"></div>
        </div>

        <div class="med-percent">{porcentaje:.1f}%</div>

        <div class="med-status">{estado}</div>

    </div>
    """, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)


