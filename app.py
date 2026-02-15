import streamlit as st
import pandas as pd
from datetime import datetime
import streamlit.components.v1 as components
from streamlit_autorefresh import st_autorefresh
import time
import hashlib
import requests
from io import StringIO

# ==============================
# CONFIGURACIÓN PRINCIPAL
# ==============================
st.set_page_config(
    page_title="Círculo de Generosidad 2026 - Dashboard",
    page_icon="🏥",
    layout="wide"
)

# ==============================
# AUTO-REFRESH
# ==============================
count = st_autorefresh(interval=8000, key="datarefresh")

# ==============================
# CARGA DE DATOS DESDE API (APPS SCRIPT)
# ==============================
API_URL = "https://script.google.com/macros/s/AKfycbzVt9cAlSVmC5kpDVBRHyj1ak_dKIDj5ZHuZcX7Niz12swOHgDhYnq9HzQegakkPFLqWg/exec"

try:
    resp = requests.get(API_URL)
    data = resp.json()

    donaciones_raw = data["donaciones"]
    metas_raw = data["metas"]

    donaciones = pd.DataFrame(donaciones_raw[1:], columns=donaciones_raw[0])
    metas = pd.DataFrame(metas_raw[1:], columns=metas_raw[0])

except Exception as e:
    st.error("❌ Error cargando datos desde la API")
    st.write(e)
    st.stop()

# ==============================
# INICIALIZAR SESSION STATE
# ==============================
if 'ultima_donacion_id' not in st.session_state:
    st.session_state.ultima_donacion_id = None

if 'mostrar_confeti' not in st.session_state:
    st.session_state.mostrar_confeti = False

# Guardar última versión "buena"
if "donaciones_guardadas" not in st.session_state:
    st.session_state.donaciones_guardadas = donaciones.copy()

# Guardar hash de dataset completo
if "hash_donaciones" not in st.session_state:
    st.session_state.hash_donaciones = hashlib.md5(pd.util.hash_pandas_object(donaciones, index=True).values.tobytes()).hexdigest()

# ==============================
# FUNCIONES
# ==============================
def generar_id_donacion(fila):
    contenido = f"{fila.get('fecha_hora', '')}{fila.get('donante_publico', '')}"
    for col in fila.index:
        if col not in ['fecha_hora', 'donante_publico', 'Donante', 'Contacto (opcional)']:
            contenido += str(fila[col])
    return hashlib.md5(contenido.encode()).hexdigest()

def formatear_numero(x):
    try:
        return f"{int(float(x)):,}".replace(",", ".")
    except:
        return "0"

def termometro_ultra_moderno_svg(pct, color="#00d4ff"):
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
        <rect x="52" y="{y}" width="26" height="{altura}" fill="url(#tube{hash(color)})" clip-path="url(#clipT{hash(color)})" filter="url(#neon{hash(color)})"/>
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
# NORMALIZAR COLUMNAS
# ==============================
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

metas["medicamento"] = metas["medicamento"].astype(str).str.strip()
metas["meta"] = pd.to_numeric(metas["meta"], errors="coerce").fillna(0)
lista_medicamentos = metas["medicamento"].tolist()

# ==============================
# NORMALIZACIÓN DONACIONES
# ==============================
if "Timestamp" in donaciones.columns:
    donaciones.rename(columns={"Timestamp": "fecha_hora"}, inplace=True)
elif "timestamp" in donaciones.columns:
    donaciones.rename(columns={"timestamp": "fecha_hora"}, inplace=True)

donaciones["donante_publico"] = donaciones.get("Contacto (opcional)", "").fillna("").astype(str).str.strip()
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
    donaciones[med] = pd.to_numeric(donaciones[med], errors="coerce").fillna(0)

# ==============================
# DETECCIÓN NUEVA DONACIÓN
# ==============================
ultimo_donante = "Donante anónimo"
ultima_hora = ""
ultimo_monto = 0
hay_nueva_donacion = False

if "fecha_hora" in donaciones.columns:
    try:
        donaciones["fecha_hora"] = pd.to_datetime(donaciones["fecha_hora"].astype(str).str.strip(), dayfirst=True, errors="coerce")
        donaciones_validas = donaciones.dropna(subset=["fecha_hora"])
        if len(donaciones_validas) > 0:
            fila_ultima = donaciones_validas.sort_values("fecha_hora", ascending=False).iloc[0]
            id_actual = generar_id_donacion(fila_ultima)

            if st.session_state.ultima_donacion_id != id_actual:
                st.session_state.ultima_donacion_id = id_actual
                st.session_state.mostrar_confeti = True
                hay_nueva_donacion = True
            else:
                st.session_state.mostrar_confeti = False

            ultimo_donante = fila_ultima["donante_publico"]
            ultimo_monto = sum([float(fila_ultima[med]) for med in lista_medicamentos])
            ultima_hora = fila_ultima["fecha_hora"].strftime("%H:%M:%S")
    except Exception as e:
        print(f"Error procesando última donación: {e}")

# ==============================
# PROCESAMIENTO DE DATOS PARA DASHBOARD
# ==============================
donaciones_largo = donaciones.melt(
    id_vars=[c for c in donaciones.columns if c not in lista_medicamentos],
    value_vars=lista_medicamentos,
    var_name="medicamento",
    value_name="cantidad"
)
donaciones_largo = donaciones_largo[donaciones_largo["cantidad"] > 0]

donado_por_med = donaciones_largo.groupby("medicamento", as_index=False)["cantidad"].sum()

avance = metas.merge(donado_por_med, on="medicamento", how="left")
avance["cantidad"] = avance["cantidad"].fillna(0)
avance["faltante"] = (avance["meta"] - avance["cantidad"]).clip(lower=0)
avance["porcentaje"] = avance.apply(lambda r: (r["cantidad"] / r["meta"] * 100) if r["meta"]>0 else 0, axis=1)

total_recaudado = avance["cantidad"].sum()
total_meta = avance["meta"].sum()
porcentaje_total = (total_recaudado / total_meta * 100) if total_meta>0 else 0
fecha_hoy = datetime.now().strftime("%d de %B de %Y")




