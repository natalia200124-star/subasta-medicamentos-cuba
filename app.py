import streamlit as st
import pandas as pd
from datetime import datetime
import streamlit.components.v1 as components

# ==============================
# CONFIGURACIÓN PRINCIPAL
# ==============================
st.set_page_config(
    page_title="Círculo de Generación 2026 - Dashboard",
    page_icon="🏥",
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
@st.cache_data(ttl=5)  # ✅ 5 SEGUNDOS - BALANCE ENTRE VELOCIDAD Y ACTUALIZACIÓN
def cargar_datos():
    """Carga datos con cache ligero de 5 segundos"""
    donaciones = pd.read_csv(CSV_DONACIONES)
    metas = pd.read_csv(CSV_METAS)
    return donaciones, metas


def formatear_numero(x):
    """Formatea números con separadores de miles"""
    try:
        return f"{int(float(x)):,}".replace(",", ".")
    except:
        return "0"


def termometro_moderno_svg(pct, color="#00d4ff"):
    """Termómetro compacto con diseño moderno"""
    pct = max(0, min(float(pct), 100))
    altura = int(100 * (pct / 100))
    y = 130 - altura

    return f"""
    <svg viewBox="0 0 110 180">
        <defs>
            <linearGradient id="bulb{hash(color)}" x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" style="stop-color:{color};stop-opacity:1" />
                <stop offset="100%" style="stop-color:{color};stop-opacity:0.7" />
            </linearGradient>
            <linearGradient id="tube{hash(color)}" x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" style="stop-color:{color};stop-opacity:1" />
                <stop offset="100%" style="stop-color:{color};stop-opacity:0.7" />
            </linearGradient>
            <filter id="neon{hash(color)}">
                <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
                <feMerge>
                    <feMergeNode in="coloredBlur"/>
                    <feMergeNode in="SourceGraphic"/>
                </feMerge>
            </filter>
        </defs>
        
        <circle cx="55" cy="150" r="18" fill="rgba(10,15,30,0.5)" stroke="{color}" stroke-width="2" opacity="0.5"/>
        <rect x="45" y="30" width="20" height="120" rx="10" fill="rgba(10,15,30,0.5)" stroke="{color}" stroke-width="2" opacity="0.5"/>

        <clipPath id="clipT{hash(color)}">
            <rect x="45" y="30" width="20" height="120" rx="10"/>
        </clipPath>

        <rect x="45" y="{y}" width="20" height="{altura}" fill="url(#tube{hash(color)})" 
              clip-path="url(#clipT{hash(color)})" filter="url(#neon{hash(color)})"/>

        <circle cx="55" cy="150" r="14" fill="url(#bulb{hash(color)})" filter="url(#neon{hash(color)})"/>
        <circle cx="55" cy="150" r="8" fill="white" opacity="0.3"/>
        
        <text x="55" y="175" text-anchor="middle" fill="{color}" font-size="12" font-weight="900">{pct:.0f}%</text>
    </svg>
    """


# ==============================
# CARGA DE DATOS
# ==============================
try:
    donaciones, metas = cargar_datos()
except Exception as e:
    st.error(f"❌ Error al cargar datos: {str(e)}")
    st.stop()

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
# NORMALIZACIÓN DONACIONES - PRIVACIDAD
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
# CREAR COLUMNAS MEDICAMENTOS
# ==============================
for med in lista_medicamentos:
    if med not in donaciones.columns:
        donaciones[med] = 0

for med in lista_medicamentos:
    donaciones[med] = pd.to_numeric(donaciones[med], errors="coerce").fillna(0)


# ==============================
# ÚLTIMA DONACIÓN
# ==============================
ultimo_donante = "Donante anónimo"
ultima_hora = ""
ultimo_monto = 0

if "fecha_hora" in donaciones.columns:
    try:
        donaciones["fecha_hora"] = pd.to_datetime(donaciones["fecha_hora"], format="%d/%m/%Y %H:%M:%S", errors="coerce")
        donaciones_validas = donaciones.dropna(subset=["fecha_hora"])
        
        if len(donaciones_validas) > 0:
            donaciones_validas = donaciones_validas.sort_values("fecha_hora", ascending=False)
            fila_ultima = donaciones_validas.iloc[0]
            
            ultimo_donante = fila_ultima["donante_publico"]
            
            suma_medicamentos = 0
            for med in lista_medicamentos:
                suma_medicamentos += float(fila_ultima[med])
            
            ultimo_monto = suma_medicamentos
            ultima_hora = fila_ultima["fecha_hora"].strftime("%H:%M:%S")
    except Exception as e:
        print(f"Error procesando última donación: {e}")


# ==============================
# CALCULOS
# ==============================
donaciones_largo = donaciones.melt(
    id_vars=[c for c in donaciones.columns if c not in lista_medicamentos],
    value_vars=lista_medicamentos,
    var_name="medicamento",
    value_name="cantidad"
)

donaciones_largo = donaciones_largo[donaciones_largo["cantidad"] > 0]

donado_por_med = donaciones_largo.groupby("medicamento", as_index=False)["cantidad"].sum()

metas_temp = metas.copy()
metas_temp["medicamento_lower"] = metas_temp["medicamento"].str.lower()

donado_por_med["medicamento_lower"] = donado_por_med["medicamento"].str.lower()

avance = metas_temp.merge(donado_por_med, on="medicamento_lower", how="left", suffixes=("", "_don"))
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
# COLORES
# ==============================
COLORES_MEDICAMENTOS = [
    "#00D4FF",  # Cyan
    "#FF3D71",  # Rosa
    "#00FF9F",  # Verde
    "#FFB800",  # Dorado
    "#B24BF3",  # Púrpura
    "#FF6B35",  # Naranja
]


# ==============================
# IMÁGENES DE MEDICAMENTOS - SOLO ILUSTRACIONES
# ==============================
IMG_MAP = {
    "multivitaminas (gotas)": "https://cdn-icons-png.flaticon.com/512/3004/3004458.png",  # ✅ Frasco gotero
    "vitaminas c (gotas)": "https://cdn-icons-png.flaticon.com/512/2966/2966493.png",  # ✅ Píldoras/tabletas
    "vitamina a y d2 (gotas)": "https://cdn-icons-png.flaticon.com/512/2966/2966334.png",  # ✅ Botella medicina
    "vitamina d2 forte (gotas)": "https://cdn-icons-png.flaticon.com/512/3774/3774299.png",  # ✅ Frasco medicina
    "vitamina b (gotas)": "https://cdn-icons-png.flaticon.com/512/2913/2913133.png",  # ✅ Cápsulas
    "fumarato ferroso en suspensión": "https://cdn-icons-png.flaticon.com/512/3037/3037069.png",  # ✅ Botella jarabe
}

DEFAULT_IMG = "https://cdn-icons-png.flaticon.com/512/2913/2913155.png"


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

hay_meta_completa = (avance["porcentaje"] >= 100).any() if len(avance) > 0 else False


# ==============================
# TARJETAS COMPACTAS
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
    thermo = termometro_moderno_svg(pct, color=color_main)

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
                             style="filter: drop-shadow(0 0 10px {color_main}) brightness(1.2);"/>
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
# HTML OPTIMIZADO
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
    font-family: 'Inter', -apple-system, system-ui, sans-serif;
    background: #060A12;
    color: #E5E9F0;
    min-height: 100vh;
    overflow-x: hidden;
    position: relative;
}}

body::before {{
    content: '';
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: 
        radial-gradient(circle at 15% 20%, rgba(0, 212, 255, 0.08) 0%, transparent 40%),
        radial-gradient(circle at 85% 80%, rgba(255, 61, 113, 0.08) 0%, transparent 40%),
        radial-gradient(circle at 50% 50%, rgba(0, 255, 159, 0.05) 0%, transparent 50%);
    pointer-events: none;
    z-index: 0;
    animation: pulse 8s ease-in-out infinite;
}}

@keyframes pulse {{
    0%, 100% {{ opacity: 1; }}
    50% {{ opacity: 0.8; }}
}}

body::after {{
    content: '';
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-image: 
        radial-gradient(2px 2px at 20% 30%, rgba(255,255,255,0.15), transparent),
        radial-gradient(2px 2px at 60% 70%, rgba(0,212,255,0.2), transparent),
        radial-gradient(1px 1px at 50% 50%, rgba(255,61,113,0.2), transparent);
    background-size: 200px 200px, 300px 300px, 250px 250px;
    background-position: 0 0, 40px 60px, 130px 270px;
    animation: float 20s linear infinite;
    pointer-events: none;
    z-index: 0;
}}

@keyframes float {{
    0% {{ transform: translateY(0px); }}
    50% {{ transform: translateY(-20px); }}
    100% {{ transform: translateY(0px); }}
}}

.main {{
    max-width: 1920px;
    margin: 0 auto;
    padding: 24px;
    position: relative;
    z-index: 1;
}}

.header {{
    background: linear-gradient(135deg, rgba(15, 23, 42, 0.95) 0%, rgba(8, 15, 30, 0.95) 100%);
    backdrop-filter: blur(30px) saturate(180%);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 24px;
    padding: 24px 32px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;
    box-shadow: 
        0 20px 60px rgba(0, 0, 0, 0.5),
        inset 0 1px 0 rgba(255, 255, 255, 0.1);
    position: relative;
    overflow: hidden;
}}

.header::before {{
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 200%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.03), transparent);
    animation: shimmer 3s infinite;
}}

@keyframes shimmer {{
    0% {{ transform: translateX(-100%); }}
    100% {{ transform: translateX(100%); }}
}}

.logo {{
    background: linear-gradient(135deg, #00D4FF 0%, #0091FF 100%);
    color: #060A12;
    padding: 12px 18px;
    border-radius: 16px;
    font-weight: 900;
    font-size: 11px;
    line-height: 1.4;
    text-align: center;
    letter-spacing: 0.8px;
    box-shadow: 
        0 8px 32px rgba(0, 212, 255, 0.4),
        inset 0 2px 0 rgba(255, 255, 255, 0.5);
    text-transform: uppercase;
}}

.title {{
    font-size: 32px;
    font-weight: 900;
    background: linear-gradient(135deg, #FFFFFF 0%, #00D4FF 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: -1px;
}}

.subtitle {{
    font-size: 14px;
    color: rgba(255, 255, 255, 0.5);
    margin-top: 4px;
    font-weight: 600;
}}

.header-badge {{
    font-size: 16px;
    font-weight: 800;
    color: #00FF9F;
    padding: 12px 24px;
    background: rgba(0, 255, 159, 0.12);
    border: 2px solid rgba(0, 255, 159, 0.3);
    border-radius: 14px;
    box-shadow: 0 0 30px rgba(0, 255, 159, 0.3);
    text-transform: uppercase;
    letter-spacing: 1px;
}}

.summary {{
    display: grid;
    grid-template-columns: 1fr 1fr 2fr;
    gap: 16px;
    margin-bottom: 24px;
}}

.summary-card {{
    background: linear-gradient(135deg, rgba(15, 23, 42, 0.9) 0%, rgba(8, 15, 30, 0.9) 100%);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 20px;
    padding: 20px;
    box-shadow: 
        0 15px 50px rgba(0, 0, 0, 0.4),
        inset 0 1px 0 rgba(255, 255, 255, 0.08);
    transition: all 0.4s ease;
}}

.summary-card:hover {{
    transform: translateY(-4px);
    border-color: rgba(0, 212, 255, 0.3);
}}

.summary-label {{
    font-size: 11px;
    color: rgba(255, 255, 255, 0.5);
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin-bottom: 8px;
}}

.summary-number {{
    font-size: 36px;
    font-weight: 900;
    background: linear-gradient(135deg, #FFFFFF 0%, #00D4FF 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    line-height: 1.1;
}}

.global-progress {{
    margin-top: 12px;
}}

.progress-track {{
    height: 24px;
    border-radius: 16px;
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.08);
    overflow: hidden;
    position: relative;
}}

.progress-active {{
    height: 100%;
    background: linear-gradient(90deg, #00D4FF 0%, #00FF9F 100%);
    width: {max(0, min(porcentaje_total, 100))}%;
    transition: width 2s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 0 30px rgba(0, 212, 255, 0.6);
}}

.progress-percent {{
    text-align: right;
    font-size: 16px;
    font-weight: 900;
    margin-top: 8px;
    color: #00FF9F;
}}

.panel {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
    margin-bottom: 24px;
}}

.panel-card {{
    background: linear-gradient(135deg, rgba(15, 23, 42, 0.9) 0%, rgba(8, 15, 30, 0.9) 100%);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 20px;
    padding: 20px;
    box-shadow: 0 15px 50px rgba(0, 0, 0, 0.4);
    transition: all 0.3s ease;
}}

.panel-card:hover {{
    transform: translateY(-3px);
}}

.panel-label {{
    font-size: 10px;
    color: rgba(255, 255, 255, 0.5);
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin-bottom: 6px;
}}

.panel-title {{
    font-size: 20px;
    font-weight: 900;
    margin-bottom: 8px;
}}

.panel-info {{
    font-size: 13px;
    color: rgba(255, 255, 255, 0.7);
    margin-top: 6px;
    font-weight: 600;
}}

/* ==================== GRID COMPACTO 3x2 ==================== */
.grid {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 18px;
}}

/* ==================== CARDS COMPACTAS ==================== */
.med-card {{
    background: linear-gradient(135deg, rgba(15, 23, 42, 0.95) 0%, rgba(8, 15, 30, 0.95) 100%);
    backdrop-filter: blur(30px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 22px;
    padding: 20px;
    min-height: 420px;  /* ✅ REDUCIDO de 580px a 420px */
    display: flex;
    flex-direction: column;
    box-shadow: 
        0 15px 50px rgba(0, 0, 0, 0.5),
        inset 0 1px 0 rgba(255, 255, 255, 0.1);
    transition: all 0.4s ease;
    position: relative;
    overflow: hidden;
}}

.med-card:hover {{
    transform: translateY(-8px) scale(1.01);
    border-color: rgba(0, 212, 255, 0.4);
    box-shadow: 
        0 25px 70px rgba(0, 0, 0, 0.6),
        0 0 50px rgba(0, 212, 255, 0.3);
}}

.med-header {{
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 16px;
    gap: 10px;
}}

.med-title {{
    font-size: 15px;
    font-weight: 900;
    background: linear-gradient(135deg, #FFFFFF 0%, #C5D9FF 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    flex: 1;
    line-height: 1.3;
}}

.med-badge {{
    padding: 6px 12px;
    border-radius: 10px;
    font-size: 12px;
    font-weight: 900;
    text-align: center;
    min-width: 60px;
}}

.med-body {{
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 16px;
    margin: 16px 0;
    flex: 1;
}}

/* ==================== IMÁGENES COMPACTAS ==================== */
.med-image-container {{
    width: 140px;  /* ✅ REDUCIDO de 180px */
    height: 170px;  /* ✅ REDUCIDO de 220px */
    border-radius: 20px;
    position: relative;
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.03) 0%, rgba(255, 255, 255, 0.01) 100%);
    border: 1px solid rgba(255, 255, 255, 0.08);
    display: flex;
    justify-content: center;
    align-items: center;
    overflow: hidden;
}}

.image-glow {{
    position: absolute;
    width: 100%;
    height: 100%;
    border-radius: 20px;
    filter: blur(25px);
    opacity: 0.4;
    z-index: 0;
}}

.img-wrapper {{
    position: relative;
    width: 110px;  /* ✅ REDUCIDO de 140px */
    height: 110px;
    z-index: 1;
}}

.img-base {{
    position: absolute;
    width: 110px;
    height: 110px;
    filter: grayscale(100%) brightness(0.3);
    opacity: 0.4;
    z-index: 1;
}}

.img-fill-container {{
    position: absolute;
    bottom: 0;
    left: 0;
    width: 110px;
    overflow: hidden;
    z-index: 2;
    transition: height 1.5s cubic-bezier(0.4, 0, 0.2, 1);
}}

.img-colored {{
    position: absolute;
    bottom: 0;
    width: 110px;
    height: 110px;
}}

.img-shimmer {{
    position: absolute;
    top: 0;
    left: 0;
    width: 110px;
    height: 110px;
    background: linear-gradient(135deg, 
        transparent 0%, 
        rgba(255, 255, 255, 0.1) 45%, 
        rgba(255, 255, 255, 0.2) 50%, 
        rgba(255, 255, 255, 0.1) 55%, 
        transparent 100%);
    z-index: 3;
    pointer-events: none;
    animation: shimmer-img 3s infinite;
}}

@keyframes shimmer-img {{
    0% {{ transform: translateX(-100%); }}
    100% {{ transform: translateX(100%); }}
}}

.med-thermo {{
    width: 90px;  /* ✅ REDUCIDO de 110px */
    height: 180px;
}}

.med-stats {{
    display: grid;
    grid-template-columns: 1fr auto 1fr auto 1fr;
    align-items: center;
    padding: 14px;  /* ✅ REDUCIDO de 20px */
    background: rgba(255, 255, 255, 0.02);
    border-radius: 14px;
    border: 1px solid rgba(255, 255, 255, 0.05);
    margin-bottom: 14px;
}}

.stat-item {{
    text-align: center;
}}

.stat-label {{
    font-size: 10px;
    color: rgba(255, 255, 255, 0.5);
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 4px;
}}

.stat-value {{
    font-size: 15px;  /* ✅ REDUCIDO de 18px */
    font-weight: 900;
    color: #FFFFFF;
}}

.stat-value.warning {{
    color: #FFB800;
}}

.stat-divider {{
    width: 1px;
    height: 35px;
    background: rgba(255, 255, 255, 0.1);
}}

.progress-bar {{
    height: 18px;  /* ✅ REDUCIDO de 22px */
    border-radius: 14px;
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.08);
    overflow: hidden;
    position: relative;
}}

.progress-fill {{
    height: 100%;
    transition: width 1.5s cubic-bezier(0.4, 0, 0.2, 1);
    z-index: 1;
}}

.progress-glow {{
    position: absolute;
    top: 0;
    left: 0;
    height: 100%;
    filter: blur(10px);
    transition: width 1.5s cubic-bezier(0.4, 0, 0.2, 1);
}}

.donation-overlay {{
    position: fixed;
    top: 24px;
    right: 24px;
    padding: 16px 24px;
    background: linear-gradient(135deg, rgba(15, 23, 42, 0.98) 0%, rgba(8, 15, 30, 0.98) 100%);
    backdrop-filter: blur(30px);
    border: 1px solid rgba(0, 212, 255, 0.4);
    border-radius: 18px;
    font-weight: 700;
    font-size: 14px;
    z-index: 999;
    box-shadow: 
        0 20px 60px rgba(0, 0, 0, 0.6),
        0 0 40px rgba(0, 212, 255, 0.3);
    animation: slideInRight 0.6s ease;
    min-width: 260px;
}}

@keyframes slideInRight {{
    from {{ transform: translateX(400px); opacity: 0; }}
    to {{ transform: translateX(0); opacity: 1; }}
}}

.donation-header {{
    opacity: 0.6;
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 6px;
    font-weight: 800;
}}

.donation-name {{
    font-size: 16px;
    color: #00FF9F;
    font-weight: 900;
    margin-bottom: 10px;
}}

.donation-details {{
    margin-top: 10px;
    padding-top: 10px;
    border-top: 1px solid rgba(255, 255, 255, 0.1);
    display: flex;
    justify-content: space-between;
    gap: 14px;
}}

.donation-detail {{
    flex: 1;
}}

.donation-detail-label {{
    font-size: 9px;
    opacity: 0.6;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 3px;
}}

.donation-detail-value {{
    font-size: 14px;
    font-weight: 900;
    color: #00D4FF;
}}

@media (max-width: 1400px) {{
    .grid {{ grid-template-columns: repeat(3, 1fr); }}
}}

@media (max-width: 1024px) {{
    .grid {{ grid-template-columns: repeat(2, 1fr); }}
    .summary {{ grid-template-columns: 1fr; }}
    .panel {{ grid-template-columns: 1fr; }}
}}

@media (max-width: 768px) {{
    .grid {{ grid-template-columns: 1fr; }}
}}
</style>
</head>

<body>

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

<div class="main">

    <div class="header">
        <div style="display: flex; align-items: center; gap: 20px;">
            <div class="logo">Generosidad<br>Colombia<br>2025</div>
            <div>
                <div class="title">Círculo de Generación 2026</div>
                <div class="subtitle">{fecha_hoy}</div>
            </div>
        </div>
        <div class="header-badge">🇨🇺 Cuba nos necesita</div>
    </div>

    <div class="summary">
        <div class="summary-card">
            <div class="summary-label">Total Meta</div>
            <div class="summary-number">{formatear_numero(total_meta)}</div>
        </div>

        <div class="summary-card">
            <div class="summary-label">Total Recolectado</div>
            <div class="summary-number">{formatear_numero(total_recaudado)}</div>
        </div>

        <div class="summary-card">
            <div class="summary-label">Avance Global</div>
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
            <div class="panel-label">🎯 Medicamento más crítico</div>
            <div class="panel-title" style="color: #FF3D71;">{critico_nombre}</div>
            <div class="panel-info">Avance: <b>{critico_pct:.1f}%</b></div>
            <div class="panel-info">Faltan: <b style="color: #FFB800;">{formatear_numero(critico_faltante)}</b></div>
        </div>

        <div class="panel-card">
            <div class="panel-label">🚀 Medicamento más avanzado</div>
            <div class="panel-title" style="color: #00FF9F;">{mas_av_nombre}</div>
            <div class="panel-info">Avance: <b>{mas_av_pct:.1f}%</b></div>
        </div>
    </div>

    <div class="grid">
        {cards_html}
    </div>

</div>

<script>
    const metaCompleta = {str(hay_meta_completa).lower()};
    
    if(metaCompleta) {{
        confetti({{
            particleCount: 300,
            spread: 160,
            origin: {{ y: 0.6 }},
            colors: ['#00D4FF', '#FF3D71', '#00FF9F', '#B24BF3', '#FFB800']
        }});
        
        setTimeout(() => {{
            confetti({{
                particleCount: 200,
                angle: 60,
                spread: 100,
                origin: {{ x: 0 }},
                colors: ['#00D4FF', '#00FF9F']
            }});
        }}, 250);
        
        setTimeout(() => {{
            confetti({{
                particleCount: 200,
                angle: 120,
                spread: 100,
                origin: {{ x: 1 }},
                colors: ['#FF3D71', '#B24BF3']
            }});
        }}, 400);
    }}

    // ✅ SOLO JAVASCRIPT RELOAD - SIN st.rerun()
    setTimeout(function() {{
        location.reload(true);
    }}, 5000);  // 5 segundos
</script>

</body>
</html>
"""

components.html(html, height=1200, scrolling=True)

