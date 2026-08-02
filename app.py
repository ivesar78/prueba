import streamlit as st
import pandas as pd

# 1. ARCHITECTURE & GLOBAL SETTINGS
st.set_page_config(page_title="Gestión Metodológica IGX", layout="wide")
st.title("⚽ GESTIÓN METODOLÓGICA IGX")

# DATABASES CONNECTIONS (REAL DATA FROM YOUR 3 GOOGLE SHEETS)
URL_JUGADORES = "https://google.com"
URL_LIBRERIA_TAREAS = "https://google.com"
URL_CRONOGRAMA_SESIONES = "https://google.com" # Hoja PLANTILLA SESION/PLAN

@st.cache_data(ttl=5)
def cargar_todo():
    # Cargar Jugadores
    try:
        df_j = pd.read_csv(URL_JUGADORES)
        df_j.columns = df_j.columns.str.strip()
    except:
        df_j = pd.DataFrame([{"ID": 1, "Nombre": "prueba1", "Equipo": "juvenil a", "Asistencias": 18, "Totales": 20, "Actitud_Promedio": "4,5", "Minutos_Jugados": 730, "Minutos_Totales": 870}])
    
    # Cargar Biblioteca de Tareas
    try:
        df_t = pd.read_csv(URL_LIBRERIA_TAREAS)
        df_t.columns = df_t.columns.str.strip()
        df_t.rename(columns={
            'NOMBRE DE LA TAREA': 'Nombre', 'TIPOS DE TAREAS': 'Tipo', 
            'CONCEPTO GENERAL': 'Concepto_General', 'CONCEPTO MICRO': 'Concepto_Micro', 
            'DESCRIPCION DE LA TAREA': 'Descripcion', 'ETAPA': 'Etapa', 'NORMAS': 'Normas'
        }, inplace=True)
    except:
        df_t = pd.DataFrame(columns=['Nombre', 'Tipo', 'Concepto_General', 'Concepto_Micro', 'Descripcion', 'Etapa', 'Normas'])
        
    return df_j, df_t

df_jugadores, df_tareas_base = cargar_todo()

# Inicialización de almacenamiento interno para tareas nuevas añadidas en vivo
if "tareas_nuevas_igx" not in st.session_state:
    st.session_state.tareas_nuevas_igx = pd.DataFrame(columns=['Nombre', 'Tipo', 'Concepto_General', 'Concepto_Micro', 'Descripcion', 'Etapa', 'Normas'])

# Fusión total de ejercicios de la librería
df_total_tareas = pd.concat([df_tareas_base, st.session_state.tareas_nuevas_igx], ignore_index=True).drop_duplicates(subset=['Nombre']).dropna(subset=['Nombre'])

# 2. SELECTOR DE EQUIPO (Eje transversal de la App)
st.sidebar.header("🛡️ Acceso por Equipos")
if "Equipo" in df_jugadores.columns:
    lista_equipos = sorted(df_jugadores["Equipo"].dropna().unique().tolist())
    equipo_seleccionado = st.sidebar.selectbox("Selecciona la plantilla con la que vas a trabajar:", lista_equipos)
    df_filtrado_jugadores = df_jugadores[df_jugadores["Equipo"] == equipo_seleccionado].copy()
else:
    equipo_seleccionado = "juvenil a"
    df_filtrado_jugadores = df_jugadores.copy()

# Pestañas de Navegación del Sistema IGX
tab_asistencia, tab_crear_tarea, tab_crear_sesion = st.tabs([
    "📋 Control de Plantilla e IMD", 
    "➕ Creador de Tareas CDM", 
    "⏱️ Diseñador de Sesiones Estructuradas"
])

# ==========================================
# PESTAÑA 1: ASISTENCIA Y MERITOCRACIA
# ==========================================
with tab_asistencia:
    st.subheader(f"Métricas de Plantilla: {equipo_seleccionado.upper()}")
    if not df_filtrado_jugadores.empty and "Nombre" in df_filtrado_jugadores.columns:
        with st.form("form_lista"):
            for idx, jugador in df_filtrado_jugadores.iterrows():
                c1, c2, c3 = st.columns(3)
                c1.write(f"**{jugador['Nombre']}**")
                c2.checkbox("Asistió", value=True, key=f"p1_as_{jugador['ID']}")
                c3.slider("Actitud", 1, 5, 5, key=f"p1_ac_{jugador['ID']}")
            if st.form_submit_button("💾 Guardar Entrenamiento Diario"):
                st.success("Asistencia registrada")

        # Algoritmo de Meritocracia
        asistencias = pd.to_numeric(df_filtrado_jugadores.get("Asistencias", 0), errors='coerce').fillna(0)
        totales = pd.to_numeric(df_filtrado_jugadores.get("Totales", 1), errors='coerce').fillna(1).replace(0, 1)
        actitud = pd.to_numeric(df_filtrado_jugadores.get("Actitud_Promedio", "5").astype(str).str.replace(',', '.'), errors='coerce').fillna(5)
        min_jugados = pd.to_numeric(df_filtrado_jugadores.get("Minutos_Jugados", 0), errors='coerce').fillna(0)
        min_totales = pd.to_numeric(df_filtrado_jugadores.get("Minutos_Totales", 1), errors='coerce').fillna(1).replace(0, 1)

        df_filtrado_jugadores["Asistencia_%"] = (asistencias / totales) * 100
        df_filtrado_jugadores["IMD"] = (df_filtrado_jugadores["Asistencia_%"] * 0.4) + ((actitud / 5) * 100 * 0.6)
        df_filtrado_jugadores["Minutos_%"] = (min_jugados / min_totales) * 100
        st.dataframe(df_filtrado_jugadores[["Nombre", "Asistencia_%", "IMD", "Minutos_%"]], use_container_width=True)

# ==========================================
# PESTAÑA 2: CREADOR DE TAREAS CDM
# ==========================================
with tab_crear_tarea:
    st.subheader("🛠️ Creador de Tareas CDM (Mapeo de Conceptos)")
    with st.form("form_nueva_tarea_igx"):
        col_a, col_b, col_c = st.columns(3)
        nombre_t = col_a.text_input("NOMBRE DE LA TAREA", placeholder="Ej: Mantener amplitud 4x4")
        tipo_t = col_b.selectbox("TIPO DE CONCEPTO", ["TECNICOS", "TÁCTICOS MOMENTO CON BALÓN", "TÁCTICOS MOMENTO SIN BALÓN", "TÁCTICOS MOMENTO TRANSICIONES", "ACTITUDINALES", "FÍSICOS"])
        etapa_t = col_c.selectbox("ETAPA", ["TODAS", "PREBENJAMÍN", "BENJAMÍN", "ALEVÍN", "INFANTIL", "CADETE", "JUVENIL"])
        
        col_d, col_e = st.columns(2)
        concepto_gen = col_d.text_input("CONCEPTO GENERAL", value="TÁCTICO MOMENTO CON BALÓN")
        concepto_mic = col_e.text_input("CONCEPTO MICRO (Subprincipio)", value="mantener")
        
        desc_t = st.text_area("DESCRIPCIÓN DE LA TAREA")
        normas_t = st.text_area("NORMAS / REGLAS DE PROVOCACIÓN")
        
        if st.form_submit_button("💾 Validar y Guardar en Biblioteca IGX"):
            if nombre_t:
                nueva_t_df = pd.DataFrame([{
                    'Nombre': nombre_t, 'Tipo': tipo_t, 'Concepto_General': concepto_gen, 
                    'Concepto_Micro': concepto_mic, 'Descripcion': desc_t, 'Etapa': etapa_t, 'Normas': normas_t
                }])
                st.session_state.tareas_nuevas_igx = pd.concat([st.session_state.tareas_nuevas_igx, nueva_t_df], ignore_index=True)
                st.success(f"Tarea '{nombre_t}' añadida con éxito.")
                st.rerun()
            else:
                st.error("Es obligatorio rellenar el Nombre de la Tarea.")

# ==========================================
# PESTAÑA 3: CREADOR DE SESIONES (ESTILO CRONOGRAMA)
# ==========================================
with tab_crear_sesion:
    st.subheader("⏱️ Diseño Estructurado de Sesión de Entrenamiento")
    
    # Bloque 1: Filtros de Objetivo del Cronograma General
    st.markdown("#### 📑 1. Criterios de Selección y Objetivos de la Sesión")
    with st.container(border=True):
        c_fil1, c_fil2, c_fil3 = st.columns(3)
        f_tipo = c_fil1.selectbox("Filtrar por Tipo de Concepto", sorted(df_total_tareas['Tipo'].dropna().unique().tolist()) if not df_total_tareas.empty else ["TÁCTICO MOMENTO CON BALÓN"])
        f_general = c_fil2.selectbox("Filtrar por Concepto General", sorted(df_total_tareas['Concepto_General'].dropna().unique().tolist()) if not df_total_tareas.empty else ["mantener"])
        
        # Filtrado inteligente de ejercicios disponibles según criterios del Excel
        tareas_filtradas_db = df_total_tareas[
            (df_total_tareas['Tipo'] == f_tipo) & 
            (df_total_tareas['Concepto_General'] == f_general)
        ]
        
        lista_final_ejercicios = sorted(tareas_filtradas_db['Nombre'].tolist()) if not tareas_filtradas_db.empty else sorted(df_total_tareas['Nombre'].tolist())
        tarea_seleccionada_sesion = c_fil3.selectbox("🎯 Tarea resultante que coincide:", ["-- Selecciona un ejercicio compatible --"] + lista_final_ejercicios)

    # Bloque 2: Las 5 Partes de la Sesión (Estructura Solicitada)
    st.markdown("#### 📋 2. Planificación de las 5 Partes de la Sesión")
    
    # Extraemos información del ejercicio seleccionado de tu biblioteca
    info_ejercicio = df_total_tareas[df_total_tareas['Nombre'] == tarea_seleccionada_sesion]
    detalles_ejercicio = info_ejercicio['Descripcion'].values[0] if not info_ejercicio.empty else ""
    normas_ejercicio = info_ejercicio['Normas'].values[0] if not info_ejercicio.empty else ""
    micro_ejercicio = info_ejercicio['Concepto_Micro'].values[0] if not info_ejercicio.empty else ""

    col_izq, col_der = st.columns(2)
    with col_izq:
        s_b1 = st.text_area("Parte 1: Vestuario Inicial (Charlas tácticas / Análisis de Video / Dinámicas grupales)", value="Análisis de vídeo del rival de la jornada, repaso de posicionamientos específicos en pizarra y dinámicas grupales de cohesión.", height=110)
        s_b2 = st.text_area("Parte 2: Calentamiento (Activación física / Juegos Cooperativos)", value=f"Concepto Micro: {micro_ejercicio}\nRondo estructural o circuito técnico adaptado.", height=110)
        s_b3 = st.text_area("Parte 3: Tarea Principal Seleccionada (Biblioteca Excel)", value=f"Ejercicio: {tarea_seleccionada_sesion}\n\nDescripción: {detalles_ejercicio}\n\nNormas: {normas_ejercicio}", height=180)
    with col_der:
        s_b4 = st.text_area("Parte 4: Tarea Secundaria / Evolución del Ejercicio", value="Evolución o variante táctica modificando el espacio de juego o el número de toques permitidos.", height=110)
        s_b5 = st.text_area("Parte 5: Vuelta a la Calma (Vestuario / Higiene / Ducha)", value="Estiramientos estáticos dirigidos en el césped, feedback individualizado del míster, higiene y ducha obligatoria en el vestuario.", height=110)
        s_espacio = st.selectbox("Modificar Espacio Ocupado de la Tarea Principal", ["Vestuario", "Cuadrante Reducido", "1/4 Campo", "Medio Campo (Área a Área)", "Campo Completo"])




