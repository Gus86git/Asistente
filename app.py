import streamlit as st
import time
import os

# Configuración
st.set_page_config(
    page_title="Asistente 4 Materias - Versión Estable",
    page_icon="🎓",
    layout="wide"
)

# Título
st.title("🎓 Asistente 4 Materias - Versión Estable")
st.markdown("### Búsqueda Semántica + IA Generativa - ¡Ahora funcionando!")

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
    st.header("⚙️ Configuración")
    
    # Selector de materia
    materia_seleccionada = st.selectbox(
        "📚 Selecciona la materia:",
        list(PROFESORES.keys()),
        format_func=lambda x: f"{PROFESORES[x]['emoji']} {PROFESORES[x]['nombre']}"
    )
    
    materia = PROFESORES[materia_seleccionada]
    
    # Selector de MODO
    st.markdown("---")
    st.header("🎛️ Modo de Estudio")
    
    modo = st.radio(
        "Elige cómo quieres estudiar:",
        ["busqueda", "ia_generativa"],
        format_func=lambda x: {
            "busqueda": "🔍 Búsqueda Semántica",
            "ia_generativa": "🤖 IA Generativa"
        }[x]
    )
    
    # Explicación de cada modo
    with st.expander("📖 ¿Qué significa cada modo?", expanded=True):
        if modo == "busqueda":
            st.success("**🔍 BÚSQUEDA SEMÁNTICA**")
            st.markdown("""
            **✅ Ventajas:**
            - Encuentra información EXACTA de tus archivos
            - Muestra las fuentes (sabes de dónde viene)
            - Muy rápido y confiable
            - Ideal para buscar información específica
            
            **⚠️ Limitaciones:**
            - Solo recupera información existente
            - No explica ni resume automáticamente
            """)
        else:
            st.info("**🤖 IA GENERATIVA**")
            st.markdown("""
            **✅ Ventajas:**
            - Explica conceptos de manera natural
            - Responde preguntas complejas
            - Sintetiza información de múltiples fuentes
            - Suena como un tutor real
            
            **⚠️ Limitaciones:**
            - Puede ocasionalmente inventar información
            - Un poco más lento
            - Requiere más recursos
            """)
    
    # Mostrar información del profesor
    st.markdown("---")
    st.markdown(f"### {materia['emoji']} {materia['profesor']}")
    st.markdown(f"**Consejo clave:** {materia['consejo']}")
    
    st.markdown("---")
    
    if st.button("🧹 Limpiar Conversación", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# Verificación de dependencias al inicio
st.markdown("---")
st.subheader("🔍 Verificación del Sistema")

# Verificar cada dependencia CRÍTICA
try:
    import streamlit
    st.success("✅ Streamlit - FUNCIONANDO")
except ImportError as e:
    st.error(f"❌ Streamlit: {e}")

try:
    import transformers
    st.success("✅ Transformers - FUNCIONANDO")
except ImportError as e:
    st.error(f"❌ Transformers: {e}")

try:
    import torch
    st.success("✅ PyTorch - FUNCIONANDO")
except ImportError as e:
    st.error(f"❌ PyTorch: {e}")

try:
    # IMPORTACIÓN CORREGIDA - Sin langchain_community
    from langchain.embeddings import HuggingFaceEmbeddings
    st.success("✅ LangChain - FUNCIONANDO")
except ImportError as e:
    st.error(f"❌ LangChain: {e}")

try:
    import sentence_transformers
    st.success("✅ Sentence Transformers - FUNCIONANDO")
except ImportError as e:
    st.error(f"❌ Sentence Transformers: {e}")

# Sistema de Búsqueda Semántica (CON IMPORTS CORREGIDOS)
@st.cache_resource
def inicializar_busqueda_semantica():
    """Inicializar el sistema de búsqueda semántica con imports compatibles"""
    try:
        # IMPORTACIÓN CORREGIDA - Usar langchain directo, no community
        from langchain.embeddings import HuggingFaceEmbeddings
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
                                if contenido:
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
                            continue
        
        if not documentos:
            st.error("❌ No se encontraron documentos con contenido")
            return None
        
        # Dividir documentos en chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        documentos_divididos = text_splitter.split_documents(documentos)
        
        # Crear base de datos vectorial
        vectorstore = FAISS.from_documents(documentos_divididos, embeddings)
        
        st.success(f"✅ Búsqueda semántica lista: {archivos_cargados} archivos")
        return vectorstore
        
    except Exception as e:
        st.error(f"❌ Error en búsqueda semántica: {str(e)}")
        return None

# Sistema de IA Generativa
@st.cache_resource
def inicializar_ia_generativa():
    """Inicializar el modelo de IA generativa"""
    try:
        from transformers import pipeline
        import torch
        
        # Usar un modelo más ligero y compatible
        model = pipeline(
            "text-generation",
            model="microsoft/DialoGPT-medium",
            torch_dtype=torch.float16,
            max_length=1024
        )
        st.success("✅ IA Generativa lista")
        return model
    except Exception as e:
        st.error(f"❌ Error en IA generativa: {str(e)}")
        return None

# Inicializar sistemas
with st.spinner("🔄 Inicializando sistemas..."):
    buscador = inicializar_busqueda_semantica()
    modelo_ia = inicializar_ia_generativa()

# Función de búsqueda semántica
def buscar_informacion_relevante(consulta, materia_objetivo=None, cantidad_resultados=3):
    """Buscar información relevante en todo el material"""
    if buscador is None:
        return [], "Sistema de búsqueda no disponible"
    
    try:
        documentos_encontrados = buscador.similarity_search(consulta, k=cantidad_resultados)
        
        if materia_objetivo:
            docs_filtrados = [doc for doc in documentos_encontrados 
                            if doc.metadata.get("materia") == materia_objetivo]
            if docs_filtrados:
                documentos_encontrados = docs_filtrados
        
        if not documentos_encontrados:
            return [], "No encontré información específica para tu búsqueda."
        
        return documentos_encontrados, None
        
    except Exception as e:
        return [], f"Error en la búsqueda: {str(e)}"

# Función para respuesta de BÚSQUEDA SEMÁNTICA
def generar_respuesta_busqueda(consulta, documentos_encontrados, materia):
    """Generar respuesta para modo búsqueda semántica"""
    
    if not documentos_encontrados:
        return "No encontré información específica para tu búsqueda."
    
    respuesta = f"**🔍 Búsqueda Semántica - Resultados para: \"{consulta}\"**\n\n"
    
    # Agrupar por archivo
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
            if len(contenido) > 500:
                contenido = contenido[:500] + "..."
            respuesta += f"{contenido}\n\n"
    
    respuesta += "---\n"
    respuesta += "**💡 Modo Búsqueda Semántica:** Estás viendo información EXACTA de tus archivos."
    
    return respuesta

# Función para respuesta de IA GENERATIVA
def generar_respuesta_ia(consulta, documentos_encontrados, materia, modelo):
    """Generar respuesta usando IA generativa"""
    
    if modelo is None:
        return "El modo IA Generativa no está disponible en este momento."
    
    if not documentos_encontrados:
        contexto = f"Información general sobre {PROFESORES[materia]['nombre']}"
    else:
        contexto = "\n\n".join([doc.page_content for doc in documentos_encontrados])
    
    try:
        prompt = f"""
        Eres un tutor educativo especializado en {PROFESORES[materia]['nombre']}.

        INFORMACIÓN DE CONTEXTO:
        {contexto}

        PREGUNTA DEL ESTUDIANTE:
        {consulta}

        Proporciona una respuesta educativa, clara y útil.
        Responde en español de manera natural.

        RESPUESTA:
        """
        
        respuesta = modelo(
            prompt,
            max_new_tokens=400,
            temperature=0.7,
            do_sample=True,
            pad_token_id=modelo.tokenizer.eos_token_id
        )
        
        generated_text = respuesta[0]['generated_text']
        
        if "RESPUESTA:" in generated_text:
            respuesta_texto = generated_text.split("RESPUESTA:")[-1].strip()
        else:
            respuesta_texto = generated_text
        
        # Agregar información sobre las fuentes
        if documentos_encontrados:
            archivos = set(doc.metadata.get("fuente") for doc in documentos_encontrados)
            respuesta_texto += f"\n\n---\n**📚 Fuentes consultadas:** {', '.join(archivos)}"
        
        respuesta_texto += "\n\n**🤖 Modo IA Generativa:** Respuesta generada por IA."
        
        return respuesta_texto
        
    except Exception as e:
        return f"Error generando respuesta: {str(e)}"

# Inicializar chat
if "messages" not in st.session_state:
    mensaje_inicial = f"¡Hola! Soy tu asistente para {PROFESORES[materia_seleccionada]['nombre']}. "
    
    if modo == "busqueda":
        mensaje_inicial += "Estoy en **modo Búsqueda Semántica** - encontraré información exacta de tus archivos. 🔍"
    else:
        mensaje_inicial += "Estoy en **modo IA Generativa** - explicaré conceptos de manera natural. 🤖"
    
    st.session_state.messages = [
        {"role": "assistant", "content": mensaje_inicial}
    ]

# Mostrar historial de chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input del usuario
placeholder_text = {
    "busqueda": f"Buscar en {PROFESORES[materia_seleccionada]['nombre']}...",
    "ia_generativa": f"Preguntar sobre {PROFESORES[materia_seleccionada]['nombre']}..."
}

if prompt := st.chat_input(placeholder_text[modo]):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        if modo == "busqueda":
            with st.spinner("🔍 Buscando en tus archivos..."):
                documentos_encontrados, error = buscar_informacion_relevante(
                    prompt, 
                    materia_seleccionada,
                    cantidad_resultados=3
                )
                
                if error:
                    respuesta = f"**{error}**"
                else:
                    respuesta = generar_respuesta_busqueda(prompt, documentos_encontrados, materia_seleccionada)
        
        else:
            with st.spinner("🤖 Analizando y generando respuesta..."):
                documentos_encontrados, _ = buscar_informacion_relevante(
                    prompt, 
                    materia_seleccionada,
                    cantidad_resultados=3
                )
                respuesta = generar_respuesta_ia(prompt, documentos_encontrados, materia_seleccionada, modelo_ia)
        
        placeholder = st.empty()
        respuesta_completa = ""
        
        for chunk in respuesta.split('\n'):
            respuesta_completa += chunk + '\n'
            time.sleep(0.03)
            placeholder.markdown(respuesta_completa + "▌")
        
        placeholder.markdown(respuesta_completa)
    
    st.session_state.messages.append({"role": "assistant", "content": respuesta_completa})

# Panel de información
st.markdown("---")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Modo Actual", 
        value="🔍 Búsqueda" if modo == "busqueda" else "🤖 IA"
    )

with col2:
    st.metric(
        label="Materia", 
        value=PROFESORES[materia_seleccionada]['emoji']
    )

with col3:
    status_busqueda = "🟢" if buscador else "🔴"
    st.metric("Búsqueda", status_busqueda)

with col4:
    status_ia = "🟢" if modelo_ia else "🔴"
    st.metric("IA Generativa", status_ia)

# Estado del sistema
st.markdown("---")
if buscador and modelo_ia:
    st.success("**🎉 ¡Sistema completamente operativo! Ambos modos están funcionando.**")
elif buscador:
    st.warning("**⚠️ Sistema parcialmente operativo: Búsqueda Semántica funciona, IA Generativa no está disponible.**")
else:
    st.error("**❌ Sistema no operativo: Revisa los errores de instalación arriba.**")

st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: green; font-weight: bold;'>"
    "🎓 ASISTENTE 4 MATERIAS - VERSIÓN ESTABLE"
    "</div>",
    unsafe_allow_html=True
)
