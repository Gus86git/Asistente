import streamlit as st
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

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
        "condicion": lambda tipo_obra, horario, duracion, zona: 
                    tipo_obra == "demolicion" and horario == "nocturno",
        "accion": "🚨 PROHIBIR trabajos nocturnos - Implementar barreras acústicas",
        "explicacion": "Demoliciones nocturnas generan alto impacto acústico en zonas urbanas según normativa ISO 9613-2",
        "riesgo": "ALTO"
    },
    {
        "id": "R2",
        "condicion": lambda tipo_obra, horario, duracion, zona: 
                    tipo_obra == "excavacion" and horario == "nocturno",
        "accion": "⚠️ LIMITAR horarios nocturnos - Usar equipos silenciosos certificados",
        "explicacion": "Excavaciones nocturnas requieren control estricto de ruido (Límite: 45 dB nocturno)",
        "riesgo": "MEDIO"
    },
    {
        "id": "R3",
        "condicion": lambda tipo_obra, horario, duracion, zona: 
                    duracion > 60 and "residencial" in zona,
        "accion": "📊 Monitoreo acústico continuo - Horarios restringidos 8:00-18:00",
        "explicacion": "Obras prolongadas en zonas residenciales necesitan control de impacto ambiental continuo",
        "riesgo": "MEDIO"
    },
    {
        "id": "R4",
        "condicion": lambda tipo_obra, horario, duracion, zona: 
                    tipo_obra == "via_publica" and "centro" in zona,
        "accion": "🚦 Plan de desvíos vial - Señalización avanzada - Coordinación con tránsito",
        "explicacion": "Obras en vía pública céntrica afectan significativamente el tráfico según estudio de impacto vial",
        "riesgo": "ALTO"
    },
    {
        "id": "R5",
        "condicion": lambda tipo_obra, horario, duracion, zona: 
                    tipo_obra == "demolicion" and "residencial" in zona,
        "accion": "🏠 Evacuación temporal vecinos - Protección fachadas colindantes - Seguro de responsabilidad",
        "explicacion": "Demoliciones en zona residencial requieren seguridad extrema y protección a vecinos",
        "riesgo": "ALTO"
    },
    {
        "id": "R6",
        "condicion": lambda tipo_obra, horario, duracion, zona: 
                    "escolar" in zona and horario == "diurno",
        "accion": "🏫 Suspender obras en horario escolar - Ruta peatonal segura",
        "explicacion": "Obras cerca de zonas escolares requieren ajuste de horarios para seguridad de estudiantes",
        "riesgo": "MEDIO"
    },
    {
        "id": "R7",
        "condicion": lambda tipo_obra, horario, duracion, zona: 
                    tipo_obra == "excavacion_profunda" and duracion > 30,
        "accion": "🕳️ Estudio geotécnico obligatorio - Monitoreo de estructuras vecinas",
        "explicacion": "Excavaciones profundas prolongadas requieren control geotécnico especializado",
        "riesgo": "ALTO"
    }
]

# -------------------------
# BASE DE HECHOS
# -------------------------
if 'base_hechos' not in st.session_state:
    st.session_state.base_hechos = {
        "tipo_obra_actual": "",
        "horario_actual": "",
        "duracion_actual": 0,
        "zona_actual": "",
        "diagnosticos": [],
        "reglas_aplicadas": []
    }

def actualizar_base_hechos(tipo_obra, horario, duracion, zona):
    st.session_state.base_hechos["tipo_obra_actual"] = tipo_obra
    st.session_state.base_hechos["horario_actual"] = horario
    st.session_state.base_hechos["duracion_actual"] = duracion
    st.session_state.base_hechos["zona_actual"] = zona
    st.session_state.base_hechos["diagnosticos"] = []
    st.session_state.base_hechos["reglas_aplicadas"] = []

# -------------------------
# MOTOR DE INFERENCIA
# -------------------------
def motor_inferencia(tipo_obra, horario, duracion, zona):
    actualizar_base_hechos(tipo_obra, horario, duracion, zona)
    resultados = []
    
    for regla in base_conocimiento:
        if regla["condicion"](tipo_obra, horario, duracion, zona):
            resultados.append({
                "accion": regla["accion"],
                "explicacion": regla["explicacion"],
                "riesgo": regla["riesgo"],
                "id": regla["id"]
            })
            st.session_state.base_hechos["diagnosticos"].append(regla["accion"])
            st.session_state.base_hechos["reglas_aplicadas"].append(regla["id"])
    
    return resultados if resultados else [{
        "accion": "✅ OBRA DE BAJO IMPACTO - Procedimientos estándar aplicables",
        "explicacion": "No se detectaron condiciones de riesgo elevado según los parámetros ingresados",
        "riesgo": "BAJO",
        "id": "R0"
    }]

# -------------------------
# MÓDULO DE EXPLICACIÓN
# -------------------------
def generar_explicacion():
    explicaciones = []
    for regla_id in st.session_state.base_hechos["reglas_aplicadas"]:
        regla = next((r for r in base_conocimiento if r["id"] == regla_id), None)
        if regla:
            explicaciones.append({
                "id": regla_id,
                "explicacion": regla['explicacion'],
                "riesgo": regla.get('riesgo', 'MEDIO')
            })
    return explicaciones

# -------------------------
# VISUALIZACIÓN DEL GRAFO
# -------------------------
def crear_grafo_decisiones():
    G = nx.DiGraph()
    
    # Nodos principales del sistema
    nodos = [
        ("INICIO", {"color": "lightgreen", "shape": "oval", "size": 2000}),
        ("TIPO_OBRA", {"color": "lightblue", "shape": "box", "size": 1500}),
        ("HORARIO", {"color": "lightblue", "shape": "box", "size": 1500}),
        ("DURACION", {"color": "lightblue", "shape": "box", "size": 1500}),
        ("ZONA", {"color": "lightblue", "shape": "box", "size": 1500}),
        ("EVALUACION", {"color": "yellow", "shape": "diamond", "size": 1800}),
        ("RIESGO_ALTO", {"color": "red", "shape": "box", "size": 1200}),
        ("RIESGO_MEDIO", {"color": "orange", "shape": "box", "size": 1200}),
        ("RIESGO_BAJO", {"color": "green", "shape": "box", "size": 1200}),
    ]

    # Agregar nodos de reglas específicas
    for regla in base_conocimiento:
        nodo_regla = (f"REGLA_{regla['id']}", {"color": "lightcoral", "shape": "ellipse", "size": 1000})
        nodos.append(nodo_regla)

    for nodo, atributos in nodos:
        G.add_node(nodo, **atributos)

    # Conexiones del flujo principal
    conexiones_principales = [
        ("INICIO", "TIPO_OBRA"),
        ("TIPO_OBRA", "EVALUACION"),
        ("HORARIO", "EVALUACION"),
        ("DURACION", "EVALUACION"),
        ("ZONA", "EVALUACION"),
        ("EVALUACION", "RIESGO_ALTO"),
        ("EVALUACION", "RIESGO_MEDIO"),
        ("EVALUACION", "RIESGO_BAJO")
    ]

    for origen, destino in conexiones_principales:
        G.add_edge(origen, destino, weight=2)

    # Conexiones de reglas específicas
    for regla in base_conocimiento:
        G.add_edge("EVALUACION", f"REGLA_{regla['id']}", weight=1)
        # Determinar nivel de riesgo basado en la acción
        if regla.get('riesgo') == 'ALTO':
            G.add_edge(f"REGLA_{regla['id']}", "RIESGO_ALTO", weight=1)
        elif regla.get('riesgo') == 'MEDIO':
            G.add_edge(f"REGLA_{regla['id']}", "RIESGO_MEDIO", weight=1)
        else:
            G.add_edge(f"REGLA_{regla['id']}", "RIESGO_BAJO", weight=1)

    return G

def visualizar_grafo():
    G = crear_grafo_decisiones()
    
    plt.figure(figsize=(14, 10))
    
    # Configurar posiciones
    pos = nx.spring_layout(G, k=3, iterations=50, seed=42)
    
    # Dibujar nodos
    node_colors = [G.nodes[n]['color'] for n in G.nodes()]
    node_sizes = [G.nodes[n]['size'] for n in G.nodes()]
    
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, 
                          node_size=node_sizes, alpha=0.9,
                          edgecolors='black', linewidths=2)
    
    # Dibujar aristas
    nx.draw_networkx_edges(G, pos, edge_color='gray', arrows=True, 
                          arrowsize=20, arrowstyle='->', width=1.5, alpha=0.7)
    
    # Dibujar etiquetas
    labels = {nodo: nodo.replace('REGLA_', 'R') for nodo in G.nodes()}
    nx.draw_networkx_labels(G, pos, labels, font_size=8, font_weight='bold')
    
    plt.title("🏗️ GRAFO DE DECISIONES - SISTEMA EXPERTO DE RIESGO URBANO", 
              fontsize=16, fontweight='bold', pad=20)
    plt.axis('off')
    
    return plt.gcf()

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
    - 🏭 Tipo de obra
    - ⏰ Horario de trabajo  
    - 📅 Duración del proyecto
    - 🗺️ Zona urbana afectada
    
    **Niveles de Riesgo:**
    - 🔴 ALTO: Medidas restrictivas
    - 🟡 MEDIO: Controles específicos  
    - 🟢 BAJO: Procedimientos estándar
    """)
    
    st.markdown("---")
    st.subheader("📊 Estadísticas del Sistema")
    st.write(f"• Reglas activas: {len(base_conocimiento)}")
    st.write("• Categorías de riesgo: 3")
    st.write("• Variables de entrada: 4")

# Layout principal en columnas
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📝 Datos del Proyecto")
    
    # Inputs del usuario
    tipo_obra = st.selectbox(
        "Tipo de obra:",
        ["demolicion", "excavacion", "via_publica", "construccion", "excavacion_profunda"],
        help="Seleccione el tipo de obra a evaluar"
    )
    
    horario = st.selectbox(
        "Horario de trabajo:",
        ["diurno", "nocturno", "mixto"],
        help="Horario principal de ejecución de la obra"
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
        help="Ej: residencial, centro, escolar, industrial, residencial centro..."
    )
    
    # Botón de evaluación
    if st.button("🚀 Evaluar Riesgo Urbano", type="primary", use_container_width=True):
        with st.spinner("Analizando riesgos urbanos..."):
            resultados = motor_inferencia(tipo_obra, horario, duracion, zona)
            st.session_state.resultados = resultados
            st.session_state.mostrar_resultados = True

with col2:
    st.subheader("🎨 Visualización del Sistema")
    
    # Mostrar grafo
    fig = visualizar_grafo()
    st.pyplot(fig)

# Mostrar resultados si existen
if hasattr(st.session_state, 'mostrar_resultados') and st.session_state.mostrar_resultados:
    st.markdown("---")
    st.subheader("🔍 Resultados de la Evaluación")
    
    resultados = st.session_state.resultados
    
    # Contadores de riesgo
    alto_riesgo = sum(1 for r in resultados if r['riesgo'] == 'ALTO')
    medio_riesgo = sum(1 for r in resultados if r['riesgo'] == 'MEDIO')
    bajo_riesgo = sum(1 for r in resultados if r['riesgo'] == 'BAJO')
    
    # Métricas de riesgo
    col_met1, col_met2, col_met3 = st.columns(3)
    
    with col_met1:
        st.metric("Riesgos ALTOS", alto_riesgo, delta_color="inverse")
    
    with col_met2:
        st.metric("Riesgos MEDIOS", medio_riesgo)
    
    with col_met3:
        st.metric("Riesgos BAJOS", bajo_riesgo, delta_color="off")
    
    # Mostrar diagnósticos
    for i, resultado in enumerate(resultados, 1):
        # Color según riesgo
        if resultado['riesgo'] == 'ALTO':
            color = "red"
            icon = "🚨"
        elif resultado['riesgo'] == 'MEDIO':
            color = "orange" 
            icon = "⚠️"
        else:
            color = "green"
            icon = "✅"
        
        with st.expander(f"{icon} Medida {i} - Riesgo {resultado['riesgo']}", expanded=True):
            st.markdown(f"**Acción requerida:** {resultado['accion']}")
            st.markdown(f"**Fundamento técnico:** {resultado['explicacion']}")
            st.markdown(f"**Regla aplicada:** {resultado['id']}")
    
    # Módulo de explicación detallada
    st.markdown("---")
    st.subheader("💡 Explicación Detallada del Diagnóstico")
    
    explicaciones = generar_explicacion()
    if explicaciones:
        for exp in explicaciones:
            st.info(f"**{exp['id']}** - {exp['explicacion']} (Riesgo: {exp['riesgo']})")
    else:
        st.success("No se aplicaron reglas específicas - El proyecto presenta impacto urbano mínimo según los parámetros analizados")
    
    # Datos procesados
    with st.expander("📈 Datos Técnicos Procesados"):
        st.json(st.session_state.base_hechos)

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray;'>
        🏗️ Sistema Experto de Evaluación de Riesgo Urbano | 
        Desarrollado con técnicas de Inteligencia Artificial
    </div>
    """,
    unsafe_allow_html=True
)
