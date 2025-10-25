import streamlit as st
import time
import os

# Configuración
st.set_page_config(
    page_title="Asistente 4 Materias + Búsqueda Inteligente",
    page_icon="🎓",
    layout="wide"
)

# Título
st.title("🎓 Asistente 4 Materias + Búsqueda Inteligente")
st.markdown("### Ahora puedo buscar en todo tu material automáticamente")

# Configuración de materias y profesores
PROFESORES = {
    "estadistica": {
        "nombre": "Estadística",
        "emoji": "📊",
        "profesor": "Prof. Ferrarre",
        "consejo": "Practica TODOS los ejercicios y enfócate en entender el proceso paso a paso",
        "color": "blue"
    },
    "desarrollo_ia": {
        "nombre": "Desarrollo de IA", 
        "emoji": "🤖",
        "profesor": "Especialista IA",
        "consejo": "Entiende los fundamentos antes de usar frameworks complejos",
        "color": "green"
    },
    "campo_laboral": {
        "nombre": "Campo Laboral",
        "emoji": "💼",
        "profesor": "Prof. Acri",
        "consejo": "Sé impecable en presentaciones y prepara exhaustivamente cada entrega",
        "color": "orange"
    },
    "comunicacion": {
        "nombre": "Comunicación",
        "emoji": "🎯", 
        "profesor": "Especialista Comunicación",
        "consejo": "Estructura tus mensajes y adapta tu lenguaje al público",
        "color": "purple"
    }
}

# Sidebar
with st.sidebar:
    st.header("📚 Configuración")
    
    materia_seleccionada = st.selectbox(
        "Selecciona la materia:",
        list(PROFESORES.keys()),
        format_func=lambda x: f"{PROFESORES[x]['emoji']} {PROFESORES[x]['nombre']}"
    )
    
    materia = PROFESORES[materia_seleccionada]
    
    # Mostrar información del profesor
    st.markdown(f"### {materia['emoji']} {materia['profesor']}")
    st.markdown(f"**Estilo:** {materia['consejo'].split('.')[0]}.")
    
    st.markdown("---")
    st.markdown("**💡 Ejemplos de búsqueda:**")
    
    if materia_seleccionada == "estadistica":
        st.markdown("- 'Ejercicios de media y mediana'")
        st.markdown("- 'Qué temas van en el parcial'")
        st.markdown("- 'Consejos del profesor Ferrarre'")
    elif materia_seleccionada == "campo_laboral":
        st.markdown("- 'Preparación para entrevistas'")
        st.markdown("- 'Consejos de la profesora Acri'")
        st.markdown("- 'Cómo hacer un buen CV'")
    elif materia_seleccionada == "desarrollo_ia":
        st.markdown("- 'Proyectos prácticos de IA'")
        st.markdown("- 'Algoritmos de machine learning'")
        st.markdown("- 'Frameworks recomendados'")
    else:
        st.markdown("- 'Técnicas de presentación'")
        st.markdown("- 'Comunicación efectiva'")
        st.markdown("- 'Estructura de mensajes'")
    
    st.markdown("---")
    
    if st.button("🧹 Limpiar Conversación", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# Sistema de Búsqueda Semántica
@st.cache_resource
def inicializar_busqueda_semantica():
    """Inicializar el sistema de búsqueda semántica"""
    try:
        from langchain_community.embeddings import HuggingFaceEmbeddings
        from langchain.vectorstores import FAISS
        from langchain.text_splitter import RecursiveCharacterTextSplitter
        from langchain.schema import Document
        
        # Verificar que existe la carpeta conocimiento
        if not os.path.exists("conocimiento"):
            st.error("❌ No se encuentra la carpeta 'conocimiento'")
            return None
        
        # Cargar embeddings
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        
        # Cargar todos los documentos
        documentos = []
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
                                if contenido:  # Solo agregar si tiene contenido
                                    documentos.append(
                                        Document(
                                            page_content=contenido,
                                            metadata={
                                                "materia": materia_dir,
                                                "archivo": archivo,
                                                "fuente": f"{materia_dir}/{archivo}"
                                            }
                                        )
                                    )
                                    archivos_cargados += 1
                        except Exception as e:
                            st.warning(f"⚠️ Error leyendo {archivo_path}: {str(e)}")
                            continue
        
        if not documentos:
            st.error("❌ No se encontraron documentos con contenido en la carpeta conocimiento")
            return None
        
        # Dividir documentos en chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        documentos_divididos = text_splitter.split_documents(documentos)
        
        # Crear base de datos vectorial
        vectorstore = FAISS.from_documents(documentos_divididos, embeddings)
        
        st.success(f"✅ Sistema de búsqueda inicializado: {archivos_cargados} archivos indexados")
        return vectorstore
        
    except Exception as e:
        st.error(f"❌ Error inicializando búsqueda semántica: {str(e)}")
        return None

# Inicializar búsqueda
with st.spinner("🔄 Inicializando sistema de búsqueda inteligente..."):
    buscador = inicializar_busqueda_semantica()

# Función de búsqueda semántica mejorada
def buscar_informacion_relevante(consulta, materia_objetivo=None, cantidad_resultados=3):
    """Buscar información relevante en todo el material"""
    if buscador is None:
        return [], "Sistema de búsqueda no disponible"
    
    try:
        # Buscar documentos similares
        documentos_encontrados = buscador.similarity_search(consulta, k=cantidad_resultados)
        
        # Si se especifica una materia, priorizar documentos de esa materia
        if materia_objetivo:
            docs_filtrados = [doc for doc in documentos_encontrados 
                            if doc.metadata.get("materia") == materia_objetivo]
            if docs_filtrados:
                documentos_encontrados = docs_filtrados
        
        if not documentos_encontrados:
            return [], "No encontré información específica para tu búsqueda en el material disponible."
        
        return documentos_encontrados, None
        
    except Exception as e:
        return [], f"Error en la búsqueda: {str(e)}"

# Función para formatear respuesta
def formatear_respuesta_busqueda(consulta, documentos_encontrados, materia):
    """Formatear una respuesta clara a partir de los documentos encontrados"""
    
    if not documentos_encontrados:
        return "No encontré información específica para tu búsqueda."
    
    # Construir respuesta
    respuesta = f"**🔍 Resultados para: \"{consulta}\"**\n\n"
    
    # Agrupar por archivo
    archivos_vistos = set()
    contenido_por_archivo = {}
    
    for doc in documentos_encontrados:
        archivo = doc.metadata.get("fuente", "Desconocido")
        if archivo not in contenido_por_archivo:
            contenido_por_archivo[archivo] = []
        contenido_por_archivo[archivo].append(doc.page_content)
    
    # Mostrar contenido de cada archivo
    for archivo, contenidos in contenido_por_archivo.items():
        respuesta += f"**📁 {archivo}**\n\n"
        for i, contenido in enumerate(contenidos, 1):
            # Limitar longitud del contenido mostrado
            if len(contenido) > 500:
                contenido = contenido[:500] + "..."
            respuesta += f"{contenido}\n\n"
    
    # Agregar consejo del profesor
    respuesta += f"**💡 {PROFESORES[materia]['profesor']} recomienda:**\n"
    respuesta += f"{PROFESORES[materia]['consejo']}\n\n"
    
    respuesta += "---\n"
    respuesta += "*💡 Tip: Sé específico en tus búsquedas para obtener resultados más precisos*"
    
    return respuesta

# Inicializar chat
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": f"¡Hola! Soy tu asistente para {PROFESORES[materia_seleccionada]['nombre']}. Ahora puedo buscar información específica en todo tu material. ¿Qué necesitas saber? 🎓"}
    ]

# Mostrar historial de chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input del usuario
if prompt := st.chat_input(f"Buscar en {PROFESORES[materia_seleccionada]['nombre']}..."):
    # Agregar mensaje del usuario
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Procesar búsqueda
    with st.chat_message("assistant"):
        with st.spinner(f"🔍 Buscando en {PROFESORES[materia_seleccionada]['nombre']}..."):
            
            # Realizar búsqueda semántica
            documentos_encontrados, error = buscar_informacion_relevante(
                prompt, 
                materia_seleccionada,
                cantidad_resultados=3
            )
            
            if error:
                respuesta = f"**⚠️ {error}**\n\n"
                respuesta += "**💡 Sugerencias:**\n"
                respuesta += "- Revisa que los archivos en la carpeta 'conocimiento' tengan contenido\n"
                respuesta += "- Intenta con otras palabras clave\n"
                respuesta += "- Sé más específico en tu búsqueda"
            else:
                respuesta = formatear_respuesta_busqueda(prompt, documentos_encontrados, materia_seleccionada)
            
            # Efecto de escritura
            placeholder = st.empty()
            respuesta_completa = ""
            
            for chunk in respuesta.split('\n'):
                respuesta_completa += chunk + '\n'
                time.sleep(0.05)
                placeholder.markdown(respuesta_completa + "▌")
            
            placeholder.markdown(respuesta_completa)
            
            # Mostrar estadísticas de búsqueda
            if documentos_encontrados:
                with st.expander("📊 Detalles de la búsqueda", expanded=False):
                    st.write(f"**Documentos encontrados:** {len(documentos_encontrados)}")
                    archivos_unicos = set(doc.metadata.get("fuente") for doc in documentos_encontrados)
                    st.write(f"**Archivos consultados:** {', '.join(archivos_unicos)}")
    
    st.session_state.messages.append({"role": "assistant", "content": respuesta_completa})

# Panel de información y estado
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="Sistema de Búsqueda", 
        value="🟢 ACTIVO" if buscador else "🔴 INACTIVO"
    )

with col2:
    if buscador:
        st.metric(
            label="Documentos Indexados", 
            value=f"{buscador.index.ntotal if hasattr(buscador, 'index') else 'N/A'}"
        )
    else:
        st.metric(label="Documentos Indexados", value="0")

with col3:
    st.metric(
        label="Materia Actual", 
        value=PROFESORES[materia_seleccionada]['emoji']
    )

# Información para el usuario
st.markdown("---")
st.success("""
**🎉 ¡Búsqueda Semántica Implementada!**

**✅ Lo que puedes hacer ahora:**
- 🔍 **Buscar en TODO tu material** automáticamente
- 📚 **Encontrar información específica** por materia
- 🎯 **Resultados relevantes** basados en similitud semántica
- 📁 **Ver las fuentes** de donde se obtuvo la información

**💡 Consejos para mejores búsquedas:**
- Usa **palabras clave específicas** ("parcial estadística", "ejercicios práctica")
- **Sé descriptivo** ("consejos profesor Ferrarre ejercicios")
- **Pregunta por temas concretos** de cada materia

**🚀 Próximos pasos:**
1. ✅ Búsqueda semántica implementada
2. 🤖 IA generativa (próxima fase)
3. 📈 Mejoras basadas en tu feedback
""")

st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: green; font-weight: bold;'>"
    "🔍 BÚSQUEDA SEMÁNTICA ACTIVA - COMPARTE CON TUS COMPAÑEROS 🎓"
    "</div>",
    unsafe_allow_html=True
)
