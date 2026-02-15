import streamlit as st
import pandas as pd
from datetime import datetime
import streamlit.components.v1 as components
from streamlit_autorefresh import st_autorefresh
import time
import hashlib
import json
import os

# ==============================
# CONFIGURACIÓN PRINCIPAL
# ==============================
st.set_page_config(
    page_title="Círculo de Generosidad 2026 - Dashboard",
    page_icon="🏥",
    layout="wide"
)

# ==============================
# AUTO-REFRESH (15 SEGUNDOS)
# ==============================
count = st_autorefresh(interval=15000, key="datarefresh")


# ==============================
# ARCHIVO JSON PARA PERSISTENCIA
# ==============================
ESTADO_JSON = "estado_donacion.json"


def guardar_estado_json(ultima_fecha, ultima_id):
    """Guarda el estado en un JSON para que no se pierda al reiniciar Streamlit"""
    try:
        data = {
            "ultima_fecha_detectada": str(ultima_fecha) if ultima_fecha is not None else None,
            "ultima_donacion_id": ultima_id
        }
        with open(ESTADO_JSON, "w", encoding="utf-8") as f:
            json.dump(data, f)
    except Exception as e:
        print(f"Error guardando JSON: {e}")


def cargar_estado_json():
    """Carga el estado guardado del JSON"""
    try:
        if os.path.exists(ESTADO_JSON):
            with open(ESTADO_JSON, "r", encoding="utf-8") as f:
                data = json.load(f)

            fecha = data.get("ultima_fecha_detectada")
            ultima_id = data.get("ultima_donacion_id")

            if fecha is not None:
                fecha = pd.to_datetime(fecha, errors="coerce")

            return fecha, ultima_id

    except Exception as e:
        print(f"Error cargando JSON: {e}")

    return None, None


# ==============================
# LINKS CSV CON ANTI-CACHÉ
# ==============================
def get_csv_url_with_timestamp(base_url):
    """Agrega un timestamp único a la URL para evitar caché del navegador"""
    timestamp = int(time.time() * 1000)
    separator = "&" if "?" in base_url else "?"
    return f"{base_url}{separator}t={timestamp}"


CSV_BASE_DONACIONES = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSQ-JoPi55tEnwRnP_SyYy5gawWPJoQaQ0jI4PLgDpA4CcEdKjSb2IFftcc475zBr5Ou34BTrSdZ8v9/pub?gid=1709067163&single=true&output=csv"
CSV_BASE_METAS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSQ-JoPi55tEnwRnP_SyYy5gawWPJoQaQ0jI4PLgDpA4CcEdKjSb2IFftcc475zBr5Ou34BTrSdZ8v9/pub?gid=1531001200&single=true&output=csv"


# ==============================
# INICIALIZAR SESSION STATE
# ==============================
if 'ultima_donacion_id' not in st.session_state:
    st.session_state.ultima_donacion_id = None

if 'ultima_fecha_detectada' not in st.session_state:
    st.session_state.ultima_fecha_detectada = None

if 'mostrar_confeti' not in st.session_state:
    st.session_state.mostrar_confeti = False


# ==============================
# CARGAR ESTADO DESDE JSON
# ==============================
if st.session_state.ultima_donacion_id is None and st.session_state.ultima_fecha_detectada is None:
    fecha_guardada, id_guardado = cargar_estado_json()
    st.session_state.ultima_fecha_detectada = fecha_guardada
    st.session_state.ultima_donacion_id = id_guardado


# ==============================
# FUNCIONES
# ==============================
def generar_id_donacion(fila):
    """Genera un ID único para una donación basado en su contenido"""
    contenido = f"{fila.get('fecha_hora', '')}{fila.get('donante_publico', '')}"
    for col in fila.index:
        if col not in ['fecha_hora', 'donante_publico', 'Donante', 'Contacto (opcional)']:
            contenido += str(fila[col])
    return hashlib.md5(contenido.encode()).hexdigest()


def cargar_datos():
    """
    Carga datos SIN CACHÉ - Siempre datos frescos
    """
    url_donaciones = get_csv_url_with_timestamp(CSV_BASE_DONACIONES)
    url_metas = get_csv_url_with_timestamp(CSV_BASE_METAS)

    donaciones = pd.read_csv(url_donaciones)
    metas = pd.read_csv(url_metas)

    return donaciones, metas


def formatear_numero(x):
    """Formatea números con separadores de miles"""
    try:
        return f"{int(float(x)):,}".replace(",", ".")
    except:
        return "0"


def termometro_ultra_moderno_svg(pct, color="#00d4ff"):
    """Termómetro con diseño ultra moderno y efectos neón"""
    pct = max(0, min(float(pct), 100))
    altura = int(120 * (pct / 100))
    y = 150 - altura

    return f"""
    <svg viewBox="0 0 130 210">
        <defs>
            <linearGradient id="bulb{hash(color)}" x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" style="stop-color:{color};stop-opacity:1" />
                <stop offset="50%" style="stop-color:{color};stop-opacity:0.8" />
                <stop offset="100%" style="stop-color:{color};stop-opacity:0.6" />
            </linearGradient>
            <linearGradient id="tube{hash(color)}" x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" style="stop-color:{color};stop-opacity:1" />
                <stop offset="100%" style="stop-color:{color};stop-opacity:0.7" />
            </linearGradient>
            <filter id="neon{hash(color)}">
                <feGaussianBlur stdDeviation="4" result="coloredBlur"/>
                <feMerge>
                    <feMergeNode in="coloredBlur"/>
                    <feMergeNode in="coloredBlur"/>
                    <feMergeNode in="SourceGraphic"/>
                </feMerge>
            </filter>
        </defs>

        <circle cx="65" cy="170" r="26" fill="{color}" opacity="0.15" filter="blur(8px)"/>
        <circle cx="65" cy="170" r="22" fill="rgba(10,15,30,0.5)" stroke="{color}" stroke-width="2.5" opacity="0.5"/>
        <rect x="52" y="35" width="26" height="135" rx="13" fill="rgba(10,15,30,0.5)" stroke="{color}" stroke-width="2.5" opacity="0.5"/>

        <clipPath id="clipT{hash(color)}">
            <rect x="52" y="35" width="26" height="135" rx="13"/>
        </clipPath>

        <rect x="52" y="{y}" width="26" height="{altura}" fill="url(#tube{hash(color)})"
              clip-path="url(#clipT{hash(color)})" filter="url(#neon{hash(color)})"/>

        <circle cx="65" cy="170" r="18" fill="url(#bulb{hash(color)})" filter="url(#neon{hash(color)})"/>
        <circle cx="65" cy="170" r="10" fill="white" opacity="0.3"/>

        <line x1="79" y1="50" x2="88" y2="50" stroke="{color}" stroke-width="2" opacity="0.6"/>
        <line x1="79" y1="80" x2="88" y2="80" stroke="{color}" stroke-width="2" opacity="0.6"/>
        <line x1="79" y1="110" x2="88" y2="110" stroke="{color}" stroke-width="2" opacity="0.6"/>
        <line x1="79" y1="140" x2="88" y2="140" stroke="{color}" stroke-width="2" opacity="0.6"/>

        <text x="65" y="200" text-anchor="middle" fill="{color}" font-size="14" font-weight="900" opacity="0.9">{pct:.0f}%</text>
    </svg>
    """


# ==============================
# CARGA DE DATOS SIN CACHÉ
# ==============================
try:
    donaciones, metas = cargar_datos()
except Exception as e:
    st.error(f"❌ Error al cargar datos: {str(e)}")
    st.stop()

# Normalizar nombres de columnas
donaciones.columns = [c.strip() for c in donaciones.columns]
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
# NORMALIZACIÓN DONACIONES - PRIVACIDAD TOTAL
# ==============================
if "Timestamp" in donaciones.columns:
    donaciones.rename(columns={"Timestamp": "fecha_hora"}, inplace=True)
elif "timestamp" in donaciones.columns:
    donaciones.rename(columns={"timestamp": "fecha_hora"}, inplace=True)

if "Contacto (opcional)" in donaciones.columns:
    donaciones["donante_publico"] = donaciones["Contacto (opcional)"].fillna("").astype(str).str.strip()
else:
    donaciones["donante_publico"] = ""

donaciones.loc[donaciones["donante_publico"] == "", "donante_publico"] = "Donante anónimo"
donaciones.loc[donaciones["donante_publico"].str.lower() == "nan", "donante_publico"] = "Donante anónimo"

if "Donante" in donaciones.columns:
    donaciones = donaciones.drop(columns=["Donante"])


# ==============================
# CREAR COLUMNAS MEDICAMENTOS SI NO EXISTEN
# ==============================
for med in lista_medicamentos:
    if med not in donaciones.columns:
        donaciones[med] = 0

for med in lista_medicamentos:
    donaciones[med] = pd.to_numeric(donaciones[med], errors="coerce").fillna(0)


# ==============================
# PROCESAMIENTO FECHAS Y DETECCIÓN NUEVA DONACIÓN
# ==============================
ultimo_donante = "Donante anónimo"
ultima_hora = ""
ultimo_monto = 0
hay_nueva_donacion = False

if "fecha_hora" in donaciones.columns:
    try:
        donaciones["fecha_hora"] = pd.to_datetime(
            donaciones["fecha_hora"].astype(str).str.strip(),
            dayfirst=True,
            errors="coerce"
        )

        donaciones_validas = donaciones.dropna(subset=["fecha_hora"]).copy()

        if len(donaciones_validas) > 0:

            donaciones_validas = donaciones_validas.sort_values("fecha_hora", ascending=False)
            fila_ultima = donaciones_validas.iloc[0]

            id_actual = generar_id_donacion(fila_ultima)
            fecha_actual = fila_ultima["fecha_hora"]

            if st.session_state.ultima_fecha_detectada is None:
                st.session_state.ultima_fecha_detectada = fecha_actual
                st.session_state.ultima_donacion_id = id_actual
                st.session_state.mostrar_confeti = False
                guardar_estado_json(fecha_actual, id_actual)

            else:
                if fecha_actual > st.session_state.ultima_fecha_detectada:
                    st.session_state.ultima_fecha_detectada = fecha_actual
                    st.session_state.ultima_donacion_id = id_actual
                    st.session_state.mostrar_confeti = True
                    hay_nueva_donacion = True
                    guardar_estado_json(fecha_actual, id_actual)
                else:
                    st.session_state.mostrar_confeti = False

            ultimo_donante = fila_ultima["donante_publico"]

            suma_medicamentos = 0
            for med in lista_medicamentos:
                suma_medicamentos += float(fila_ultima[med])

            ultimo_monto = suma_medicamentos
            ultima_hora = fila_ultima["fecha_hora"].strftime("%H:%M:%S")

    except Exception as e:
        st.session_state.mostrar_confeti = False
        print(f"Error procesando última donación: {e}")


# ==============================
# DONACIONES EN FORMATO LARGO
# ==============================
donaciones_largo = donaciones.melt(
    id_vars=[c for c in donaciones.columns if c not in lista_medicamentos],
    value_vars=lista_medicamentos,
    var_name="medicamento",
    value_name="cantidad"
)

donaciones_largo = donaciones_largo[donaciones_largo["cantidad"] > 0]


# ==============================
# CALCULOS PRINCIPALES
# ==============================
donado_por_med = donaciones_largo.groupby("medicamento", as_index=False)["cantidad"].sum()

avance = metas.merge(donado_por_med, on="medicamento", how="left")
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

fecha_hoy = datetime.now().strftime("%d de %B de %Y")


# ==============================
# PALETA DE COLORES PREMIUM
# ==============================
COLORES_MEDICAMENTOS = [
    "#00D4FF",
    "#FF3D71",
    "#00FF9F",
    "#FFB800",
    "#B24BF3",
    "#FF6B35",
]


# ==============================
# MAP IMÁGENES
# ==============================
IMG_MAP = {
    "multivitaminas (gotas)": "https://img.icons8.com/?size=100&id=BayY6C34iXTA&format=png&color=000000",
    "vitaminas c (gotas)": "https://img.icons8.com/?size=100&id=p514QFRInGPV&format=png&color=000000",
    "vitamina a y d2 (gotas)": "https://img.icons8.com/?size=100&id=56345&format=png&color=000000g",
    "vitamina d2 forte (gotas)": "https://img.icons8.com/?size=100&id=aRMbtEpJbrOj&format=png&color=000000",
    "vitamina b (gotas)": "https://img.icons8.com/?size=100&id=2t4G6lB9hX4X&format=png&color=000000",
    "fumarato ferroso en suspensión": "https://img.icons8.com/?size=100&id=10XEPhqyfdJh&format=png&color=000000",
}

DEFAULT_IMG = "https://cdn-icons-png.flaticon.com/512/2966/2966334.png"


# ==============================
# MEDICAMENTO CRÍTICO Y AVANZADO
# ==============================
if len(avance) > 0:
    critico = avance.sort_values("porcentaje", ascending=True).iloc[0]
    critico_nombre = critico["medicamento"]
    critico_pct = float(critico["porcentaje"])
    critico_faltante = float(critico["faltante"])

    mas_avanzado = avance.sort_values("porcentaje", ascending=False).iloc[0]
    mas_av_nombre = mas_avanzado["medicamento"]
    mas_av_pct = float(mas_avanzado["porcentaje"])
else:
    critico_nombre = "N/A"
    critico_pct = 0
    critico_faltante = 0
    mas_av_nombre = "N/A"
    mas_av_pct = 0


# ==============================
# TARJETAS
# ==============================
cards_html = ""

for _, r in avance.iterrows():
    nombre_original = r["medicamento"]
    nombre_lower = nombre_original.lower()

    donado = float(r["cantidad"])
    meta = float(r["meta"])
    faltante = float(r["faltante"])
    pct = float(r["porcentaje"])
    pct_bar = max(0, min(pct, 100))

    idx = lista_medicamentos.index(nombre_original) if nombre_original in lista_medicamentos else 0
    color_main = COLORES_MEDICAMENTOS[idx % len(COLORES_MEDICAMENTOS)]

    img_url = IMG_MAP.get(nombre_lower, DEFAULT_IMG)
    thermo = termometro_ultra_moderno_svg(pct, color=color_main)

    cards_html += f"""
    <div class="med-card">

        <div class="med-header">
            <div class="med-title">{nombre_original}</div>
            <div class="med-badge" style="background: {color_main}20; color: {color_main}; border: 1px solid {color_main}40;">
                {pct:.1f}%
            </div>
        </div>

        <div class="med-body">

            <div class="med-image-container">
                <div class="image-glow" style="background: {color_main}30;"></div>

                <div class="img-wrapper">
                    <img src="{img_url}" class="img-base"/>

                    <div class="img-fill-container" style="height: {pct_bar}%;">

                        <img src="{img_url}" class="img-colored"
                             style="filter: drop-shadow(0 0 12px {color_main}) brightness(1.2);"/>
                    </div>

                    <div class="img-shimmer"></div>
                </div>
            </div>

            <div class="med-thermo">{thermo}</div>
        </div>

        <div class="med-stats">
            <div class="stat-item">
                <div class="stat-label">Donado</div>
                <div class="stat-value" style="color: {color_main};">{formatear_numero(donado)}</div>
            </div>
            <div class="stat-divider"></div>
            <div class="stat-item">
                <div class="stat-label">Meta</div>
                <div class="stat-value">{formatear_numero(meta)}</div>
            </div>
            <div class="stat-divider"></div>
            <div class="stat-item">
                <div class="stat-label">Faltan</div>
                <div class="stat-value warning">{formatear_numero(faltante)}</div>
            </div>
        </div>

        <div class="progress-bar">
            <div class="progress-fill" style="width: {pct_bar}%; background: linear-gradient(90deg, {color_main}, {color_main}cc);"></div>
            <div class="progress-glow" style="width: {pct_bar}%; background: {color_main}; opacity: 0.3;"></div>
        </div>

    </div>
    """


# ==============================
# HTML COMPLETO (AQUÍ ESTABA EL ERROR)
# ==============================
html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
<meta http-equiv="Pragma" content="no-cache">
<meta http-equiv="Expires" content="0">
<script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.5.1/dist/confetti.browser.min.js"></script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

* {{
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}}

body {{
    font-family: 'Inter', -apple-system, system-ui, sans-serif;
    background: #060A12;
    color: #E5E9F0;
    min-height: 100vh;
    overflow-x: hidden;
    position: relative;
}}

.main {{
    max-width: 1920px;
    margin: 0 auto;
    padding: 30px;
    position: relative;
    z-index: 1;
}}

.header {{
    background: linear-gradient(135deg, rgba(15, 23, 42, 0.95) 0%, rgba(8, 15, 30, 0.95) 100%);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 28px;
    padding: 32px 40px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 30px;
}}

.logo {{
    background: linear-gradient(135deg, #00D4FF 0%, #0091FF 100%);
    color: #060A12;
    padding: 16px 22px;
    border-radius: 18px;
    font-weight: 900;
    font-size: 12px;
    line-height: 1.4;
    text-align: center;
}}

.title {{
    font-size: 38px;
    font-weight: 900;
    color: white;
}}

.subtitle {{
    font-size: 15px;
    color: rgba(255, 255, 255, 0.5);
    margin-top: 6px;
    font-weight: 600;
}}

.header-badge {{
    font-size: 18px;
    font-weight: 800;
    color: #00FF9F;
    padding: 14px 28px;
    background: rgba(0, 255, 159, 0.12);
    border: 2px solid rgba(0, 255, 159, 0.3);
    border-radius: 16px;
}}

.summary {{
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 20px;
    margin-bottom: 30px;
}}

.summary-card {{
    background: rgba(15, 23, 42, 0.9);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 24px;
    padding: 28px;
}}

.summary-label {{
    font-size: 12px;
    color: rgba(255, 255, 255, 0.5);
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin-bottom: 12px;
}}

.summary-number {{
    font-size: 42px;
    font-weight: 900;
    color: white;
}}

.global-progress {{
    margin-top: 8px;
}}

.progress-track {{
    height: 28px;
    border-radius: 20px;
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    overflow: hidden;
}}

.progress-active {{
    height: 100%;
    width: {porcentaje_total:.1f}%;
    background: linear-gradient(90deg, #00FF9F 0%, #00D4FF 100%);
    border-radius: 20px;
}}

.progress-percent {{
    text-align: right;
    font-size: 18px;
    font-weight: 900;
    margin-top: 10px;
    color: #00FF9F;
}}

.panel {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
    margin-bottom: 30px;
}}

.panel-card {{
    background: rgba(15, 23, 42, 0.9);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 24px;
    padding: 24px;
}}

.panel-label {{
    font-size: 11px;
    color: rgba(255, 255, 255, 0.5);
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin-bottom: 8px;
}}

.panel-title {{
    font-size: 24px;
    font-weight: 900;
    margin-bottom: 12px;
}}

.panel-info {{
    font-size: 14px;
    color: rgba(255, 255, 255, 0.7);
    margin-top: 8px;
    font-weight: 600;
}}

.grid {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 24px;
}}

.med-card {{
    background: rgba(15, 23, 42, 0.95);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 28px;
    padding: 28px;
    min-height: 580px;
    display: flex;
    flex-direction: column;
}}

.donation-overlay {{
    position: fixed;
    top: 30px;
    right: 30px;
    padding: 20px 28px;
    background: rgba(15, 23, 42, 0.98);
    border: 1px solid rgba(0, 212, 255, 0.4);
    border-radius: 20px;
    font-weight: 700;
    font-size: 15px;
    z-index: 999;
    min-width: 280px;
}}
</style>
</head>

<body>

<div class="main">

    <div class="header">
        <div style="display:flex; gap:20px; align-items:center;">
            <div class="logo">CÍRCULO<br>DE<br>GENEROSIDAD</div>

            <div>
                <div class="title">Círculo de Generosidad 2026</div>
                <div class="subtitle">Actualizado automáticamente - {fecha_hoy}</div>
            </div>
        </div>

        <div class="header-badge">💙 En progreso</div>
    </div>


    <div class="summary">
        <div class="summary-card">
            <div class="summary-label">Total recaudado</div>
            <div class="summary-number">{formatear_numero(total_recaudado)}</div>
        </div>

        <div class="summary-card">
            <div class="summary-label">Meta total</div>
            <div class="summary-number">{formatear_numero(total_meta)}</div>
        </div>

        <div class="summary-card">
            <div class="summary-label">Avance global</div>

            <div class="global-progress">
                <div class="progress-track">
                    <div class="progress-active"></div>
                </div>
                <div class="progress-percent">{porcentaje_total:.1f}%</div>
            </div>
        </div>
    </div>


    <div class="panel">

        <div class="panel-card">
            <div class="panel-label">Medicamento más crítico</div>
            <div class="panel-title">{critico_nombre}</div>
            <div class="panel-info">Avance: {critico_pct:.1f}% | Faltan: {formatear_numero(critico_faltante)}</div>
        </div>

        <div class="panel-card">
            <div class="panel-label">Medicamento más avanzado</div>
            <div class="panel-title">{mas_av_nombre}</div>
            <div class="panel-info">Avance: {mas_av_pct:.1f}%</div>
        </div>

    </div>


    <div class="grid">
        {cards_html}
    </div>

</div>


<!-- OVERLAY ÚLTIMA DONACIÓN -->
<div class="donation-overlay">
    <div class="donation-header">🎁 Última donación</div>
    <div class="donation-name">{ultimo_donante}</div>

    <div class="donation-details">
        <div class="donation-detail">
            <div class="donation-detail-label">Monto</div>
            <div class="donation-detail-value">{formatear_numero(ultimo_monto)}</div>
        </div>
        <div class="donation-detail">
            <div class="donation-detail-label">Hora</div>
            <div class="donation-detail-value">{ultima_hora}</div>
        </div>
    </div>
</div>


<script>
    const mostrarConfeti = {str(st.session_state.mostrar_confeti).lower()};

    if(mostrarConfeti) {{
        confetti({{
            particleCount: 200,
            spread: 120,
            origin: {{ y: 0.6 }},
            colors: ['#00D4FF', '#FF3D71', '#00FF9F', '#B24BF3', '#FFB800']
        }});
    }}
</script>

</body>
</html>
"""

components.html(html, height=1400, scrolling=True)

