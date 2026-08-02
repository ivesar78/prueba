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
        df_j = pd.read_csv(URL_JUGADORES).rename(columns=lambda x: x.strip())
        df_t = pd.read_csv(URL_LIBRERIA_TAREAS).rename(columns=lambda x: x.strip())
    except:
        df_j = pd.DataFrame()
        df_t = pd.DataFrame(columns=['ETAPA', 'TIPO DE CONCEPTO', 'CONCEPTO GENERAL', 'CONCEPTO MICRO', 'TIPOS DE TAREAS', 'NOMBRE DE LA TAREA', 'LINK IMAGEN', 'LINK VIDEO TAREA', 'DESCRIPCION DE LA TAREA', 'NORMAS', 'TAREA NOMBRE VARIANTE', 'LINK VARIANTE TAREA'])
    return df_j, df_t

df_jugadores, df_tareas_base = cargar_datos_base()

# Memoria para nuevas tareas y unificación
if "tareas_creadas_en_vivo" not in st.session_state:
    st.session_state.tareas_creadas_en_vivo = pd.DataFrame()

df_total_tareas = pd.concat([df_tareas_base, st.session_state.tareas_creadas_en_vivo], ignore_index=True).drop_duplicates(subset=['NOMBRE DE LA TAREA'])

# SELECTOR DE EQUIPO
st.sidebar.header("🛡️ Acceso por Equipos")
if not df_jugadores.empty and "Equipo" in df_jugadores.columns:
    lista_equipos = sorted(df_jugadores["Equipo"].dropna().unique().tolist())
    equipo_seleccionado = st.sidebar.selectbox("Selecciona la plantilla:", lista_equipos)
    df_filtrado_jugadores = df_jugadores[df_jugadores["Equipo"] == equipo_seleccionado]
else:
    df_filtrado_jugadores = pd.DataFrame()

st.markdown("---")

# 2. SELECCIÓN DE OPCIÓN PRINCIPAL
opcion_menu = st.radio(
    "👉 **SELECCIONA UNA OPCIÓN:**", 
    ["Añadir Nuevas Tareas", "Diseñar una Nueva Sesión"],
    horizontal=True
)

st.markdown("---")

# ==========================================
# OPCIÓN 1: CREAR TAREAS (CON LAS 12 OPCIONES DE LA IMAGEN)
# ==========================================
if opcion_menu == "Añadir Nuevas Tareas":
    st.subheader("🛠️ CREADOR DE TAREAS")
    with st.form("formulario_crear_tarea_igx"):
        col1, col2, col3 = st.columns(3)
        c_etapa = col1.selectbox("ETAPA", ["TODAS", "PREBENJAMÍN", "BENJAMÍN", "ALEVÍN", "INFANTIL", "CADETE", "JUVENIL"])
        c_tipo_concepto = col2.selectbox("TIPO DE CONCEPTO", ["TACTICOS", "TECNICOS", "FISICOS", "ACTITUDINALES"])
        c_concepto_general = col3.text_input("CONCEPTO GENERAL")
        
        col4, col5, col6 = st.columns(3)
        c_concepto_micro = col4.text_input("CONCEPTO MICRO")
        
        # Opciones actualizadas letra por letra según la imagen:
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
# OPCIÓN 2: CREAR SESIÓN
# ==========================================
else:
    st.subheader("⏱️ DISEÑADOR DE SESIONES")
    with st.container(border=True):
        c_f1, c_f2, c_f3 = st.columns(3)
        f_tipo = c_f1.selectbox("Filtrar TIPO DE CONCEPTO", sorted(df_total_tareas['TIPO DE CONCEPTO'].dropna().unique()) if not df_total_tareas.empty else ["TACTICOS"])
        f_general = c_f2.selectbox("Filtrar CONCEPTO GENERAL", sorted(df_total_tareas['CONCEPTO GENERAL'].dropna().unique()) if not df_total_tareas.empty else [""])
        
        tareas_filtradas = df_total_tareas[
            (df_total_tareas['TIPO DE CONCEPTO'] == f_tipo) & 
            (df_total_tareas['CONCEPTO GENERAL'] == f_general)
        ]
        
        lista_nombres = tareas_filtradas['NOMBRE DE LA TAREA'].dropna().tolist() if not tareas_filtradas.empty else []
        tarea_seleccionada = c_f3.selectbox("🎯 NOMBRE DE LA TAREA DISPONIBLE:", ["-- Selecciona --"] + lista_nombres)

    if tarea_seleccionada != "-- Selecciona --":
        info_t = df_total_tareas[df_total_tareas['NOMBRE DE LA TAREA'] == tarea_seleccionada].iloc[0]
        
        st.markdown(f"### 📋 {info_t['NOMBRE DE LA TAREA']}")
        col_det1, col_det2 = st.columns(2)
        with col_det1:
            st.write(f"**Etapa:** {info_t['ETAPA']}")
            st.write(f"**Tipo de Tarea:** {info_t['TIPOS DE TAREAS']}")
            st.write(f"**Concepto Micro:** {info_t['CONCEPTO MICRO']}")
            st.write(f"**Descripción:** {info_t['DESCRIPCION DE LA TAREA']}")
        with col_det2:
            st.write(f"**Normas:** {info_t['NORMAS']}")
            if pd.notna(info_t['LINK IMAGEN']) and str(info_t['LINK IMAGEN']).startswith("http"):
                st.image(info_t['LINK IMAGEN'], caption="Imagen del ejercicio")

    st.markdown("---")
    if not df_filtrado_jugadores.empty:
        st.subheader("👥 Convocatoria del Equipo")
        st.multiselect("Selecciona los jugadores convocados:", df_filtrado_jugadores["Nombre"].tolist(), default=df_filtrado_jugadores["Nombre"].tolist())
    
    st.info("💡 Recuerda que puedes exportar la planificación completa pulsando **Ctrl+P** / **Cmd+P** en tu teclado.")





