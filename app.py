import streamlit as st
import pandas as pd

# 1. PAGE CONFIGURATION
st.set_page_config(page_title="Gestión Cantera Fútbol", layout="wide")
st.title("⚽ Sistema Integral de Metodología y Meritocracia")

# EXCEL CONNECTIONS (REAL CSV EXPORTS FROM GOOGLE SHEETS)
URL_JUGADORES = "https://google.com"
# Enlace que apunta a la pestaña de TAREAS del segundo documento
URL_TAREAS = "https://google.com"

@st.cache_data(ttl=5)
def cargar_jugadores():
    try:
        df = pd.read_csv(URL_JUGADORES)
        df.columns = df.columns.str.strip()
        return df
    except:
        return pd.DataFrame([{"ID": 1, "Nombre": "prueba1", "Equipo": "juvenil a", "Asistencias": 18, "Totales": 20, "Actitud_Promedio": "4,5", "Minutos_Jugados": 730, "Minutos_Totales": 870}])

@st.cache_data(ttl=5)
def cargar_libreria_tareas():
    try:
        df = pd.read_csv(URL_TAREAS)
        df.columns = df.columns.str.strip()
        # Normalizamos nombres de columnas comunes según tu Excel de Tareas
        df.rename(columns={'NOMBRE DE LA TAREA': 'Nombre', 'TIPOS DE TAREAS': 'Tipo', 'CONCEPTO GENERAL': 'Principio', 'CONCEPTO MICRO': 'Subprincipio', 'DESCRIPCION DE LA TAREA': 'Descripcion'}, inplace=True)
        return df
    except:
        # Estructura por defecto si falla o está vacío el enlace
        return pd.DataFrame(columns=['Nombre', 'Tipo', 'Principio', 'Subprincipio', 'Descripcion', 'Etapa', 'Normas'])

# Inicializar estados de memoria local para almacenar nuevas tareas creadas en la sesión
if "tareas_nuevas" not in st.session_state:
    st.session_state.tareas_nuevas = pd.DataFrame(columns=['Nombre', 'Tipo', 'Principio', 'Subprincipio', 'Descripcion', 'Etapa', 'Normas'])

df_jugadores = cargar_jugadores()
df_tareas_base = cargar_libreria_tareas()

# Unimos las tareas del Excel con las que vayas creando en la App
df_total_tareas = pd.concat([df_tareas_base, st.session_state.tareas_nuevas], ignore_index=True).drop_duplicates(subset=['Nombre']).dropna(subset=['Nombre'])

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
            col1, col2, col3 = st.columns(3)
            col1.write(f"**{jugador['Nombre']}**")
            col2.checkbox("Asistió", value=True, key=f"as_{jugador['ID']}")
            col3.slider("Actitud en sesión", 1, 5, 5, key=f"ac_{jugador['ID']}")
        
        if st.form_submit_button("Registrar Sesión de Hoy"):
            st.success("¡Asistencia registrada localmente!")

# 4. NEW MODULE: CREAR NUEVAS TAREAS (IGX STYLE)
st.header("➕ Creador de Nuevas Tareas (Añadir a la Biblioteca)")
with st.expander("🛠️ Abrir Formulario para diseñar una Tarea Nueva"):
    with st.form("crear_tarea_form"):
        c1, c2, c3 = st.columns(3)
        nt_nombre = c1.text_input("Nombre de la Tarea")
        nt_tipo = c2.selectbox("Tipo de Tarea", ["COLECTIVA CONTEX", "ANALÍTICA", "RONDO", "SSG", "PARTIDO JUEGO"])
        nt_etapa = c3.selectbox("Etapa Destinada", ["TODAS", "PREBENJAMÍN", "BENJAMÍN", "ALEVÍN", "INFANTIL", "CADETE", "JUVENIL"])
        
        c4, c5 = st.columns(2)
        nt_principio = c4.text_input("Concepto General / Principio Táctico", "TÁCTICO MOMENTO CON BALÓN")
        nt_subprincipio = c5.text_input("Concepto Micro / Subprincipio", "balón parado def")
        
        nt_desc = st.text_area("Descripción de la Tarea")
        nt_normas = st.text_area("Normas / Reglas de Provocación")
        
        if st.form_submit_button("💾 Guardar y Añadir a la Biblioteca"):
            if nt_nombre:
                nueva_fila = pd.DataFrame([{
                    'Nombre': nt_nombre, 'Tipo': nt_tipo, 'Principio': nt_principio, 
                    'Subprincipio': nt_subprincipio, 'Descripcion': nt_desc, 'Etapa': nt_etapa, 'Normas': nt_normas
                }])
                st.session_state.tareas_nuevas = pd.concat([st.session_state.tareas_nuevas, nueva_fila], ignore_index=True)
                st.success(f"¡Tarea '{nt_nombre}' guardada con éxito! Ya puedes elegirla en el diseñador de abajo.")
                st.rerun()
            else:
                st.error("El nombre de la tarea es obligatorio.")

# 5. METHODOLOGICAL DESIGNER: CHOOSE FROM LIBRERÍA
st.header("📝 Diseñador Estructurado de Sesiones")
st.write("Selecciona ejercicios de la biblioteca importada desde tu Excel o introduce nuevos datos:")

lista_nombres_tareas = ["-- Introducir Tarea Manual / Personalizada --"] + sorted(df_total_tareas['Nombre'].dropna().tolist())

with st.container(border=True):
    st.subheader("Planificación de Tareas Principales")
    tarea_elegida = st.selectbox("🎯 Buscar y Elegir Tarea de la Biblioteca de tu Excel", lista_nombres_tareas)
    
    # Auto-completado de campos si la tarea se selecciona de la librería
    info_tarea = df_total_tareas[df_total_tareas['Nombre'] == tarea_elegida]
    
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        v_tipo = info_tarea['Tipo'].values[0] if not info_tarea.empty and pd.notna(info_tarea['Tipo'].values[0]) else "COLECTIVA CONTEX"
        tipo_tarea = st.text_input("Tipo de Tarea", value=str(v_tipo))
        
        v_principio = info_tarea['Principio'].values[0] if not info_tarea.empty and pd.notna(info_tarea['Principio'].values[0]) else ""
        principio = st.text_input("Principio Táctico a Trabajar", value=str(v_principio))
    with col_t2:
        v_sub = info_tarea['Subprincipio'].values[0] if not info_tarea.empty and pd.notna(info_tarea['Subprincipio'].values[0]) else ""
        subprincipio = st.text_input("Subprincipio Táctico", value=str(v_sub))
        
        espacio = st.selectbox("Espacio del Campo Utilizado", ["Vestuario", "Cuadrante Reducido", "1/4 de Campo", "Medio Campo", "Campo Completo"])

    st.markdown("---")
    v_desc = info_tarea['Descripcion'].values[0] if not info_tarea.empty and pd.notna(info_tarea['Descripcion'].values[0]) else ""
    
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        st.text_area("Bloque 1: Vestuario Inicial (Charlas / Video)", "Charlas de cohesión de grupo táctico.", height=80)
        st.text_area("Bloque 2: Calentamiento Técnico/Físico", "Rondo estructural dinámico.", height=80)
        st.text_area("Bloque 3: Tarea Principal 1", value=f"Ejercicio Seleccionado: {tarea_elegida}\nDescripción: {v_desc}", height=80)
    with col_b2:
        st.text_area("Bloque 4: Tarea Principal 2", "Situación real orientada al partido.", height=80)
        st.text_area("Bloque 5: Tarea Principal 3", "Evolución condicionada final.", height=80)
        st.text_area("Bloque 6: Vuelta a la Calma (Vestuario / Ducha)", "Estiramientos dirigidos, higiene y ducha obligatorio.", height=80)

# 6. ALGORITHM: MERITOCRACY INDEX (IMD) VS MINUTES
st.header("📊 Índice de Meritocracia Deportiva vs Minutos")
if not df_filtrado.empty and "Nombre" in df_filtrado.columns:
    asistencias = pd.to_numeric(df_filtrado.get("Asistencias", 0), errors='coerce').fillna(0)
    totales = pd.to_numeric(df_filtrado.get("Totales", 1), errors='coerce').fillna(1).replace(0, 1)
    actitud = pd.to_numeric(df_filtrado.get("Actitud_Promedio", "5").astype(str).str.replace(',', '.'), errors='coerce').fillna(5)
    min_jugados = pd.to_numeric(df_filtrado.get("Minutos_Jugados", 0), errors='coerce').fillna(0)
    min_totales = pd.to_numeric(df_filtrado.get("Minutos_Totales", 1), errors='coerce').fillna(1).replace(0, 1)

    df_filtrado["Asistencia_%"] = (asistencias / totales) * 100
    df_filtrado["IMD"] = (df_filtrado["Asistencia_%"] * 0.4) + ((actitud / 5) * 100 * 0.6)
    df_filtrado["Minutos_%"] = (min_jugados / min_totales) * 100
    
    for index, row in df_filtrado.iterrows():
        if row["IMD"] >= 85 and row["minutos_%"] < 50:
            st.warning(f"⚠️ **Alerta de Injusticia**: {row['Nombre']} tiene un IMD excelente ({row['IMD']:.1f}%) pero juega menos de lo entrenado.")
        if row["IMD"] < 65 and row["minutos_%"] >= 75:
            st.error(f"🚨 **Alerta de Privilegio**: {row['Nombre']} entrena poco o rinde bajo en actitud ({row['IMD']:.1f}%) pero juega el máximo de minutos.")

    st.dataframe(df_filtrado[["Nombre", "Asistencia_%", "IMD", "Minutos_%"]], use_container_width=True)

# 7. MATCH CONVOCATIONS FOR WHATSAPP
st.header("📱 Generador de Convocatorias")
if not df_filtrado.empty and "Nombre" in df_filtrado.columns:
    jugadores_convocados = st.multiselect("Selecciona los Convocados para el Partido", df_filtrado["Nombre"].tolist(), default=df_filtrado["Nombre"].tolist())
    rival = st.text_input("Rival de la Jornada", "C.F. Rival Cantera")
    hora = st.text_input("Hora de la Cita en Vestuarios", "10:15 H")

    texto_whatsapp = f"⚽ *CONVOCATORIA OFICIAL: {equipo_seleccionado.upper()}* ⚽\n\n🗓️ *Rival:* {rival}\n🕒 *Hora Cita:* {hora}\n\n*Convocados:*\n"
    for i, j in enumerate(jugadores_convocados, 1):
        texto_whatsapp += f"{i}. {j}\n"
    texto_whatsapp += "\n⚠️ _Por favor, confirmad asistencia respondiendo a este mensaje. ¡Vamos equipo!_"
    st.text_area("Copia este texto listo para enviar por WhatsApp:", texto_whatsapp, height=150)


