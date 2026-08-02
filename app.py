import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Gestión Cantera Fútbol", layout="wide")
st.title("⚽ Sistema Integral de Metodología y Meritocracia")

# LÍNEA 8: PEGA AQUÍ TU ENLACE LARGO DE "PUBLICAR EN LA WEB" (EL CSV)
URL_CSV = "https://google.com"

@st.cache_data(ttl=10)
def cargar_datos():
    try:
        df = pd.read_csv(URL_CSV)
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        return pd.DataFrame([
            {"ID": 1, "Nombre": "Carlos Gómez", "Equipo": "juvenil a", "Asistencias": 18, "Totales": 20, "Actitud_Promed": 4.5, "Minutos_Jugadc": 720, "Minutos_Total": 900},
            {"ID": 2, "Nombre": "Dani Ruiz", "Equipo": "juvenil a", "Asistencias": 12, "Totales": 20, "Actitud_Promed": 3.0, "Minutos_Jugadc": 680, "Minutos_Total": 900}
        ])

df_jugadores = cargar_datos()

# 2. SELECCIÓN DE EQUIPO
st.sidebar.header("⚙️ Panel de Control")
lista_equipos = sorted(df_jugadores["Equipo"].dropna().unique().tolist()) if "Equipo" in df_jugadores.columns else ["juvenil a"]
equipo_seleccionado = st.sidebar.selectbox("Selecciona Equipo", lista_equipos)

df_filtrado = df_jugadores[df_jugadores["Equipo"] == equipo_seleccionado].copy()

# 3. CONTROL DE ASISTENCIA DIARIA
st.header(f"📋 Control Diario - {equipo_seleccionado}")
if not df_filtrado.empty:
    with st.form("asistencia_form"):
        for idx, jugador in df_filtrado.iterrows():
            col1, col2, col3 = st.columns(3)
            col1.write(jugador["Nombre"])
            col2.checkbox("Asistió", value=True, key=f"as_{jugador['ID']}")
            col3.slider("Actitud", 1, 5, 5, key=f"ac_{jugador['ID']}")
        st.form_submit_button("Registrar Entrenamiento")

# 4. ALGORITMO DE MERITOCRACIA
st.header("📊 Índice de Meritocracia vs Minutos")
if not df_filtrado.empty:
    df_filtrado["Asistencias"] = pd.to_numeric(df_filtrado["Asistencias"], errors='coerce').fillna(0)
    df_filtrado["Totales"] = pd.to_numeric(df_filtrado["Totales"], errors='coerce').fillna(1)
    df_filtrado["Actitud_Promed"] = pd.to_numeric(df_filtrado["Actitud_Promed"].astype(str).str.replace(',', '.'), errors='coerce').fillna(0)
    df_filtrado["Minutos_Jugadc"] = pd.to_numeric(df_filtrado["Minutos_Jugadc"], errors='coerce').fillna(0)
    df_filtrado["Minutos_Total"] = pd.to_numeric(df_filtrado["Minutos_Total"], errors='coerce').fillna(1)

    df_filtrado["Asistencia_%"] = (df_filtrado["Asistencias"] / df_filtrado["Totales"]) * 100
    df_filtrado["IMD"] = (df_filtrado["Asistencia_%"] * 0.4) + ((df_filtrado["Actitud_Promed"] / 5) * 100 * 0.6)
    df_filtrado["Minutos_%"] = (df_filtrado["Minutos_Jugadc"] / df_filtrado["Minutos_Total"]) * 100
    st.dataframe(df_filtrado[["Nombre", "Asistencia_%", "Actitud_Promed", "IMD", "Minutos_%"]], use_container_width=True)

# 5. CONVOCATORIAS WHATSAPP
st.header("📱 Generador de Convocatorias")
if not df_filtrado.empty:
    jugadores_convocados = st.multiselect("Convocados", df_filtrado["Nombre"].tolist(), default=df_filtrado["Nombre"].tolist())
    texto_whatsapp = f"⚽ *CONVOCATORIA {equipo_seleccionado}*\n\n" + "\n".join([f"- {j}" for j in jugadores_convocados])
    st.text_area("Copia para WhatsApp:", texto_whatsapp, height=120)

