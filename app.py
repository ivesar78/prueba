import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Gestión Cantera Fútbol", layout="wide")
st.title("⚽ Sistema Integral de Metodología y Meritocracia")

# LÍNEA 8: PEGA AQUÍ TU ENLACE LARGO DE "PUBLICAR EN LA WEB" (EL CSV)
URL_CSV = "https://google.com"

@st.cache_data(ttl=5)
def cargar_datos():
    try:
        # Intentamos leer tu Google Sheets publicado
        df = pd.read_csv(URL_CSV)
        # Forzamos a que todas las columnas limpien sus espacios y se escriban igual
        df.columns = df.columns.str.strip().str.capitalize()
        
        # Si a pesar de todo falta la columna clave, forzamos el error para ir al plan B
        if "Equipo" not in df.columns:
            raise ValueError("Falta columna Equipo")
        return df
    except Exception as e:
        # PLAN B: Si tu enlace falla o tu Excel no está listo, la App carga esto para que funcione ya
        return pd.DataFrame([
            {"Id": 1, "Nombre": "Carlos Gómez", "Equipo": "juvenil a", "Asistencias": 18, "Totales": 20, "Actitud_promed": 4.5, "Minutos_jugadc": 720, "Minutos_total": 900},
            {"Id": 2, "Nombre": "Dani Ruiz", "Equipo": "juvenil a", "Asistencias": 12, "Totales": 20, "Actitud_promed": 3.0, "Minutos_jugadc": 680, "Minutos_total": 900},
            {"Id": 3, "Nombre": "Mikel Lasa", "Equipo": "juvenil a", "Asistencias": 20, "Totales": 20, "Actitud_promed": 4.8, "Minutos_jugadc": 450, "Minutos_total": 900}
        ])

df_jugadores = cargar_datos()

# 2. SELECCIÓN DE EQUIPO
st.sidebar.header("⚙️ Panel de Control")

# Buscamos la columna de equipos de forma inteligente (sin importar mayúsculas)
col_equipo = [c for c in df_jugadores.columns if c.lower() == "equipo"]
if col_equipo:
    lista_equipos = sorted(df_jugadores[col_equipo[0]].dropna().unique().tolist())
    equipo_seleccionado = st.sidebar.selectbox("Selecciona Equipo", lista_equipos)
    df_filtrado = df_jugadores[df_jugadores[col_equipo[0]] == equipo_seleccionado].copy()
else:
    equipo_seleccionado = "juvenil a"
    df_filtrado = df_jugadores.copy()

# Normalizamos las columnas filtradas para el algoritmo
df_filtrado.columns = df_filtrado.columns.str.lower()

# 3. CONTROL DE ASISTENCIA DIARIA
st.header(f"📋 Control Diario - {equipo_seleccionado}")
if not df_filtrado.empty and "nombre" in df_filtrado.columns:
    with st.form("asistencia_form"):
        for idx, jugador in df_filtrado.iterrows():
            col1, col2, col3 = st.columns(3)
            col1.write(jugador["nombre"])
            col2.checkbox("Asistió", value=True, key=f"as_{jugador['id']}")
            col3.slider("Actitud", 1, 5, 5, key=f"ac_{jugador['id']}")
        st.form_submit_button("Registrar Entrenamiento")

# 4. ALGORITMO DE MERITOCRACIA
st.header("📊 Índice de Meritocracia vs Minutos")
if not df_filtrado.empty and "nombre" in df_filtrado.columns:
    # Aseguramos que los datos sean numéricos y rellenamos vacíos
    asistencias = pd.to_numeric(df_filtrado.get("asistencias", 0), errors='coerce').fillna(0)
    totales = pd.to_numeric(df_filtrado.get("totales", 1), errors='coerce').fillna(1).replace(0, 1)
    actitud = pd.to_numeric(df_filtrado.get("actitud_promed", 0).astype(str).str.replace(',', '.'), errors='coerce').fillna(0)
    min_jugados = pd.to_numeric(df_filtrado.get("minutos_jugadc", 0), errors='coerce').fillna(0)
    min_totales = pd.to_numeric(df_filtrado.get("minutos_total", 1), errors='coerce').fillna(1).replace(0, 1)

    df_filtrado["asistencia_%"] = (asistencias / totales) * 100
    df_filtrado["imd"] = (df_filtrado["asistencia_%"] * 0.4) + ((actitud / 5) * 100 * 0.6)
    df_filtrado["minutos_%"] = (min_jugados / min_totales) * 100
    
    st.dataframe(df_filtrado[["nombre", "asistencia_%", "actitud_promed", "imd", "minutos_%"]], use_container_width=True)

# 5. CONVOCATORIAS WHATSAPP
st.header("📱 Generador de Convocatorias")
if not df_filtrado.empty and "nombre" in df_filtrado.columns:
    jugadores_convocados = st.multiselect("Convocados", df_filtrado["nombre"].tolist(), default=df_filtrado["nombre"].tolist())
    texto_whatsapp = f"⚽ *CONVOCATORIA {equipo_seleccionado}*\n\n" + "\n".join([f"- {j}" for j in jugadores_convocados])
    st.text_area("Copia para WhatsApp:", texto_whatsapp, height=120)
