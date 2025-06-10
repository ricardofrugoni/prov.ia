import tempfile
import os
import shutil
from pathlib import Path

import streamlit as st
from langchain.memory import ConversationBufferMemory
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

from loaders import *

# API Key da OpenAI (SUBSTITUA PELA SUA CHAVE VÁLIDA)
OPENAI_API_KEY = "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"  # ← COLOQUE SUA API KEY REAL AQUI

# Diretório para armazenar arquivos uploaded
UPLOAD_DIR = "uploaded_files"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

TIPOS_ARQUIVOS_VALIDOS = [
    'Site', 'Youtube', 'Pdf', 'Csv', 'Txt'
]

# Configuração fixa para OpenAI GPT-4o
MODELO_FIXO = 'gpt-4o'

MEMORIA = ConversationBufferMemory()

def salvar_arquivo_uploaded(arquivo, tipo_arquivo):
    """Salva o arquivo uploaded no diretório de uploads"""
    if arquivo is not None:
        # Criar nome único baseado no timestamp
        import time
        timestamp = str(int(time.time()))
        nome_arquivo = f"{timestamp}_{arquivo.name}"
        caminho_arquivo = os.path.join(UPLOAD_DIR, nome_arquivo)
        
        with open(caminho_arquivo, "wb") as f:
            f.write(arquivo.getbuffer())
        
        return caminho_arquivo
    return None

def carrega_arquivos(tipo_arquivo, arquivo):
    if tipo_arquivo == 'Site':
        documento = carrega_site(arquivo)
    elif tipo_arquivo == 'Youtube':
        documento = carrega_youtube(arquivo)
    elif tipo_arquivo == 'Pdf':
        # Salvar arquivo permanentemente
        caminho_salvo = salvar_arquivo_uploaded(arquivo, tipo_arquivo)
        documento = carrega_pdf(caminho_salvo)
    elif tipo_arquivo == 'Csv':
        # Salvar arquivo permanentemente
        caminho_salvo = salvar_arquivo_uploaded(arquivo, tipo_arquivo)
        documento = carrega_csv(caminho_salvo)
    elif tipo_arquivo == 'Txt':
        # Salvar arquivo permanentemente
        caminho_salvo = salvar_arquivo_uploaded(arquivo, tipo_arquivo)
        documento = carrega_txt(caminho_salvo)
    return documento

def inicializar_provia(tipo_arquivo, arquivo):
    """Inicializa o ProV.ia com documento específico"""
    
    documento = carrega_arquivos(tipo_arquivo, arquivo)

    system_message = '''Você é um assistente amigável chamado ProV.ia.
    Você é especialista em assuntos internos, dúvidas e questionamentos sobre a Provion.
    
    Você possui acesso às seguintes informações vindas de um documento {}: 

    ####
    {}
    ####

    Utilize as informações fornecidas para basear as suas respostas quando relevante.
    Seja prestativo, profissional e cordial em suas respostas.

    Sempre que houver $ na sua saída, substitua por S.

    Se a informação do documento for algo como "Just a moment...Enable JavaScript and cookies to continue" 
    sugira ao usuário carregar novamente o documento!'''.format(tipo_arquivo, documento)

    template = ChatPromptTemplate.from_messages([
        ('system', system_message),
        ('placeholder', '{chat_history}'),
        ('user', '{input}')
    ])
    
    # Usar sempre GPT-4o com API key fixa
    chat = ChatOpenAI(model=MODELO_FIXO, api_key=OPENAI_API_KEY)
    chain = template | chat

    st.session_state['chain'] = chain
    st.session_state['provia_ativo'] = True

def inicializar_provia_padrao():
    """Inicializa o ProV.ia com configuração padrão (sem documento específico)"""
    
    system_message = '''Você é um assistente amigável chamado ProV.ia.
    Você é especialista em assuntos internos, dúvidas e questionamentos sobre a Provion.
    
    Seja prestativo, profissional e cordial em suas respostas.
    Ajude com informações gerais, tire dúvidas e forneça suporte aos usuários.
    
    Sempre que houver $ na sua saída, substitua por S.'''

    template = ChatPromptTemplate.from_messages([
        ('system', system_message),
        ('placeholder', '{chat_history}'),
        ('user', '{input}')
    ])
    
    # Usar sempre GPT-4o com API key fixa
    chat = ChatOpenAI(model=MODELO_FIXO, api_key=OPENAI_API_KEY)
    chain = template | chat

    return chain

def adicionar_css_customizado():
    """CSS corrigido - Dropdown funcional e mensagens sem caixas pretas"""
    st.markdown("""
    <style>
    /* FORÇA FUNDO PRETO EM TUDO */
    *, *::before, *::after {
        background-color: transparent !important;
    }
    
    .stApp, 
    .stApp > div,
    .main,
    .block-container,
    [data-testid="stMain"],
    [data-testid="stAppViewContainer"],
    .css-18e3th9,
    .css-1d391kg,
    .css-k1vhr4,
    .element-container,
    .stMarkdown {
        background-color: #000000 !important;
        color: white !important;
    }
    
    /* Remover margens e paddings */
    .main, .main > div, .block-container {
        padding: 0 !important;
        margin: 0 !important;
        max-width: 100% !important;
        width: 100% !important;
    }
    
    /* Ocultar header do Streamlit */
    .stAppHeader,
    header[data-testid="stHeader"],
    .stDeployButton {
        display: none !important;
        height: 0 !important;
        visibility: hidden !important;
    }
    
    /* SIDEBAR - CINZA ESCURO E MENOR */
    section[data-testid="stSidebar"],
    [data-testid="stSidebar"] {
        background-color: #2a2a2a !important;
        border-right: 3px solid #8FD14F !important;
        width: 280px !important;
        min-width: 280px !important;
        max-width: 280px !important;
    }
    
    /* Sidebar elementos internos */
    section[data-testid="stSidebar"] *,
    [data-testid="stSidebar"] * {
        color: white !important;
        background-color: transparent !important;
    }
    
    /* Sidebar inputs, botões e containers */
    section[data-testid="stSidebar"] .stSelectbox,
    section[data-testid="stSidebar"] .stTextInput,
    section[data-testid="stSidebar"] .stFileUploader,
    section[data-testid="stSidebar"] .stButton {
        background-color: #404040 !important;
        border-radius: 8px !important;
        margin: 8px 0 !important;
        border: 1px solid #666 !important;
        padding: 8px !important;
    }
    
    section[data-testid="stSidebar"] .stButton button {
        background-color: #8FD14F !important;
        color: #000000 !important;
        border: none !important;
        font-weight: bold !important;
        border-radius: 8px !important;
        padding: 10px 15px !important;
        width: 100% !important;
    }
    
    /* DROPDOWN SIDEBAR - CORRIGIDO COMPLETAMENTE */
    section[data-testid="stSidebar"] .stSelectbox > div > div,
    section[data-testid="stSidebar"] .stSelectbox > div > div > div,
    section[data-testid="stSidebar"] .stSelectbox [data-baseweb="select"] {
        background-color: #404040 !important;
        border: 1px solid #8FD14F !important;
        color: white !important;
        border-radius: 8px !important;
    }
    
    /* Dropdown texto selecionado */
    section[data-testid="stSidebar"] .stSelectbox [data-baseweb="select"] > div {
        background-color: #404040 !important;
        color: white !important;
        border: none !important;
    }
    
    /* Menu dropdown quando aberto */
    section[data-testid="stSidebar"] .stSelectbox ul,
    section[data-testid="stSidebar"] .stSelectbox [role="listbox"],
    div[data-baseweb="popover"] ul {
        background-color: #404040 !important;
        border: 1px solid #8FD14F !important;
        color: white !important;
        border-radius: 8px !important;
    }
    
    /* Itens do dropdown */
    section[data-testid="stSidebar"] .stSelectbox li,
    section[data-testid="stSidebar"] .stSelectbox [role="option"],
    div[data-baseweb="popover"] li {
        background-color: #404040 !important;
        color: white !important;
        padding: 8px 12px !important;
        border-radius: 4px !important;
    }
    
    section[data-testid="stSidebar"] .stSelectbox li:hover,
    section[data-testid="stSidebar"] .stSelectbox [role="option"]:hover,
    div[data-baseweb="popover"] li:hover {
        background-color: #8FD14F !important;
        color: black !important;
    }
    
    /* Seta do dropdown */
    section[data-testid="stSidebar"] .stSelectbox svg {
        fill: white !important;
        color: white !important;
    }
    
    /* Input de texto da sidebar */
    section[data-testid="stSidebar"] input,
    section[data-testid="stSidebar"] .stTextInput input {
        background-color: #404040 !important;
        border: 1px solid #8FD14F !important;
        color: white !important;
        border-radius: 8px !important;
        padding: 8px 12px !important;
    }
    
    section[data-testid="stSidebar"] input::placeholder {
        color: #aaa !important;
    }
    
    /* File uploader da sidebar */
    section[data-testid="stSidebar"] .stFileUploader > div,
    section[data-testid="stSidebar"] .stFileUploader label {
        background-color: #404040 !important;
        border: 1px solid #8FD14F !important;
        color: white !important;
        border-radius: 8px !important;
        padding: 12px !important;
    }
    
    /* ÁREA PRINCIPAL - SEMPRE CENTRALIZADA */
    [data-testid="stMain"] {
        background-color: #000000 !important;
        padding: 0 !important;
        margin: 0 !important;
        position: relative !important;
        overflow-x: hidden !important;
        display: flex !important;
        justify-content: center !important;
        align-items: flex-start !important;
        min-height: 100vh !important;
    }
    
    /* CONTAINER PRINCIPAL - CENTRALIZADO COM OU SEM SIDEBAR */
    .main > div:first-child {
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: flex-start !important;
        min-height: 100vh !important;
        padding: 20px !important;
        background-color: #000000 !important;
        width: 100% !important;
        max-width: 700px !important;
        margin: 0 auto !important;
        box-sizing: border-box !important;
        position: relative !important;
        z-index: 1 !important;
    }
    
    /* FORÇAR CENTRALIZAÇÃO QUANDO SIDEBAR FECHADA */
    .main[data-testid="stMain"]:not(:has(section[data-testid="stSidebar"][aria-expanded="true"])) > div:first-child {
        margin-left: auto !important;
        margin-right: auto !important;
        transform: translateX(0) !important;
    }
    
    /* ÁREA DO CHAT - SEMPRE CENTRALIZADA */
    .main .element-container {
        width: 100% !important;
        max-width: 600px !important;
        margin: 0 auto !important;
        background-color: transparent !important;
    }
    
    /* TÍTULO - CENTRALIZADO */
    .main h1 {
        color: #8FD14F !important;
        font-size: 2.5rem !important;
        font-weight: bold !important;
        text-align: center !important;
        text-shadow: 0 0 20px #8FD14F !important;
        margin: 20px 0 !important;
        background-color: transparent !important;
        width: 100% !important;
    }
    
    /* CHAT MESSAGES - SEM CAIXAS PRETAS */
    .stChatMessage {
        background: rgba(30, 30, 30, 0.6) !important;
        border: 1px solid rgba(143, 209, 79, 0.3) !important;
        border-radius: 15px !important;
        margin: 10px auto !important;
        padding: 15px !important;
        color: white !important;
        max-width: 580px !important;
        width: 100% !important;
        box-sizing: border-box !important;
        backdrop-filter: blur(10px) !important;
    }
    
    /* Mensagem do usuário - estilo diferenciado */
    .stChatMessage[data-testid="chat-message-human"] {
        background: rgba(143, 209, 79, 0.1) !important;
        border: 1px solid rgba(143, 209, 79, 0.4) !important;
        border-left: 4px solid #8FD14F !important;
    }
    
    /* Mensagem da IA - estilo diferenciado */
    .stChatMessage[data-testid="chat-message-ai"] {
        background: rgba(30, 30, 30, 0.4) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-left: 4px solid #888 !important;
    }
    
    /* Avatar das mensagens */
    .stChatMessage .stChatMessageAvatar {
        background-color: transparent !important;
    }
    
    /* Conteúdo das mensagens - sem fundo */
    .stChatMessage .stMarkdown,
    .stChatMessage p,
    .stChatMessage div {
        background-color: transparent !important;
        color: white !important;
    }
    
    /* CHAT INPUT - CENTRALIZADO DINÂMICO */
    [data-testid="stChatInput"] {
        background-color: rgba(0, 0, 0, 0.95) !important;
        border-top: 2px solid #333 !important;
        position: fixed !important;
        bottom: 0 !important;
        left: 0 !important;
        right: 0 !important;
        padding: 15px !important;
        z-index: 1000 !important;
        display: flex !important;
        justify-content: center !important;
    }
    
    /* Ajustar input quando sidebar aberta */
    .stApp:has(section[data-testid="stSidebar"][aria-expanded="true"]) [data-testid="stChatInput"] {
        left: 280px !important;
    }
    
    /* Container do input sempre centralizado */
    [data-testid="stChatInput"] > div {
        width: 100% !important;
        max-width: 600px !important;
        margin: 0 auto !important;
    }
    
    .stChatInput > div > div > div > div > div {
        background-color: rgba(30, 30, 30, 0.95) !important;
        border: 2px solid #8FD14F !important;
        border-radius: 25px !important;
        padding: 5px 15px !important;
    }
    
    .stChatInput input {
        background-color: transparent !important;
        color: white !important;
        border: none !important;
        font-size: 16px !important;
        padding: 10px !important;
    }
    
    .stChatInput input::placeholder {
        color: #aaa !important;
    }
    
    .stChatInput button {
        background-color: #8FD14F !important;
        color: #000 !important;
        border: none !important;
        border-radius: 20px !important;
        padding: 8px 15px !important;
        font-weight: bold !important;
    }
    
    /* COLUNAS - LAYOUT FLEXÍVEL */
    .main [data-testid="column"] {
        background-color: transparent !important;
        padding: 5px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
    
    /* IMAGEM LOGO */
    .main img {
        max-width: 80px !important;
        height: auto !important;
        border-radius: 10px !important;
    }
    
    /* SCROLLBAR CUSTOMIZADA */
    ::-webkit-scrollbar {
        width: 8px;
        background-color: #000000;
    }
    
    ::-webkit-scrollbar-track {
        background-color: #333;
    }
    
    ::-webkit-scrollbar-thumb {
        background-color: #8FD14F;
        border-radius: 4px;
    }
    
    /* RESPONSIVIDADE */
    @media (max-width: 768px) {
        [data-testid="stChatInput"] {
            left: 0 !important;
        }
        
        .main h1 {
            font-size: 2rem !important;
        }
        
        .stChatMessage {
            max-width: 95% !important;
        }
        
        section[data-testid="stSidebar"] {
            width: 250px !important;
            min-width: 250px !important;
            max-width: 250px !important;
        }
    }
    
    /* FORÇA FUNDO PRETO ÚLTIMO RECURSO */
    body, html {
        background-color: #000000 !important;
    }
    
    .stApp::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: #000000;
        z-index: -999;
    }
    </style>
    """, unsafe_allow_html=True)

def pagina_chat():
    # Adicionar CSS customizado
    adicionar_css_customizado()
    
    # IMAGEM DO CÉREBRO - SEM TRANSPARÊNCIA
    brain_loaded = False
    try:
        if os.path.exists("cerebro_ia.png"):
            with open("cerebro_ia.png", "rb") as img_file:
                import base64
                img_data = img_file.read()
                img_base64 = base64.b64encode(img_data).decode()
                
                # Inserir imagem do cérebro SEM transparência
                st.markdown(f"""
                <div style="position: fixed; right: 50px; top: 50%; transform: translateY(-50%); 
                           width: 350px; height: 400px; opacity: 1.0; z-index: -1; 
                           pointer-events: none; background-size: contain; 
                           background-repeat: no-repeat; background-position: center;
                           background-image: url(data:image/png;base64,{img_base64});">
                </div>
                """, unsafe_allow_html=True)
                brain_loaded = True
                print("✅ Imagem cerebro_ia.png carregada SEM transparência!")
        else:
            print("❌ Arquivo cerebro_ia.png não encontrado")
    except Exception as e:
        print(f"❌ Erro ao carregar cerebro_ia.png: {e}")
    
    # Fallback se não carregou a imagem real - TAMBÉM SEM TRANSPARÊNCIA
    if not brain_loaded:
        print("🔄 Usando SVG como fallback SEM transparência")
        st.markdown("""
        <div style="position: fixed; right: 50px; top: 50%; transform: translateY(-50%); 
                   width: 350px; height: 400px; opacity: 1.0; z-index: -1; 
                   pointer-events: none;">
            <svg width="100%" height="100%" viewBox="0 0 400 400" xmlns="http://www.w3.org/2000/svg">
                <defs>
                    <radialGradient id="brainGlow" cx="50%" cy="50%" r="50%">
                        <stop offset="0%" style="stop-color:#8FD14F;stop-opacity:1.0"/>
                        <stop offset="100%" style="stop-color:#00FF41;stop-opacity:0.7"/>
                    </radialGradient>
                    <filter id="glow">
                        <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
                        <feMerge>
                            <feMergeNode in="coloredBlur"/>
                            <feMergeNode in="SourceGraphic"/>
                        </feMerge>
                    </filter>
                </defs>
                
                <!-- Forma principal do cérebro -->
                <ellipse cx="200" cy="180" rx="120" ry="100" fill="none" stroke="#8FD14F" stroke-width="3" opacity="1.0" filter="url(#glow)"/>
                
                <!-- Hemisférios -->
                <path d="M100,150 Q150,100 200,120 Q250,100 300,150 Q280,200 200,180 Q120,200 100,150" 
                      fill="none" stroke="#8FD14F" stroke-width="2" opacity="0.8"/>
                
                <!-- Circunvoluções cerebrais -->
                <path d="M120,160 Q160,140 200,160 Q240,140 280,160" fill="none" stroke="#8FD14F" stroke-width="1.5" opacity="0.7"/>
                <path d="M130,180 Q170,160 210,180 Q250,160 290,180" fill="none" stroke="#8FD14F" stroke-width="1.5" opacity="0.7"/>
                <path d="M125,200 Q165,180 205,200 Q245,180 285,200" fill="none" stroke="#8FD14F" stroke-width="1.5" opacity="0.7"/>
                
                <!-- Conexões neurais -->
                <circle cx="160" cy="140" r="4" fill="#8FD14F" opacity="1.0"/>
                <circle cx="240" cy="140" r="4" fill="#8FD14F" opacity="1.0"/>
                <circle cx="200" cy="200" r="4" fill="#8FD14F" opacity="1.0"/>
                
                <!-- Linhas de conexão -->
                <line x1="160" y1="140" x2="240" y2="140" stroke="#8FD14F" stroke-width="1" opacity="0.6"/>
                <line x1="160" y1="140" x2="200" y2="200" stroke="#8FD14F" stroke-width="1" opacity="0.6"/>
                <line x1="240" y1="140" x2="200" y2="200" stroke="#8FD14F" stroke-width="1" opacity="0.6"/>
                
                <!-- Efeito de brilho central -->
                <circle cx="200" cy="180" r="80" fill="url(#brainGlow)" opacity="0.3"/>
                
                <!-- Partículas flutuantes -->
                <circle cx="150" cy="120" r="2" fill="#8FD14F" opacity="1.0">
                    <animate attributeName="opacity" values="1.0;0.4;1.0" dur="3s" repeatCount="indefinite"/>
                </circle>
                <circle cx="250" cy="120" r="2" fill="#8FD14F" opacity="0.8">
                    <animate attributeName="opacity" values="0.8;0.3;0.8" dur="2.5s" repeatCount="indefinite"/>
                </circle>
                <circle cx="200" cy="100" r="2" fill="#8FD14F" opacity="0.9">
                    <animate attributeName="opacity" values="0.9;0.4;0.9" dur="2s" repeatCount="indefinite"/>
                </circle>
            </svg>
        </div>
        """, unsafe_allow_html=True)
    
    # Header com logo e título
    col1, col2 = st.columns([1, 4])
    
    with col1:
        try:
            if os.path.exists("logo_provion.png"):
                st.image("logo_provion.png", width=80)
            else:
                st.markdown("""
                <div style="width: 80px; height: 60px; background: linear-gradient(45deg, #8FD14F, #00FF41); 
                            border-radius: 10px; display: flex; align-items: center; justify-content: center; 
                            font-size: 2rem; font-weight: bold; color: black;">P</div>
                """, unsafe_allow_html=True)
        except:
            st.markdown("""
            <div style="width: 80px; height: 60px; background: linear-gradient(45deg, #8FD14F, #00FF41); 
                        border-radius: 10px; display: flex; align-items: center; justify-content: center; 
                        font-size: 2rem; font-weight: bold; color: black;">P</div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("# ProV.ia")
    
    # Mensagem de boas-vindas
    st.markdown("""
    <div style="background: rgba(0, 0, 0, 0.8); color: #8FD14F; padding: 15px; 
                border-radius: 15px; text-align: center; font-weight: bold; 
                margin: 20px auto; max-width: 550px; border: 2px solid #8FD14F; 
                text-shadow: 0 0 10px #8FD14F;">
        Sou sua assistente para assuntos internos, dúvidas e questionamentos sobre a Provion
    </div>
    """, unsafe_allow_html=True)

    # Inicializar ProV.ia automaticamente
    if 'chain' not in st.session_state:
        st.session_state['chain'] = inicializar_provia_padrao()

    chain = st.session_state['chain']
    memoria = st.session_state.get('memoria', MEMORIA)
    
    # Exibir histórico de conversas
    for mensagem in memoria.buffer_as_messages:
        with st.chat_message(mensagem.type):
            st.markdown(mensagem.content)

    # Input do usuário
    input_usuario = st.chat_input('Fale com o ProV.ia', key="provia_chat_input_unique")
    if input_usuario:
        # Mostrar mensagem do usuário
        with st.chat_message('human'):
            st.markdown(input_usuario)

        # Gerar e mostrar resposta da IA
        with st.chat_message('ai'):
            resposta = st.write_stream(chain.stream({
                'input': input_usuario, 
                'chat_history': memoria.buffer_as_messages
                }))
        
        # Adicionar à memória
        memoria.chat_memory.add_user_message(input_usuario)
        memoria.chat_memory.add_ai_message(resposta)
        st.session_state['memoria'] = memoria
        
        # Rerun para atualizar
        st.rerun()

def listar_arquivos_salvos():
    """Lista arquivos salvos no diretório de uploads"""
    arquivos = []
    if os.path.exists(UPLOAD_DIR):
        for arquivo in os.listdir(UPLOAD_DIR):
            caminho_completo = os.path.join(UPLOAD_DIR, arquivo)
            if os.path.isfile(caminho_completo):
                arquivos.append(arquivo)
    return arquivos

def sidebar():
    st.sidebar.title("⚙️ Configurações do ProV.ia")
    
    # Seção de Upload de Arquivos
    st.sidebar.subheader("📁 Upload de Documentos")
    tipo_arquivo = st.sidebar.selectbox('Tipo de documento', TIPOS_ARQUIVOS_VALIDOS)
    
    arquivo = None
    if tipo_arquivo == 'Site':
        arquivo = st.sidebar.text_input('URL do site')
    elif tipo_arquivo == 'Youtube':
        arquivo = st.sidebar.text_input('URL do vídeo YouTube')
    elif tipo_arquivo == 'Pdf':
        arquivo = st.sidebar.file_uploader('Upload arquivo PDF', type=['pdf'])
    elif tipo_arquivo == 'Csv':
        arquivo = st.sidebar.file_uploader('Upload arquivo CSV', type=['csv'])
    elif tipo_arquivo == 'Txt':
        arquivo = st.sidebar.file_uploader('Upload arquivo TXT', type=['txt'])
    
    # Botão para processar documento
    if st.sidebar.button('🚀 Processar Documento', use_container_width=True):
        if not arquivo:
            st.sidebar.error('Por favor, selecione um documento!')
        else:
            # Usar spinner normal em vez de sidebar.spinner
            with st.spinner('Processando documento...'):
                try:
                    inicializar_provia(tipo_arquivo, arquivo)
                    st.sidebar.success('Documento processado! ProV.ia atualizado com as novas informações.')
                except Exception as e:
                    st.sidebar.error(f'Erro ao processar documento: {str(e)}')
    
    st.sidebar.markdown("---")
    
    # Seção de Arquivos Salvos
    st.sidebar.subheader("💾 Arquivos Armazenados")
    arquivos_salvos = listar_arquivos_salvos()
    if arquivos_salvos:
        st.sidebar.write(f"Total de arquivos: {len(arquivos_salvos)}")
        with st.sidebar.expander("Ver arquivos salvos"):
            for arquivo in arquivos_salvos[-10:]:  # Mostrar últimos 10
                st.write(f"📄 {arquivo}")
    else:
        st.sidebar.write("Nenhum arquivo salvo ainda")
    
    # Botão para limpar histórico
    if st.sidebar.button('🗑️ Limpar Histórico', use_container_width=True):
        st.session_state['memoria'] = ConversationBufferMemory()
        st.sidebar.success('Histórico limpo!')
    
    # Informações do modelo
    st.sidebar.markdown("---")
    st.sidebar.subheader("🤖 Modelo Ativo")
    st.sidebar.info(f"**Modelo:** {MODELO_FIXO}\n**Provider:** OpenAI\n**Status:** ✅ Configurado")

def main():
    # Configurar página
    st.set_page_config(
        page_title="ProV.ia - Assistente Inteligente",
        page_icon="🧠",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Limpar estado para evitar duplicações
    if 'app_clean' not in st.session_state:
        # Limpar tudo exceto algumas chaves essenciais
        keys_to_keep = ['app_clean', 'chain', 'memoria']
        for key in list(st.session_state.keys()):
            if key not in keys_to_keep:
                del st.session_state[key]
        st.session_state['app_clean'] = True
    
    # Sidebar
    sidebar()
    
    # Página principal
    pagina_chat()

if __name__ == '__main__':
    main()