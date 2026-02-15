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

# REFRESH MÁS SUAVE (NO 2s)
st_autorefresh(interval=5000, key="autorefresh")

# ==============================
# LINKS CSV
# ==============================
CSV_DONACIONES = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSQ-JoPi55tEnwRnP_SyYy5gawWPJoQaQ0jI4PLgDpA4CcEdKjSb2IFftcc475zBr5Ou34BTrSdZ8v9/pub?gid=1709067163&single=true&output=csv"
CSV_METAS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSQ-JoPi55tEnwRnP_SyYy5gawWPJoQaQ0jI4PLgDpA4CcEdKjSb2IFftcc475zBr5Ou34BTrSdZ8v9/pub?gid=1531001200&single=true&output=csv"

# ==============================
# FUNCIONES
# ==============================
@st.cache_data(ttl=5)
def cargar_datos():
    donaciones = pd.read_csv(CSV_DONACIONES)
    metas = pd.read_csv(CSV_METAS)
    return donaciones, metas


def formatear_numero(x):
    try:
        return f"{int(float(x)):,}".replace(",", ".")
    except:
        return "0"


# ==============================
# TERMÓMETRO SVG (vertical)
# ==============================
def termometro_svg(pct, color="#2b7cff"):
    pct = max(0, min(float(pct), 100))
    altura = int(110 * (pct / 100))
    y = 140 - altura

    return f"""
    <svg viewBox="0 0 120 190">
        <circle cx="60" cy="160" r="18" fill="rgba(255,255,255,0.10)" stroke="#dbeafe" stroke-width="3"/>
        <rect x="50" y="25" width="20" height="130" rx="10" fill="rgba(255,255,255,0.08)" stroke="#dbeafe" stroke-width="3"/>

        <clipPath id="clipT">
            <rect x="50" y="25" width="20" height="130" rx="10"/>
        </clipPath>

        <rect x="50" y="{y}" width="20" height="{altura}" fill="{color}" clip-path="url(#clipT)"/>

        <circle cx="60" cy="160" r="14" fill="{color}" opacity="0.85"/>
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
# NORMALIZACIÓN METAS
# ==============================
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

for col in donaciones.columns:
    if "dashboard" in col and "nombre" in col:
        donaciones.rename(columns={col: "donante_publico"}, inplace=True)

if "donante_publico" not in donaciones.columns:
    donaciones["donante_publico"] = "Anónimo"

donaciones["donante_publico"] = donaciones["donante_publico"].fillna("").astype(str).str.strip()
donaciones.loc[donaciones["donante_publico"] == "", "donante_publico"] = "Anónimo"

# ==============================
# CREAR COLUMNAS MEDICAMENTOS SI NO EXISTEN
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
# CALCULOS PRINCIPALES
# ==============================
donado_por_med = donaciones_largo.groupby("medicamento", as_index=False)["cantidad"].sum()

metas_temp = metas.copy()
metas_temp["medicamento"] = metas_temp["medicamento"].str.lower()

avance = metas_temp.merge(donado_por_med, on="medicamento", how="left")
avance["cantidad"] = avance["cantidad"].fillna(0)

avance["faltante"] = avance["meta"] - avance["cantidad"]
avance.loc[avance["faltante"] < 0, "faltante"] = 0

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
# COLORES DIFERENTES
# ==============================
COLORES_MEDICAMENTOS = [
    "#2b7cff",
    "#00e0a4",
    "#ffb100",
    "#ff4b4b",
    "#a855f7",
    "#00d4ff",
    "#ff6a00",
    "#22c55e",
    "#3b82f6",
    "#f43f5e",
]

# ==============================
# IMÁGENES DIFERENTES POR MEDICAMENTO
# (puedes cambiar los links por imágenes reales tuyas)
# ==============================
IMG_MAP = {
    "multivitaminas (gotas)": "https://cdn-icons-png.flaticon.com/512/2966/2966486.png",
    "vitaminas c (gotas)": "https://cdn-icons-png.flaticon.com/512/415/415733.png",
    "vitamina a y d2 (gotas)": "https://cdn-icons-png.flaticon.com/512/822/822143.png",
    "vitamina d2 forte (gotas)": "https://cdn-icons-png.flaticon.com/512/822/822087.png",
    "vitamina b (gotas)": "https://cdn-icons-png.flaticon.com/512/2966/2966327.png",
    "fumarato ferroso en suspensión": "https://cdn-icons-png.flaticon.com/512/2966/2966391.png",
}

DEFAULT_IMG = "https://cdn-icons-png.flaticon.com/512/2966/2966493.png"

# ==============================
# ÚLTIMA DONACIÓN
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
# MEDICAMENTO MÁS CRÍTICO
# ==============================
critico = avance.sort_values("porcentaje", ascending=True).iloc[0]
critico_nombre = map_nombre_original.get(critico["medicamento"], critico["medicamento"])
critico_pct = float(critico["porcentaje"])
critico_faltante = float(critico["faltante"])

# TOP 3 críticos
top_criticos = avance.sort_values("porcentaje", ascending=True).head(3)

# MÁS AVANZADO
mas_avanzado = avance.sort_values("porcentaje", ascending=False).iloc[0]
mas_av_nombre = map_nombre_original.get(mas_avanzado["medicamento"], mas_avanzado["medicamento"])
mas_av_pct = float(mas_avanzado["porcentaje"])

# ==============================
# CONFETTI SI ALGUNO LLEGA A 100%
# ==============================
hay_meta_completa = (avance["porcentaje"] >= 100).any()

# ==============================
# HTML TARJETAS
# ==============================
cards_html = ""

for _, r in avance.iterrows():
    nombre_original = map_nombre_original.get(r["medicamento"], r["medicamento"])
    nombre_lower = nombre_original.lower()

    donado = float(r["cantidad"])
    meta = float(r["meta"])
    faltante = float(r["faltante"])
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

    idx = lista_medicamentos.index(nombre_original) if nombre_original in lista_medicamentos else 0
    color_main = COLORES_MEDICAMENTOS[idx % len(COLORES_MEDICAMENTOS)]

    img_url = IMG_MAP.get(nombre_lower, DEFAULT_IMG)

    thermo = termometro_svg(pct, color=color_main)

    cards_html += f"""
    <div class="med-card">

        <div class="med-title">
            {nombre_original}
        </div>

        <div class="med-body">

            <div class="med-image-box">
                <img src="{img_url}" class="med-img"/>

                <div class="med-fill" style="height:{pct_bar}%; background: linear-gradient(180deg, {color_main}, rgba(0,224,164,0.7));"></div>
            </div>

            <div class="med-thermo">
                {thermo}
            </div>

        </div>

        <div class="med-values">
            <div>Donado: <b>{formatear_numero(donado)}</b></div>
            <div>Meta: <b>{formatear_numero(meta)}</b></div>
            <div>Faltan: <b style="color:#ffd44a;">{formatear_numero(faltante)}</b></div>
        </div>

        <div class="bar-outer">
            <div class="bar-inner" style="width:{pct_bar}%; background: linear-gradient(90deg, {color_main}, #00e0a4);"></div>
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

<script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.6.0/dist/confetti.browser.min.js"></script>

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
    animation: fadeIn 0.45s ease-in-out;
}}

@keyframes fadeIn {{
    from {{ opacity: 0.2; filter: blur(2px); transform: translateY(6px); }}
    to {{ opacity: 1; filter: blur(0px); transform: translateY(0px); }}
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

.panel {{
    margin-top: 14px;
    display: flex;
    gap: 12px;
}}

.panel-card {{
    flex: 1;
    background: linear-gradient(145deg, #141c2e, #070b12);
    padding: 14px;
    border-radius: 18px;
    border: 1px solid rgba(255,255,255,0.10);
    box-shadow: 0px 6px 22px rgba(0,0,0,0.55);
}}

.panel-title {{
    font-size: 13px;
    opacity: 0.7;
    font-weight: 800;
}}

.panel-value {{
    font-size: 20px;
    font-weight: 900;
    margin-top: 6px;
}}

.panel-sub {{
    font-size: 13px;
    opacity: 0.85;
    margin-top: 4px;
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
    min-height: 520px;
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

.med-title {{
    font-size: 16px;
    font-weight: 900;
    text-align: center;
}}

.med-body {{
    margin-top: 12px;
    display: flex;
    justify-content: center;
    gap: 12px;
    align-items: center;
}}

.med-image-box {{
    width: 130px;
    height: 180px;
    border-radius: 18px;
    position: relative;
    overflow: hidden;
    border: 1px solid rgba(255,255,255,0.12);
    background: rgba(255,255,255,0.03);
    display: flex;
    justify-content: center;
    align-items: center;
}}

.med-img {{
    width: 85px;
    height: 85px;
    opacity: 0.95;
    z-index: 2;
    filter: drop-shadow(0px 4px 10px rgba(0,0,0,0.75));
}}

.med-fill {{
    position: absolute;
    bottom: 0;
    left: 0;
    width: 100%;
    opacity: 0.50;
    z-index: 1;
    transition: 0.7s;
}}

.med-thermo {{
    width: 90px;
    height: 180px;
    display: flex;
    justify-content: center;
    align-items: center;
}}

.med-values {{
    font-size: 13px;
    opacity: 0.9;
    text-align: center;
    margin-top: 10px;
    line-height: 1.7;
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
    transition: 0.6s;
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
}}

.overlay b {{
    color: #00e0a4;
}}

.refresh-badge {{
    position: fixed;
    bottom: 18px;
    right: 18px;
    padding: 8px 14px;
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 14px;
    font-size: 12px;
    font-weight: 800;
    opacity: 0.75;
}}

</style>
</head>

<body>

<div class="overlay">
    Última donación: <b>{ultimo_donante}</b><br>
    Hora: {ultima_hora}
</div>

<div class="refresh-badge">
    Dashboard en vivo · Actualización automática
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

    <div class="panel">
        <div class="panel-card">
            <div class="panel-title">Medicamento más crítico</div>
            <div class="panel-value" style="color:#ff4b4b;">{critico_nombre}</div>
            <div class="panel-sub">Avance: <b>{critico_pct:.1f}%</b></div>
            <div class="panel-sub">Faltan: <b style="color:#ffd44a;">{formatear_numero(critico_faltante)}</b></div>
        </div>

        <div class="panel-card">
            <div class="panel-title">Medicamento más avanzado</div>
            <div class="panel-value" style="color:#00e0a4;">{mas_av_nombre}</div>
            <div class="panel-sub">Avance: <b>{mas_av_pct:.1f}%</b></div>
        </div>
    </div>

    <div class="grid">
        {cards_html}
    </div>

</div>

<script>
    const metaCompleta = {str(hay_meta_completa).lower()};
    if(metaCompleta){{
        confetti({{
            particleCount: 200,
            spread: 120,
            origin: {{ y: 0.6 }}
        }});
    }}
</script>

</body>
</html>
"""

components.html(html, height=1250, scrolling=True)




