import streamlit as st
import os
import time
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
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
st.title("🎓 Asistente 4 Materias - Búsqueda Inteligente")
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

# Sistema de Búsqueda con TF-IDF
@st.cache_resource
def inicializar_sistema_busqueda():
    """Inicializar el sistema de búsqueda con TF-IDF"""
    try:
        # Verificar carpeta conocimiento
        if not os.path.exists("conocimiento"):
            st.error("❌ No se encuentra la carpeta 'conocimiento'")
            return None, None, None
        
        # Cargar todos los documentos
        textos = []
        metadatos = []
        archivos_cargados = 0
        
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
                                    chunks = dividir_texto(contenido, 600, 100)
                                    for i, chunk in enumerate(chunks):
                                        textos.append(chunk)
                                        metadatos.append({
                                            "materia": materia_dir,
                                            "archivo": archivo,
                                            "fuente": f"{materia_dir}/{archivo}",
                                            "chunk": i
                                        })
                                    archivos_cargados += 1
                        except Exception as e:
                            continue
        
        if not textos:
            st.error("❌ No se encontraron documentos con contenido")
            return None, None, None
        
        # Crear vectorizador TF-IDF
        vectorizer = TfidfVectorizer(
            max_features=5000,
            ngram_range=(1, 2),
            stop_words=None,  # Mantener todas las palabras en español
            min_df=1,
            max_df=0.95
        )
        
        # Generar vectores TF-IDF
        matriz_tfidf = vectorizer.fit_transform(textos)
        
        st.success(f"✅ Sistema listo: {archivos_cargados} archivos, {len(textos)} fragmentos indexados")
        return vectorizer, matriz_tfidf, (textos, metadatos)
        
    except Exception as e:
        st.error(f"❌ Error al inicializar: {str(e)}")
        return None, None, None

def dividir_texto(texto, tamano_chunk=600, overlap=100):
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
        
        if chunk.strip():
            chunks.append(chunk.strip())
        
        inicio = fin - overlap
        
        if inicio >= len(texto):
            break
    
    return chunks

# Inicializar sistema
with st.spinner("🔄 Cargando sistema de búsqueda..."):
    vectorizer, matriz_tfidf, datos = inicializar_sistema_busqueda()

# Función de búsqueda
def buscar_informacion(consulta, materia_objetivo=None, k=3):
    """Buscar información relevante usando TF-IDF"""
    if vectorizer is None or matriz_tfidf is None or datos is None:
        return [], "Sistema de búsqueda no disponible"
    
    try:
        textos, metadatos = datos
        
        # Vectorizar la consulta
        query_vector = vectorizer.transform([consulta])
        
        # Calcular similitud coseno
        similitudes = cosine_similarity(query_vector, matriz_tfidf)[0]
        
        # Obtener índices ordenados por similitud
        indices_ordenados = np.argsort(similitudes)[::-1]
        
        # Filtrar y obtener los mejores resultados
        resultados = []
        for idx in indices_ordenados:
            if similitudes[idx] < 0.05:  # Umbral mínimo de similitud
                continue
            
            if materia_objetivo and metadatos[idx]["materia"] != materia_objetivo:
                continue
            
            resultados.append({
                "texto": textos[idx],
                "metadata": metadatos[idx],
                "score": float(similitudes[idx])
            })
            
            if len(resultados) >= k:
                break
        
        if not resultados:
            return [], "No encontré información relevante para tu búsqueda"
        
        return resultados, None
        
    except Exception as e:
        return [], f"Error en búsqueda: {str(e)}"

def generar_respuesta(consulta, resultados, materia):
    """Generar respuesta formateada"""
    
    if not resultados:
        return "No encontré información específica para tu búsqueda.\n\n💡 **Sugerencias:**\n- Intenta usar palabras clave diferentes\n- Reformula tu pregunta\n- Verifica que la información esté en los archivos de la materia"
    
    respuesta = f"**🔍 Resultados para: \"{consulta}\"**\n\n"
    
    # Agrupar por archivo
    por_archivo = {}
    for r in resultados:
        fuente = r['metadata']['fuente']
        if fuente not in por_archivo:
            por_archivo[fuente] = []
        por_archivo[fuente].append({
            'texto': r['texto'],
            'score': r['score']
        })
    
    # Mostrar resultados
    for fuente, items in por_archivo.items():
        respuesta += f"**📁 {fuente}**\n\n"
        for item in items:
            texto = item['texto']
            score = item['score']
            
            # Truncar si es muy largo
            if len(texto) > 500:
                texto = texto[:500] + "..."
            
            # Mostrar con indicador de relevancia
            relevancia = "🟢" if score > 0.3 else "🟡" if score > 0.15 else "🟠"
            respuesta += f"{relevancia} {texto}\n\n"
    
    respuesta += "---\n"
    respuesta += f"**💡 Tip:** Encontré **{len(resultados)}** fragmentos relevantes.\n"
    
    # Mostrar nivel de confianza
    score_promedio = sum(r['score'] for r in resultados) / len(resultados)
    if score_promedio > 0.3:
        respuesta += "✅ Alta confianza en los resultados"
    elif score_promedio > 0.15:
        respuesta += "⚠️ Confianza media - verifica la información"
    else:
        respuesta += "⚠️ Baja confianza - los resultados pueden ser aproximados"
    
    return respuesta

# Inicializar chat
if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant",
        "content": f"¡Hola! 👋 Soy tu asistente para **{PROFESORES[materia_seleccionada]['nombre']}** {PROFESORES[materia_seleccionada]['emoji']}\n\nHazme cualquier pregunta sobre el material de la materia y buscaré en tus archivos."
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
                respuesta = f"**❌ {error}**\n\n💡 Intenta con otras palabras clave o verifica que los archivos de la materia contengan información sobre este tema."
            else:
                respuesta = generar_respuesta(prompt, resultados, materia_seleccionada)
        
        # Mostrar con efecto de escritura
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
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("📚 Materia", PROFESORES[materia_seleccionada]['nombre'][:8] + "...")

with col2:
    status = "🟢" if vectorizer else "🔴"
    st.metric("Estado", status)

with col3:
    if datos:
        st.metric("📄 Fragmentos", len(datos[0]))
    else:
        st.metric("📄 Fragmentos", "0")

with col4:
    if datos and matriz_tfidf is not None:
        archivos = len(set(m['fuente'] for m in datos[1]))
        st.metric("📁 Archivos", archivos)
    else:
        st.metric("📁 Archivos", "0")

# Ejemplos de uso
st.markdown("---")

col_ej1, col_ej2 = st.columns(2)

with col_ej1:
    st.info(f"""
**💡 Ejemplos de búsqueda:**

- "¿Cuál es la fórmula de...?"
- "Ejercicio 3 de la guía"
- "Fecha del examen parcial"
- "Explicación de [concepto]"
""")

with col_ej2:
    st.success(f"""
**✨ Tips para mejores resultados:**

- Usa palabras clave específicas
- Menciona el tema o concepto exacto
- Si no encuentras algo, reformula
- Verifica el nombre de los archivos
""")

st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: green; font-weight: bold;'>"
    "🎓 ASISTENTE 4 MATERIAS - BÚSQUEDA INTELIGENTE OPTIMIZADA PARA STREAMLIT CLOUD"
    "</div>",
    unsafe_allow_html=True
)
