import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh
from datetime import datetime

# ==========================================================
# CONFIGURACIÓN GENERAL
# ==========================================================
st.set_page_config(
    page_title="Círculo de Generosidad",
    page_icon="💙",
    layout="wide"
)

# Auto refresco cada 20 segundos
st_autorefresh(interval=20000, key="data_refresh")

# ==========================================================
# LINKS CSV PUBLICADOS DESDE GOOGLE SHEETS
# ==========================================================
DONACIONES_URL = "PON_AQUI_EL_LINK_DE_DONACIONES_PUBLICO.csv"
METAS_URL = "PON_AQUI_EL_LINK_DE_METAS.csv"

# ==========================================================
# CARGA DE DATOS
# ==========================================================
@st.cache_data(ttl=20)
def cargar_donaciones():
    df = pd.read_csv(DONACIONES_URL)
    df.columns = [c.strip() for c in df.columns]
    return df

@st.cache_data(ttl=20)
def cargar_metas():
    df = pd.read_csv(METAS_URL)
    df.columns = [c.strip() for c in df.columns]
    return df

# ==========================================================
# VALIDACIÓN Y LIMPIEZA
# ==========================================================
def limpiar_donaciones(df):
    if "Timestamp" in df.columns:
        df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce")

    # Convertir columnas de medicamentos a numérico
    for col in df.columns:
        if col != "Timestamp" and col != "Nombre para mostrar":
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    return df

def limpiar_metas(df):
    df["Meta"] = pd.to_numeric(df["Meta"], errors="coerce").fillna(0)
    return df

# ==========================================================
# ESTILOS PROFESIONALES (CSS)
# ==========================================================
st.markdown("""
<style>

body {
    background: linear-gradient(180deg, #f6f9ff 0%, #eef3ff 100%);
    font-family: "Segoe UI", sans-serif;
}

.main {
    padding-top: 0px;
}

.dashboard-header {
    display:flex;
    align-items:center;
    justify-content:space-between;
    background:white;
    border-radius:18px;
    padding:18px 25px;
    box-shadow: 0px 8px 22px rgba(0,0,0,0.08);
    margin-bottom: 18px;
}

.header-left {
    display:flex;
    align-items:center;
    gap:18px;
}

.logo-box {
    width:90px;
    height:90px;
    background: #244a87;
    border-radius:16px;
    display:flex;
    justify-content:center;
    align-items:center;
    color:white;
    font-weight:800;
    font-size:14px;
    text-align:center;
    line-height:1.2;
}

.title-box h1 {
    margin:0px;
    font-size:32px;
    font-weight:800;
    color:#0d1b3d;
}

.title-box p {
    margin:0px;
    color:#506089;
    font-size:14px;
}

.header-right {
    font-size:15px;
    color:#0d1b3d;
    font-weight:600;
    text-align:right;
}

.kpi-container {
    display:flex;
    gap:18px;
    width:100%;
    margin-bottom: 20px;
}

.kpi-card {
    flex:1;
    background:white;
    border-radius:18px;
    padding:18px 22px;
    box-shadow: 0px 8px 18px rgba(0,0,0,0.06);
    border-left: 6px solid #2c6bed;
}

.kpi-title {
    font-size:14px;
    color:#667085;
    font-weight:600;
    margin-bottom:6px;
}

.kpi-value {
    font-size:28px;
    font-weight:900;
    color:#0d1b3d;
}

.progress-global {
    background:white;
    border-radius:18px;
    padding:18px 22px;
    box-shadow: 0px 8px 18px rgba(0,0,0,0.06);
    margin-bottom: 18px;
}

.progress-title {
    font-size:15px;
    font-weight:700;
    color:#0d1b3d;
    margin-bottom:10px;
}

.progress-bar-outer {
    width:100%;
    height:16px;
    background:#e7ecf7;
    border-radius:12px;
    overflow:hidden;
}

.progress-bar-inner {
    height:16px;
    border-radius:12px;
    background: linear-gradient(90deg, #2c6bed, #00d4ff);
    transition: width 1.2s ease-in-out;
}

.progress-label {
    margin-top:8px;
    font-weight:700;
    color:#244a87;
}

.section-title {
    font-size:18px;
    font-weight:800;
    color:#0d1b3d;
    margin-top:10px;
    margin-bottom:12px;
}

.med-grid {
    display:grid;
    grid-template-columns: repeat(4, 1fr);
    gap:18px;
}

.med-card {
    background:white;
    border-radius:18px;
    padding:18px;
    box-shadow: 0px 8px 18px rgba(0,0,0,0.06);
    position:relative;
    overflow:hidden;
}

.med-icon {
    font-size:40px;
    margin-bottom:10px;
}

.med-name {
    font-size:14px;
    font-weight:800;
    color:#0d1b3d;
}

.med-values {
    margin-top:10px;
    font-size:13px;
    color:#506089;
    font-weight:600;
}

.med-progress-outer {
    width:100%;
    height:12px;
    background:#edf1fb;
    border-radius:10px;
    overflow:hidden;
    margin-top:10px;
}

.med-progress-inner {
    height:12px;
    border-radius:10px;
    background: linear-gradient(90deg, #244a87, #2c6bed, #00d4ff);
    transition: width 1.2s ease-in-out;
}

.med-percentage {
    margin-top:6px;
    font-size:12px;
    font-weight:800;
    color:#244a87;
}

.alert-box {
    background: linear-gradient(90deg, #fff7d6, #ffeaa1);
    padding:14px 18px;
    border-radius:14px;
    border-left: 7px solid #ffb300;
    font-weight:800;
    color:#5b3d00;
    box-shadow: 0px 6px 16px rgba(0,0,0,0.06);
    margin-bottom: 18px;
    font-size:14px;
}

.chart-box {
    background:white;
    border-radius:18px;
    padding:18px 18px;
    box-shadow: 0px 8px 18px rgba(0,0,0,0.06);
    margin-bottom: 18px;
}

</style>
""", unsafe_allow_html=True)

# ==========================================================
# ICONOS DIFERENTES PARA CADA MEDICAMENTO
# ==========================================================
ICONOS_MEDICAMENTOS = {
    "Multivitaminas (gotas)": "🧴",
    "Vitaminas C (gotas)": "🍊",
    "Vitamina A y D2 (gotas)": "🌞",
    "Vitamina D2 forte (gotas)": "💊",
    "Vitamina B (gotas)": "⚡",
    "Fumarato ferroso en suspensión": "🩸",
    "Acetaminofén": "🌡️",
    "Ibuprofeno": "💠",
    "Jarabe para la tos": "🍯",
    "Suero oral": "💧",
    "Antibiótico": "🧫"
}

def icono_por_defecto(nombre):
    return ICONOS_MEDICAMENTOS.get(nombre, "💊")

# ==========================================================
# LECTURA DATOS
# ==========================================================
try:
    df_don = cargar_donaciones()
    df_meta = cargar_metas()
except Exception as e:
    st.error("❌ Error cargando datos. Verifica que los links CSV estén bien publicados.")
    st.stop()

df_don = limpiar_donaciones(df_don)
df_meta = limpiar_metas(df_meta)

# ==========================================================
# LISTA DE MEDICAMENTOS DESDE METAS
# ==========================================================
lista_meds = df_meta["Medicamento"].tolist()

# ==========================================================
# TOTALES
# ==========================================================
total_meta = df_meta["Meta"].sum()

total_recolectado = 0
for med in lista_meds:
    if med in df_don.columns:
        total_recolectado += df_don[med].sum()

avance_global = 0
if total_meta > 0:
    avance_global = (total_recolectado / total_meta) * 100

avance_global = min(avance_global, 100)

# ==========================================================
# ALERTA DE ÚLTIMA DONACIÓN (CAMPANA)
# ==========================================================
ultima_donacion = None
if "Timestamp" in df_don.columns:
    ultima_donacion = df_don.sort_values("Timestamp", ascending=False).head(1)

if ultima_donacion is not None and not ultima_donacion.empty:
    fecha_ultima = ultima_donacion["Timestamp"].iloc[0]
    fecha_ultima_str = fecha_ultima.strftime("%d/%m/%Y %H:%M") if pd.notnull(fecha_ultima) else "Sin fecha"

    nombre_publico = "Donante Anónimo"
    if "Nombre para mostrar" in ultima_donacion.columns:
        if pd.notnull(ultima_donacion["Nombre para mostrar"].iloc[0]) and str(ultima_donacion["Nombre para mostrar"].iloc[0]).strip() != "":
            nombre_publico = ultima_donacion["Nombre para mostrar"].iloc[0]

    st.markdown(f"""
    <div class="alert-box">
        🔔 Nueva donación registrada: <b>{nombre_publico}</b> | <span style="font-weight:700;">{fecha_ultima_str}</span>
    </div>
    """, unsafe_allow_html=True)

# ==========================================================
# HEADER
# ==========================================================
st.markdown(f"""
<div class="dashboard-header">
    <div class="header-left">
        <div class="logo-box">
            GENEROSIDAD<br>COLOMBIA<br>2025
        </div>
        <div class="title-box">
            <h1>Círculo de Generosidad</h1>
            <p>{datetime.now().strftime("%d de %B de %Y")}</p>
        </div>
    </div>

    <div class="header-right">
        Córdoba nos necesita 💙
    </div>
</div>
""", unsafe_allow_html=True)

# ==========================================================
# KPIs
# ==========================================================
st.markdown(f"""
<div class="kpi-container">
    <div class="kpi-card">
        <div class="kpi-title">Total meta</div>
        <div class="kpi-value">{int(total_meta):,}</div>
    </div>

    <div class="kpi-card">
        <div class="kpi-title">Total recolectado</div>
        <div class="kpi-value">{int(total_recolectado):,}</div>
    </div>

    <div class="kpi-card">
        <div class="kpi-title">% avance global</div>
        <div class="kpi-value">{avance_global:.1f}%</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ==========================================================
# PROGRESO GLOBAL
# ==========================================================
st.markdown(f"""
<div class="progress-global">
    <div class="progress-title">Avance global de la campaña</div>
    <div class="progress-bar-outer">
        <div class="progress-bar-inner" style="width:{avance_global:.1f}%;"></div>
    </div>
    <div class="progress-label">{avance_global:.1f}% completado</div>
</div>
""", unsafe_allow_html=True)

# ==========================================================
# SECCIÓN MEDICAMENTOS
# ==========================================================
st.markdown("<div class='section-title'>📦 Avance por medicamento</div>", unsafe_allow_html=True)

med_cards_html = "<div class='med-grid'>"

for med in lista_meds:
    meta = df_meta.loc[df_meta["Medicamento"] == med, "Meta"].values[0]
    recolectado = df_don[med].sum() if med in df_don.columns else 0

    porcentaje = 0
    if meta > 0:
        porcentaje = (recolectado / meta) * 100
    porcentaje = min(porcentaje, 100)

    icono = icono_por_defecto(med)

    med_cards_html += f"""
    <div class="med-card">
        <div class="med-icon">{icono}</div>
        <div class="med-name">{med}</div>
        <div class="med-values">Recolectado: {int(recolectado):,} / Meta: {int(meta):,}</div>

        <div class="med-progress-outer">
            <div class="med-progress-inner" style="width:{porcentaje:.1f}%;"></div>
        </div>

        <div class="med-percentage">{porcentaje:.1f}%</div>
    </div>
    """

med_cards_html += "</div>"

st.markdown(med_cards_html, unsafe_allow_html=True)

# ==========================================================
# GRÁFICOS PROFESIONALES
# ==========================================================
st.markdown("<div class='section-title'>📊 Análisis y gráficos</div>", unsafe_allow_html=True)

# Dataset resumen para gráficos
resumen = []
for med in lista_meds:
    meta = df_meta.loc[df_meta["Medicamento"] == med, "Meta"].values[0]
    recolectado = df_don[med].sum() if med in df_don.columns else 0
    faltante = max(meta - recolectado, 0)

    resumen.append({
        "Medicamento": med,
        "Recolectado": recolectado,
        "Meta": meta,
        "Faltante": faltante
    })

df_resumen = pd.DataFrame(resumen)

col1, col2 = st.columns(2)

with col1:
    st.markdown("<div class='chart-box'>", unsafe_allow_html=True)

    fig_bar = px.bar(
        df_resumen,
        x="Medicamento",
        y="Recolectado",
        title="Cantidad recolectada por medicamento",
        text="Recolectado"
    )
    fig_bar.update_layout(
        title_font_size=16,
        xaxis_title="Medicamento",
        yaxis_title="Cantidad",
        height=420
    )
    fig_bar.update_traces(textposition="outside")
    st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown("<div class='chart-box'>", unsafe_allow_html=True)

    fig_meta = go.Figure()

    fig_meta.add_trace(go.Bar(
        x=df_resumen["Medicamento"],
        y=df_resumen["Meta"],
        name="Meta"
    ))

    fig_meta.add_trace(go.Bar(
        x=df_resumen["Medicamento"],
        y=df_resumen["Recolectado"],
        name="Recolectado"
    ))

    fig_meta.update_layout(
        barmode="group",
        title="Comparación Meta vs Recolectado",
        height=420,
        title_font_size=16
    )

    st.plotly_chart(fig_meta, use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)

# ==========================================================
# HISTÓRICO DE DONACIONES (LINEA)
# ==========================================================
if "Timestamp" in df_don.columns:
    st.markdown("<div class='chart-box'>", unsafe_allow_html=True)

    df_time = df_don.copy()
    df_time = df_time.dropna(subset=["Timestamp"])

    if not df_time.empty:
        df_time["Fecha"] = df_time["Timestamp"].dt.date

        df_time["Total Donado"] = 0
        for med in lista_meds:
            if med in df_time.columns:
                df_time["Total Donado"] += df_time[med]

        df_daily = df_time.groupby("Fecha")["Total Donado"].sum().reset_index()

        fig_line = px.line(
            df_daily,
            x="Fecha",
            y="Total Donado",
            markers=True,
            title="Donaciones acumuladas por día"
        )

        fig_line.update_layout(
            title_font_size=16,
            height=420
        )

        st.plotly_chart(fig_line, use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)

# ==========================================================
# TABLA DETALLE (OPCIONAL)
# ==========================================================
with st.expander("📌 Ver detalle de donaciones (solo si es necesario)"):
    st.dataframe(df_don, use_container_width=True)




