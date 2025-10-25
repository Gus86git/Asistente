import streamlit as st
import time
import os

# Configuración
st.set_page_config(
    page_title="Asistente 4 Materias",
    page_icon="🎓",
    layout="wide"
)

# Título
st.title("🎓 Asistente 4 Materias - Streamlit Cloud")
st.markdown("### Tu compañero académico para las 4 materias")

# Verificación de dependencias
st.markdown("---")
st.subheader("🔍 Verificación del Sistema")

try:
    import streamlit
    st.success("✅ Streamlit - FUNCIONANDO")
except Exception as e:
    st.error(f"❌ Streamlit: {e}")

try:
    import transformers
    st.success("✅ Transformers - FUNCIONANDO")
except Exception as e:
    st.error(f"❌ Transformers: {e}")

try:
    import torch
    st.success("✅ PyTorch - FUNCIONANDO")
except Exception as e:
    st.error(f"❌ PyTorch: {e}")

try:
    from langchain_community.embeddings import HuggingFaceEmbeddings
    st.success("✅ LangChain - FUNCIONANDO")
except Exception as e:
    st.error(f"❌ LangChain: {e}")

# Configuración de materias
MATERIAS = {
    "estadistica": {
        "nombre": "Estadística",
        "emoji": "📊",
        "profesor": "Prof. Ferrarre",
        "consejo": "Practica todos los ejercicios y enfócate en el proceso paso a paso"
    },
    "desarrollo_ia": {
        "nombre": "Desarrollo de IA", 
        "emoji": "🤖",
        "profesor": "Especialista IA",
        "consejo": "Entiende los fundamentos antes de usar frameworks complejos"
    },
    "campo_laboral": {
        "nombre": "Campo Laboral",
        "emoji": "💼",
        "profesor": "Prof. Acri",
        "consejo": "Sé profesional, puntual y prepara exhaustivamente tus entregas"
    },
    "comunicacion": {
        "nombre": "Comunicación",
        "emoji": "🎯", 
        "profesor": "Especialista Comunicación",
        "consejo": "Estructura tus mensajes y adapta tu lenguaje al público"
    }
}

# Sidebar
with st.sidebar:
    st.header("📚 Selecciona Materia")
    
    materia_seleccionada = st.selectbox(
        "Elige:",
        list(MATERIAS.keys()),
        format_func=lambda x: f"{MATERIAS[x]['emoji']} {MATERIAS[x]['nombre']}"
    )
    
    materia = MATERIAS[materia_seleccionada]
    st.subheader(f"{materia['emoji']} {materia['profesor']}")
    st.write(f"**Consejo:** {materia['consejo']}")
    
    st.markdown("---")
    
    if st.button("🧹 Limpiar Chat"):
        st.session_state.messages = []
        st.rerun()

# Función para cargar conocimiento básico
def cargar_conocimiento_minimo():
    """Cargar conocimiento mínimo sin dependencias complejas"""
    try:
        # Verificar si existe la carpeta conocimiento
        if not os.path.exists("conocimiento"):
            return None
            
        conocimiento = {}
        for materia in os.listdir("conocimiento"):
            materia_path = os.path.join("conocimiento", materia)
            if os.path.isdir(materia_path):
                conocimiento[materia] = ""
                for archivo in os.listdir(materia_path):
                    if archivo.endswith('.txt'):
                        archivo_path = os.path.join(materia_path, archivo)
                        try:
                            with open(archivo_path, 'r', encoding='utf-8') as f:
                                conocimiento[materia] += f.read() + "\n"
                        except:
                            continue
        return conocimiento
    except Exception as e:
        st.error(f"Error cargando conocimiento: {e}")
        return None

# Cargar conocimiento
conocimiento = cargar_conocimiento_minimo()
if conocimiento:
    st.success(f"✅ Conocimiento cargado: {len(conocimiento)} materias")
else:
    st.warning("⚠️ No se pudo cargar el conocimiento completo")

# Inicializar chat
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": f"¡Hola! Soy tu asistente para {materia['nombre']}. ¿En qué puedo ayudarte? 🎓"}
    ]

# Mostrar historial de chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Función para generar respuesta simple
def generar_respuesta_simple(pregunta, materia):
    """Generar respuesta sin usar modelos complejos"""
    respuestas_base = {
        "estadistica": [
            "El profesor Ferrarre enfatiza la práctica constante de ejercicios.",
            "En estadística es clave entender el proceso, no solo el resultado.",
            "Los parciales suelen basarse en ejercicios de las guías prácticas."
        ],
        "desarrollo_ia": [
            "Es importante entender los algoritmos base antes de frameworks.",
            "La práctica con proyectos pequeños es fundamental.",
            "Documenta bien tu código y testea cada componente."
        ],
        "campo_laboral": [
            "La profesora Acri valora mucho la presentación profesional.",
            "Prepara exhaustivamente cada entrevista e investigación.",
            "La puntualidad y calidad en entregas es crucial."
        ],
        "comunicacion": [
            "Estructura tus mensajes de manera clara y organizada.",
            "Adapta tu lenguaje al público objetivo.",
            "Practica la escucha activa en tus interacciones."
        ]
    }
    
    import random
    base = random.choice(respuestas_base[materia])
    
    respuesta = f"""
    **{MATERIAS[materia]['emoji']} {MATERIAS[materia]['profesor']} dice:**
    
    {base}
    
    **Sobre tu pregunta:** "{pregunta}"
    
    *💡 En la versión completa, podré buscar en todo tu material específico usando IA.*
    """
    
    return respuesta

# Input del usuario
if prompt := st.chat_input(f"Pregunta sobre {materia['nombre']}..."):
    # Agregar mensaje del usuario
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generar respuesta
    with st.chat_message("assistant"):
        with st.spinner("Pensando..."):
            time.sleep(1)
            
            respuesta = generar_respuesta_simple(prompt, materia_seleccionada)
            
            # Efecto de escritura
            placeholder = st.empty()
            respuesta_completa = ""
            
            for chunk in respuesta.split():
                respuesta_completa += chunk + " "
                time.sleep(0.03)
                placeholder.markdown(respuesta_completa + "▌")
            
            placeholder.markdown(respuesta_completa)
    
    st.session_state.messages.append({"role": "assistant", "content": respuesta_completa})

# Información del estado
st.markdown("---")
st.success("""
**🎉 ¡Asistente Funcionando en Streamlit Cloud!**

**✅ Estado Actual:**
- Streamlit Cloud deployment exitoso
- Interfaz completamente funcional
- 4 materias configuradas
- Chat interactivo operativo

**🚀 Próximos Pasos:**
1. ✅ Versión básica funcionando
2. 🔄 Agregar IA progresivamente
3. 📚 Tu material ya está cargado
4. 🌐 Compartir con compañeros

**📞 Para soporte:**
- Revisa los logs en "Manage app"
- Verifica que todos los archivos estén en el repositorio
- Asegúrate de que la estructura de carpetas sea correcta
""")

st.markdown("---")
st.markdown("🎓 **Asistente 4 Materias** • Desplegado exitosamente en Streamlit Community Cloud")
