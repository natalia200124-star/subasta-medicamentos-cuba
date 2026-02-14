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
# ESTILO CORPORATIVO PREMIUM (SIN EMOJIS)
# ==============================
st.markdown("""
<style>
body {
    background: radial-gradient(circle at top, #121b2e 0%, #070a12 70%);
    color: white;
    font-family: 'Segoe UI', sans-serif;
}

.block-container {
    padding-top: 1.0rem;
}

.header-bar {
    background: linear-gradient(90deg, #101624, #0b0f17);
    padding: 18px 25px;
    border-radius: 18px;
    border: 1px solid rgba(255,255,255,0.08);
    margin-bottom: 20px;
    box-shadow: 0px 0px 20px rgba(0,0,0,0.55);
}

.header-title {
    font-size: 34px;
    font-weight: 800;
    margin: 0px;
}

.header-subtitle {
    font-size: 15px;
    opacity: 0.75;
    margin-top: 4px;
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
    transform: scale(1.01);
}

.metric-title {
    font-size: 13px;
    opacity: 0.75;
    margin-bottom: 6px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.metric-value {
    font-size: 28px;
    font-weight: 900;
}

.metric-sub {
    font-size: 13px;
    opacity: 0.70;
}

.badge {
    display: inline-block;
    padding: 6px 12px;
    border-radius: 14px;
    font-size: 12px;
    font-weight: 700;
    background-color: rgba(255,255,255,0.10);
    margin-right: 8px;
    margin-top: 8px;
}

.alertbox {
    padding: 14px;
    border-radius: 14px;
    background: rgba(0, 200, 255, 0.12);
    border: 1px solid rgba(0, 200, 255, 0.35);
    font-weight: 700;
    font-size: 15px;
    margin-bottom: 15px;
}

.celebration {
    padding: 18px;
    border-radius: 14px;
    background: rgba(0, 255, 130, 0.12);
    border: 1px solid rgba(0, 255, 130, 0.35);
    font-weight: 900;
    font-size: 18px;
    margin-bottom: 15px;
    text-align: center;
}

.ticker {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    padding: 12px;
    border-radius: 14px;
    overflow: hidden;
    height: 200px;
    position: relative;
}

.ticker-content {
    position: absolute;
    width: 100%;
    animation: scrollTicker 15s linear infinite;
}

@keyframes scrollTicker {
    0% { top: 100%; }
    100% { top: -120%; }
}

.ticker-item {
    padding: 10px 8px;
    border-bottom: 1px solid rgba(255,255,255,0.05);
    font-size: 14px;
    opacity: 0.85;
}

.med-title {
    font-size: 16px;
    font-weight: 900;
    margin-bottom: 10px;
}

/* ==============================
   NUEVO DISEÑO PREMIUM MEDICAMENTOS
============================== */
.med-card {
    background: linear-gradient(145deg, #131a29, #0b0f17);
    border-radius: 22px;
    padding: 18px;
    border: 1px solid rgba(255,255,255,0.10);
    box-shadow: 0px 0px 25px rgba(0,0,0,0.65);
    transition: all 0.25s ease-in-out;
    min-height: 320px;
    margin-bottom: 16px;
}

.med-card:hover {
    transform: translateY(-4px);
    border: 1px solid rgba(0, 220, 255, 0.35);
    box-shadow: 0px 0px 40px rgba(0,0,0,0.75);
}

.med-img {
    width: 100%;
    height: 130px;
    border-radius: 18px;
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.08);
    display: flex;
    justify-content: center;
    align-items: center;
    margin-bottom: 14px;
}

.med-name {
    font-size: 18px;
    font-weight: 900;
    margin-bottom: 8px;
}

.med-meta {
    font-size: 13px;
    opacity: 0.75;
    margin-bottom: 10px;
}

.progress-bar {
    width: 100%;
    height: 12px;
    border-radius: 10px;
    background: rgba(255,255,255,0.08);
    overflow: hidden;
    margin-top: 8px;
    margin-bottom: 12px;
}

.progress-fill {
    height: 100%;
    border-radius: 10px;
    background: linear-gradient(90deg, rgba(0,220,255,0.95), rgba(0,110,255,0.75));
    transition: width 0.9s ease-in-out;
}

.progress-percent {
    font-size: 14px;
    font-weight: 800;
    margin-bottom: 6px;
}

.status-pill {
    display: inline-block;
    padding: 6px 12px;
    border-radius: 16px;
    font-size: 12px;
    font-weight: 800;
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.12);
    margin-top: 10px;
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
    ding_base64 = """
    UklGRiQAAABXQVZFZm10IBAAAAABAAEAQB8AAIA+AAACABAAZGF0YQAAAAA=
    """
    audio_html = f"""
    <audio autoplay>
        <source src="data:audio/wav;base64,{ding_base64}" type="audio/wav">
    </audio>
    """
    st.markdown(audio_html, unsafe_allow_html=True)


def obtener_svg_medicamento(nombre):
    nombre = nombre.lower()

    if "gota" in nombre or "gotas" in nombre:
        return """
        <svg width="120" height="120" viewBox="0 0 200 200">
            <rect x="70" y="30" width="60" height="120" rx="20" fill="rgba(255,255,255,0.15)" stroke="rgba(255,255,255,0.35)" stroke-width="4"/>
            <rect x="80" y="10" width="40" height="30" rx="8" fill="rgba(255,255,255,0.20)" stroke="rgba(255,255,255,0.35)" stroke-width="4"/>
            <circle cx="100" cy="170" r="22" fill="rgba(255,255,255,0.10)" stroke="rgba(255,255,255,0.35)" stroke-width="4"/>
        </svg>
        """

    if "capsula" in nombre or "cápsula" in nombre:
        return """
        <svg width="140" height="120" viewBox="0 0 220 180">
            <rect x="50" y="60" width="120" height="60" rx="30" fill="rgba(255,255,255,0.15)" stroke="rgba(255,255,255,0.35)" stroke-width="4"/>
            <line x1="110" y1="60" x2="110" y2="120" stroke="rgba(255,255,255,0.35)" stroke-width="4"/>
        </svg>
        """

    if "jarabe" in nombre or "suspensión" in nombre or "suspension" in nombre:
        return """
        <svg width="130" height="130" viewBox="0 0 200 200">
            <rect x="70" y="40" width="60" height="120" rx="15" fill="rgba(255,255,255,0.12)" stroke="rgba(255,255,255,0.35)" stroke-width="4"/>
            <rect x="75" y="20" width="50" height="30" rx="8" fill="rgba(255,255,255,0.18)" stroke="rgba(255,255,255,0.35)" stroke-width="4"/>
            <rect x="75" y="95" width="50" height="25" rx="10" fill="rgba(255,255,255,0.08)" stroke="rgba(255,255,255,0.25)" stroke-width="3"/>
        </svg>
        """

    return """
    <svg width="130" height="130" viewBox="0 0 200 200">
        <rect x="65" y="50" width="70" height="110" rx="18" fill="rgba(255,255,255,0.12)" stroke="rgba(255,255,255,0.35)" stroke-width="4"/>
        <rect x="75" y="25" width="50" height="35" rx="10" fill="rgba(255,255,255,0.18)" stroke="rgba(255,255,255,0.35)" stroke-width="4"/>
    </svg>
    """


# ==============================
# CARGAR DATOS
# ==============================
try:
    donaciones, metas = cargar_datos()
except:
    st.error("No se pudieron cargar los datos. Revisa los links CSV.")
    st.stop()

donaciones.columns = [c.strip().lower() for c in donaciones.columns]
metas.columns = [c.strip().lower() for c in metas.columns]

# Google Forms suele traer "timestamp"
if "timestamp" in donaciones.columns and "fecha_hora" not in donaciones.columns:
    donaciones.rename(columns={"timestamp": "fecha_hora"}, inplace=True)

# ==============================
# AJUSTE IMPORTANTE: NOMBRE PÚBLICO PARA DASHBOARD
# ==============================
if "nombre o entidad para mostrar en el dashboard (opcional)" in donaciones.columns:
    donaciones.rename(
        columns={"nombre o entidad para mostrar en el dashboard (opcional)": "donante_publico"},
        inplace=True
    )

if "nombre o entidad para mostrar en el dashboard" in donaciones.columns:
    donaciones.rename(
        columns={"nombre o entidad para mostrar en el dashboard": "donante_publico"},
        inplace=True
    )

if "donante_publico" not in donaciones.columns:
    donaciones["donante_publico"] = "Anónimo"

donaciones["donante_publico"] = donaciones["donante_publico"].fillna("").astype(str).str.strip()
donaciones.loc[donaciones["donante_publico"] == "", "donante_publico"] = "Anónimo"

# ==============================
# VALIDACIÓN METAS
# ==============================
if "medicamento" not in metas.columns or "meta" not in metas.columns:
    st.error("El archivo METAS debe tener columnas: medicamento, meta")
    st.stop()

lista_medicamentos = metas["medicamento"].dropna().tolist()

# Validar que existan esas columnas en donaciones
for med in lista_medicamentos:
    if med.lower() not in donaciones.columns:
        donaciones[med.lower()] = 0

# Convertir a numérico
for med in lista_medicamentos:
    donaciones[med.lower()] = pd.to_numeric(donaciones[med.lower()], errors="coerce").fillna(0)

# ==============================
# CONTROL NUEVA DONACIÓN (BANNER + SONIDO)
# ==============================
if "ultima_fila" not in st.session_state:
    st.session_state.ultima_fila = len(donaciones)

if len(donaciones) > st.session_state.ultima_fila:
    st.markdown("""
    <div class="alertbox">Nueva donación registrada en tiempo real</div>
    """, unsafe_allow_html=True)
    reproducir_sonido_ding()

st.session_state.ultima_fila = len(donaciones)

# ==============================
# FORMATO LARGO DONACIONES
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
metas_temp = metas.copy()
metas_temp["medicamento"] = metas_temp["medicamento"].astype(str).str.strip().str.lower()
metas_temp["meta"] = pd.to_numeric(metas_temp["meta"], errors="coerce").fillna(0)

avance = donaciones_largo.groupby("medicamento", as_index=False)["cantidad"].sum()
avance = avance.merge(metas_temp, on="medicamento", how="left")
avance["meta"] = avance["meta"].fillna(0)

avance["porcentaje"] = avance.apply(
    lambda row: (row["cantidad"] / row["meta"] * 100) if row["meta"] > 0 else 0,
    axis=1
)

total_recaudado = avance["cantidad"].sum()
total_meta = metas_temp["meta"].sum()
porcentaje_total = (total_recaudado / total_meta * 100) if total_meta > 0 else 0

ranking = avance.sort_values("porcentaje", ascending=False)

ultimas = donaciones_largo.sort_values("fecha_hora", ascending=False).head(10)

donacion_mas_grande = donaciones_largo.loc[donaciones_largo["cantidad"].idxmax()] if len(donaciones_largo) > 0 else None

# ==============================
# CREAR AVANCE COMPLETO (MUESTRA TODOS LOS MEDICAMENTOS)
# ==============================
donado_por_med = donaciones_largo.groupby("medicamento", as_index=False)["cantidad"].sum()

avance_completo = metas_temp.merge(donado_por_med, on="medicamento", how="left")
avance_completo["cantidad"] = avance_completo["cantidad"].fillna(0)

avance_completo["porcentaje"] = avance_completo.apply(
    lambda row: (row["cantidad"] / row["meta"] * 100) if row["meta"] > 0 else 0,
    axis=1
)

avance_completo = avance_completo.sort_values("porcentaje", ascending=False)

# Para mostrar nombres originales como están en metas
map_nombre_original = dict(zip(metas_temp["medicamento"], metas["medicamento"]))

# ==============================
# HEADER CORPORATIVO
# ==============================
st.markdown(f"""
<div class="header-bar">
    <div class="header-title">Subasta Solidaria - Medicamentos para Cuba</div>
    <div class="header-subtitle">
        Dashboard en vivo | Metas dinámicas | Registro inmediato de donaciones
    </div>
</div>
""", unsafe_allow_html=True)

# ==============================
# CELEBRACIÓN 100%
# ==============================
completados = avance_completo[avance_completo["porcentaje"] >= 100]

if len(completados) > 0:
    meds = ", ".join([map_nombre_original.get(m, m) for m in completados["medicamento"].tolist()])
    st.markdown(f"""
    <div class="celebration">Meta alcanzada: {meds}</div>
    """, unsafe_allow_html=True)
    st.balloons()

# ==============================
# PANEL SUPERIOR
# ==============================
c1, c2, c3, c4 = st.columns([2, 1, 1, 1])

with c1:
    st.markdown(f"""
    <div class="card">
        <div class="metric-title">Progreso global</div>
        <div class="metric-value">{formatear_numero(total_recaudado)} / {formatear_numero(total_meta)}</div>
        <div class="metric-sub">Cumplimiento total: <b>{porcentaje_total:.2f}%</b></div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="card">
        <div class="metric-title">Total donado</div>
        <div class="metric-value">{formatear_numero(total_recaudado)}</div>
        <div class="metric-sub">Unidades registradas</div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="card">
        <div class="metric-title">Meta total</div>
        <div class="metric-value">{formatear_numero(total_meta)}</div>
        <div class="metric-sub">Editable en Google Sheets</div>
    </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown(f"""
    <div class="card">
        <div class="metric-title">Registros</div>
        <div class="metric-value">{len(donaciones)}</div>
        <div class="metric-sub">Donaciones registradas</div>
    </div>
    """, unsafe_allow_html=True)

st.progress(min(porcentaje_total / 100, 1.0))
st.divider()

# ==============================
# AVANCE POR MEDICAMENTO (TARJETAS PREMIUM)
# ==============================
st.markdown("## Avance por medicamento")

cols = st.columns(3)

for i, r in enumerate(avance_completo.to_dict("records")):
    porcentaje = float(r["porcentaje"])
    cantidad = float(r["cantidad"])
    meta = float(r["meta"])
    med = r["medicamento"]

    nombre_original = map_nombre_original.get(med, med)

    estado = "Nivel bajo"
    if porcentaje >= 70:
        estado = "Nivel excelente"
    elif porcentaje >= 40:
        estado = "Nivel medio"

    porcentaje_barra = max(0, min(porcentaje, 100))

    svg = obtener_svg_medicamento(nombre_original)

    with cols[i % 3]:
        st.markdown(f"""
        <div class="med-card">

            <div class="med-img">
                {svg}
            </div>

            <div class="med-name">{nombre_original}</div>

            <div class="progress-percent">{porcentaje:.1f}%</div>

            <div class="progress-bar">
                <div class="progress-fill" style="width:{porcentaje_barra}%;"></div>
            </div>

            <div class="med-meta">
                Donado: <b>{formatear_numero(cantidad)}</b> &nbsp; | &nbsp;
                Meta: <b>{formatear_numero(meta)}</b>
            </div>

            <div class="status-pill">{estado}</div>

        </div>
        """, unsafe_allow_html=True)

st.divider()

# ==============================
# RANKING + MAYOR DONACIÓN
# ==============================
left, right = st.columns([1.1, 1])

with left:
    st.markdown("## Ranking de avance")

    ranking_completo = avance_completo.sort_values("porcentaje", ascending=False)

    for pos, r in enumerate(ranking_completo.head(6).to_dict("records"), start=1):
        med = r["medicamento"]
        nombre_original = map_nombre_original.get(med, med)

        st.markdown(f"""
        <div class="card">
            <b>{pos}</b> {nombre_original}<br>
            <span class="badge">Cumplimiento: {r['porcentaje']:.2f}%</span>
            <span class="badge">Donado: {formatear_numero(r['cantidad'])}</span>
        </div>
        """, unsafe_allow_html=True)

with right:
    st.markdown("## Mayor donación registrada")

    if donacion_mas_grande is not None:
        st.markdown(f"""
        <div class="card">
            <div class="metric-title">Mayor donación</div>
            <div class="metric-value">{formatear_numero(donacion_mas_grande['cantidad'])} unidades</div>
            <div class="metric-sub">
                Donante: <b>{donacion_mas_grande['donante_publico']}</b><br>
                Medicamento: <b>{map_nombre_original.get(donacion_mas_grande['medicamento'], donacion_mas_grande['medicamento'])}</b>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("Aún no hay donaciones registradas.")

st.divider()

# ==============================
# ÚLTIMAS DONACIONES (TICKER)
# ==============================
st.markdown("## Últimas donaciones registradas")

if len(ultimas) > 0:
    ticker_html = "<div class='ticker'><div class='ticker-content'>"

    for _, row in ultimas.iterrows():
        fecha = str(row.get("fecha_hora", ""))
        donante = str(row.get("donante_publico", "Anónimo"))
        med = str(row.get("medicamento", ""))
        med = map_nombre_original.get(med, med)
        cantidad = formatear_numero(row.get("cantidad", 0))

        ticker_html += f"""
        <div class='ticker-item'>
            <b>{donante}</b> donó <b>{cantidad}</b> unidades de <b>{med}</b><br>
            <span style="opacity:0.6; font-size:12px;">{fecha}</span>
        </div>
        """

    ticker_html += "</div></div>"

    st.markdown(ticker_html, unsafe_allow_html=True)

else:
    st.info("No hay donaciones registradas todavía.")

st.divider()

# ==============================
# GRÁFICO DONACIONES POR MINUTO
# ==============================
st.markdown("## Velocidad del evento (donaciones por minuto)")

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
st.markdown("## Comparativo general (donado vs meta)")

fig = px.bar(
    avance_completo.sort_values("cantidad", ascending=True),
    x="cantidad",
    y="medicamento",
    orientation="h",
    text="cantidad",
    title="Donaciones acumuladas por medicamento"
)

fig.update_layout(template="plotly_dark", height=500)
st.plotly_chart(fig, use_container_width=True)

st.caption("Este dashboard se actualiza automáticamente cada 2 segundos.")


st.caption("Este dashboard se actualiza automáticamente cada 2 segundos.")

