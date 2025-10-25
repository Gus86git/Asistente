import streamlit as st
import os
import time
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import torch

# Configuración de la página
st.set_page_config(
    page_title="Asistente 4 Materias - Dual Mode",
    page_icon="🎓",
    layout="wide"
)

# Definición de materias y profesores
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

# Estilos CSS personalizados
st.markdown("""
<style>
    .stMetric {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
    }
    .modo-activo {
        background-color: #d4edda;
        border-left: 4px solid #28a745;
        padding: 10px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Título principal
st.title("🎓 Asistente 4 Materias")
st.markdown("**Búsqueda Semántica 🔍 + IA Generativa 🤖 - Lo mejor de ambos mundos**")

# ==================== SIDEBAR ====================
with st.sidebar:
    st.header("⚙️ Configuración")
    
    # Selector de materia
    materia_seleccionada = st.selectbox(
        "📚 Materia:",
        options=list(PROFESORES.keys()),
        format_func=lambda x: f"{PROFESORES[x]['emoji']} {PROFESORES[x]['nombre']}"
    )
    
    materia = PROFESORES[materia_seleccionada]
    
    st.markdown("---")
    
    # Selector de modo
    modo = st.radio(
        "🎯 Modo de Respuesta:",
        options=["busqueda", "ia_generativa"],
        format_func=lambda x: "🔍 Búsqueda Semántica" if x == "busqueda" else "🤖 IA Generativa",
        help="Búsqueda: información exacta | IA: explicaciones naturales"
    )
    
    st.markdown("---")
    
    # Información de la materia
    st.markdown(f"**👨‍🏫 Profesor:** {materia['profesor']}")
    st.markdown(f"**💡 Consejo:** {materia['consejo']}")
    
    st.markdown("---")
    
    # Configuración avanzada
    with st.expander("🔧 Configuración Avanzada"):
        cantidad_resultados = st.slider(
            "Resultados a mostrar:",
            min_value=1,
            max_value=7,
            value=3
        )
        
        temperatura = st.slider(
            "Temperatura IA (creatividad):",
            min_value=0.1,
            max_value=1.0,
            value=0.7,
            step=0.1,
            help="Más alto = más creativo, más bajo = más conservador"
        )
    
    st.markdown("---")
    
    # Botón de limpiar
    if st.button("🧹 Limpiar Conversación", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ==================== SISTEMA DE BÚSQUEDA SEMÁNTICA ====================
@st.cache_resource
def inicializar_busqueda_semantica():
    """Inicializar embeddings y base de conocimiento"""
    try:
        # Cargar modelo de embeddings
        modelo = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Verificar carpeta conocimiento
        if not os.path.exists("conocimiento"):
            st.warning("⚠️ Carpeta 'conocimiento' no encontrada")
            return None, None, None
        
        # Cargar documentos
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
                                    chunks = dividir_texto(contenido, 800, 150)
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
                            st.error(f"Error leyendo {archivo}: {str(e)}")
                            continue
        
        if not textos:
            st.warning("⚠️ No se encontraron documentos")
            return None, None, None
        
        # Generar embeddings
        with st.spinner("🔄 Generando embeddings..."):
            embeddings = modelo.encode(textos, show_progress_bar=False, convert_to_numpy=True)
        
        st.success(f"✅ Sistema listo: {archivos_cargados} archivos, {len(textos)} fragmentos")
        return modelo, embeddings, (textos, metadatos)
        
    except Exception as e:
        st.error(f"❌ Error en búsqueda semántica: {str(e)}")
        return None, None, None

# ==================== SISTEMA DE IA GENERATIVA ====================
@st.cache_resource
def inicializar_ia_generativa():
    """Inicializar modelo generativo"""
    try:
        from transformers import AutoModelForCausalLM, AutoTokenizer
        
        # Usar modelo pequeño y eficiente
        model_name = "distilgpt2"  # Más pequeño que DialoGPT
        
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        modelo = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
        )
        
        # Configurar pad token
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        
        st.success("✅ IA Generativa lista")
        return modelo, tokenizer
        
    except Exception as e:
        st.error(f"❌ Error en IA generativa: {str(e)}")
        return None, None

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

def buscar_informacion_relevante(consulta, modelo_embed, embeddings_bd, datos, materia_obj=None, k=3):
    """Buscar información usando similitud de embeddings"""
    if modelo_embed is None or embeddings_bd is None or datos is None:
        return [], "Sistema de búsqueda no disponible"
    
    try:
        textos, metadatos = datos
        
        # Generar embedding de la consulta
        query_embedding = modelo_embed.encode([consulta], convert_to_numpy=True)
        
        # Calcular similitudes
        similitudes = cosine_similarity(query_embedding, embeddings_bd)[0]
        
        # Ordenar por similitud
        indices_ordenados = np.argsort(similitudes)[::-1]
        
        # Filtrar resultados
        resultados = []
        for idx in indices_ordenados:
            if similitudes[idx] < 0.1:  # Umbral mínimo
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
        
        if not resultados:
            return [], "No encontré información relevante"
        
        return resultados, None
        
    except Exception as e:
        return [], f"Error: {str(e)}"

def generar_respuesta_busqueda(consulta, resultados, materia):
    """Generar respuesta para modo búsqueda"""
    if not resultados:
        return "❌ No encontré información específica.\n\n💡 Intenta reformular tu pregunta o usa el modo IA Generativa."
    
    respuesta = f"**🔍 Resultados para: \"{consulta}\"**\n\n"
    
    # Agrupar por archivo
    por_archivo = {}
    for r in resultados:
        fuente = r['metadata']['fuente']
        if fuente not in por_archivo:
            por_archivo[fuente] = []
        por_archivo[fuente].append(r)
    
    # Mostrar resultados
    for fuente, items in por_archivo.items():
        respuesta += f"**📁 {fuente}**\n\n"
        for item in items:
            texto = item['texto']
            score = item['score']
            
            if len(texto) > 600:
                texto = texto[:600] + "..."
            
            relevancia = "🟢" if score > 0.4 else "🟡" if score > 0.25 else "🟠"
            respuesta += f"{relevancia} {texto}\n\n"
    
    respuesta += "---\n"
    respuesta += f"**💡 Encontré {len(resultados)} fragmentos relevantes**\n"
    respuesta += "**🔍 Modo Búsqueda Semántica:** Información EXACTA de tus archivos"
    
    return respuesta

def generar_respuesta_ia(consulta, resultados, materia, modelo_gen, tokenizer_gen, temp=0.7):
    """Generar respuesta con IA generativa"""
    if modelo_gen is None or tokenizer_gen is None:
        return "❌ IA Generativa no disponible. Usa el modo Búsqueda Semántica."
    
    # Construir contexto
    if resultados:
        contexto = "\n\n".join([r['texto'][:400] for r in resultados[:3]])
        fuentes = list(set(r['metadata']['fuente'] for r in resultados))
    else:
        contexto = f"Material general de {materia['nombre']}"
        fuentes = []
    
    # Crear prompt
    prompt = f"""Eres un tutor educativo de {materia['nombre']}.

Contexto del material:
{contexto}

Pregunta del estudiante: {consulta}

Respuesta clara y educativa:"""
    
    try:
        # Tokenizar
        inputs = tokenizer_gen(prompt, return_tensors="pt", max_length=512, truncation=True)
        
        # Generar respuesta
        with torch.no_grad():
            outputs = modelo_gen.generate(
                inputs.input_ids,
                max_new_tokens=200,
                temperature=temp,
                do_sample=True,
                top_p=0.9,
                top_k=50,
                pad_token_id=tokenizer_gen.eos_token_id,
                no_repeat_ngram_size=3
            )
        
        # Decodificar
        respuesta_completa = tokenizer_gen.decode(outputs[0], skip_special_tokens=True)
        
        # Extraer solo la respuesta nueva
        if "Respuesta clara y educativa:" in respuesta_completa:
            respuesta_texto = respuesta_completa.split("Respuesta clara y educativa:")[-1].strip()
        else:
            respuesta_texto = respuesta_completa[len(prompt):].strip()
        
        # Limitar longitud
        if len(respuesta_texto) > 800:
            respuesta_texto = respuesta_texto[:800] + "..."
        
        # Agregar información de fuentes
        if fuentes:
            respuesta_texto += f"\n\n---\n**📚 Fuentes consultadas:** {', '.join(fuentes[:3])}"
        
        respuesta_texto += "\n\n**🤖 Modo IA Generativa:** Respuesta generada por IA basada en tu material"
        
        return respuesta_texto
        
    except Exception as e:
        return f"❌ Error generando respuesta: {str(e)}\n\n💡 Intenta con el modo Búsqueda Semántica."

# ==================== INICIALIZACIÓN ====================
with st.spinner("🔄 Inicializando sistemas..."):
    modelo_embed, embeddings_bd, datos = inicializar_busqueda_semantica()
    modelo_gen, tokenizer_gen = inicializar_ia_generativa()

# ==================== CHAT ====================
# Inicializar mensajes
if "messages" not in st.session_state:
    modo_texto = "**Búsqueda Semántica** 🔍" if modo == "busqueda" else "**IA Generativa** 🤖"
    st.session_state.messages = [{
        "role": "assistant",
        "content": f"¡Hola! 👋 Soy tu asistente para **{materia['nombre']}** {materia['emoji']}\n\nEstoy en modo {modo_texto}. ¿En qué puedo ayudarte?"
    }]

# Mostrar historial
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input del usuario
placeholder_text = f"Pregunta sobre {materia['nombre']}..."
if prompt := st.chat_input(placeholder_text):
    # Agregar mensaje del usuario
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generar respuesta
    with st.chat_message("assistant"):
        # Primero buscar información relevante
        with st.spinner("🔍 Buscando información relevante..."):
            resultados, error = buscar_informacion_relevante(
                prompt,
                modelo_embed,
                embeddings_bd,
                datos,
                materia_seleccionada,
                cantidad_resultados
            )
        
        # Generar respuesta según el modo
        if modo == "busqueda":
            if error:
                respuesta = f"**❌ {error}**\n\n💡 Intenta reformular tu pregunta."
            else:
                respuesta = generar_respuesta_busqueda(prompt, resultados, materia)
        
        else:  # IA Generativa
            with st.spinner("🤖 Generando respuesta con IA..."):
                respuesta = generar_respuesta_ia(
                    prompt,
                    resultados,
                    materia,
                    modelo_gen,
                    tokenizer_gen,
                    temperatura
                )
        
        # Efecto de escritura
        placeholder = st.empty()
        texto_completo = ""
        for linea in respuesta.split('\n'):
            texto_completo += linea + '\n'
            time.sleep(0.02)
            placeholder.markdown(texto_completo + "▌")
        placeholder.markdown(texto_completo)
    
    st.session_state.messages.append({"role": "assistant", "content": texto_completo})

# ==================== PANEL DE INFORMACIÓN ====================
st.markdown("---")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("🎯 Modo", "🔍 Búsqueda" if modo == "busqueda" else "🤖 IA")

with col2:
    st.metric("📚 Materia", materia['emoji'])

with col3:
    status_busqueda = "🟢" if modelo_embed else "🔴"
    st.metric("Búsqueda", status_busqueda)

with col4:
    status_ia = "🟢" if modelo_gen else "🔴"
    st.metric("IA", status_ia)

# ==================== GUÍA DE USO ====================
st.markdown("---")
col_guia1, col_guia2 = st.columns(2)

with col_guia1:
    st.success("""
**🔍 BÚSQUEDA SEMÁNTICA**

**Usa cuando necesites:**
- Información EXACTA de tus archivos
- Datos específicos (fechas, fórmulas)
- Saber en qué archivo está algo
- Velocidad y confiabilidad absoluta
""")

with col_guia2:
    st.info("""
**🤖 IA GENERATIVA**

**Usa cuando quieras:**
- Explicaciones naturales y didácticas
- Síntesis de múltiples fuentes
- Respuestas elaboradas
- Razonamiento y contextualización
""")

# ==================== EJEMPLOS ====================
st.markdown("---")
col_ej1, col_ej2 = st.columns(2)

with col_ej1:
    st.markdown("**📝 Ejemplos - Búsqueda Semántica:**")
    for ejemplo in materia['ejemplos_busqueda']:
        st.markdown(f"- {ejemplo}")

with col_ej2:
    st.markdown("**💬 Ejemplos - IA Generativa:**")
    for ejemplo in materia['ejemplos_ia']:
        st.markdown(f"- {ejemplo}")

# ==================== FOOTER ====================
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #28a745; font-weight: bold;'>"
    "🎓 ASISTENTE 4 MATERIAS - POWERED BY SEMANTIC SEARCH + GENERATIVE AI"
    "</div>",
    unsafe_allow_html=True
)
