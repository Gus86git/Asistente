import streamlit as st
import matplotlib.pyplot as plt
import networkx as nx

# -------------------------
# BASE DE CONOCIMIENTO
# -------------------------
base_conocimiento = [
    {
        "id": "R1",
        "condicion": lambda tipo_obra, horario, duracion, zona: \
                    tipo_obra == "demolicion" and horario == "nocturno",
        "accion": "PROHIBIR trabajos nocturnos - Implementar barreras acústicas",
        "explicacion": "Demoliciones nocturnas generan alto impacto acústico en zonas urbanas"
    },
    {
        "id": "R2",
        "condicion": lambda tipo_obra, horario, duracion, zona: \
                    tipo_obra == "excavacion" and horario == "nocturno",
        "accion": "LIMITAR horarios nocturnos - Usar equipos silenciosos",
        "explicacion": "Excavaciones nocturnas requieren control estricto de ruido"
    },
    {
        "id": "R3",
        "condicion": lambda tipo_obra, horario, duracion, zona: \
                    duracion > 60 and zona == "residencial",
        "accion": "Monitoreo acústico continuo - Horarios restringidos 8:00-18:00",
        "explicacion": "Obras prolongadas en zonas residenciales necesitan control de impacto"
    },
    {
        "id": "R4",
        "condicion": lambda tipo_obra, horario, duracion, zona: \
                    tipo_obra == "via_publica" and "centro" in zona,
        "accion": "Plan de desvíos vial - Señalización avanzada",
        "explicacion": "Obras en vía pública céntrica afectan significativamente el tráfico"
    },
    {
        "id": "R5",
        "condicion": lambda tipo_obra, horario, duracion, zona: \
                    tipo_obra == "demolicion" and "residencial" in zona,
        "accion": "Evacuación temporal vecinos - Protección fachadas colindantes",
        "explicacion": "Demoliciones en zona residencial requieren seguridad extrema"
    }
]

# -------------------------
# BASE DE HECHOS
# -------------------------
base_hechos = {
    "tipo_obra_actual": "",
    "horario_actual": "",
    "duracion_actual": 0,
    "zona_actual": "",
    "diagnosticos": [],
    "reglas_aplicadas": []
}

def actualizar_base_hechos(tipo_obra, horario, duracion, zona):
    base_hechos["tipo_obra_actual"] = tipo_obra
    base_hechos["horario_actual"] = horario
    base_hechos["duracion_actual"] = duracion
    base_hechos["zona_actual"] = zona
    base_hechos["diagnosticos"] = []
    base_hechos["reglas_aplicadas"] = []

# -------------------------
# MOTOR DE INFERENCIA
# -------------------------
def motor_inferencia(tipo_obra, horario, duracion, zona):
    actualizar_base_hechos(tipo_obra, horario, duracion, zona)
    resultados = []
    for regla in base_conocimiento:
        if regla["condicion"](tipo_obra, horario, duracion, zona):
            resultados.append(regla["accion"])
            base_hechos["diagnosticos"].append(regla["accion"])
            base_hechos["reglas_aplicadas"].append(regla["id"])
    return resultados if resultados else ["OBRA DE BAJO IMPACTO - Procedimientos estándar"]

# -------------------------
# MÓDULO DE EXPLICACIÓN
# -------------------------
def generar_explicacion():
    explicaciones = []
    for regla_id in base_hechos["reglas_aplicadas"]:
        regla = next((r for r in base_conocimiento if r["id"] == regla_id), None)
        if regla:
            explicaciones.append(f"Regla {regla_id}: {regla['explicacion']}")
    return explicaciones

# -------------------------
# VISUALIZACIÓN DEL GRAFO
# -------------------------
def crear_grafo_decisiones():
    G = nx.DiGraph()
    nodos = [
        ("INICIO", {"color": "lightgreen", "size": 2000}),
        ("TIPO_OBRA", {"color": "lightblue", "size": 1500}),
        ("HORARIO", {"color": "lightblue", "size": 1500}),
        ("DURACION", {"color": "lightblue", "size": 1500}),
        ("ZONA", {"color": "lightblue", "size": 1500}),
        ("EVALUACION", {"color": "yellow", "size": 1800}),
        ("RIESGO_ALTO", {"color": "red", "size": 1200}),
        ("RIESGO_MEDIO", {"color": "orange", "size": 1200}),
        ("RIESGO_BAJO", {"color": "green", "size": 1200}),
    ]
    for i, regla in enumerate(base_conocimiento):
        nodo_regla = (f"REGLA_{regla['id']}", {"color": "lightcoral", "size": 1000})
        nodos.append(nodo_regla)
    for nodo, atributos in nodos:
        G.add_node(nodo, **atributos)

    conexiones = [
        ("INICIO", "TIPO_OBRA"),
        ("TIPO_OBRA", "EVALUACION"),
        ("HORARIO", "EVALUACION"),
        ("DURACION", "EVALUACION"),
        ("ZONA", "EVALUACION"),
        ("EVALUACION", "RIESGO_ALTO"),
        ("EVALUACION", "RIESGO_MEDIO"),
        ("EVALUACION", "RIESGO_BAJO")
    ]
    for o, d in conexiones:
        G.add_edge(o, d)

    for regla in base_conocimiento:
        G.add_edge("EVALUACION", f"REGLA_{regla['id']}")
        if "PROHIBIR" in regla["accion"] or "Evacuación" in regla["accion"]:
            G.add_edge(f"REGLA_{regla['id']}", "RIESGO_ALTO")
        elif "LIMITAR" in regla["accion"] or "Monitoreo" in regla["accion"]:
            G.add_edge(f"REGLA_{regla['id']}", "RIESGO_MEDIO")
        else:
            G.add_edge(f"REGLA_{regla['id']}", "RIESGO_BAJO")
    return G

def visualizar_grafo():
    G = crear_grafo_decisiones()
    plt.figure(figsize=(12,8))
    pos = nx.spring_layout(G, seed=42)
    node_colors = [G.nodes[n]['color'] for n in G.nodes()]
    node_sizes = [G.nodes[n]['size'] for n in G.nodes()]
    nx.draw(G, pos, with_labels=True, node_color=node_colors, node_size=node_sizes,
            font_size=7, font_weight="bold", edgecolors="black")
    st.pyplot(plt.gcf())

# -------------------------
# INTERFAZ STREAMLIT
# -------------------------
st.title("🏗️ Sistema Experto de Riesgo Urbano")

tipo_obra = st.selectbox("Tipo de obra:", ["demolicion", "excavacion", "via_publica", "construccion", "excavacion_profunda"])
horario = st.selectbox("Horario:", ["diurno", "nocturno", "mixto"])
duracion = st.slider("Duración (días):", 1, 180, 30)
zona = st.text_input("Zona:", "residencial")

if st.button("Evaluar Riesgo"):
    resultados = motor_inferencia(tipo_obra, horario, duracion, zona)
    explicaciones = generar_explicacion()

    st.subheader("🔍 Diagnóstico de Riesgo Urbano")
    for r in resultados:
        st.write(f"- {r}")

    st.subheader("💡 Explicación del Diagnóstico")
    if explicaciones:
        for exp in explicaciones:
            st.write(f"- {exp}")
    else:
        st.write("No se aplicaron reglas específicas - Impacto urbano mínimo")

    st.subheader("📈 Datos procesados")
    st.json(base_hechos)

    st.subheader("🎨 Grafo de Decisiones")
    visualizar_grafo()
