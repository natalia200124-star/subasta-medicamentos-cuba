import streamlit as st
import pandas as pd
from streamlit_autorefresh import st_autorefresh
from datetime import datetime
import streamlit.components.v1 as components

# ==============================
# CONFIGURACIÓN PRINCIPAL
# ==============================
st.set_page_config(
    page_title="Subasta Solidaria - Medicamentos para Cuba",
    page_icon="💊",
    layout="wide"
)

# Refresh cada 2 segundos
st_autorefresh(interval=2000, key="autorefresh")

# ==============================
# LINKS CSV
# ==============================
CSV_DONACIONES = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSQ-JoPi55tEnwRnP_SyYy5gawWPJoQaQ0jI4PLgDpA4CcEdKjSb2IFftcc475zBr5Ou34BTrSdZ8v9/pub?gid=1709067163&single=true&output=csv"
CSV_METAS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSQ-JoPi55tEnwRnP_SyYy5gawWPJoQaQ0jI4PLgDpA4CcEdKjSb2IFftcc475zBr5Ou34BTrSdZ8v9/pub?gid=1531001200&single=true&output=csv"


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


def frasco_svg(pct, color="#2b7cff"):
    pct = max(0, min(float(pct), 100))
    altura = int(110 * (pct / 100))
    y = 140 - altura

    return f"""
    <svg viewBox="0 0 120 170">
        <rect x="40" y="15" width="40" height="18" rx="4" fill="#94a3b8"/>
        <rect x="32" y="33" width="56" height="120" rx="18" fill="none" stroke="#dbeafe" stroke-width="3"/>

        <clipPath id="clip">
            <rect x="32" y="33" width="56" height="120" rx="18"/>
        </clipPath>

        <rect x="32" y="{y}" width="56" height="{altura}" fill="{color}" clip-path="url(#clip)"/>

        <rect x="32" y="33" width="56" height="120" rx="18" fill="none" stroke="#dbeafe" stroke-width="3"/>
    </svg>
    """


# ==============================
# CARGA DE DATOS
# ==============================
try:
    donaciones, metas = cargar_datos()
except:
    st.error("❌ No se pudieron cargar los datos. Revisa los links CSV.")
    st.stop()


donaciones.columns = [c.strip().lower() for c in donaciones.columns]
metas.columns = [c.strip().lower() for c in metas.columns]


# ==============================
# NORMALIZACIÓN METAS (ANTI ERROR)
# ==============================
# Compatibilidad si la hoja METAS trae nombres distintos
if "meta" not in metas.columns:
    for c in metas.columns:
        if "meta" in c:
            metas.rename(columns={c: "meta"}, inplace=True)

if "medicamento" not in metas.columns:
    for c in metas.columns:
        if "medicamento" in c or "nombre" in c:
            metas.rename(columns={c: "medicamento"}, inplace=True)

if "medicamento" not in metas.columns or "meta" not in metas.columns:
    st.error("❌ El archivo METAS debe tener columnas: medicamento, meta")
    st.stop()

metas["medicamento"] = metas["medicamento"].astype(str).str.strip()
metas["meta"] = pd.to_numeric(metas["meta"], errors="coerce").fillna(0)

lista_medicamentos = metas["medicamento"].tolist()


# ==============================
# NORMALIZACIÓN DONACIONES
# ==============================
if "timestamp" in donaciones.columns:
    donaciones.rename(columns={"timestamp": "fecha_hora"}, inplace=True)

# Donante público
for col in donaciones.columns:
    if "dashboard" in col and "nombre" in col:
        donaciones.rename(columns={col: "donante_publico"}, inplace=True)

if "donante_publico" not in donaciones.columns:
    donaciones["donante_publico"] = "Anónimo"

donaciones["donante_publico"] = donaciones["donante_publico"].fillna("").astype(str).str.strip()
donaciones.loc[donaciones["donante_publico"] == "", "donante_publico"] = "Anónimo"


# ==============================
# CREAR COLUMNAS SI NO EXISTEN
# ==============================
for med in lista_medicamentos:
    if med.lower() not in donaciones.columns:
        donaciones[med.lower()] = 0

for med in lista_medicamentos:
    donaciones[med.lower()] = pd.to_numeric(donaciones[med.lower()], errors="coerce").fillna(0)


# ==============================
# DONACIONES EN FORMATO LARGO
# ==============================
donaciones_largo = donaciones.melt(
    id_vars=[c for c in donaciones.columns if c not in [m.lower() for m in lista_medicamentos]],
    value_vars=[m.lower() for m in lista_medicamentos],
    var_name="medicamento",
    value_name="cantidad"
)

donaciones_largo = donaciones_largo[donaciones_largo["cantidad"] > 0]


# ==============================
# CALCULOS
# ==============================
donado_por_med = donaciones_largo.groupby("medicamento", as_index=False)["cantidad"].sum()

metas_temp = metas.copy()
metas_temp["medicamento"] = metas_temp["medicamento"].str.lower()

avance = metas_temp.merge(donado_por_med, on="medicamento", how="left")
avance["cantidad"] = avance["cantidad"].fillna(0)

avance["porcentaje"] = avance.apply(
    lambda r: (r["cantidad"] / r["meta"] * 100) if r["meta"] > 0 else 0,
    axis=1
)

total_recaudado = avance["cantidad"].sum()
total_meta = avance["meta"].sum()
porcentaje_total = (total_recaudado / total_meta * 100) if total_meta > 0 else 0

map_nombre_original = dict(zip(metas_temp["medicamento"], metas["medicamento"]))

fecha_hoy = datetime.now().strftime("%d %B %Y")


# ==============================
# COLORES DIFERENTES POR MEDICAMENTO
# ==============================
COLORES_MEDICAMENTOS = [
    "#2b7cff",  # azul
    "#00e0a4",  # verde
    "#ffb100",  # amarillo
    "#ff4b4b",  # rojo
    "#a855f7",  # morado
    "#00d4ff",  # cyan
    "#ff6a00",  # naranja
    "#22c55e",  # verde fuerte
    "#3b82f6",  # azul brillante
    "#f43f5e",  # rosado
]


# ==============================
# ÚLTIMA DONACIÓN (CAPA ALERTA)
# ==============================
ultimo_donante = "Anónimo"
ultima_hora = ""

if "fecha_hora" in donaciones.columns:
    try:
        donaciones["fecha_hora"] = pd.to_datetime(donaciones["fecha_hora"], errors="coerce")
        donaciones = donaciones.sort_values("fecha_hora", ascending=False)
        ultimo_donante = donaciones.iloc[0]["donante_publico"]
        ultima_hora = donaciones.iloc[0]["fecha_hora"].strftime("%H:%M:%S")
    except:
        pass


# ==============================
# HTML TARJETAS
# ==============================
cards_html = ""

for _, r in avance.iterrows():
    nombre = map_nombre_original.get(r["medicamento"], r["medicamento"])
    donado = float(r["cantidad"])
    meta = float(r["meta"])
    pct = float(r["porcentaje"])

    pct_bar = max(0, min(pct, 100))

    if pct >= 100:
        estado = "Meta alcanzada"
        estado_color = "#00e0a4"
    elif pct >= 70:
        estado = "Avance alto"
        estado_color = "#2b7cff"
    elif pct >= 40:
        estado = "Avance medio"
        estado_color = "#ffb100"
    else:
        estado = "Avance bajo"
        estado_color = "#ff4b4b"

    idx = lista_medicamentos.index(nombre) if nombre in lista_medicamentos else 0
    color_frasco = COLORES_MEDICAMENTOS[idx % len(COLORES_MEDICAMENTOS)]

    svg = frasco_svg(pct, color=color_frasco)

    cards_html += f"""
    <div class="med-card">
        <div class="med-name">{nombre}</div>

        <div class="med-img">
            {svg}
        </div>

        <div class="med-values">
            <div>Donado: <b>{formatear_numero(donado)}</b></div>
            <div>Meta: <b>{formatear_numero(meta)}</b></div>
        </div>

        <div class="bar-outer">
            <div class="bar-inner" style="width:{pct_bar}%; background: linear-gradient(90deg, {color_frasco}, #00e0a4);"></div>
        </div>

        <div class="pct">{pct:.1f}%</div>

        <div class="status" style="border:1px solid {estado_color}; color:{estado_color};">
            {estado}
        </div>
    </div>
    """


# ==============================
# HTML COMPLETO
# ==============================
html = f"""
<!DOCTYPE html>
<html>
<head>
<style>

body {{
    margin: 0;
    padding: 0;
    background: #070b12;
    color: white;
    font-family: "Segoe UI", Arial, sans-serif;
    overflow-x: hidden;
}}

.main {{
    padding: 18px;
    animation: fadeIn 0.35s ease-in-out;
}}

@keyframes fadeIn {{
    from {{ opacity: 0.7; transform: translateY(4px); }}
    to {{ opacity: 1; transform: translateY(0px); }}
}}

.header {{
    background: linear-gradient(145deg, #141c2e, #070b12);
    padding: 18px 22px;
    border-radius: 18px;
    box-shadow: 0px 6px 25px rgba(0,0,0,0.70);
    border: 1px solid rgba(255,255,255,0.10);
    display: flex;
    justify-content: space-between;
    align-items: center;
}}

.logo {{
    width: 140px;
    height: 80px;
    background: linear-gradient(135deg, #2b7cff, #00e0a4);
    border-radius: 14px;
    display: flex;
    justify-content: center;
    align-items: center;
    font-weight: 900;
    text-align: center;
    font-size: 14px;
    letter-spacing: 1px;
    box-shadow: 0px 4px 18px rgba(43,124,255,0.45);
}}

.title {{
    font-size: 34px;
    font-weight: 900;
}}

.subtitle {{
    font-size: 13px;
    opacity: 0.7;
    margin-top: 4px;
}}

.header-right {{
    font-size: 22px;
    font-weight: 900;
    color: #ffd44a;
}}

.summary {{
    margin-top: 14px;
    display: flex;
    gap: 12px;
}}

.summary-card {{
    flex: 1;
    background: linear-gradient(145deg, #141c2e, #070b12);
    padding: 14px;
    border-radius: 18px;
    border: 1px solid rgba(255,255,255,0.10);
    box-shadow: 0px 6px 22px rgba(0,0,0,0.55);
    text-align: center;
    transition: 0.25s;
}}

.summary-card:hover {{
    transform: translateY(-4px);
    border: 1px solid rgba(43,124,255,0.35);
}}

.summary-title {{
    font-size: 13px;
    opacity: 0.7;
    font-weight: 700;
}}

.summary-value {{
    font-size: 36px;
    font-weight: 900;
    margin-top: 6px;
}}

.global {{
    flex: 2;
    background: linear-gradient(145deg, #141c2e, #070b12);
    padding: 14px;
    border-radius: 18px;
    border: 1px solid rgba(255,255,255,0.10);
    box-shadow: 0px 6px 22px rgba(0,0,0,0.55);
}}

.global-title {{
    font-size: 13px;
    opacity: 0.7;
    font-weight: 800;
    margin-bottom: 8px;
}}

.global-bar {{
    height: 20px;
    border-radius: 14px;
    overflow: hidden;
    background: rgba(255,255,255,0.10);
}}

.global-fill {{
    height: 100%;
    background: linear-gradient(90deg, #2b7cff, #00e0a4);
    width: {max(0, min(porcentaje_total, 100))}%;
    transition: 0.4s;
}}

.global-pct {{
    text-align: right;
    font-size: 14px;
    font-weight: 900;
    margin-top: 6px;
}}

.grid {{
    margin-top: 16px;
    display: grid;
    grid-template-columns: repeat(6, 1fr);
    gap: 12px;
}}

.med-card {{
    background: linear-gradient(145deg, #141c2e, #070b12);
    padding: 14px;
    border-radius: 18px;
    border: 1px solid rgba(255,255,255,0.10);
    box-shadow: 0px 6px 22px rgba(0,0,0,0.55);
    min-height: 430px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    transition: 0.25s;
}}

.med-card:hover {{
    transform: translateY(-5px);
    border: 1px solid rgba(255,255,255,0.18);
    box-shadow: 0px 10px 28px rgba(0,0,0,0.80);
}}

.med-name {{
    font-size: 18px;
    font-weight: 900;
    text-align: center;
}}

.med-img {{
    margin-top: 10px;
    display: flex;
    justify-content: center;
    filter: drop-shadow(0px 6px 10px rgba(0,0,0,0.70));
}}

.med-values {{
    font-size: 13px;
    opacity: 0.88;
    text-align: center;
    margin-top: 10px;
    line-height: 1.6;
}}

.bar-outer {{
    height: 18px;
    border-radius: 12px;
    background: rgba(255,255,255,0.10);
    overflow: hidden;
    margin-top: 10px;
}}

.bar-inner {{
    height: 100%;
    transition: 0.4s;
}}

.pct {{
    font-size: 14px;
    font-weight: 900;
    text-align: right;
    margin-top: 5px;
}}

.status {{
    margin-top: 10px;
    padding: 7px;
    border-radius: 12px;
    text-align: center;
    font-size: 12px;
    font-weight: 900;
    background: rgba(255,255,255,0.05);
}}

.overlay {{
    position: fixed;
    top: 18px;
    right: 18px;
    padding: 12px 16px;
    background: rgba(20, 28, 46, 0.92);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 14px;
    font-weight: 900;
    font-size: 13px;
    z-index: 999;
    box-shadow: 0px 8px 28px rgba(0,0,0,0.65);
    animation: pulse 1.2s infinite alternate;
}}

@keyframes pulse {{
    from {{ transform: scale(1); opacity: 0.9; }}
    to {{ transform: scale(1.03); opacity: 1; }}
}}

.overlay b {{
    color: #00e0a4;
}}

</style>
</head>

<body>

<div class="overlay">
    Última donación: <b>{ultimo_donante}</b><br>
    Hora: {ultima_hora}
</div>

<div class="main">

    <div class="header">
        <div style="display:flex; align-items:center; gap:16px;">
            <div class="logo">GENEROSIDAD<br>COLOMBIA<br>2025</div>
            <div>
                <div class="title">Círculo de Generosidad</div>
                <div class="subtitle">{fecha_hoy}</div>
            </div>
        </div>

        <div class="header-right">Córdoba nos necesita</div>
    </div>

    <div class="summary">
        <div class="summary-card">
            <div class="summary-title">Total meta</div>
            <div class="summary-value">{formatear_numero(total_meta)}</div>
        </div>

        <div class="summary-card">
            <div class="summary-title">Total recolectado</div>
            <div class="summary-value">{formatear_numero(total_recaudado)}</div>
        </div>

        <div class="global">
            <div class="global-title">Avance global</div>
            <div class="global-bar">
                <div class="global-fill"></div>
            </div>
            <div class="global-pct">{porcentaje_total:.1f}%</div>
        </div>
    </div>

    <div class="grid">
        {cards_html}
    </div>

</div>

</body>
</html>
"""

components.html(html, height=1100, scrolling=True)




