import streamlit as st
import pandas as pd

# 1. PAGE CONFIGURATION
st.set_page_config(page_title="Gestión Cantera Fútbol", layout="wide")
st.title("⚽ Sistema Integral de Metodología y Meritocracia")

# EXCEL CONNECTION (REAL CSV LINK FROM GOOGLE SHEETS)
URL_CSV = "https://google.com"

@st.cache_data(ttl=5)
def cargar_datos():
    try:
        df = pd.read_csv(URL_CSV)
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        st.error(f"Error al cargar Google Sheets: {e}")
        # Backup Data if connection fails
        return pd.DataFrame([
            {"ID": 1, "Nombre": "prueba1", "Equipo": "juvenil a", "Asistencias": 18, "Totales": 20, "Actitud_Promedio": "4,5", "Minutos_Jugados": 730, "Minutos_Totales": 870},
            {"ID": 2, "Nombre": "prueba2", "Equipo": "juvenil a", "Asistencias": 18, "Totales": 20, "Actitud_Promedio": "4,5", "Minutos_Jugados": 730, "Minutos_Totales": 870}
        ])

df_jugadores = cargar_datos()

# 2. SIDEBAR PANEL (TEAM SELECTOR)
st.sidebar.header("⚙️ Panel de Control")
if "Equipo" in df_jugadores.columns:
    lista_equipos = sorted(df_jugadores["Equipo"].dropna().unique().tolist())
    equipo_seleccionado = st.sidebar.selectbox("Selecciona Equipo", lista_equipos)
    df_filtrado = df_jugadores[df_jugadores["Equipo"] == equipo_seleccionado].copy()
else:
    equipo_seleccionado = "juvenil a"
    df_filtrado = df_jugadores.copy()

# 3. INTERACTIVE MODULE: ROLL CALL AND ATTITUDE
st.header(f"📋 Control Diario de Entrenamiento - {equipo_seleccionado}")
if not df_filtrado.empty and "Nombre" in df_filtrado.columns:
    with st.form("asistencia_form"):
        st.write("Registra la asistencia y comportamiento de la sesión de hoy:")
        for idx, jugador in df_filtrado.iterrows():
            col1, col2, col3 = st.columns([2, 1, 2])
            col1.write(f"**{jugador['Nombre']}**")
            col2.checkbox("Asistió", value=True, key=f"as_{jugador['ID']}")
            col3.slider("Actitud en sesión", 1, 5, 5, key=f"ac_{jugador['ID']}")
        
        btn_guardar = st.form_submit_button("Registrar Sesión de Hoy")
        if btn_guardar:
            st.success("¡Asistencia registrada localmente! (Para persistir los cambios acumulados en el Excel de forma permanente, actualiza periódicamente tu archivo original de Google Sheets).")

# 4. METHODOLOGICAL DESIGNER: 6 SESSION BLOCKS
st.header("📝 Diseñador Estructurado de Sesiones")
st.write("Planifica las 5 partes del entrenamiento definiendo tipos de tarea, principios y subprincipios tácticos:")

with st.container(border=True):
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        tipo_tarea = st.selectbox("Tipo de Tarea Principal", ["Analítica", "Globalizada", "Rondo", "SSG (Espacios Reducidos)", "Partido Condicionado"])
        principio = st.text_input("Principio Táctico a Trabajar", placeholder="Ej: Amplitud, Bloque Bajo, Transición Defensiva")
    with col_t2:
        subprincipio = st.text_input("Subprincipio Táctico", placeholder="Ej: Tercer Hombre, Basculación de Líneas")
        espacio = st.selectbox("Espacio del Campo Utilizado", ["Vestuario", "Cuadrante Reducido", "1/4 de Campo", "Medio Campo", "Campo Completo"])

    st.markdown("---")
    
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        st.text_area("Bloque 1: Vestuario Inicial (Charlas / Video / Dinámicas grupales)", "Objetivos del día, análisis del rival y cohesión de grupo.", height=80)
        st.text_area("Bloque 2: Calentamiento Técnico/Físico", "Rondo de posesión estructural o activación preventiva.", height=80)
        st.text_area("Bloque 3: Tarea Principal 1", "Evolución táctica del principio trabajado.", height=80)
    with col_b2:
        st.text_area("Bloque 4: Tarea Principal 2", "Situación real orientada a la conservación o finalización.", height=80)
        st.text_area("Bloque 5: Tarea Principal 3", "Partido aplicado con reglas de provocación.", height=80)
        st.text_area("Bloque 6: Vuelta a la Calma (Vestuario / Ducha)", "Estiramientos, feedback del míster, higiene y ducha obligatorio.", height=80)

# 5. ALGORITHM: MERITOCRACY INDEX (IMD) VS MINUTES
st.header("📊 Índice de Meritocracia Deportiva vs Minutos")
if not df_filtrado.empty and "Nombre" in df_filtrado.columns:
    # Clean up numerical inputs
    asistencias = pd.to_numeric(df_filtrado.get("Asistencias", 0), errors='coerce').fillna(0)
    totales = pd.to_numeric(df_filtrado.get("Totales", 1), errors='coerce').fillna(1).replace(0, 1)
    
    # Adapt to European comma decimals for Attitude
    actitud_str = df_filtrado.get("Actitud_Promedio", "5").astype(str).str.replace(',', '.')
    actitud = pd.to_numeric(actitud_str, errors='coerce').fillna(5)
    
    min_jugados = pd.to_numeric(df_filtrado.get("Minutos_Jugados", 0), errors='coerce').fillna(0)
    min_totales = pd.to_numeric(df_filtrado.get("Minutos_Totales", 1), errors='coerce').fillna(1).replace(0, 1)

    # Core Calculations
    df_filtrado["Asistencia_%"] = (asistencias / totales) * 100
    df_filtrado["IMD"] = (df_filtrado["Asistencia_%"] * 0.4) + ((actitud / 5) * 100 * 0.6)
    df_filtrado["Minutos_%"] = (min_jugados / min_totales) * 100
    
    # Automatic Alerts View
    for index, row in df_filtrado.iterrows():
        if row["IMD"] >= 85 and row["Minutos_%"] < 50:
            st.warning(f"⚠️ **Alerta de Injusticia**: {row['Nombre']} tiene un IMD excelente ({row['IMD']:.1f}%) pero solo juega el {row['Minutos_%']:.1f}% de los minutos.")
        if row["IMD"] < 65 and row["Minutos_%"] >= 75:
            st.error(f"🚨 **Alerta de Privilegio**: {row['Nombre']} entrena poco o rinde bajo en actitud ({row['IMD']:.1f}%) pero juega el {row['Minutos_%']:.1f}% de los minutos.")

    # Render Table
    st.dataframe(df_filtrado[["Nombre", "Asistencia_%", "IMD", "Minutos_%"]], use_container_width=True)

# 6. MATCH CONVOCATIONS FOR WHATSAPP
st.header("📱 Generador de Convocatorias")
if not df_filtrado.empty and "Nombre" in df_filtrado.columns:
    jugadores_convocados = st.multiselect("Selecciona los Convocados para el Partido", df_filtrado["Nombre"].tolist(), default=df_filtrado["Nombre"].tolist())
    
    col_r, col_h = st.columns(2)
    with col_r:
        rival = st.text_input("Rival de la Jornada", "C.F. Rival Cantera")
    with col_h:
        hora = st.text_input("Hora de la Cita en Vestuarios", "10:15 H")

    texto_whatsapp = f"⚽ *CONVOCATORIA OFICIAL: {equipo_seleccionado.upper()}* ⚽\n\n"
    texto_whatsapp += f"🗓️ *Partido contra:* {rival}\n"
    texto_whatsapp += f"🕒 *Hora de Cita:* {hora} (Puntualidad en Vestuarios)\n"
    texto_whatsapp += f"👟 *Equipación:* Primera Equipación Oficial\n\n"
    texto_whatsapp += "*Lista de Convocados:*\n"
    
    for i, j in enumerate(jugadores_convocados, 1):
        texto_whatsapp += f"{i}. {j}\n"
        
    texto_whatsapp += "\n⚠️ _Se ruega confirmar asistencia respondiendo a este mensaje cuanto antes. ¡Vamos equipo!_ 💪🔴"
    st.text_area("Copia este texto listo para enviar por WhatsApp:", texto_whatsapp, height=180)

