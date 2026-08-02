import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN E IDENTIDAD
st.set_page_config(page_title="Gestión Metodológica IGX", layout="wide")
st.title("⚽ GESTIÓN METODOLÓGICA IGX")

# CONEXIONES DIRECTAS A GOOGLE SHEETS
URL_JUGADORES = "https://google.com"
URL_LIBRERIA_TAREAS = "https://google.com"

@st.cache_data(ttl=5)
def cargar_datos_base():
    try:
        df_j = pd.read_csv(URL_JUGADORES)
        df_j.columns = df_j.columns.str.strip()
    except:
        df_j = pd.DataFrame(columns=['Nombre', 'Equipo', 'ID', 'Asistencias', 'Totales', 'Actitud_Promedio', 'Minutos_Jugados', 'Minutos_Totales'])
        
    try:
        df_t = pd.read_csv(URL_LIBRERIA_TAREAS)
        df_t.columns = df_t.columns.str.strip().str.upper()
    except:
        df_t = pd.DataFrame(columns=['ETAPA', 'TIPO DE CONCEPTO', 'CONCEPTO GENERAL', 'CONCEPTO MICRO', 'TIPOS DE TAREAS', 'NOMBRE DE LA TAREA', 'LINK IMAGEN', 'LINK VIDEO TAREA', 'DESCRIPCION DE LA TAREA', 'NORMAS', 'TAREA NOMBRE VARIANTE', 'LINK VARIANTE TAREA'])
    return df_j, df_t

df_jugadores, df_tareas_base = cargar_datos_base()

columnas_oficiales = ['ETAPA', 'TIPO DE CONCEPTO', 'CONCEPTO GENERAL', 'CONCEPTO MICRO', 'TIPOS DE TAREAS', 'NOMBRE DE LA TAREA', 'LINK IMAGEN', 'LINK VIDEO TAREA', 'DESCRIPCION DE LA TAREA', 'NORMAS', 'TAREA NOMBRE VARIANTE', 'LINK VARIANTE TAREA']

for col in columnas_oficiales:
    if col not in df_tareas_base.columns:
        df_tareas_base[col] = None

df_tareas_base = df_tareas_base[columnas_oficiales]

if "tareas_creadas_en_vivo" not in st.session_state:
    st.session_state.tareas_creadas_en_vivo = pd.DataFrame(columns=columnas_oficiales)

df_total_tareas = pd.concat([df_tareas_base, st.session_state.tareas_creadas_en_vivo], ignore_index=True)
df_total_tareas = df_total_tareas.dropna(subset=['NOMBRE DE LA TAREA']).drop_duplicates(subset=['NOMBRE DE LA TAREA'])

# SELECTOR DE EQUIPO
st.sidebar.header("🛡️ Acceso por Equipos")
if not df_jugadores.empty and "Equipo" in df_jugadores.columns:
    lista_equipos = sorted(df_jugadores["Equipo"].dropna().unique().tolist())
    equipo_seleccionado = st.sidebar.selectbox("Selecciona la plantilla:", lista_equipos)
    df_filtrado_jugadores = df_jugadores[df_jugadores["Equipo"] == equipo_seleccionado]
else:
    equipo_seleccionado = "juvenil a"
    df_filtrado_jugadores = pd.DataFrame()

st.markdown("---")

opcion_menu = st.radio(
    "👉 **SELECCIONA UNA OPCIÓN:**", 
    ["Añadir Nuevas Tareas", "Diseñar una Nueva Sesión"],
    horizontal=True
)

st.markdown("---")

# ==========================================
# OPCIÓN 1: CREAR TAREAS (SIN MODIFICACIONES)
# ==========================================
if opcion_menu == "Añadir Nuevas Tareas":
    st.subheader("🛠️ CREADOR DE TAREAS")
    with st.form("formulario_crear_tarea_igx"):
        col1, col2, col3 = st.columns(3)
        c_etapa = col1.selectbox("ETAPA", ["TODAS", "PREBENJAMÍN", "BENJAMÍN", "ALEVÍN", "INFANTIL", "CADETE", "JUVENIL"])
        c_tipo_concepto = col2.selectbox("TIPO DE CONCEPTO", ["TACTICOS", "TECNICOS", "FISICOS", "ACTITUDINALES"])
        c_concepto_general = col3.selectbox("CONCEPTO GENERAL", [
            "TÁCTICOS MOMENTO SIN BALÓN",
            "TÁCTICO MOMENTO CON BALÓN",
            "TÉCNICOS CON BALÓN",
            "FÍSICOS",
            "TÁCTICOS MOMENTO TRANSICIONES",
            "TÉCNICOS SIN BALÓN",
            "ACTITUDINALES"
        ])
        
        col4, col5, col6 = st.columns(3)
        c_concepto_micro = col4.text_input("CONCEPTO MICRO")
        c_tipos_tareas = col5.selectbox("TIPOS DE TAREAS", [
            "COLECTIVA CONTEX",
            "PARTIDO CONDICIONADO(APLICACIONES)",
            "SIT JUGADA REDUCIDA",
            "SIT JUGADA AMPLIA",
            "CIRCUITO FISICO TECNICO",
            "JUEGO CORTO",
            "CIRCUITO FISICO MOTRIZ",
            "PARTIDO",
            "TECNIFICACION PASILLOS",
            "JUEGO COOPERATIVOS",
            "TEST",
            "DINAMICA"
        ])
        c_nombre_tarea = col6.text_input("NOMBRE DE LA TAREA")
        
        col7, col8 = st.columns(2)
        c_link_imagen = col7.text_input("LINK IMAGEN")
        c_link_video = col8.text_input("LINK VIDEO TAREA")
        
        c_descripcion = st.text_area("DESCRIPCION DE LA TAREA")
        c_normas = st.text_area("NORMAS")
        
        col9, col10 = st.columns(2)
        c_variante_nombre = col9.text_input("TAREA NOMBRE VARIANTE")
        c_link_variante = col10.text_input("LINK VARIANTE TAREA")
        
        if st.form_submit_button("💾 Guardar Tarea"):
            if c_nombre_tarea:
                nueva_tarea = pd.DataFrame([{
                    'ETAPA': c_etapa, 'TIPO DE CONCEPTO': c_tipo_concepto, 'CONCEPTO GENERAL': c_concepto_general,
                    'CONCEPTO MICRO': c_concepto_micro, 'TIPOS DE TAREAS': c_tipos_tareas, 'NOMBRE DE LA TAREA': c_nombre_tarea,
                    'LINK IMAGEN': c_link_imagen, 'LINK VIDEO TAREA': c_link_video, 'DESCRIPCION DE LA TAREA': c_descripcion,
                    'NORMAS': c_normas, 'TAREA NOMBRE VARIANTE': c_variante_nombre, 'LINK VARIANTE TAREA': c_link_variante
                }])
                st.session_state.tareas_creadas_en_vivo = pd.concat([st.session_state.tareas_creadas_en_vivo, nueva_tarea], ignore_index=True)
                st.success(f"¡Tarea '{c_nombre_tarea}' guardada con éxito!")
                st.rerun()
            else:
                st.error("Por favor, introduce el NOMBRE DE LA TAREA.")

# ==========================================
# OPCIÓN 2: CREAR SESIÓN (NUEVO DISEÑO GALDAKAO)
# ==========================================
else:
    st.subheader("📋 DISEÑADOR DE SESIONES - ESTILO GALDAKAO")
    
    # --- BLOQUE superior: DATOS DE LA SESIÓN ---
    st.markdown("### 🗓️ DATOS DE LA SESIÓN")
    with st.container(border=True):
        col_ds1, col_ds2, col_ds3, col_ds4, col_ds5 = st.columns(5)
        ds_club = col_ds1.text_input("CLUB / EQUIPO", value="GALDAKAO")
        ds_fecha = col_ds2.text_input("FECHA", value="24 mar 2026")
        ds_meso = col_ds3.text_input("MESOCICLO", value="MARZO")
        ds_etapa = col_ds4.selectbox("ETAPA SESIÓN", ["TODAS", "PREBENJAMÍN", "BENJAMÍN", "ALEVÍN", "INFANTIL", "CADETE", "JUVENIL"], index=0)
        ds_num = col_ds5.text_input("Nº SESION", value="21")

    st.markdown("---")
    
    # --- Estructura principal en dos grandes columnas (Estructura espejo del Excel) ---
    col_izquierda_metodologia, col_derecha_jugadores = st.columns([3, 1])
    
    with col_izquierda_metodologia:
        st.markdown("### 🧠 PARTE DE LA SESIÓN Y METODOLOGÍA")
        
        # Fila superior metodológica
        with st.container(border=True):
            col_m1, col_m2, col_m3, col_m4 = st.columns(4)
            s_parte = col_m1.selectbox("PARTE DE LA SESIÓN", ["CALENTAMIENTO", "PARTE PRINCIPAL 1", "PARTE PRINCIPAL 2", "PARTE PRINCIPAL 3", "VUELTA A LA CALMA"])
            
            opciones_gen = sorted(df_total_tareas['CONCEPTO GENERAL'].dropna().unique()) if not df_total_tareas.empty else ["TÁCTICO MOMENTO CON BALÓN"]
            s_general = col_m2.selectbox("CONCEPTO GENERAL", opciones_gen if len(opciones_gen) > 0 else ["TÁCTICO MOMENTO CON BALÓN"])
            
            # Filtrado reactivo para rellenar micro y tipo de tarea según la base de datos
            tareas_filtradas_prev = df_total_tareas[df_total_tareas['CONCEPTO GENERAL'] == s_general]
            
            opciones_micro = sorted(tareas_filtradas_prev['CONCEPTO MICRO'].dropna().unique()) if not tareas_filtradas_prev.empty else ["pase"]
            s_micro = col_m3.selectbox("CONCEPTO MICRO", opciones_micro if len(opciones_micro) > 0 else ["pase"])
            
            opciones_tipo_t = sorted(tareas_filtradas_prev['TIPOS DE TAREAS'].dropna().unique()) if not tareas_filtradas_prev.empty else ["TECNIFICACION PASILLOS"]
            s_tipo_tarea = col_m4.selectbox("TIPO DE TAREA", opciones_tipo_t if len(opciones_tipo_t) > 0 else ["TECNIFICACION PASILLOS"])

        # Fila de Aspectos a Incidir e Información Complementaria
        col_inc1, col_inc2 = st.columns([3, 1])
        with col_inc1:
            st.text_input("ASPECTOS A INCIDIR", value="Velocidad en la circulación de balón y perfiles de recepción.")
        with col_inc2:
            st.text_input("MATERIAL NECESARIO", value="Conos, Petos, Balones")

        st.markdown("---")
        
        # Selección y carga del ejercicio
        tareas_finales = df_total_tareas[
            (df_total_tareas['CONCEPTO GENERAL'] == s_general) & 
            (df_total_tareas['CONCEPTO MICRO'] == s_micro) & 
            (df_total_tareas['TIPOS DE TAREAS'] == s_tipo_tarea)
        ]
        lista_nombres_disponibles = tareas_finales['NOMBRE DE LA TAREA'].dropna().tolist() if not tareas_finales.empty else sorted(df_total_tareas['NOMBRE DE LA TAREA'].dropna().tolist())
        
        s_tarea_seleccionada = st.selectbox("🎯 NOMBRE TAREA (Biblioteca):", ["-- Selecciona un ejercicio --"] + lista_nombres_disponibles)
        
        info_ejercicio_actual = df_total_tareas[df_total_tareas['NOMBRE DE LA TAREA'] == s_tarea_seleccionada]
        
        link_i = str(info_ejercicio_actual['LINK IMAGEN'].values[0]) if not info_ejercicio_actual.empty and pd.notna(info_ejercicio_actual['LINK IMAGEN'].values[0]) else ""
        link_v = str(info_ejercicio_actual['LINK VIDEO TAREA'].values[0]) if not info_ejercicio_actual.empty and pd.notna(info_ejercicio_actual['LINK VIDEO TAREA'].values[0]) else ""
        desc_t = str(info_ejercicio_actual['DESCRIPCION DE LA TAREA'].values[0]) if not info_ejercicio_actual.empty and pd.notna(info_ejercicio_actual['DESCRIPCION DE LA TAREA'].values[0]) else "Selecciona una tarea de la lista para mostrar su descripción."
