import requests
import pandas as pd
import streamlit as st
import altair as alt
#Aprendase el codigo 
# --- 1. Configuración ---
st.set_page_config(
    page_title="SpaceX Dashboard",
    page_icon="🚀",
    layout="wide"
)

# --- 2. Definiciones Globales ---
MAPA_MESES = {
    1: "01-Ene", 2: "02-Feb", 3: "03-Mar", 4: "04-Abr", 5: "05-May", 6: "06-Jun",
    7: "07-Jul", 8: "08-Ago", 9: "09-Sep", 10: "10-Oct", 11: "11-Nov", 12: "12-Dic"
}

# --- 3. Carga de Datos ---
URL_LAUNCHES = "https://api.spacexdata.com/v4/launches"
URL_PADS = "https://api.spacexdata.com/v4/launchpads"

@st.cache_data
def cargar_datos():
    try:
        resp_launches = requests.get(URL_LAUNCHES)
        resp_pads = requests.get(URL_PADS)
        
        if resp_launches.status_code == 200 and resp_pads.status_code == 200:
            df = pd.DataFrame(resp_launches.json())
            pads_data = resp_pads.json()
            
            # Mapeos
            mapa_pads = {pad['id']: pad['name'] for pad in pads_data}
            mapa_cohetes = {
                "5e9d0d95eda69955f709d1eb": "Falcon 1", "5e9d0d95eda69973a809d1ec": "Falcon 9",
                "5e9d0d95eda69974db09d1ed": "Falcon Heavy", "5e9d0d96eda699382d09d1ee": "Starship"
            }
            
            # --- LIMPIEZA CLAVE ---
            df = df[df['success'].notna()]
            
            # Transformaciones
            df['rocket_name'] = df['rocket'].map(mapa_cohetes).fillna("Otro")
            df['launchpad_name'] = df['launchpad'].map(mapa_pads).fillna("Sin Asignar")
            df['date_utc'] = pd.to_datetime(df['date_utc'])
            df['mes_nombre'] = df['date_utc'].dt.month.map(MAPA_MESES)
            
            # Estado descriptivo (Solo Éxito o Fallo)
            df['estado_desc'] = df['success'].apply(lambda x: "Éxito" if x is True else "Fallo")
            
            return df
        return pd.DataFrame()
    except Exception:
        return pd.DataFrame()

df = cargar_datos()

# --- 4. Sidebar ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/9/96/SpaceX_Logo_Black.png", use_container_width=True)
    st.header("Configuración")
    
    if st.button("🔄 Refrescar Datos", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    
    st.divider()
    
    # Filtro simplificado: Solo Éxito o Fallo
    filtro_estado = st.radio("Estado de Misión:", ["Todos", "Éxito", "Fallo"])
    
    if not df.empty:
        anio_min = int(df['date_utc'].dt.year.min())
        anio_max = int(df['date_utc'].dt.year.max())
        rango_anios = st.slider("📅 Periodo:", min_value=anio_min, max_value=anio_max, value=(anio_min, anio_max))
    else:
        st.stop()

# --- 5. Filtro Principal ---
df_filtrado = df[
    (df['date_utc'].dt.year >= rango_anios[0]) & 
    (df['date_utc'].dt.year <= rango_anios[1])
]

if filtro_estado == "Éxito":
    df_filtrado = df_filtrado[df_filtrado['estado_desc'] == "Éxito"]
elif filtro_estado == "Fallo":
    df_filtrado = df_filtrado[df_filtrado['estado_desc'] == "Fallo"]

# --- 6. Dashboard ---
st.title("🚀 SpaceX Mission Analytics")

tab_visual, tab_data = st.tabs(["📊 Dashboard Ejecutivo", "📋 Base de Datos"])

with tab_visual:
    if not df_filtrado.empty:
        
        # KPIs, apartado con datos como números sobre cantidad de lanzamientos , porcentaje de éxito y fallo
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Misiones Totales", len(df_filtrado))
        k2.metric("Éxitos", len(df_filtrado[df_filtrado['estado_desc'] == "Éxito"]))
        k3.metric("Fallos", len(df_filtrado[df_filtrado['estado_desc'] == "Fallo"]))
        
        # Tasa de éxito solo con datos reales
        total = len(df_filtrado)
        exitos = len(df_filtrado[df_filtrado['estado_desc'] == "Éxito"])
        tasa = (exitos / total * 100) if total > 0 else 0
        k4.metric("Tasa de Éxito", f"{tasa:.1f}%")
        
        st.write("") 
        
        # Escala de colores estricta (Verde/Rojo)
        scale_estados = alt.Scale(domain=["Éxito", "Fallo"], range=["#2ca02c", "#d62728"])

        # --- FILA 1 ---
        c1, c2 = st.columns(2, gap="medium")
        
        with c1:
            with st.container(border=True):
                st.subheader("Evolución Temporal")
                
                # --- LÓGICA DE RELLENO DE CEROS ---
                # 1. Crear esqueleto con TODOS los años y estados posibles
                anios_rango = list(range(rango_anios[0], rango_anios[1] + 1))
                estados_posibles = ["Éxito", "Fallo"]
                
                # Crear DataFrame base con todas las combinaciones (Producto cartesiano manual)
                esqueleto = pd.DataFrame(
                    [(y, s) for y in anios_rango for s in estados_posibles],
                    columns=['Año', 'estado_desc']
                )
                
                # 2. Agrupar datos reales
                datos_reales = df_filtrado.groupby([df_filtrado['date_utc'].dt.year, 'estado_desc']).size().reset_index(name='Lanzamientos')
                datos_reales.columns = ['Año', 'estado_desc', 'Lanzamientos'] # Asegurar nombres
                
                # 3. Combinar (Merge) para rellenar huecos con 0
                df_linea = pd.merge(esqueleto, datos_reales, on=['Año', 'estado_desc'], how='left').fillna(0)

                # Gráfico
                chart_line = alt.Chart(df_linea).mark_line(point=True).encode(
                    x=alt.X('Año:O', title='Año'),
                    y=alt.Y('Lanzamientos', axis=alt.Axis(format='d', tickMinStep=1), scale=alt.Scale(domainMin=0)),
                    color=alt.Color('estado_desc', scale=scale_estados, legend=alt.Legend(title="Resultado")),
                    tooltip=['Año', 'estado_desc', 'Lanzamientos']
                ).interactive()
                st.altair_chart(chart_line, use_container_width=True)

        with c2:
            with st.container(border=True):
                # Gráfico Circular (Donut)
                if filtro_estado == "Todos":
                    st.subheader("Proporción Global")
                    data_pie = df_filtrado['estado_desc'].value_counts().reset_index()
                    data_pie.columns = ['Categoría', 'Cantidad']
                    colores_pie = scale_estados
                else:
                    st.subheader(f"Rendimiento por Cohete: {filtro_estado}")
                    data_pie = df_filtrado['rocket_name'].value_counts().reset_index()
                    data_pie.columns = ['Categoría', 'Cantidad']
                    colores_pie = alt.Scale(scheme="category10")

                base = alt.Chart(data_pie).encode(theta=alt.Theta("Cantidad", stack=True))
                
                pie = base.mark_arc(innerRadius=60, outerRadius=120).encode(
                    color=alt.Color("Categoría", scale=colores_pie),
                    order=alt.Order("Cantidad", sort="descending"),
                    tooltip=["Categoría", "Cantidad"]
                )
                # Texto centrado en el anillo
                text = base.mark_text(radius=90).encode(
                    text="Cantidad",
                    order=alt.Order("Cantidad", sort="descending"),
                    color=alt.value("white")
                )
                st.altair_chart(pie + text, use_container_width=True)

        # --- FILA 2 ---
        c3, c4 = st.columns(2, gap="medium")
        
        with c3:
            with st.container(border=True):
                st.subheader("Estacionalidad (Lanzamientos por Mes)")
                chart_mes = alt.Chart(df_filtrado).mark_bar(color='#17becf').encode(
                    x=alt.X('mes_nombre', title='Mes', sort=list(MAPA_MESES.values())), 
                    y=alt.Y('count()', title='Misiones', axis=alt.Axis(format='d', tickMinStep=1)),
                    tooltip=['mes_nombre', 'count()']
                ).interactive()
                st.altair_chart(chart_mes, use_container_width=True)

        with c4:
            with st.container(border=True):
                st.subheader("Carga por Plataforma")
                chart_horiz = alt.Chart(df_filtrado).mark_bar().encode(
                    x=alt.X('count()', title='Cantidad', axis=alt.Axis(format='d', tickMinStep=1)),
                    y=alt.Y('launchpad_name', sort='-x', title=None),
                    color=alt.Color('estado_desc', scale=scale_estados, legend=None),
                    tooltip=['launchpad_name', 'count()']
                ).interactive()
                st.altair_chart(chart_horiz, use_container_width=True)
        
        # --- Análisis ---
        st.markdown("### 📝 Interpretación de Resultados")
        
        with st.expander("Ver Análisis Detallado", expanded=True):
            
            # 1. Cálculos auxiliares para el texto (Variables inteligentes)
            if not df_filtrado.empty:
                top_rocket = df_filtrado['rocket_name'].mode()[0] if not df_filtrado['rocket_name'].empty else "N/A"
                top_pad = df_filtrado['launchpad_name'].mode()[0] if not df_filtrado['launchpad_name'].empty else "N/A"
                peak_year = df_filtrado['date_utc'].dt.year.mode()[0] if not df_filtrado.empty else "N/A"
            
            # 2. Lógica del Texto según el Filtro
            if filtro_estado == "Todos":
                st.markdown(f"""
                **1. Visión General:**
                En el periodo analizado, SpaceX ha realizado un total de **{len(df_filtrado)} lanzamientos**. 
                La gráfica de evolución temporal muestra cómo la cadencia de lanzamiento alcanzó su punto máximo en el año **{peak_year}**, 
                impulsada principalmente por el despliegue de la constelación Starlink.
                
                **2. Infraestructura y Vehículos:**
                El vehículo **{top_rocket}** se consolida como la pieza central de las operaciones, mientras que la plataforma **{top_pad}** ha soportado la mayor carga de trabajo logística. La tasa global de éxito ({tasa:.1f}%) refleja la madurez tecnológica alcanzada tras las etapas iniciales.
                """)
                
            elif filtro_estado == "Éxito":
                st.markdown(f"""
                **1. Factores de Fiabilidad:**
                Se han completado con éxito **{len(df_filtrado)} misiones**. Este alto rendimiento se debe a la estandarización del cohete **{top_rocket}**.
                El gráfico circular destaca que este vehículo es el responsable de la gran mayoría de los éxitos comerciales y gubernamentales.
                
                **2. Estacionalidad Operativa:**
                El análisis mensual (barras azules) indica que las operaciones exitosas se distribuyen a lo largo de todo el año, 
                demostrando la capacidad de SpaceX para operar independientemente de ciertas ventanas estacionales, 
                con una alta concentración de despegues exitosos desde **{top_pad}**.
                """)
                
            elif filtro_estado == "Fallo":
                st.markdown(f"""
                **1. Análisis de Incidentes:**
                Los **{len(df_filtrado)} fallos** registrados se concentran históricamente en las etapas de desarrollo y pruebas experimentales. 
                Al observar la línea de tiempo, se nota que estos eventos no son recientes, sino que corresponden al aprendizaje inicial (Falcon 1) 
                o a pruebas de límites técnicos.
                
                **2. Puntos Críticos:**
                El cohete **{top_rocket}** aparece en esta categoría principalmente debido a sus primeras versiones o pruebas de aterrizaje. 
                Es crucial notar que la plataforma **{top_pad}** estuvo involucrada en estos eventos, lo que a menudo conlleva periodos de reconstrucción y mejora de la infraestructura.
                """)

    else:
        st.warning("⚠️ No se encontraron datos que coincidan con los filtros seleccionados.")

with tab_data:
    st.markdown("### 📋 Datos Detallados")
    st.dataframe(df_filtrado[['name', 'date_utc', 'estado_desc', 'rocket_name', 'launchpad_name', 'details']], use_container_width=True)
