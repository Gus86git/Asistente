import streamlit as st
import json

# Configuración de la página
st.set_page_config(
    page_title="Sistema Experto de Riesgo Urbano",
    page_icon="🏗️",
    layout="wide"
)

# -------------------------
# BASE DE CONOCIMIENTO
# -------------------------
base_conocimiento = [
    {
        "id": "R1",
        "condicion": lambda datos: datos["tipo_obra"] == "demolicion" and datos["horario"] == "nocturno",
        "accion": "🚨 PROHIBIR trabajos nocturnos - Implementar barreras acústicas",
        "explicacion": "Demoliciones nocturnas generan alto impacto acústico en zonas urbanas según normativa ISO 9613-2",
        "riesgo": "ALTO",
        "categoria": "Acústico"
    },
    {
        "id": "R2",
        "condicion": lambda datos: datos["tipo_obra"] == "excavacion" and datos["horario"] == "nocturno",
        "accion": "⚠️ LIMITAR horarios nocturnos - Usar equipos silenciosos certificados",
        "explicacion": "Excavaciones nocturnas requieren control estricto de ruido (Límite: 45 dB nocturno)",
        "riesgo": "MEDIO",
        "categoria": "Acústico"
    },
    {
        "id": "R3",
        "condicion": lambda datos: datos["duracion"] > 60 and "residencial" in datos["zona"],
        "accion": "📊 Monitoreo acústico continuo - Horarios restringidos 8:00-18:00",
        "explicacion": "Obras prolongadas en zonas residenciales necesitan control de impacto ambiental continuo",
        "riesgo": "MEDIO",
        "categoria": "Social"
    },
    {
        "id": "R4",
        "condicion": lambda datos: datos["tipo_obra"] == "via_publica" and "centro" in datos["zona"],
        "accion": "🚦 Plan de desvíos vial - Señalización avanzada - Coordinación con tránsito",
        "explicacion": "Obras en vía pública céntrica afectan significativamente el tráfico según estudio de impacto vial",
        "riesgo": "ALTO",
        "categoria": "Vial"
    },
    {
        "id": "R5",
        "condicion": lambda datos: datos["tipo_obra"] == "demolicion" and "residencial" in datos["zona"],
        "accion": "🏠 Evacuación temporal vecinos - Protección fachadas colindantes - Seguro de responsabilidad",
        "explicacion": "Demoliciones en zona residencial requieren seguridad extrema y protección a vecinos",
        "riesgo": "ALTO",
        "categoria": "Seguridad"
    },
    {
        "id": "R6",
        "condicion": lambda datos: "escolar" in datos["zona"] and datos["horario"] == "diurno",
        "accion": "🏫 Suspender obras en horario escolar - Ruta peatonal segura",
        "explicacion": "Obras cerca de zonas escolares requieren ajuste de horarios para seguridad de estudiantes",
        "riesgo": "MEDIO",
        "categoria": "Social"
    },
    {
        "id": "R7",
        "condicion": lambda datos: datos["tipo_obra"] == "excavacion_profunda" and datos["duracion"] > 30,
        "accion": "🕳️ Estudio geotécnico obligatorio - Monitoreo de estructuras vecinas",
        "explicacion": "Excavaciones profundas prolongadas requieren control geotécnico especializado",
        "riesgo": "ALTO",
        "categoria": "Seguridad"
    }
]

# -------------------------
# MOTOR DE INFERENCIA
# -------------------------
def motor_inferencia(tipo_obra, horario, duracion, zona):
    datos_entrada = {
        "tipo_obra": tipo_obra,
        "horario": horario,
        "duracion": duracion,
        "zona": zona.lower()
    }
    
    resultados = []
    reglas_aplicadas = []
    
    for regla in base_conocimiento:
        if regla["condicion"](datos_entrada):
            resultados.append({
                "accion": regla["accion"],
                "explicacion": regla["explicacion"],
                "riesgo": regla["riesgo"],
                "id": regla["id"],
                "categoria": regla["categoria"]
            })
            reglas_aplicadas.append(regla["id"])
    
    if not resultados:
        resultados.append({
            "accion": "✅ OBRA DE BAJO IMPACTO - Procedimientos estándar aplicables",
            "explicacion": "No se detectaron condiciones de riesgo elevado según los parámetros ingresados",
            "riesgo": "BAJO",
            "id": "R0",
            "categoria": "General"
        })
    
    return resultados, reglas_aplicadas, datos_entrada

# -------------------------
# VISUALIZACIÓN ALTERNATIVA - SIN MATPLOTLIB
# -------------------------
def mostrar_grafo_textual():
    st.subheader("Estructura del Sistema Experto")
    
    st.markdown("""
    **Flujo de Decisiones:**
    ```
    ENTRADA → [Tipo Obra, Horario, Duración, Zona] 
              ↓
    EVALUACIÓN → Motor de Inferencia
              ↓
    REGLAS APLICABLES → [R1, R2, R3, ...]
              ↓
    DIAGNÓSTICO → [Riesgo ALTO/MEDIO/BAJO]
              ↓
    RECOMENDACIONES → Medidas Específicas
    ```
    """)
    
    st.subheader("📋 Reglas del Sistema")
    for regla in base_conocimiento:
        with st.expander(f"Regla {regla['id']} - Riesgo {regla['riesgo']} - {regla['categoria']}"):
            st.write(f"**Condición:** {regla['condicion'].__doc__ or 'Evaluación específica del contexto'}")
            st.write(f"**Acción:** {regla['accion']}")
            st.write(f"**Explicación:** {regla['explicacion']}")

# -------------------------
# INTERFAZ STREAMLIT
# -------------------------

# Header principal
st.title("🏗️ Sistema Experto de Evaluación de Riesgo e Impacto Urbano")
st.markdown("---")

# Sidebar con información
with st.sidebar:
    st.header("ℹ️ Información del Sistema")
    st.markdown("""
    **Variables de Evaluación:**
    - 🏭 **Tipo de obra**: Naturaleza de la construcción
    - ⏰ **Horario**: Turnos de trabajo  
    - 📅 **Duración**: Tiempo total del proyecto
    - 🗺️ **Zona**: Área urbana afectada
    
    **Niveles de Riesgo:**
    - 🔴 **ALTO**: Medidas restrictivas inmediatas
    - 🟡 **MEDIO**: Controles y monitoreo específico  
    - 🟢 **BAJO**: Procedimientos estándar
    
    **Categorías de Impacto:**
    - 🔊 Acústico
    - 🚗 Vial
    - 🛡️ Seguridad  
    - 👥 Social
    - 🌿 Ambiental
    """)
    
    st.markdown("---")
    st.subheader("📊 Estadísticas del Sistema")
    st.write(f"• **Reglas activas:** {len(base_conocimiento)}")
    st.write(f"• **Categorías de riesgo:** 3 niveles")
    st.write(f"• **Tipos de impacto:** 5 categorías")

# Layout principal
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📝 Datos del Proyecto")
    
    # Inputs del usuario
    tipo_obra = st.selectbox(
        "Tipo de obra:",
        ["demolicion", "excavacion", "via_publica", "construccion", "excavacion_profunda"],
        help="Seleccione el tipo de obra a evaluar",
        index=0
    )
    
    horario = st.selectbox(
        "Horario de trabajo:",
        ["diurno", "nocturno", "mixto"],
        help="Horario principal de ejecución de la obra",
        index=0
    )
    
    duracion = st.slider(
        "Duración estimada (días):",
        min_value=1,
        max_value=180,
        value=30,
        help="Duración total estimada del proyecto"
    )
    
    zona = st.text_input(
        "Zona urbana:",
        value="residencial",
        help="Ejemplos: residencial, centro, escolar, industrial, comercial, residencial centro...",
        placeholder="Ingrese el tipo de zona urbana"
    )
    
    # Botón de evaluación
    if st.button("🚀 Evaluar Riesgo Urbano", type="primary", use_container_width=True):
        with st.spinner("Analizando riesgos urbanos..."):
            resultados, reglas_aplicadas, datos_entrada = motor_inferencia(tipo_obra, horario, duracion, zona)
            st.session_state.resultados = resultados
            st.session_state.reglas_aplicadas = reglas_aplicadas
            st.session_state.datos_entrada = datos_entrada
            st.session_state.mostrar_resultados = True

with col2:
    st.subheader("🎯 Sistema de Decisiones")
    mostrar_grafo_textual()

# Mostrar resultados si existen
if hasattr(st.session_state, 'mostrar_resultados') and st.session_state.mostrar_resultados:
    st.markdown("---")
    st.subheader("🔍 Resultados de la Evaluación")
    
    resultados = st.session_state.resultados
    datos_entrada = st.session_state.datos_entrada
    
    # Resumen ejecutivo
    st.info(f"""
    **Proyecto Analizado:** {datos_entrada['tipo_obra'].title()} | 
    **Horario:** {datos_entrada['horario'].title()} | 
    **Duración:** {datos_entrada['duracion']} días | 
    **Zona:** {datos_entrada['zona'].title()}
    """)
    
    # Contadores de riesgo
    alto_riesgo = sum(1 for r in resultados if r['riesgo'] == 'ALTO')
    medio_riesgo = sum(1 for r in resultados if r['riesgo'] == 'MEDIO')
    bajo_riesgo = sum(1 for r in resultados if r['riesgo'] == 'BAJO')
    
    # Métricas de riesgo
    col_met1, col_met2, col_met3, col_met4 = st.columns(4)
    
    with col_met1:
        st.metric("Riesgos ALTOS", alto_riesgo, delta_color="inverse")
    
    with col_met2:
        st.metric("Riesgos MEDIOS", medio_riesgo)
    
    with col_met3:
        st.metric("Riesgos BAJOS", bajo_riesgo, delta_color="off")
        
    with col_met4:
        st.metric("Total Medidas", len(resultados))
    
    # Mostrar diagnósticos por categoría de riesgo
    st.subheader("📋 Medidas Recomendadas")
    
    # Agrupar por nivel de riesgo
    resultados_altos = [r for r in resultados if r['riesgo'] == 'ALTO']
    resultados_medios = [r for r in resultados if r['riesgo'] == 'MEDIO']
    resultados_bajos = [r for r in resultados if r['riesgo'] == 'BAJO']
    
    if resultados_altos:
        st.error("### 🔴 Medidas de Alto Riesgo")
        for i, resultado in enumerate(resultados_altos, 1):
            with st.expander(f"{resultado['id']}: {resultado['accion']}", expanded=True):
                st.write(f"**Categoría:** {resultado['categoria']}")
                st.write(f"**Fundamento técnico:** {resultado['explicacion']}")
    
    if resultados_medios:
        st.warning("### 🟡 Medidas de Riesgo Medio")
        for i, resultado in enumerate(resultados_medios, 1):
            with st.expander(f"{resultado['id']}: {resultado['accion']}", expanded=True):
                st.write(f"**Categoría:** {resultado['categoria']}")
                st.write(f"**Fundamento técnico:** {resultado['explicacion']}")
    
    if resultados_bajos:
        st.success("### 🟢 Medidas de Bajo Riesgo")
        for i, resultado in enumerate(resultados_bajos, 1):
            with st.expander(f"{resultado['id']}: {resultado['accion']}", expanded=True):
                st.write(f"**Categoría:** {resultado['categoria']}")
                st.write(f"**Fundamento técnico:** {resultado['explicacion']}")
    
    # Resumen técnico
    st.subheader("📊 Resumen Técnico")
    col_tech1, col_tech2 = st.columns(2)
    
    with col_tech1:
        st.write("**Reglas Aplicadas:**")
        for regla_id in st.session_state.reglas_aplicadas:
            st.write(f"• {regla_id}")
        if not st.session_state.reglas_aplicadas:
            st.write("• R0 (Procedimiento estándar)")
    
    with col_tech2:
        st.write("**Distribución por Categoría:**")
        categorias = {}
        for resultado in resultados:
            cat = resultado['categoria']
            categorias[cat] = categorias.get(cat, 0) + 1
        
        for categoria, count in categorias.items():
            st.write(f"• {categoria}: {count} medida(s)")

# Información adicional
st.markdown("---")
st.subheader("📖 Guía Rápida de Uso")

col_guide1, col_guide2, col_guide3 = st.columns(3)

with col_guide1:
    st.markdown("""
    **🏭 Tipos de Obra:**
    - Demolición: Derribo de estructuras
    - Excavación: Movimientos de tierra
    - Vía Pública: Trabajos en calles
    - Construcción: Edificaciones nuevas
    - Excavación Profunda: Subsuelo > 3m
    """)

with col_guide2:
    st.markdown("""
    **⏰ Horarios:**
    - Diurno: 6:00 - 20:00
    - Nocturno: 20:00 - 6:00  
    - Mixto: Combinación ambos
    """)

with col_guide3:
    st.markdown("""
    **🗺️ Zonas Comunes:**
    - Residencial: Viviendas
    - Centro: Área central
    - Escolar: Cerca de escuelas
    - Industrial: Zonas fabriles
    - Comercial: Área de comercios
    """)

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray;'>
        🏗️ Sistema Experto de Evaluación de Riesgo Urbano |
        Versión 2.0 - Streamlit Native
    </div>
    """,
    unsafe_allow_html=True
)

