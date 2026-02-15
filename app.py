import streamlit as st
import pandas as pd
from datetime import datetime
import streamlit.components.v1 as components

# ==============================
# CONFIGURACIÓN PRINCIPAL
# ==============================
st.set_page_config(
    page_title="Círculo de Generosidad - Dashboard Ejecutivo",
    page_icon="💊",
    layout="wide"
)

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


def termometro_moderno_svg(pct, color="#00d4ff"):
    """Termómetro con diseño moderno y efectos de brillo"""
    pct = max(0, min(float(pct), 100))
    altura = int(115 * (pct / 100))
    y = 145 - altura

    return f"""
    <svg viewBox="0 0 120 200">
        <defs>
            <linearGradient id="bulbGrad{hash(color)}" x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" style="stop-color:{color};stop-opacity:1" />
                <stop offset="100%" style="stop-color:{color};stop-opacity:0.7" />
            </linearGradient>
            <linearGradient id="tubeGrad{hash(color)}" x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" style="stop-color:{color};stop-opacity:0.9" />
                <stop offset="100%" style="stop-color:{color};stop-opacity:0.6" />
            </linearGradient>
            <filter id="glow{hash(color)}">
                <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
                <feMerge>
                    <feMergeNode in="coloredBlur"/>
                    <feMergeNode in="SourceGraphic"/>
                </feMerge>
            </filter>
        </defs>
        
        <!-- Bulbo externo con gradiente -->
        <circle cx="60" cy="165" r="20" fill="rgba(10,15,30,0.4)" stroke="rgba(100,180,255,0.3)" stroke-width="2"/>
        
        <!-- Tubo externo -->
        <rect x="48" y="30" width="24" height="130" rx="12" fill="rgba(10,15,30,0.4)" stroke="rgba(100,180,255,0.3)" stroke-width="2"/>

        <clipPath id="clipThermo{hash(color)}">
            <rect x="48" y="30" width="24" height="130" rx="12"/>
        </clipPath>

        <!-- Relleno del tubo con gradiente y brillo -->
        <rect x="48" y="{y}" width="24" height="{altura}" fill="url(#tubeGrad{hash(color)})" 
              clip-path="url(#clipThermo{hash(color)})" filter="url(#glow{hash(color)})"/>

        <!-- Bulbo interno con gradiente y brillo -->
        <circle cx="60" cy="165" r="16" fill="url(#bulbGrad{hash(color)})" filter="url(#glow{hash(color)})"/>
        
        <!-- Marcas de medición -->
        <line x1="73" y1="50" x2="80" y2="50" stroke="rgba(255,255,255,0.3)" stroke-width="1.5"/>
        <line x1="73" y1="80" x2="80" y2="80" stroke="rgba(255,255,255,0.3)" stroke-width="1.5"/>
        <line x1="73" y1="110" x2="80" y2="110" stroke="rgba(255,255,255,0.3)" stroke-width="1.5"/>
        <line x1="73" y1="140" x2="80" y2="140" stroke="rgba(255,255,255,0.3)" stroke-width="1.5"/>
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
# NORMALIZACIÓN DONACIONES - PRIVACIDAD
# ==============================
if "timestamp" in donaciones.columns:
    donaciones.rename(columns={"timestamp": "fecha_hora"}, inplace=True)

# ⚠️ CORRECCIÓN CRÍTICA: Buscar columna "Contacto (opcional)" para privacidad
col_contacto = None
for col in donaciones.columns:
    if "contacto" in col.lower() and "opcional" in col.lower():
        col_contacto = col
        break

# Si no se encuentra, buscar solo "contacto"
if not col_contacto:
    for col in donaciones.columns:
        if "contacto" in col.lower():
            col_contacto = col
            break

# Renombrar a "donante_publico" para claridad
if col_contacto:
    donaciones.rename(columns={col_contacto: "donante_publico"}, inplace=True)
else:
    donaciones["donante_publico"] = "Donante anónimo"

# Limpiar valores vacíos y convertir a "Donante anónimo"
donaciones["donante_publico"] = donaciones["donante_publico"].fillna("").astype(str).str.strip()
donaciones.loc[donaciones["donante_publico"] == "", "donante_publico"] = "Donante anónimo"
donaciones.loc[donaciones["donante_publico"].str.lower() == "nan", "donante_publico"] = "Donante anónimo"


# ==============================
# CREAR COLUMNAS MEDICAMENTOS SI NO EXISTEN
# ==============================
for med in lista_medicamentos:
    if med.lower() not in donaciones.columns:
        donaciones[med.lower()] = 0

for med in lista_medicamentos:
    donaciones[med.lower()] = pd.to_numeric(donaciones[med.lower()], errors="coerce").fillna(0)


# ==============================
# ÚLTIMA DONACIÓN - SOLO CONTACTO PÚBLICO
# ==============================
ultimo_donante = "Donante anónimo"
ultima_hora = ""
ultimo_monto = 0

if "fecha_hora" in donaciones.columns:
    try:
        donaciones["fecha_hora"] = pd.to_datetime(donaciones["fecha_hora"], errors="coerce")
        donaciones = donaciones.sort_values("fecha_hora", ascending=False)

        fila_ultima = donaciones.iloc[0]
        # ✅ USAR SOLO CONTACTO PÚBLICO, NUNCA NOMBRE REAL
        ultimo_donante = fila_ultima["donante_publico"]

        suma_medicamentos = 0
        for med in lista_medicamentos:
            suma_medicamentos += float(fila_ultima[med.lower()])

        ultimo_monto = suma_medicamentos

        if pd.notnull(fila_ultima["fecha_hora"]):
            ultima_hora = fila_ultima["fecha_hora"].strftime("%H:%M:%S")

    except:
        pass


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
# PALETA DE COLORES MODERNA - HEALTHTECH
# ==============================
COLORES_MEDICAMENTOS = [
    "#00d4ff",  # Cyan brillante
    "#ff6b9d",  # Rosa vibrante
    "#00ff88",  # Verde neón
    "#ff9f43",  # Naranja cálido
    "#a855f7",  # Púrpura
    "#ffd93d",  # Amarillo dorado
]


# ==============================
# IMÁGENES CON COLORES ORIGINALES
# ==============================
IMG_MAP = {
    "multivitaminas (gotas)": "https://cdn-icons-png.flaticon.com/512/1047/1047711.png",
    "vitaminas c (gotas)": "https://cdn-icons-png.flaticon.com/512/415/415680.png",
    "vitamina a y d2 (gotas)": "https://cdn-icons-png.flaticon.com/512/822/822143.png",
    "vitamina d2 forte (gotas)": "https://cdn-icons-png.flaticon.com/512/2966/2966367.png",
    "vitamina b (gotas)": "https://cdn-icons-png.flaticon.com/512/2966/2966320.png",
    "fumarato ferroso en suspensión": "https://cdn-icons-png.flaticon.com/512/4320/4320351.png",
}

DEFAULT_IMG = "https://cdn-icons-png.flaticon.com/512/2966/2966493.png"


# ==============================
# MEDICAMENTO CRÍTICO Y AVANZADO
# ==============================
critico = avance.sort_values("porcentaje", ascending=True).iloc[0]
critico_nombre = map_nombre_original.get(critico["medicamento"], critico["medicamento"])
critico_pct = float(critico["porcentaje"])
critico_faltante = float(critico["faltante"])

mas_avanzado = avance.sort_values("porcentaje", ascending=False).iloc[0]
mas_av_nombre = map_nombre_original.get(mas_avanzado["medicamento"], mas_avanzado["medicamento"])
mas_av_pct = float(mas_avanzado["porcentaje"])

hay_meta_completa = (avance["porcentaje"] >= 100).any()


# ==============================
# TARJETAS CON DISEÑO MODERNO
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

    idx = lista_medicamentos.index(nombre_original) if nombre_original in lista_medicamentos else 0
    color_main = COLORES_MEDICAMENTOS[idx % len(COLORES_MEDICAMENTOS)]

    img_url = IMG_MAP.get(nombre_lower, DEFAULT_IMG)
    thermo = termometro_moderno_svg(pct, color=color_main)

    cards_html += f"""
    <div class="med-card">

        <div class="med-title">{nombre_original}</div>

        <div class="med-body">

            <div class="med-image-box">

                <div class="img-container">
                    <!-- Imagen base en escala de grises -->
                    <img src="{img_url}" class="img-base"/>
                    
                    <!-- Capa de color que se llena progresivamente -->
                    <div class="img-fill" style="height:{pct_bar}%;">
                        <img src="{img_url}" class="img-colored" style="filter: drop-shadow(0 0 8px {color_main}80);"/>
                    </div>
                    
                    <!-- Brillo superior -->
                    <div class="img-shine"></div>
                </div>

            </div>

            <div class="med-thermo">{thermo}</div>
        </div>

        <div class="med-values">
            <div class="value-row">
                <span class="value-label">Donado:</span>
                <span class="value-num">{formatear_numero(donado)}</span>
            </div>
            <div class="value-row">
                <span class="value-label">Meta:</span>
                <span class="value-num">{formatear_numero(meta)}</span>
            </div>
            <div class="value-row">
                <span class="value-label">Faltan:</span>
                <span class="value-num highlight">{formatear_numero(faltante)}</span>
            </div>
        </div>

        <div class="bar-container">
            <div class="bar-fill" style="width:{pct_bar}%; background: linear-gradient(90deg, {color_main}, {color_main}dd);"></div>
        </div>

        <div class="pct-display">{pct:.1f}%</div>

    </div>
    """


# ==============================
# HTML COMPLETO - DISEÑO PREMIUM
# ==============================
html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.5.1/dist/confetti.browser.min.js"></script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

* {{
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}}

body {{
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    background: linear-gradient(135deg, #0a0e1a 0%, #1a1f2e 50%, #0f1419 100%);
    color: #f0f4f8;
    min-height: 100vh;
    padding: 20px;
    overflow-x: hidden;
}}

/* Efecto de partículas animadas en el fondo */
body::before {{
    content: '';
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-image: 
        radial-gradient(circle at 20% 50%, rgba(0, 212, 255, 0.03) 0%, transparent 50%),
        radial-gradient(circle at 80% 80%, rgba(255, 107, 157, 0.03) 0%, transparent 50%),
        radial-gradient(circle at 40% 20%, rgba(168, 85, 247, 0.03) 0%, transparent 50%);
    pointer-events: none;
    z-index: 0;
}}

.main {{
    max-width: 1800px;
    margin: 0 auto;
    position: relative;
    z-index: 1;
}}

/* ==================== HEADER ==================== */
.header {{
    background: linear-gradient(135deg, rgba(20, 28, 46, 0.95) 0%, rgba(10, 15, 26, 0.95) 100%);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid rgba(100, 180, 255, 0.15);
    border-radius: 24px;
    padding: 24px 32px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;
    box-shadow: 
        0 8px 32px rgba(0, 0, 0, 0.4),
        inset 0 1px 0 rgba(255, 255, 255, 0.05);
}}

.logo {{
    background: linear-gradient(135deg, #00d4ff 0%, #0091ff 100%);
    color: #0a0e1a;
    padding: 14px 18px;
    border-radius: 16px;
    font-weight: 900;
    font-size: 11px;
    line-height: 1.3;
    text-align: center;
    letter-spacing: 0.5px;
    box-shadow: 
        0 4px 16px rgba(0, 212, 255, 0.3),
        inset 0 1px 0 rgba(255, 255, 255, 0.4);
}}

.title {{
    font-size: 32px;
    font-weight: 900;
    background: linear-gradient(135deg, #ffffff 0%, #c5d9ff 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: -0.5px;
}}

.subtitle {{
    font-size: 14px;
    color: rgba(255, 255, 255, 0.6);
    margin-top: 4px;
    font-weight: 500;
}}

.header-right {{
    font-size: 16px;
    font-weight: 700;
    color: #00ff88;
    padding: 12px 24px;
    background: rgba(0, 255, 136, 0.1);
    border: 1px solid rgba(0, 255, 136, 0.3);
    border-radius: 12px;
    box-shadow: 0 0 20px rgba(0, 255, 136, 0.2);
}}

/* ==================== SUMMARY ==================== */
.summary {{
    display: flex;
    gap: 16px;
    margin-bottom: 24px;
}}

.summary-card {{
    flex: 1;
    background: linear-gradient(135deg, rgba(20, 28, 46, 0.9) 0%, rgba(10, 15, 26, 0.9) 100%);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(100, 180, 255, 0.15);
    border-radius: 20px;
    padding: 20px;
    box-shadow: 
        0 8px 32px rgba(0, 0, 0, 0.3),
        inset 0 1px 0 rgba(255, 255, 255, 0.05);
    position: relative;
    overflow: hidden;
}}

.summary-card::before {{
    content: '';
    position: absolute;
    top: -50%;
    right: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle, rgba(0, 212, 255, 0.05) 0%, transparent 70%);
    pointer-events: none;
}}

.summary-title {{
    font-size: 13px;
    color: rgba(255, 255, 255, 0.6);
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 8px;
}}

.summary-value {{
    font-size: 38px;
    font-weight: 900;
    background: linear-gradient(135deg, #ffffff 0%, #00d4ff 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-top: 6px;
}}

.global {{
    flex: 2;
    background: linear-gradient(135deg, rgba(20, 28, 46, 0.9) 0%, rgba(10, 15, 26, 0.9) 100%);
    backdrop-filter: blur(10px);
    padding: 20px;
    border-radius: 20px;
    border: 1px solid rgba(100, 180, 255, 0.15);
    box-shadow: 
        0 8px 32px rgba(0, 0, 0, 0.3),
        inset 0 1px 0 rgba(255, 255, 255, 0.05);
}}

.global-title {{
    font-size: 13px;
    color: rgba(255, 255, 255, 0.6);
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 12px;
}}

.global-bar {{
    height: 24px;
    border-radius: 16px;
    overflow: hidden;
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(100, 180, 255, 0.1);
    position: relative;
}}

.global-bar::before {{
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 50%;
    background: linear-gradient(180deg, rgba(255, 255, 255, 0.1) 0%, transparent 100%);
    pointer-events: none;
}}

.global-fill {{
    height: 100%;
    background: linear-gradient(90deg, #00d4ff 0%, #00ff88 100%);
    width: {max(0, min(porcentaje_total, 100))}%;
    transition: width 1.5s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 0 20px rgba(0, 212, 255, 0.5);
    position: relative;
}}

.global-fill::after {{
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 50%;
    background: linear-gradient(180deg, rgba(255, 255, 255, 0.3) 0%, transparent 100%);
}}

.global-pct {{
    text-align: right;
    font-size: 16px;
    font-weight: 900;
    margin-top: 8px;
    color: #00ff88;
}}

/* ==================== PANEL ==================== */
.panel {{
    margin-top: 16px;
    display: flex;
    gap: 16px;
}}

.panel-card {{
    flex: 1;
    background: linear-gradient(135deg, rgba(20, 28, 46, 0.9) 0%, rgba(10, 15, 26, 0.9) 100%);
    backdrop-filter: blur(10px);
    padding: 20px;
    border-radius: 20px;
    border: 1px solid rgba(100, 180, 255, 0.15);
    box-shadow: 
        0 8px 32px rgba(0, 0, 0, 0.3),
        inset 0 1px 0 rgba(255, 255, 255, 0.05);
}}

.panel-title {{
    font-size: 12px;
    color: rgba(255, 255, 255, 0.6);
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
}}

.panel-value {{
    font-size: 22px;
    font-weight: 900;
    margin-top: 8px;
}}

.panel-sub {{
    font-size: 13px;
    color: rgba(255, 255, 255, 0.7);
    margin-top: 6px;
    font-weight: 500;
}}

/* ==================== GRID ==================== */
.grid {{
    margin-top: 24px;
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 20px;
}}

/* ==================== TARJETAS MEDICAMENTOS ==================== */
.med-card {{
    background: linear-gradient(135deg, rgba(20, 28, 46, 0.95) 0%, rgba(10, 15, 26, 0.95) 100%);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(100, 180, 255, 0.15);
    border-radius: 24px;
    padding: 24px;
    min-height: 560px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    box-shadow: 
        0 12px 40px rgba(0, 0, 0, 0.4),
        inset 0 1px 0 rgba(255, 255, 255, 0.05);
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    overflow: hidden;
}}

.med-card::before {{
    content: '';
    position: absolute;
    top: -50%;
    right: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle, rgba(100, 180, 255, 0.03) 0%, transparent 70%);
    pointer-events: none;
    transition: opacity 0.4s;
}}

.med-card:hover {{
    transform: translateY(-8px);
    border-color: rgba(0, 212, 255, 0.4);
    box-shadow: 
        0 20px 60px rgba(0, 0, 0, 0.5),
        0 0 40px rgba(0, 212, 255, 0.2),
        inset 0 1px 0 rgba(255, 255, 255, 0.1);
}}

.med-card:hover::before {{
    opacity: 1.5;
}}

.med-title {{
    font-size: 17px;
    font-weight: 900;
    text-align: center;
    background: linear-gradient(135deg, #ffffff 0%, #c5d9ff 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 16px;
}}

.med-body {{
    display: flex;
    justify-content: center;
    gap: 16px;
    align-items: center;
    margin: 20px 0;
}}

/* ==================== IMÁGENES CON COLORES ORIGINALES ==================== */
.med-image-box {{
    width: 160px;
    height: 200px;
    border-radius: 20px;
    position: relative;
    overflow: hidden;
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.02) 0%, rgba(255, 255, 255, 0.01) 100%);
    border: 1px solid rgba(100, 180, 255, 0.1);
    display: flex;
    justify-content: center;
    align-items: center;
    box-shadow: inset 0 2px 10px rgba(0, 0, 0, 0.2);
}}

.img-container {{
    position: relative;
    width: 130px;
    height: 130px;
}}

.img-base {{
    position: absolute;
    width: 130px;
    height: 130px;
    filter: grayscale(100%) brightness(0.4);
    opacity: 0.5;
    z-index: 1;
}}

.img-fill {{
    position: absolute;
    bottom: 0;
    left: 0;
    width: 130px;
    overflow: hidden;
    z-index: 2;
    transition: height 1.2s cubic-bezier(0.4, 0, 0.2, 1);
}}

.img-colored {{
    position: absolute;
    bottom: 0;
    width: 130px;
    height: 130px;
}}

.img-shine {{
    position: absolute;
    top: 0;
    left: 0;
    width: 130px;
    height: 130px;
    background: linear-gradient(135deg, 
        transparent 0%, 
        rgba(255, 255, 255, 0.1) 45%, 
        rgba(255, 255, 255, 0.2) 50%, 
        rgba(255, 255, 255, 0.1) 55%, 
        transparent 100%);
    z-index: 3;
    pointer-events: none;
}}

.med-thermo {{
    width: 100px;
    height: 200px;
}}

/* ==================== VALORES ==================== */
.med-values {{
    margin: 16px 0;
    padding: 16px;
    background: rgba(255, 255, 255, 0.02);
    border-radius: 12px;
    border: 1px solid rgba(100, 180, 255, 0.08);
}}

.value-row {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 0;
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}}

.value-row:last-child {{
    border-bottom: none;
}}

.value-label {{
    font-size: 13px;
    color: rgba(255, 255, 255, 0.6);
    font-weight: 600;
}}

.value-num {{
    font-size: 15px;
    font-weight: 800;
    color: #ffffff;
}}

.value-num.highlight {{
    color: #ffd93d;
}}

/* ==================== BARRA DE PROGRESO ==================== */
.bar-container {{
    height: 20px;
    border-radius: 14px;
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(100, 180, 255, 0.1);
    overflow: hidden;
    margin-top: 12px;
    position: relative;
}}

.bar-container::before {{
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 50%;
    background: linear-gradient(180deg, rgba(255, 255, 255, 0.05) 0%, transparent 100%);
    pointer-events: none;
    z-index: 1;
}}

.bar-fill {{
    height: 100%;
    transition: width 1.2s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 0 16px rgba(0, 212, 255, 0.4);
    position: relative;
}}

.bar-fill::after {{
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 50%;
    background: linear-gradient(180deg, rgba(255, 255, 255, 0.2) 0%, transparent 100%);
}}

.pct-display {{
    font-size: 16px;
    font-weight: 900;
    text-align: right;
    margin-top: 8px;
    color: #00ff88;
}}

/* ==================== OVERLAY DONACIÓN ==================== */
.overlay {{
    position: fixed;
    top: 24px;
    right: 24px;
    padding: 16px 24px;
    background: linear-gradient(135deg, rgba(20, 28, 46, 0.98) 0%, rgba(10, 15, 26, 0.98) 100%);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(0, 212, 255, 0.3);
    border-radius: 16px;
    font-weight: 700;
    font-size: 14px;
    z-index: 999;
    box-shadow: 
        0 12px 40px rgba(0, 0, 0, 0.5),
        0 0 30px rgba(0, 212, 255, 0.2),
        inset 0 1px 0 rgba(255, 255, 255, 0.1);
    animation: slideIn 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}}

@keyframes slideIn {{
    from {{
        transform: translateX(400px);
        opacity: 0;
    }}
    to {{
        transform: translateX(0);
        opacity: 1;
    }}
}}

.overlay b {{
    color: #00ff88;
    font-weight: 900;
}}

/* ==================== RESPONSIVE ==================== */
@media (max-width: 1400px) {{
    .grid {{
        grid-template-columns: repeat(3, 1fr);
    }}
}}

@media (max-width: 1024px) {{
    .grid {{
        grid-template-columns: repeat(2, 1fr);
    }}
}}

@media (max-width: 768px) {{
    .grid {{
        grid-template-columns: 1fr;
    }}
    
    .summary {{
        flex-direction: column;
    }}
    
    .panel {{
        flex-direction: column;
    }}
}}
</style>
</head>

<body>

<!-- OVERLAY CON ÚLTIMA DONACIÓN (SOLO CONTACTO PÚBLICO O ANÓNIMO) -->
<div class="overlay">
    <div style="opacity: 0.7; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px;">
        🎁 Última donación
    </div>
    <div style="font-size: 16px;">
        <b>{ultimo_donante}</b>
    </div>
    <div style="margin-top: 8px; padding-top: 8px; border-top: 1px solid rgba(255,255,255,0.1);">
        Monto: <b>{formatear_numero(ultimo_monto)}</b><br>
        Hora: <b>{ultima_hora}</b>
    </div>
</div>

<div class="main">

    <!-- HEADER -->
    <div class="header">
        <div style="display:flex; align-items:center; gap:20px;">
            <div class="logo">GENEROSIDAD<br>COLOMBIA<br>2025</div>
            <div>
                <div class="title">Círculo de Generosidad</div>
                <div class="subtitle">{fecha_hoy}</div>
            </div>
        </div>

        <div class="header-right">✨ Córdoba nos necesita</div>
    </div>

    <!-- SUMMARY -->
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

    <!-- PANEL -->
    <div class="panel">
        <div class="panel-card">
            <div class="panel-title">🎯 Medicamento más crítico</div>
            <div class="panel-value" style="color:#ff6b9d;">{critico_nombre}</div>
            <div class="panel-sub">Avance: <b>{critico_pct:.1f}%</b></div>
            <div class="panel-sub">Faltan: <b style="color:#ffd93d;">{formatear_numero(critico_faltante)}</b></div>
        </div>

        <div class="panel-card">
            <div class="panel-title">🚀 Medicamento más avanzado</div>
            <div class="panel-value" style="color:#00ff88;">{mas_av_nombre}</div>
            <div class="panel-sub">Avance: <b>{mas_av_pct:.1f}%</b></div>
        </div>
    </div>

    <!-- GRID -->
    <div class="grid">
        {cards_html}
    </div>

</div>

<script>
    const metaCompleta = {str(hay_meta_completa).lower()};
    
    if(metaCompleta){{
        // Confetti cuando se alcanza una meta
        confetti({{
            particleCount: 250,
            spread: 140,
            origin: {{ y: 0.6 }},
            colors: ['#00d4ff', '#ff6b9d', '#00ff88', '#a855f7']
        }});
        
        setTimeout(() => {{
            confetti({{
                particleCount: 150,
                angle: 60,
                spread: 100,
                origin: {{ x: 0 }}
            }});
        }}, 300);
        
        setTimeout(() => {{
            confetti({{
                particleCount: 150,
                angle: 120,
                spread: 100,
                origin: {{ x: 1 }}
            }});
        }}, 300);
    }}

    // Auto-refresh cada 5 segundos
    setTimeout(() => {{
        window.location.reload();
    }}, 5000);
</script>

</body>
</html>
"""

components.html(html, height=1300, scrolling=True)




