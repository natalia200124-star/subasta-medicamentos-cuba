import streamlit as st
import pandas as pd
from datetime import datetime
import streamlit.components.v1 as components
import time

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
def cargar_datos():
    """Carga datos SIN cache - actualización inmediata garantizada"""
    donaciones = pd.read_csv(CSV_DONACIONES)
    metas = pd.read_csv(CSV_METAS)
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
        
        <!-- Glow externo -->
        <circle cx="65" cy="170" r="26" fill="{color}" opacity="0.15" filter="blur(8px)"/>
        
        <!-- Bulbo base -->
        <circle cx="65" cy="170" r="22" fill="rgba(10,15,30,0.5)" stroke="{color}" stroke-width="2.5" opacity="0.5"/>
        
        <!-- Tubo base -->
        <rect x="52" y="35" width="26" height="135" rx="13" fill="rgba(10,15,30,0.5)" stroke="{color}" stroke-width="2.5" opacity="0.5"/>

        <clipPath id="clipT{hash(color)}">
            <rect x="52" y="35" width="26" height="135" rx="13"/>
        </clipPath>

        <!-- Relleno animado -->
        <rect x="52" y="{y}" width="26" height="{altura}" fill="url(#tube{hash(color)})" 
              clip-path="url(#clipT{hash(color)})" filter="url(#neon{hash(color)})"/>

        <!-- Bulbo lleno -->
        <circle cx="65" cy="170" r="18" fill="url(#bulb{hash(color)})" filter="url(#neon{hash(color)})"/>
        
        <!-- Brillo interno -->
        <circle cx="65" cy="170" r="10" fill="white" opacity="0.3"/>
        
        <!-- Marcas -->
        <line x1="79" y1="50" x2="88" y2="50" stroke="{color}" stroke-width="2" opacity="0.6"/>
        <line x1="79" y1="80" x2="88" y2="80" stroke="{color}" stroke-width="2" opacity="0.6"/>
        <line x1="79" y1="110" x2="88" y2="110" stroke="{color}" stroke-width="2" opacity="0.6"/>
        <line x1="79" y1="140" x2="88" y2="140" stroke="{color}" stroke-width="2" opacity="0.6"/>
        
        <!-- Texto de porcentaje -->
        <text x="65" y="200" text-anchor="middle" fill="{color}" font-size="14" font-weight="900" opacity="0.9">{pct:.0f}%</text>
    </svg>
    """


# ==============================
# CARGA DE DATOS DIRECTA
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

# ✅ CRÍTICO: Solo usar "Contacto (opcional)", NUNCA "Donante"
if "Contacto (opcional)" in donaciones.columns:
    donaciones["donante_publico"] = donaciones["Contacto (opcional)"].fillna("").astype(str).str.strip()
else:
    donaciones["donante_publico"] = ""

# Convertir vacíos a "Donante anónimo"
donaciones.loc[donaciones["donante_publico"] == "", "donante_publico"] = "Donante anónimo"
donaciones.loc[donaciones["donante_publico"].str.lower() == "nan", "donante_publico"] = "Donante anónimo"

# Eliminar la columna "Donante" para evitar confusiones
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
# ÚLTIMA DONACIÓN - SOLO CONTACTO PÚBLICO
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
            
            # ✅ USAR SOLO CONTACTO PÚBLICO
            ultimo_donante = fila_ultima["donante_publico"]
            
            suma_medicamentos = 0
            for med in lista_medicamentos:
                suma_medicamentos += float(fila_ultima[med])
            
            ultimo_monto = suma_medicamentos
            ultima_hora = fila_ultima["fecha_hora"].strftime("%H:%M:%S")
    except Exception as e:
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

metas_temp = metas.copy()
metas_temp["medicamento_lower"] = metas_temp["medicamento"].str.lower()

# Crear diccionario para mapear nombres
map_medicamentos = {}
for med in lista_medicamentos:
    map_medicamentos[med.lower()] = med

# Normalizar nombres en donado_por_med
donado_por_med["medicamento_lower"] = donado_por_med["medicamento"].str.lower()

# Merge
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
# PALETA DE COLORES PREMIUM HEALTHTECH
# ==============================
COLORES_MEDICAMENTOS = [
    "#00D4FF",  # Cyan eléctrico
    "#FF3D71",  # Rosa neón
    "#00FF9F",  # Verde esmeralda
    "#FFB800",  # Dorado brillante
    "#B24BF3",  # Púrpura vibrante
    "#FF6B35",  # Naranja cálido
]


# ==============================
# ✅ IMÁGENES DE MEDICAMENTOS REALES - SIN JERINGAS NI INSTRUMENTAL
# ==============================
IMG_MAP = {
    "multivitaminas (gotas)": "https://cdn-icons-png.flaticon.com/512/3774/3774239.png",  # Frasco con gotero
    "vitaminas c (gotas)": "https://cdn-icons-png.flaticon.com/512/2966/2966327.png",  # Cápsula de vitamina
    "vitamina a y d2 (gotas)": "https://cdn-icons-png.flaticon.com/512/3209/3209265.png",  # Jarabe/frasco líquido
    "vitamina d2 forte (gotas)": "https://cdn-icons-png.flaticon.com/512/3643/3643747.png",  # Gotero/gotas
    "vitamina b (gotas)": "https://cdn-icons-png.flaticon.com/512/10473/10473325.png",  # Pastillas/tabletas
    "fumarato ferroso en suspensión": "https://cdn-icons-png.flaticon.com/512/2785/2785629.png",  # Botella de medicina líquida
}

DEFAULT_IMG = "https://cdn-icons-png.flaticon.com/512/3774/3774299.png"  # Medicamento genérico

# ✅ Imagen especial del corazón (mantener la original o usar una bonita)
CORAZON_IMG = "https://cdn-icons-png.flaticon.com/512/833/833472.png"  # Corazón ilustrado bonito


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
# TARJETAS CON DISEÑO ULTRA PREMIUM
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
                    <!-- Imagen base gris -->
                    <img src="{img_url}" class="img-base"/>
                    
                    <!-- Contenedor de llenado -->
                    <div class="img-fill-container" style="height: {pct_bar}%;">
                        <img src="{img_url}" class="img-colored" 
                             style="filter: drop-shadow(0 0 12px {color_main}) brightness(1.2);"/>
                    </div>
                    
                    <!-- Efecto de brillo -->
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
# HTML ULTRA PREMIUM - DISEÑO REVOLUCIONARIO
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

/* ==================== FONDO ANIMADO ==================== */
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

/* Partículas flotantes */
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
        radial-gradient(1px 1px at 50% 50%, rgba(255,61,113,0.2), transparent),
        radial-gradient(1px 1px at 80% 10%, rgba(0,255,159,0.15), transparent);
    background-size: 200px 200px, 300px 300px, 250px 250px, 350px 350px;
    background-position: 0 0, 40px 60px, 130px 270px, 70px 100px;
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
    padding: 30px;
    position: relative;
    z-index: 1;
}}

/* ==================== HEADER PREMIUM ==================== */
.header {{
    background: linear-gradient(135deg, rgba(15, 23, 42, 0.95) 0%, rgba(8, 15, 30, 0.95) 100%);
    backdrop-filter: blur(30px) saturate(180%);
    -webkit-backdrop-filter: blur(30px) saturate(180%);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 28px;
    padding: 32px 40px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 30px;
    box-shadow: 
        0 20px 60px rgba(0, 0, 0, 0.5),
        0 0 80px rgba(0, 212, 255, 0.1),
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
    padding: 16px 22px;
    border-radius: 18px;
    font-weight: 900;
    font-size: 12px;
    line-height: 1.4;
    text-align: center;
    letter-spacing: 0.8px;
    box-shadow: 
        0 8px 32px rgba(0, 212, 255, 0.4),
        inset 0 2px 0 rgba(255, 255, 255, 0.5);
    text-transform: uppercase;
}}

.title {{
    font-size: 38px;
    font-weight: 900;
    background: linear-gradient(135deg, #FFFFFF 0%, #00D4FF 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: -1px;
    text-shadow: 0 0 40px rgba(0, 212, 255, 0.3);
}}

.subtitle {{
    font-size: 15px;
    color: rgba(255, 255, 255, 0.5);
    margin-top: 6px;
    font-weight: 600;
    letter-spacing: 0.5px;
}}

.header-badge {{
    font-size: 18px;
    font-weight: 800;
    color: #00FF9F;
    padding: 14px 28px;
    background: rgba(0, 255, 159, 0.12);
    border: 2px solid rgba(0, 255, 159, 0.3);
    border-radius: 16px;
    box-shadow: 
        0 0 30px rgba(0, 255, 159, 0.3),
        inset 0 1px 0 rgba(255, 255, 255, 0.1);
    text-transform: uppercase;
    letter-spacing: 1px;
}}

/* ==================== SUMMARY ==================== */
.summary {{
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 20px;
    margin-bottom: 30px;
}}

.summary-card {{
    background: linear-gradient(135deg, rgba(15, 23, 42, 0.9) 0%, rgba(8, 15, 30, 0.9) 100%);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 24px;
    padding: 28px;
    box-shadow: 
        0 15px 50px rgba(0, 0, 0, 0.4),
        inset 0 1px 0 rgba(255, 255, 255, 0.08);
    transition: all 0.3s ease;
}}

.summary-card:hover {{
    transform: translateY(-5px);
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
    border-color: rgba(0, 212, 255, 0.3);
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
    background: linear-gradient(135deg, #FFFFFF 0%, #00D4FF 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}}

/* ==================== PROGRESO GLOBAL ==================== */
.global-progress {{
    margin-top: 8px;
}}

.progress-track {{
    height: 28px;
    border-radius: 20px;
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    overflow: hidden;
    position: relative;
}}

.progress-active {{
    height: 100%;
    width: {porcentaje_total:.1f}%;
    background: linear-gradient(90deg, #00FF9F 0%, #00D4FF 100%);
    border-radius: 20px;
    position: relative;
    transition: width 2s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 
        0 0 30px rgba(0, 255, 159, 0.5),
        inset 0 2px 0 rgba(255, 255, 255, 0.3);
}}

.progress-active::before {{
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 50%;
    background: linear-gradient(180deg, rgba(255, 255, 255, 0.08) 0%, transparent 100%);
    pointer-events: none;
    z-index: 2;
}}

.progress-active::after {{
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 50%;
    background: linear-gradient(180deg, rgba(255, 255, 255, 0.4) 0%, transparent 100%);
}}

.progress-percent {{
    text-align: right;
    font-size: 18px;
    font-weight: 900;
    margin-top: 10px;
    color: #00FF9F;
    text-shadow: 0 0 20px rgba(0, 255, 159, 0.5);
}}

/* ==================== PANEL ==================== */
.panel {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
    margin-bottom: 30px;
}}

.panel-card {{
    background: linear-gradient(135deg, rgba(15, 23, 42, 0.9) 0%, rgba(8, 15, 30, 0.9) 100%);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 24px;
    padding: 24px;
    box-shadow: 
        0 15px 50px rgba(0, 0, 0, 0.4),
        inset 0 1px 0 rgba(255, 255, 255, 0.08);
    transition: all 0.3s ease;
}}

.panel-card:hover {{
    transform: translateY(-3px);
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
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

/* ==================== GRID 3x2 MEDICAMENTOS ==================== */
.grid {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 24px;
}}

/* ==================== TARJETAS MEDICAMENTOS ULTRA PREMIUM ==================== */
.med-card {{
    background: linear-gradient(135deg, rgba(15, 23, 42, 0.95) 0%, rgba(8, 15, 30, 0.95) 100%);
    backdrop-filter: blur(30px) saturate(180%);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 28px;
    padding: 28px;
    min-height: 580px;
    display: flex;
    flex-direction: column;
    box-shadow: 
        0 20px 60px rgba(0, 0, 0, 0.5),
        inset 0 1px 0 rgba(255, 255, 255, 0.1);
    transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
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
    background: radial-gradient(circle, rgba(255, 255, 255, 0.03) 0%, transparent 70%);
    pointer-events: none;
    transition: opacity 0.5s;
}}

.med-card:hover {{
    transform: translateY(-12px) scale(1.02);
    border-color: rgba(0, 212, 255, 0.5);
    box-shadow: 
        0 30px 80px rgba(0, 0, 0, 0.6),
        0 0 60px rgba(0, 212, 255, 0.3),
        inset 0 1px 0 rgba(255, 255, 255, 0.2);
}}

.med-card:hover::before {{
    opacity: 1.8;
}}

.med-header {{
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 24px;
    gap: 12px;
}}

.med-title {{
    font-size: 18px;
    font-weight: 900;
    background: linear-gradient(135deg, #FFFFFF 0%, #C5D9FF 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    flex: 1;
    line-height: 1.3;
}}

.med-badge {{
    padding: 8px 16px;
    border-radius: 12px;
    font-size: 14px;
    font-weight: 900;
    text-align: center;
    min-width: 70px;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
}}

.med-body {{
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 24px;
    margin: 24px 0;
    flex: 1;
}}

/* ==================== IMÁGENES MEJORADAS ==================== */
.med-image-container {{
    width: 180px;
    height: 220px;
    border-radius: 24px;
    position: relative;
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.03) 0%, rgba(255, 255, 255, 0.01) 100%);
    border: 1px solid rgba(255, 255, 255, 0.08);
    display: flex;
    justify-content: center;
    align-items: center;
    overflow: hidden;
    box-shadow: 
        inset 0 2px 20px rgba(0, 0, 0, 0.3),
        0 8px 24px rgba(0, 0, 0, 0.2);
}}

.image-glow {{
    position: absolute;
    width: 100%;
    height: 100%;
    border-radius: 24px;
    filter: blur(30px);
    opacity: 0.4;
    z-index: 0;
}}

.img-wrapper {{
    position: relative;
    width: 140px;
    height: 140px;
    z-index: 1;
}}

.img-base {{
    position: absolute;
    width: 140px;
    height: 140px;
    filter: grayscale(100%) brightness(0.3);
    opacity: 0.4;
    z-index: 1;
}}

.img-fill-container {{
    position: absolute;
    bottom: 0;
    left: 0;
    width: 140px;
    overflow: hidden;
    z-index: 2;
    transition: height 1.5s cubic-bezier(0.4, 0, 0.2, 1);
}}

.img-colored {{
    position: absolute;
    bottom: 0;
    width: 140px;
    height: 140px;
}}

.img-shimmer {{
    position: absolute;
    top: 0;
    left: 0;
    width: 140px;
    height: 140px;
    background: linear-gradient(135deg, 
        transparent 0%, 
        rgba(255, 255, 255, 0.1) 45%, 
        rgba(255, 255, 255, 0.25) 50%, 
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
    width: 110px;
    height: 210px;
}}

/* ==================== ESTADÍSTICAS ==================== */
.med-stats {{
    display: grid;
    grid-template-columns: 1fr auto 1fr auto 1fr;
    align-items: center;
    padding: 20px;
    background: rgba(255, 255, 255, 0.02);
    border-radius: 16px;
    border: 1px solid rgba(255, 255, 255, 0.05);
    margin-bottom: 20px;
}}

.stat-item {{
    text-align: center;
}}

.stat-label {{
    font-size: 11px;
    color: rgba(255, 255, 255, 0.5);
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 6px;
}}

.stat-value {{
    font-size: 18px;
    font-weight: 900;
    color: #FFFFFF;
}}

.stat-value.warning {{
    color: #FFB800;
}}

.stat-divider {{
    width: 1px;
    height: 40px;
    background: rgba(255, 255, 255, 0.1);
}}

/* ==================== BARRA DE PROGRESO ==================== */
.progress-bar {{
    height: 22px;
    border-radius: 16px;
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.08);
    overflow: hidden;
    position: relative;
}}

.progress-bar::before {{
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 50%;
    background: linear-gradient(180deg, rgba(255, 255, 255, 0.08) 0%, transparent 100%);
    pointer-events: none;
    z-index: 2;
}}

.progress-fill {{
    height: 100%;
    transition: width 1.5s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    z-index: 1;
}}

.progress-fill::after {{
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 50%;
    background: linear-gradient(180deg, rgba(255, 255, 255, 0.25) 0%, transparent 100%);
}}

.progress-glow {{
    position: absolute;
    top: 0;
    left: 0;
    height: 100%;
    filter: blur(12px);
    transition: width 1.5s cubic-bezier(0.4, 0, 0.2, 1);
}}

/* ==================== OVERLAY DONACIÓN ==================== */
.donation-overlay {{
    position: fixed;
    top: 30px;
    right: 30px;
    padding: 20px 28px;
    background: linear-gradient(135deg, rgba(15, 23, 42, 0.98) 0%, rgba(8, 15, 30, 0.98) 100%);
    backdrop-filter: blur(30px) saturate(180%);
    border: 1px solid rgba(0, 212, 255, 0.4);
    border-radius: 20px;
    font-weight: 700;
    font-size: 15px;
    z-index: 999;
    box-shadow: 
        0 20px 60px rgba(0, 0, 0, 0.6),
        0 0 40px rgba(0, 212, 255, 0.3),
        inset 0 1px 0 rgba(255, 255, 255, 0.15);
    animation: slideInRight 0.6s cubic-bezier(0.4, 0, 0.2, 1);
    min-width: 280px;
}}

@keyframes slideInRight {{
    from {{
        transform: translateX(500px);
        opacity: 0;
    }}
    to {{
        transform: translateX(0);
        opacity: 1;
    }}
}}

.donation-header {{
    opacity: 0.6;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 8px;
    font-weight: 800;
}}

.donation-name {{
    font-size: 18px;
    color: #00FF9F;
    font-weight: 900;
    margin-bottom: 12px;
    text-shadow: 0 0 20px rgba(0, 255, 159, 0.5);
}}

.donation-details {{
    margin-top: 12px;
    padding-top: 12px;
    border-top: 1px solid rgba(255, 255, 255, 0.1);
    display: flex;
    justify-content: space-between;
    gap: 16px;
}}

.donation-detail {{
    flex: 1;
}}

.donation-detail-label {{
    font-size: 10px;
    opacity: 0.6;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 4px;
}}

.donation-detail-value {{
    font-size: 16px;
    font-weight: 900;
    color: #00D4FF;
}}

/* ==================== RESPONSIVE ==================== */
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

<div class="main">

    <!-- HEADER -->
    <div class="header">
        <div style="display: flex; align-items: center; gap: 24px;">
            <div class="logo">Generosidad<br>Colombia<br>2025</div>
            <div>
                <div class="title">Círculo de Generación 2026</div>
                <div class="subtitle">{fecha_hoy}</div>
            </div>
        </div>
        <div class="header-badge">🇨🇺 Cuba nos necesita</div>
    </div>

    <!-- SUMMARY -->
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

    <!-- PANEL -->
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

    <!-- GRID 3x2 -->
    <div class="grid">
        {cards_html}
    </div>

</div>

<script>
    const metaCompleta = {str(hay_meta_completa).lower()};
    
    if(metaCompleta) {{
        // Celebración cuando se alcanza meta
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

    // ✅ ACTUALIZACIÓN EN TIEMPO REAL - RECARGA CADA 3 SEGUNDOS
    setTimeout(function() {{
        location.reload(true);
    }}, 3000);
</script>

</body>
</html>
"""

components.html(html, height=1400, scrolling=True)

# ✅ ACTUALIZACIÓN DIRECTA - Recarga cada 3 segundos
time.sleep(3)
st.rerun()
