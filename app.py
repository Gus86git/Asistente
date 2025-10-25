import streamlit as st
import os
import time
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# Configuración de la página
st.set_page_config(
    page_title="Asistente 4 Materias - Dual Mode",
    page_icon="🎓",
    layout="wide"
)

# ==================== IMPORTACIONES CONDICIONALES ====================
SENTENCE_TRANSFORMERS_AVAILABLE = False
TRANSFORMERS_AVAILABLE = False

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    st.warning("⚠️ sentence-transformers no disponible. Usando modo fallback.")

try:
    from transformers import AutoModelForCausalLM, AutoTokenizer
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    st.warning("⚠️ transformers no disponible. IA Generativa deshabilitada.")

# ==================== DEFINICIONES ====================
PROFESORES = {
    "estadistica": {
        "nombre": "Estadística",
        "emoji": "📊",
        "profesor": "Prof. Matemáticas",
        "consejo": "Practica con ejercicios y memoriza las fórmulas clave",
        "ejemplos_busqueda": [
            "Ejercicio 3 de la guía 2",
            "Fórmula de la media ponderada",
            "Fecha del parcial"
        ],
        "ejemplos_ia": [
            "Explícame el teorema de Bayes",
            "¿Cómo estudio para el parcial?",
            "Diferencia entre media y mediana"
        ]
    },
    "campo_laboral": {
        "nombre": "Campo Laboral",
        "emoji": "💼",
        "profesor": "Prof. Acri",
        "consejo": "Participa activamente y prepara excelentes presentaciones",
        "ejemplos_busqueda": [
            "Requisitos del trabajo práctico",
            "Consejos para entrevistas",
            "Criterios de evaluación"
        ],
        "ejemplos_ia": [
            "¿Cómo preparo una buena entrevista?",
            "Qué valora la profesora Acri?",
            "Consejos para mi CV"
        ]
    },
    "algoritmos": {
        "nombre": "Algoritmos",
        "emoji": "💻",
        "profesor": "Prof. Código",
        "consejo": "Codifica, practica y entiende la complejidad",
        "ejemplos_busqueda": [
            "Algoritmo de ordenamiento quicksort",
            "Complejidad de búsqueda binaria",
            "Ejercicio 5 de recursión"
        ],
        "ejemplos_ia": [
            "¿Cuándo usar recursión vs iteración?",
            "Explícame la notación Big O",
            "¿Cómo optimizo mi código?"
        ]
    },
    "redes": {
        "nombre": "Redes",
        "emoji": "🌐",
        "profesor": "Prof. Conectividad",
        "consejo": "Entiende los protocolos y practica con casos reales",
        "ejemplos_busqueda": [
            "Modelo OSI capas",
            "Protocolo TCP vs UDP",
            "Configuración de subredes"
        ],
        "ejemplos_ia": [
            "¿Cómo funciona el protocolo HTTP?",
            "Diferencias entre router y switch",
            "¿Qué es el DNS?"
        ]
    }
}

# ==================== UI ====================
st.title("🎓 Asistente 4 Materias")
st.markdown("**Búsqueda Semántica 🔍 + IA Generativa 🤖**")

# ==================== SIDEBAR ====================
with st.sidebar:
    st.header("⚙️ Configuración")
    
    materia_seleccionada = st.selectbox(
        "📚 Materia:",
        options=list(PROFESORES.keys()),
        format_func=lambda x: f"{PROFESORES[x]['emoji']} {PROFESORES[x]['nombre']}"
    )
    
    materia = PROFESORES[materia_seleccionada]
    
    st.markdown("---")
    
    # Selector de modo - solo si hay al menos un sistema disponible
    if SENTENCE_TRANSFORMERS_AVAILABLE or TRANSFORMERS_AVAILABLE:
        opciones_modo = []
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            opciones_modo.append("busqueda")
        if TRANSFORMERS_AVAILABLE:
            opciones_modo.append("ia_generativa")
        
        if len(opciones_modo) > 1:
            modo = st.radio(
                "🎯 Modo de Respuesta:",
                options=opciones_modo,
                format_func=lambda x: "🔍 Búsqueda Semántica" if x == "busqueda" else "🤖 IA Generativa"
            )
        else:
            modo = opciones_modo[0]
            st.info(f"Modo activo: {'🔍 Búsqueda' if modo == 'busqueda' else '🤖 IA'}")
    else:
        st.error("❌ Ningún sistema disponible")
        modo = "busqueda"
    
    st.markdown("---")
    st.markdown(f"**👨‍🏫 Profesor:** {materia['profesor']}")
    st.markdown(f"**💡 Consejo:** {materia['consejo']}")
    
    st.markdown("---")
    
    with st.expander("🔧 Configuración Avanzada"):
        cantidad_resultados = st.slider("Resultados:", 1, 7, 3)
        temperatura = st.slider("Temperatura IA:", 0.1, 1.0, 0.7, 0.1)
    
    st.markdown("---")
    
    if st.button("🧹 Limpiar Conversación", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ==================== FUNCIONES AUXILIARES ====================
def dividir_texto(texto, tamano_chunk=800, overlap=150):
    """Dividir texto en chunks con overlap"""
    chunks = []
    inicio = 0
    
    while inicio < len(texto):
        fin = inicio + tamano_chunk
        chunk = texto[inicio:fin]
        
        if fin < len(texto):
            ultimo_punto = chunk.rfind('.')
            ultimo_salto = chunk.rfind('\n')
            corte = max(ultimo_punto, ultimo_salto)
            if corte > tamano_chunk * 0.6:
                chunk = chunk[:corte+1]
                fin = inicio + corte + 1
        
        if chunk.strip():
            chunks.append(chunk.strip())
        
        inicio = fin - overlap
        if inicio >= len(texto):
            break
    
    return chunks

def cargar_documentos():
    """Cargar todos los documentos de la carpeta conocimiento"""
    if not os.path.exists("conocimiento"):
        return [], []
    
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
                                chunks = dividir_texto(contenido, 800, 150)
                                for i, chunk in enumerate(chunks):
                                    textos.append(chunk)
                                    metadatos.append({
                                        "materia": materia_dir,
                                        "archivo": archivo,
                                        "fuente": f"{materia_dir}/{archivo}",
                                        "chunk": i
                                    })
                    except Exception:
                        continue
    
    return textos, metadatos

# ==================== SISTEMA DE BÚSQUEDA SEMÁNTICA ====================
@st.cache_resource
def inicializar_busqueda_semantica():
    """Inicializar sistema de búsqueda con sentence-transformers"""
    if not SENTENCE_TRANSFORMERS_AVAILABLE:
        return None, None, None
    
    try:
        modelo = SentenceTransformer('all-MiniLM-L6-v2')
        textos, metadatos = cargar_documentos()
        
        if not textos:
            st.warning("⚠️ No se encontraron documentos")
            return None, None, None
        
        with st.spinner("🔄 Generando embeddings..."):
            embeddings = modelo.encode(textos, show_progress_bar=False, convert_to_numpy=True)
        
        st.success(f"✅ Búsqueda semántica lista: {len(textos)} fragmentos")
        return modelo, embeddings, (textos, metadatos)
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        return None, None, None

# ==================== SISTEMA FALLBACK TF-IDF ====================
@st.cache_resource
def inicializar_busqueda_tfidf():
    """Sistema de búsqueda fallback con TF-IDF"""
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        
        textos, metadatos = cargar_documentos()
        
        if not textos:
            st.warning("⚠️ No se encontraron documentos")
            return None, None, None
        
        vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1, 2))
        matriz_tfidf = vectorizer.fit_transform(textos)
        
        st.success(f"✅ Búsqueda TF-IDF lista: {len(textos)} fragmentos")
        return vectorizer, matriz_tfidf, (textos, metadatos)
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        return None, None, None

# ==================== SISTEMA IA GENERATIVA ====================
@st.cache_resource
def inicializar_ia_generativa():
    """Inicializar modelo generativo"""
    if not TRANSFORMERS_AVAILABLE:
        return None, None
    
    try:
        model_name = "distilgpt2"
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        modelo = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
        )
        
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        
        st.success("✅ IA Generativa lista")
        return modelo, tokenizer
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        return None, None

# ==================== INICIALIZACIÓN ====================
with st.spinner("🔄 Inicializando sistemas..."):
    if SENTENCE_TRANSFORMERS_AVAILABLE:
        modelo_embed, embeddings_bd, datos = inicializar_busqueda_semantica()
    else:
        modelo_embed, embeddings_bd, datos = inicializar_busqueda_tfidf()
    
    if TRANSFORMERS_AVAILABLE:
        modelo_gen, tokenizer_gen = inicializar_ia_generativa()
    else:
        modelo_gen, tokenizer_gen = None, None

# ==================== FUNCIONES DE BÚSQUEDA ====================
def buscar_con_embeddings(consulta, modelo, embeddings, datos, materia_obj, k):
    """Buscar usando embeddings de sentence-transformers"""
    textos, metadatos = datos
    query_embedding = modelo.encode([consulta], convert_to_numpy=True)
    similitudes = cosine_similarity(query_embedding, embeddings)[0]
    indices_ordenados = np.argsort(similitudes)[::-1]
    
    resultados = []
    for idx in indices_ordenados:
        if similitudes[idx] < 0.1:
            continue
        if materia_obj and metadatos[idx]["materia"] != materia_obj:
            continue
        
        resultados.append({
            "texto": textos[idx],
            "metadata": metadatos[idx],
            "score": float(similitudes[idx])
        })
        
        if len(resultados) >= k:
            break
    
    return resultados

def buscar_con_tfidf(consulta, vectorizer, matriz, datos, materia_obj, k):
    """Buscar usando TF-IDF"""
    textos, metadatos = datos
    query_vector = vectorizer.transform([consulta])
    similitudes = cosine_similarity(query_vector, matriz)[0]
    indices_ordenados = np.argsort(similitudes)[::-1]
    
    resultados = []
    for idx in indices_ordenados:
        if similitudes[idx] < 0.05:
            continue
        if materia_obj and metadatos[idx]["materia"] != materia_obj:
            continue
        
        resultados.append({
            "texto": textos[idx],
            "metadata": metadatos[idx],
            "score": float(similitudes[idx])
        })
        
        if len(resultados) >= k:
            break
    
    return resultados

def buscar_informacion(consulta, materia_obj, k):
    """Buscar información relevante"""
    if datos is None:
        return [], "Sistema no disponible"
    
    try:
        if SENTENCE_TRANSFORMERS_AVAILABLE and modelo_embed is not None:
            resultados = buscar_con_embeddings(consulta, modelo_embed, embeddings_bd, datos, materia_obj, k)
        else:
            resultados = buscar_con_tfidf(consulta, modelo_embed, embeddings_bd, datos, materia_obj, k)
        
        if not resultados:
            return [], "No encontré información relevante"
        
        return resultados, None
    except Exception as e:
        return [], f"Error: {str(e)}"

def generar_respuesta_busqueda(consulta, resultados):
    """Generar respuesta formateada para búsqueda"""
    if not resultados:
        return "❌ No encontré información específica.\n\n💡 Intenta reformular tu pregunta."
    
    respuesta = f"**🔍 Resultados para: \"{consulta}\"**\n\n"
    
    por_archivo = {}
    for r in resultados:
        fuente = r['metadata']['fuente']
        if fuente not in por_archivo:
            por_archivo[fuente] = []
        por_archivo[fuente].append(r)
    
    for fuente, items in por_archivo.items():
        respuesta += f"**📁 {fuente}**\n\n"
        for item in items:
            texto = item['texto']
            if len(texto) > 600:
                texto = texto[:600] + "..."
            
            score = item['score']
            relevancia = "🟢" if score > 0.4 else "🟡" if score > 0.25 else "🟠"
            respuesta += f"{relevancia} {texto}\n\n"
    
    respuesta += f"---\n**💡 {len(resultados)} fragmentos encontrados**"
    return respuesta

def generar_respuesta_ia(consulta, resultados, temp):
    """Generar respuesta con IA"""
    if modelo_gen is None:
        return "❌ IA Generativa no disponible"
    
    contexto = "\n".join([r['texto'][:300] for r in resultados[:2]]) if resultados else "Material general"
    
    prompt = f"Pregunta: {consulta}\nContexto: {contexto}\nRespuesta:"
    
    try:
        inputs = tokenizer_gen(prompt, return_tensors="pt", max_length=400, truncation=True)
        
        with torch.no_grad():
            outputs = modelo_gen.generate(
                inputs.input_ids,
                max_new_tokens=150,
                temperature=temp,
                do_sample=True,
                top_p=0.9,
                pad_token_id=tokenizer_gen.eos_token_id
            )
        
        respuesta = tokenizer_gen.decode(outputs[0], skip_special_tokens=True)
        respuesta = respuesta[len(prompt):].strip()
        
        if len(respuesta) > 500:
            respuesta = respuesta[:500] + "..."
        
        return f"{respuesta}\n\n---\n**🤖 Generado por IA**"
    except Exception as e:
        return f"❌ Error: {str(e)}"

# ==================== CHAT ====================
if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant",
        "content": f"¡Hola! 👋 Soy tu asistente para **{materia['nombre']}** {materia['emoji']}"
    }]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input(f"Pregunta sobre {materia['nombre']}..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        with st.spinner("🔍 Procesando..."):
            resultados, error = buscar_informacion(prompt, materia_seleccionada, cantidad_resultados)
            
            if modo == "busqueda":
                respuesta = generar_respuesta_busqueda(prompt, resultados) if not error else f"❌ {error}"
            else:
                respuesta = generar_respuesta_ia(prompt, resultados, temperatura)
        
        placeholder = st.empty()
        texto = ""
        for linea in respuesta.split('\n'):
            texto += linea + '\n'
            time.sleep(0.02)
            placeholder.markdown(texto + "▌")
        placeholder.markdown(texto)
    
    st.session_state.messages.append({"role": "assistant", "content": texto})

# ==================== FOOTER ====================
st.markdown("---")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Modo", "🔍" if modo == "busqueda" else "🤖")
with col2:
    st.metric("Materia", materia['emoji'])
with col3:
    st.metric("Búsqueda", "🟢" if datos else "🔴")
with col4:
    st.metric("IA", "🟢" if modelo_gen else "🔴")

st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #28a745; font-weight: bold;'>"
    "🎓 ASISTENTE 4 MATERIAS - DUAL MODE AI"
    "</div>",
    unsafe_allow_html=True
)
