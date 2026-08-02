import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Gestión Cantera Fútbol", layout="wide")
st.title("⚽ Sistema Integral de Metodología y Meritocracia")

# 2. CONEXIÓN A GOOGLE SHEETS
# Conectamos usando el gestor de conexiones nativo de Streamlit
conn = st.connection("gsheets", type=GSheetsConnection)

# Cargamos los datos de la pestaña "Jugadores"
try:
    df_jugadores = conn.read(worksheet="Jugadores", ttl=0) # ttl=0 fuerza a leer datos frescos sin caché
except Exception as e:
    st.error("Error al conectar con Google Sheets. Verifica las credenciales en Streamlit Cloud.")
    st.stop()

# 3. PANELES LATERALES (FILTRO DE EQUIPOS)
st.sidebar.header("⚙️ Panel de Control")
# Extraemos de forma dinámica los equipos que existen en tu Excel
lista_equipos = sorted(df_jugadores["Equipo"].unique().tolist())
equipo_seleccionado = st.sidebar.selectbox("Selecciona Equipo", lista_equipos)

# Filtrar jugadores del equipo seleccionado
df_filtrado = df_jugadores[df_jugadores["Equipo"] == equipo_seleccionado].copy()

# 4. MÓDULO INTERACTIVO: PASAR ASISTENCIA Y REGISTRAR ACTITUD
st.header(f"📋 Pasar Lista y Evaluar Actitud - {equipo_seleccionado}")

if not df_filtrado.empty:
    st.write("Registra el entrenamiento de hoy de forma rápida:")
    
    # Creamos un formulario para procesar todo el equipo junto
    with st.form(key="formulario_asistencia"):
        nuevos_datos_asistencia = []
        
        for idx, jugador in df_filtrado.iterrows():
            col_nom, col_asist, col_act = st.columns([2, 1, 2])
            with col_nom:
                st.markdown(f"**{jugador['Nombre']}**")
            with col_asist:
                # Selector de asistencia sencillo
                asiste = st.checkbox("Asiste", value=True, key=f"asist_{jugador['ID']}")
            with col_act:
                # Selector de actitud de 1 a 5 estrellas
                actitud = st.slider("Actitud en el entreno", 1.0, 5.0, 5.0, 0.5, key=f"act_{jugador['ID']}")
            
            nuevos_datos_asistencia.append({
                "ID": jugador["ID"], 
                "Asiste": asiste, 
                "Actitud": actitud
            })
            
        guardar_btn = st.form_submit_button(label="💾 Guardar Entrenamiento de Hoy")
        
    if guardar_btn:
        # Procesar y actualizar el DataFrame global con los nuevos cálculos acumulados
        for registro in nuevos_datos_asistencia:
            idx_global = df_jugadores[df_jugadores["ID"] == registro["ID"]].index[0]
            
            # Sumamos 1 al total de entrenamientos obligatoriamente
            df_jugadores.at[idx_global, "Totales"] += 1
            
            if registro["Asiste"]:
                # Si asistió, sumamos la sesión de asistencia
                df_jugadores.at[idx_global, "Asistencias"] += 1
                # Recalculamos la actitud promedio de forma ponderada básica
                act_actual = df_jugadores.at[idx_global, "Actitud_Promedio"]
                totales = df_jugadores.at[idx_global, "Totales"]
                df_jugadores.at[idx_global, "Actitud_Promedio"] = round(((act_actual * (totales - 1)) + registro["Actitud"]) / totales, 2)
        
        # Guardamos la tabla actualizada directamente en Google Sheets de forma gratuita
        conn.update(worksheet="Jugadores", data=df_jugadores)
        st.success("¡Entrenamiento guardado y métricas actualizadas en Google Sheets!")
        st.rerun()
else:
    st.info("No hay jugadores registrados en este equipo dentro del Excel.")

# 5. MÓDULO: ALGORITMO DE MERITOCRACIA DEPORTIVA
st.header("📊 Índice de Meritocracia vs Minutos")

if not df_filtrado.empty:
    # Cálculos dinámicos del algoritmo solicitado
    df_filtrado["Asistencia_%"] = (df_filtrado["Asistencias"] / df_filtrado["Totales"]) * 100
    df_filtrado["IMD"] = (df_filtrado["Asistencia_%"] * 0.4) + ((df_filtrado["Actitud_Promedio"] / 5) * 100 * 0.6)
    df_filtrado["Minutos_%"] = (df_filtrado["Minutos_Jugados"] / df_filtrado["Minutos_Totales"]) * 100

    # Lógica de alertas automatizadas por pantalla
    for index, row in df_filtrado.iterrows():
        if row["IMD"] >= 85 and row["Minutos_%"] < 50:
            st.warning(f"⚠️ **Alerta de Injusticia**: {row['Nombre']} tiene un IMD excelente ({row['IMD']:.1f}%) pero solo juega el {row['Minutos_%']:.1f}% de los minutos.")
        if row["IMD"] < 60 and row["Minutos_%"] >= 70:
            st.error(f"🚨 **Alerta de Privilegio**: {row['Nombre']} entrena poco o con mala actitud ({row['IMD']:.1f}%) pero juega el {row['Minutos_%']:.1f}% de los minutos.")

    # Vista limpia de la tabla de rendimiento
    st.dataframe(df_filtrado[["Nombre", "Asistencia_%", "Actitud_Promedio", "IMD", "Minutos_%"]], use_container_width=True)

# 6. MÓDULO: DISEÑADOR DE SESIÓN EN 6 BLOQUES
st.header("📝 Diseñador Estructurado de Sesiones")

col1, col2 = st.columns(2)
with col1:
    b1 = st.text_area("Bloque 1: Vestuario Inicial (Charlas/Video)", "Charla sobre la basculación defensiva y dinámicas grupales.")
    b2 = st.text_area("Bloque 2: Calentamiento", "Rondo de activación de juego posicional 4x4 + 2 comodines.")
    espacio_b2 = st.selectbox("Espacio Calentamiento", ["Cuadrante", "1/4 Campo", "Medio Campo", "Campo Completo"])

with col2:
    b3 = st.text_area("Bloque 3, 4, 5: Tareas Principales", "Partido condicionado a un máximo de 3 toques con comodines exteriores.")
    espacio_b3 = st.selectbox("Espacio Tareas Principales", ["Medio Campo", "1/4 Campo", "Área a Área"])
    b6 = st.text_area("Bloque 6: Vuelta a la Calma y Vestuario", "Estiramientos dirigidos, feedback colectivo, ducha e higiene.")

# 7. MÓDULO: CONVOCATORIAS PARA WHATSAPP
st.header("📱 Generador de Convocatorias")
if not df_filtrado.empty:
    jugadores_convocados = st.multiselect("Selecciona los convocados", df_filtrado["Nombre"].tolist(), default=df_filtrado["Nombre"].tolist())

    col_riv, col_hor = st.columns(2)
    with col_riv:
        rival = st.text_input("Rival", "C.F. Las Arenas")
    with col_hor:
        hora = st.text_input("Hora de Cita", "10:30 H")

    texto_whatsapp = f"⚽ *CONVOCATORIA {equipo_seleccionado}* ⚽\n\n🗓️ *Rival:* {rival}\n📍 *Lugar:* Campo Local\n🕒 *Hora:* {hora}\n\n*Convocados:*\n"
    for i, jugador in enumerate(jugadores_convocados, 1):
        texto_whatsapp += f"{i}. {jugador}\n"
    texto_whatsapp += "\n¡Por favor, confirmad asistencia! 💪🔴"

    st.text_area("Copia este texto para WhatsApp:", texto_whatsapp, height=180)
