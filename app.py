import streamlit as st
import os
import time
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import pickle

# Configuración de la página
st.set_page_config(
    page_title="Asistente 4 Materias",
    page_icon="🎓",
    layout="wide"
)

# Definición de materias y profesores
PROFESORES = {
    "estadistica": {
        "nombre": "Estadística",
        "emoji": "📊",
        "profesor": "Prof. Ejemplo",
        "consejo": "Practica con ejercicios y revisa las fórmulas"
    },
    "campo_laboral": {
        "nombre": "Campo Laboral",
        "emoji": "💼",
        "profesor": "Prof. Acri",
        "consejo": "Participa activamente y prepara bien las presentaciones"
    },
    "algoritmos": {
        "nombre": "Algoritmos",
        "emoji": "💻",
        "profesor": "Prof. Tech",
        "consejo": "Codifica ejemplos y entiende la lógica"
    },
    "redes": {
        "nombre": "Redes",
        "emoji": "🌐",
        "profesor": "Prof. Net",
        "consejo": "Comprende los protocolos y sus aplicaciones"
    }
}

# Título
st.title("🎓 Asistente 4 Materias - Búsqueda Semántica")
st.markdown("**Encuentra información exacta en tus materiales de estudio** 🔍")

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuración")
    
    materia_seleccionada = st.selectbox(
        "📚 Selecciona la materia:",
        options=list(PROFESORES.keys()),
        format_func=lambda x: f"{PROFESORES[x]['emoji']} {PROFESORES[x]['nombre']}"
    )
    
    materia = PROFESORES[materia_seleccionada]
    
    st.markdown("---")
    st.markdown(f"**Profesor:** {materia['profesor']}")
    st.markdown(f"**Consejo clave:** {materia['consejo']}")
    
    st.markdown("---")
    
    cantidad_resultados = st.slider(
        "Cantidad de resultados:",
        min_value=1,
        max_value=5,
        value=3
    )
    
    if st.button("🧹 Limpiar Conversación", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# Sistema de Búsqueda Semántica Optimizado
@st.cache_resource
def inicializar_busqueda_semantica():
    """Inicializar el sistema de búsqueda semántica"""
    try:
        # Verificar carpeta conocimiento
        if not os.path.exists("conocimiento"):
            st.error("❌ No se encuentra la carpeta 'conocimiento'")
            return None, None, None
        
        # Cargar modelo de embeddings (más ligero)
        modelo = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Cargar todos los documentos
        documentos = []
        textos = []
        metadatos = []
        
        for materia_dir in os.listdir("conocimiento"):
            materia_path = os.path.join("conocimiento", materia_dir)
            if os.path.isdir(materia_path):
                for archivo in os.listdir(materia_path):
                    if archivo.endswith('.txt'):
                        archivo_path = os.path.join(materia_path, archivo)
                        try:
                            with open(archivo_path, 'r', encoding='utf-8') as f:
                                contenido = f.read().strip()
                                if contenido:
                                    # Dividir en chunks
                                    chunks = dividir_texto(contenido, 500)
                                    for i, chunk in enumerate(chunks):
                                        textos.append(chunk)
                                        metadatos.append({
                                            "materia": materia_dir,
                                            "archivo": archivo,
                                            "fuente": f"{materia_dir}/{archivo}",
                                            "chunk": i
                                        })
                        except Exception as e:
                            continue
        
        if not textos:
            st.error("❌ No se encontraron documentos con contenido")
            return None, None, None
        
        # Crear embeddings
        embeddings = modelo.encode(textos, show_progress_bar=False)
        
        # Crear índice FAISS
        dimension = embeddings.shape[1]
        index = faiss.IndexFlatL2(dimension)
        index.add(embeddings.astype('float32'))
        
        st.success(f"✅ Sistema listo: {len(textos)} fragmentos indexados")
        return modelo, index, (textos, metadatos)
        
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        return None, None, None

def dividir_texto(texto, tamano_chunk=500, overlap=100):
    """Dividir texto en chunks con overlap"""
    chunks = []
    inicio = 0
    
    while inicio < len(texto):
        fin = inicio + tamano_chunk
        chunk = texto[inicio:fin]
        
        # Intentar cortar en punto o salto de línea
        if fin < len(texto):
            ultimo_punto = chunk.rfind('.')
            ultimo_salto = chunk.rfind('\n')
            corte = max(ultimo_punto, ultimo_salto)
            if corte > tamano_chunk * 0.5:
                chunk = chunk[:corte+1]
                fin = inicio + corte + 1
        
        chunks.append(chunk.strip())
        inicio = fin - overlap
    
    return chunks

# Inicializar sistema
with st.spinner("🔄 Cargando sistema de búsqueda..."):
    modelo, index, datos = inicializar_busqueda_semantica()

# Función de búsqueda
def buscar_informacion(consulta, materia_objetivo=None, k=3):
    """Buscar información relevante"""
    if modelo is None or index is None or datos is None:
        return [], "Sistema de búsqueda no disponible"
    
    try:
        textos, metadatos = datos
        
        # Generar embedding de la consulta
        query_embedding = modelo.encode([consulta])
        
        # Buscar en FAISS
        distances, indices = index.search(query_embedding.astype('float32'), k*3)
        
        # Filtrar por materia si es necesario
        resultados = []
        for idx, dist in zip(indices[0], distances[0]):
            if materia_objetivo and metadatos[idx]["materia"] != materia_objetivo:
                continue
            resultados.append({
                "texto": textos[idx],
                "metadata": metadatos[idx],
                "score": float(dist)
            })
            if len(resultados) >= k:
                break
        
        if not resultados:
            return [], "No encontré información relevante"
        
        return resultados, None
        
    except Exception as e:
        return [], f"Error en búsqueda: {str(e)}"

def generar_respuesta(consulta, resultados, materia):
    """Generar respuesta formateada"""
    
    if not resultados:
        return "No encontré información específica para tu búsqueda.\n\n💡 Intenta reformular tu pregunta o usar otras palabras clave."
    
    respuesta = f"**🔍 Resultados para: \"{consulta}\"**\n\n"
    
    # Agrupar por archivo
    por_archivo = {}
    for r in resultados:
        fuente = r['metadata']['fuente']
        if fuente not in por_archivo:
            por_archivo[fuente] = []
        por_archivo[fuente].append(r['texto'])
    
    # Mostrar resultados
    for fuente, textos in por_archivo.items():
        respuesta += f"**📁 {fuente}**\n\n"
        for texto in textos:
            if len(texto) > 400:
                texto = texto[:400] + "..."
            respuesta += f"> {texto}\n\n"
    
    respuesta += "---\n"
    respuesta += f"**💡 Tip:** Encontré {len(resultados)} fragmentos relevantes en tus archivos."
    
    return respuesta

# Inicializar chat
if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant",
        "content": f"¡Hola! Soy tu asistente para **{PROFESORES[materia_seleccionada]['nombre']}**. 🔍\n\nHazme cualquier pregunta sobre el material de la materia."
    }]

# Mostrar historial
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input del usuario
if prompt := st.chat_input(f"Buscar en {PROFESORES[materia_seleccionada]['nombre']}..."):
    # Mensaje del usuario
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Respuesta del asistente
    with st.chat_message("assistant"):
        with st.spinner("🔍 Buscando en tus archivos..."):
            resultados, error = buscar_informacion(
                prompt,
                materia_seleccionada,
                cantidad_resultados
            )
            
            if error:
                respuesta = f"**{error}**\n\n💡 Intenta con otras palabras clave."
            else:
                respuesta = generar_respuesta(prompt, resultados, materia_seleccionada)
        
        # Mostrar con efecto
        placeholder = st.empty()
        texto_completo = ""
        
        for linea in respuesta.split('\n'):
            texto_completo += linea + '\n'
            time.sleep(0.02)
            placeholder.markdown(texto_completo + "▌")
        
        placeholder.markdown(texto_completo)
    
    st.session_state.messages.append({"role": "assistant", "content": texto_completo})

# Panel de estado
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Materia", PROFESORES[materia_seleccionada]['emoji'])

with col2:
    status = "🟢 Activo" if modelo else "🔴 Inactivo"
    st.metric("Estado", status)

with col3:
    if datos:
        st.metric("Documentos", len(datos[0]))
    else:
        st.metric("Documentos", "0")

# Ejemplos de uso
st.markdown("---")
st.info(f"""
**💡 Ejemplos de búsqueda para {PROFESORES[materia_seleccionada]['nombre']}:**

- "¿Cuál es la fórmula de...?"
- "Ejercicio 3 de la guía"
- "Fecha del examen"
- "Requisitos del trabajo práctico"
- "Explicación de [concepto]"
""")

st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: green; font-weight: bold;'>"
    "🎓 ASISTENTE 4 MATERIAS - BÚSQUEDA SEMÁNTICA OPTIMIZADA"
    "</div>",
    unsafe_allow_html=True
)
