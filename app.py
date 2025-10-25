import streamlit as st
import torch
from transformers import pipeline
from langchain.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
import os
import time

# =========================================
# CONFIGURACIÓN DE PROFESORES Y MATERIAS
# =========================================
PROFESORES = {
    "estadistica": {
        "nombre": "Profesor Ferrarre",
        "emoji": "📊",
        "estilo": "Práctico y numérico",
        "consejos": [
            "Practica TODOS los ejercicios de las guías",
            "Enfócate en entender el proceso, no solo el resultado", 
            "Los parciales suelen ser similares a los ejercicios de clase",
            "No te saltes pasos en los desarrollos",
            "Revisa bien las unidades de medida y decimales"
        ],
        "tono": "directo, técnico, motivador"
    },
    "desarrollo_ia": {
        "nombre": "Especialista IA", 
        "emoji": "🤖",
        "estilo": "Técnico y práctico",
        "consejos": [
            "Empieza con los fundamentos antes de frameworks",
            "Practica con proyectos pequeños primero", 
            "Documenta bien tu código",
            "Revisa los algoritmos base antes de implementaciones complejas",
            "Testea cada componente por separado"
        ],
        "tono": "preciso, moderno, práctico"
    },
    "campo_laboral": {
        "nombre": "Profesora Acri",
        "emoji": "💼", 
        "estilo": "Exigente y profesional", 
        "consejos": [
            "Sé impecable en presentaciones y entregas",
            "Investiga la empresa antes de entrevistas",
            "Prepara preguntas inteligentes para los reclutadores",
            "Tu CV debe ser claro y sin errores",
            "Practica tu pitch personal múltiples veces"
        ],
        "tono": "profesional, directo, orientado a resultados"
    },
    "comunicacion": {
        "nombre": "Especialista Comunicación",
        "emoji": "🎯",
        "estilo": "Claro y estructurado", 
        "consejos": [
            "Estructura tu mensaje antes de hablar",
            "Practica la escucha activa",
            "Adapta tu lenguaje al público", 
            "Usa ejemplos concretos en tus explicaciones",
            "Maneja bien los tiempos en presentaciones"
        ],
        "tono": "amable, organizado, ejemplificador"
    }
}

# =========================================
# CONFIGURACIÓN STREAMLIT
# =========================================
st.set_page_config(
    page_title="Asistente 4 Materias - Streamlit Cloud",
    page_icon="🎓", 
    layout="wide"
)

# =========================================
# FUNCIONES PRINCIPALES
# =========================================
@st.cache_resource
def load_chat_model():
    """Cargar modelo de chat optimizado para Streamlit Cloud"""
    try:
        model = pipeline(
            "text-generation", 
            model="microsoft/DialoGPT-medium",
            torch_dtype=torch.float16,
            device_map="auto",
            max_length=1024
        )
        return model
    except Exception as e:
        st.error(f"Error cargando modelo: {e}")
        return None

@st.cache_resource  
def load_knowledge_base():
    """Cargar base de conocimiento desde archivos locales"""
    try:
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        
        # Cargar documentos de la carpeta conocimiento
        documents = []
        conocimiento_path = "conocimiento"
        
        if not os.path.exists(conocimiento_path):
            st.error("❌ No se encuentra la carpeta 'conocimiento'")
            return None
            
        for materia in os.listdir(conocimiento_path):
            materia_path = os.path.join(conocimiento_path, materia)
            if os.path.isdir(materia_path):
                for archivo in os.listdir(materia_path):
                    if archivo.endswith('.txt'):
                        archivo_path = os.path.join(materia_path, archivo)
                        try:
                            with open(archivo_path, 'r', encoding='utf-8') as f:
                                contenido = f.read()
                                documents.append(f"MATERIA: {materia.upper()}\nCONTENIDO:\n{contenido}")
                        except Exception as e:
                            st.warning(f"⚠️ Error leyendo {archivo_path}: {e}")
        
        if not documents:
            st.error("❌ No se encontraron archivos en la carpeta conocimiento")
            return None
            
        # Procesar documentos
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        texts = text_splitter.create_documents(documents)
        
        # Crear vectorstore
        vectorstore = FAISS.from_documents(texts, embeddings)
        st.success(f"✅ Base de conocimiento cargada: {len(documents)} documentos")
        return vectorstore
        
    except Exception as e:
        st.error(f"Error cargando conocimiento: {e}")
        return None

def get_professor_guidance(materia):
    """Obtener guía específica del profesor"""
    profesor = PROFESORES[materia]
    
    guidance = f"""
    Eres el {profesor['nombre']} {profesor['emoji']}
    Estilo: {profesor['estilo']}
    Tono: {profesor['tono']}
    
    Consejos clave:
    {chr(10).join(['• ' + c for c in profesor['consejos']])}
    """
    return guidance

def generate_response(pregunta, contexto, materia, modelo):
    """Generar respuesta con personalidad del profesor"""
    try:
        profesor_guidance = get_professor_guidance(materia)
        
        system_prompt = f"""
        Eres un tutor educativo especializado.
        {profesor_guidance}
        
        Responde como este profesor, manteniendo su estilo.
        Sé práctico y enfocado en ayudar a aprobar.
        Usa el contexto para respuestas precisas.
        Responde SOLO en español.
        """

        full_prompt = f"""
        {system_prompt}

        CONTEXTO:
        {contexto}

        PREGUNTA: {pregunta}

        RESPUESTA:
        """
        
        response = modelo(
            full_prompt,
            max_new_tokens=500,
            temperature=0.7,
            do_sample=True,
            pad_token_id=modelo.tokenizer.eos_token_id
        )
        
        generated_text = response[0]['generated_text']
        
        if "RESPUESTA:" in generated_text:
            return generated_text.split("RESPUESTA:")[-1].strip()
        return generated_text
        
    except Exception as e:
        return f"Error: {str(e)}"

# =========================================
# INTERFAZ PRINCIPAL
# =========================================
st.title("🎓 Asistente 4 Materias - Streamlit Cloud")
st.markdown("### Tu compañero académico para Estadística, IA, Campo Laboral y Comunicación")

# Sidebar
with st.sidebar:
    st.header("📚 Materias")
    
    materia = st.selectbox(
        "Selecciona:",
        ["estadistica", "desarrollo_ia", "campo_laboral", "comunicacion"],
        format_func=lambda x: {
            "estadistica": "📊 Estadística (Ferrare)",
            "desarrollo_ia": "🤖 Desarrollo IA", 
            "campo_laboral": "💼 Campo Laboral (Acri)",
            "comunicacion": "🎯 Comunicación"
        }[x]
    )
    
    profe = PROFESORES[materia]
    st.subheader(f"{profe['emoji']} {profe['nombre']}")
    st.write(f"**Estilo:** {profe['estilo']}")
    
    st.markdown("**Consejos:**")
    for c in profe['consejos'][:2]:
        st.write(f"• {c}")
    
    st.markdown("---")
    
    if st.button("🧹 Limpiar Chat"):
        st.session_state.messages = []
        st.rerun()

# Cargar recursos
with st.spinner("🔄 Cargando asistente..."):
    chat_model = load_chat_model()
    knowledge_base = load_knowledge_base()

# Inicializar chat
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": f"¡Hola! Soy tu asistente para {PROFESORES[materia]['nombre']}. ¿En qué puedo ayudarte? 🎓"}
    ]

# Mostrar chat
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Input usuario
if prompt := st.chat_input(f"Pregunta sobre {materia.replace('_', ' ')}..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Buscar contexto
    contexto = f"Información sobre {materia}"
    if knowledge_base:
        try:
            docs = knowledge_base.similarity_search(prompt, k=2)
            contexto = "\n".join([d.page_content for d in docs])
        except Exception as e:
            st.error(f"Búsqueda error: {e}")
    
    # Generar respuesta
    with st.chat_message("assistant"):
        with st.spinner(f"💭 {PROFESORES[materia]['nombre']} piensa..."):
            if chat_model:
                respuesta = generate_response(prompt, contexto, materia, chat_model)
            else:
                respuesta = "Modelo no disponible."
            
            # Efecto escritura
            placeholder = st.empty()
            full_resp = ""
            
            for chunk in respuesta.split():
                full_resp += chunk + " "
                time.sleep(0.02)
                placeholder.markdown(full_resp + "▌")
            
            placeholder.markdown(full_resp)
    
    st.session_state.messages.append({"role": "assistant", "content": full_resp})

# Footer
st.markdown("---")
st.markdown("🎓 **Asistente 4 Materias** • Desplegado en Streamlit Community Cloud")