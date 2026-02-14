import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_autorefresh import st_autorefresh
from datetime import datetime
import base64

# ==============================
# CONFIGURACIÓN PRINCIPAL
# ==============================
st.set_page_config(
    page_title="Subasta Solidaria - Medicamentos para Cuba",
    page_icon="💊",
    layout="wide"
)

# Refresco automático cada 2 segundos (NO requiere F5)
st_autorefresh(interval=2000, key="autorefresh")

# ==============================
# LINKS CSV (PEGA AQUÍ LOS TUYOS)
# ==============================
CSV_DONACIONES = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT2zRpYc-c3ZznxlPo51_k-5W3mNMzsxl8zlUzxCtugfc2ONIK_C-ht1DzKCR6vy2f1YSnwBx8umQxs/pub?gid=1533440022&single=true&output=csv"
CSV_METAS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT2zRpYc-c3ZznxlPo51_k-5W3mNMzsxl8zlUzxCtugfc2ONIK_C-ht1DzKCR6vy2f1YSnwBx8umQxs/pub?gid=199575778&single=true&output=csv"

# ==============================
# ESTILO PREMIUM
# ==============================
st.markdown("""
<style>
body {
    background-color: #0b0f17;
    color: white;
    font-family: 'Segoe UI', sans-serif;
}

.block-container {
    padding-top: 1.5rem;
}

.card {
    background: linear-gradient(145deg, #141a28, #0b0f17);
    padding: 18px;
    border-radius: 18px;
    box-shadow: 0px 0px 22px rgba(0,0,0,0.55);
    border: 1px solid rgba(255,255,255,0.10);
    transition: transform 0.2s ease-in-out;
    margin-bottom: 15px;
}

.card:hover {
    transform: scale(1.02);
}

.metric-title {
    font-size: 14px;
    opacity: 0.75;
    margin-bottom: 6px;
}

.metric-value {
    font-size: 26px;
    font-weight: 800;
}

.metric-sub {
    font-size: 13px;
    opacity: 0.75;
}

.badge {
    display: inline-block;
    padding: 5px 12px;
    border-radius: 12px;
    font-size: 12px;
    font-weight: 700;
    background-color: rgba(255,255,255,0.10);
    margin-right: 8px;
}

.alertbox {
    padding: 15px;
    border-radius: 14px;
    background: rgba(0, 200, 255, 0.12);
    border: 1px solid rgba(0, 200, 255, 0.35);
    font-weight: 700;
    font-size: 16px;
    margin-bottom: 15px;
}

.celebration {
    padding: 18px;
    border-radius: 14px;
    background: rgba(0, 255, 130, 0.12);
    border: 1px solid rgba(0, 255, 130, 0.35);
    font-weight: 800;
    font-size: 18px;
    margin-bottom: 15px;
    text-align: center;
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
        return f"{int(x):,}".replace(",", ".")
    except:
        return "0"


def reproducir_sonido_ding():
    # Sonido corto en base64 (beep simple)
    ding_base64 = """
    UklGRiQAAABXQVZFZm10IBAAAAABAAEAQB8AAIA+AAACABAAZGF0YQAAAAA=
    """
    audio_html = f"""
    <audio autoplay>
        <source src="data:audio/wav;base64,{ding_base64}" type="audio/wav">
    </audio>
    """
    st.markdown(audio_html, unsafe_allow_html=True)


# ==============================
# CARGAR DATOS
# ==============================
try:
    donaciones, metas = cargar_datos()
except:
    st.error("⚠️ No se pudieron cargar los datos. Revisa los links CSV.")
    st.stop()

donaciones.columns = [c.strip().lower() for c in donaciones.columns]
metas.columns = [c.strip().lower() for c in metas.columns]

# Google Forms suele traer "timestamp"
if "timestamp" in donaciones.columns and "fecha_hora" not in donaciones.columns:
    donaciones.rename(columns={"timestamp": "fecha_hora"}, inplace=True)

# ==============================
# AJUSTE IMPORTANTE: NOMBRE PÚBLICO PARA DASHBOARD
# ==============================
# Este campo viene del Google Form:
# "Nombre o entidad para mostrar en el dashboard (opcional)"

if "nombre o entidad para mostrar en el dashboard (opcional)" in donaciones.columns:
    donaciones.rename(
        columns={"nombre o entidad para mostrar en el dashboard (opcional)": "donante_publico"},
        inplace=True
    )

# Si el CSV público trae otra variante sin "(opcional)"
if "nombre o entidad para mostrar en el dashboard" in donaciones.columns:
    donaciones.rename(
        columns={"nombre o entidad para mostrar en el dashboard": "donante_publico"},
        inplace=True
    )

# Si no existe, crearla para evitar errores
if "donante_publico" not in donaciones.columns:
    donaciones["donante_publico"] = "Anónimo"

# Reemplazar vacíos por "Anónimo"
donaciones["donante_publico"] = donaciones["donante_publico"].fillna("").astype(str).str.strip()
donaciones.loc[donaciones["donante_publico"] == "", "donante_publico"] = "Anónimo"

# ==============================
# CAMBIO PRINCIPAL: SOPORTAR MULTI-MEDICAMENTOS POR FILA
# ==============================
# metas debe tener: medicamento | meta
# donaciones ahora tiene columnas: fecha_hora | donante_publico | medicamento1 | medicamento2 | ...
# cada medicamento es una columna numérica

if "medicamento" not in metas.columns or "meta" not in metas.columns:
    st.error("⚠️ El archivo METAS debe tener columnas: medicamento, meta")
    st.stop()

lista_medicamentos = metas["medicamento"].dropna().tolist()

# Validar que existan esas columnas en donaciones
for med in lista_medicamentos:
    if med not in donaciones.columns:
        donaciones[med] = 0

# Convertir a numérico todas las columnas de medicamentos
for med in lista_medicamentos:
    donaciones[med] = pd.to_numeric(donaciones[med], errors="coerce").fillna(0)

# ==============================
# CONTROL NUEVA DONACIÓN (BANNER + SONIDO)
# ==============================
if "ultima_fila" not in st.session_state:
    st.session_state.ultima_fila = len(donaciones)

if len(donaciones) > st.session_state.ultima_fila:
    st.markdown("""
    <div class="alertbox">🔔 Nueva donación registrada en tiempo real</div>
    """, unsafe_allow_html=True)
    reproducir_sonido_ding()

st.session_state.ultima_fila = len(donaciones)

# ==============================
# REESTRUCTURAR DONACIONES A FORMATO LARGO (medicamento, cantidad)
# ==============================
donaciones_largo = donaciones.melt(
    id_vars=[c for c in donaciones.columns if c not in lista_medicamentos],
    value_vars=lista_medicamentos,
    var_name="medicamento",
    value_name="cantidad"
)

# Quitar ceros (medicamentos que no donó)
donaciones_largo = donaciones_largo[donaciones_largo["cantidad"] > 0]

# ==============================
# CÁLCULOS PRINCIPALES
# ==============================
avance = donaciones_largo.groupby("medicamento", as_index=False)["cantidad"].sum()
avance = avance.merge(metas, on="medicamento", how="left")
avance["meta"] = avance["meta"].fillna(0)

avance["porcentaje"] = avance.apply(
    lambda row: (row["cantidad"] / row["meta"] * 100) if row["meta"] > 0 else 0,
    axis=1
)

total_recaudado = avance["cantidad"].sum()
total_meta = metas["meta"].sum()
porcentaje_total = (total_recaudado / total_meta * 100) if total_meta > 0 else 0

ranking = avance.sort_values("porcentaje", ascending=False)

# Últimas donaciones
ultimas = donaciones_largo.sort_values("fecha_hora", ascending=False).head(10)

# Donación más grande
donacion_mas_grande = donaciones_largo.loc[donaciones_largo["cantidad"].idxmax()] if len(donaciones_largo) > 0 else None

# ==============================
# CELEBRACIÓN 100%
# ==============================
completados = avance[avance["porcentaje"] >= 100]

if len(completados) > 0:
    meds = ", ".join(completados["medicamento"].tolist())
    st.markdown(f"""
    <div class="celebration">🎉 META ALCANZADA: {meds} 🎉</div>
    """, unsafe_allow_html=True)
    st.balloons()

# ==============================
# HEADER
# ==============================
st.markdown("""
<h1 style="text-align:center; font-size:48px;">💊 Subasta Solidaria - Medicamentos para Cuba</h1>
<p style="text-align:center; font-size:18px; opacity:0.8;">
Dashboard en vivo | Metas dinámicas | Registro inmediato de donaciones
</p>
""", unsafe_allow_html=True)

st.divider()

# ==============================
# PANEL PRINCIPAL SUPERIOR
# ==============================
c1, c2, c3, c4 = st.columns([2, 1, 1, 1])

with c1:
    st.markdown(f"""
    <div class="card">
        <div class="metric-title">🌍 Progreso Global</div>
        <div class="metric-value">{formatear_numero(total_recaudado)} / {formatear_numero(total_meta)}</div>
        <div class="metric-sub">Cumplimiento total: <b>{porcentaje_total:.2f}%</b></div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="card">
        <div class="metric-title">📦 Total Donado</div>
        <div class="metric-value">{formatear_numero(total_recaudado)}</div>
        <div class="metric-sub">Unidades registradas</div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="card">
        <div class="metric-title">🎯 Meta Total</div>
        <div class="metric-value">{formatear_numero(total_meta)}</div>
        <div class="metric-sub">Editable en Sheets</div>
    </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown(f"""
    <div class="card">
        <div class="metric-title">🧾 Registros</div>
        <div class="metric-value">{len(donaciones)}</div>
        <div class="metric-sub">Donaciones ingresadas</div>
    </div>
    """, unsafe_allow_html=True)

st.progress(min(porcentaje_total / 100, 1.0))
st.divider()

# ==============================
# TARJETAS POR MEDICAMENTO
# ==============================
st.markdown("## 💊 Avance por medicamento (en vivo)")

cols = st.columns(3)

for i, r in enumerate(avance.sort_values("porcentaje", ascending=False).to_dict("records")):
    porcentaje = r["porcentaje"]
    cantidad = r["cantidad"]
    meta = r["meta"]

    estado = "🔴 Bajo"
    if porcentaje >= 70:
        estado = "🟢 Excelente"
    elif porcentaje >= 40:
        estado = "🟠 Medio"

    with cols[i % 3]:
        st.markdown(f"""
        <div class="card">
            <h3>{r['medicamento']}</h3>
            <span class="badge">{estado}</span>
            <span class="badge">{porcentaje:.2f}%</span>
            <p style="margin-top:10px; font-size:20px; font-weight:800;">
                {formatear_numero(cantidad)} / {formatear_numero(meta)}
            </p>
            <p style="opacity:0.7; font-size:13px;">
                Donado: {formatear_numero(cantidad)} unidades
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.progress(min(porcentaje / 100, 1.0))

st.divider()

# ==============================
# RANKING + DONACIÓN MÁS GRANDE
# ==============================
left, right = st.columns([1.1, 1])

with left:
    st.markdown("## 🏆 Ranking de avance")
    for pos, r in enumerate(ranking.head(6).to_dict("records"), start=1):
        st.markdown(f"""
        <div class="card">
            <b>#{pos}</b> {r['medicamento']} <br>
            <span class="badge">Cumplimiento: {r['porcentaje']:.2f}%</span>
            <span class="badge">Donado: {formatear_numero(r['cantidad'])}</span>
        </div>
        """, unsafe_allow_html=True)

with right:
    st.markdown("## 💎 Donación más grande registrada")

    if donacion_mas_grande is not None:
        st.markdown(f"""
        <div class="card">
            <div class="metric-title">Mayor donación</div>
            <div class="metric-value">{formatear_numero(donacion_mas_grande['cantidad'])} unidades</div>
            <div class="metric-sub">
                Donante: <b>{donacion_mas_grande['donante_publico']}</b><br>
                Medicamento: <b>{donacion_mas_grande['medicamento']}</b>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("Aún no hay donaciones registradas.")

st.divider()

# ==============================
# ÚLTIMAS DONACIONES EN VIVO
# ==============================
st.markdown("## ⚡ Últimas donaciones registradas (en vivo)")

cols_tabla = ["fecha_hora", "donante_publico", "medicamento", "cantidad"]

st.dataframe(
    ultimas[cols_tabla],
    use_container_width=True,
    hide_index=True
)

st.divider()

# ==============================
# GRÁFICO DONACIONES POR MINUTO (VELOCIDAD)
# ==============================
st.markdown("## 🚀 Velocidad del evento (donaciones por minuto)")

try:
    donaciones_largo["fecha_hora"] = pd.to_datetime(donaciones_largo["fecha_hora"])
    donaciones_largo["minuto"] = donaciones_largo["fecha_hora"].dt.floor("min")

    velocidad = donaciones_largo.groupby("minuto", as_index=False)["cantidad"].sum()
    velocidad.rename(columns={"cantidad": "unidades_donadas"}, inplace=True)

    fig_vel = px.line(
        velocidad,
        x="minuto",
        y="unidades_donadas",
        markers=True,
        title="Unidades donadas por minuto"
    )

    fig_vel.update_layout(template="plotly_dark", height=400)
    st.plotly_chart(fig_vel, use_container_width=True)

except:
    st.warning("No se pudo generar el gráfico de velocidad. Revisa el formato de fecha_hora.")

# ==============================
# GRÁFICO DONADO VS META
# ==============================
st.markdown("## 📊 Comparativo general (donado vs meta)")

fig = px.bar(
    avance.sort_values("cantidad", ascending=True),
    x="cantidad",
    y="medicamento",
    orientation="h",
    text="cantidad",
    title="Donaciones acumuladas por medicamento"
)

fig.update_layout(template="plotly_dark", height=500)
st.plotly_chart(fig, use_container_width=True)

st.caption("📌 Este dashboard se actualiza automáticamente cada 2 segundos.")
