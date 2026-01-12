import streamlit as st
import time
import pandas as pd
import numpy as np

# Configuração da Página
st.set_page_config(
    page_title="Liderança Psicanalítica",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Definição de Cores
COLOR_DARK_BLUE = "#0D3B66"
COLOR_GRAY = "#F5F5F5"
COLOR_GOLD = "#F4D35E"
COLOR_BLACK = "#000000"

# Estilos CSS Personalizados
st.markdown(f"""
    <style>
    /* Fundo Geral */
    .stApp {{
        background-color: {COLOR_GRAY};
    }}
    
    /* Cores de Texto Globais */
    .stApp, .stApp p, .stApp span, .stApp label, .stApp li {{
        color: {COLOR_BLACK} !important;
    }}
    
    /* Sidebar */
    [data-testid="stSidebar"] {{
        background-color: {COLOR_DARK_BLUE};
    }}
    [data-testid="stSidebar"] * {{
        color: white !important;
    }}
    
    /* Títulos e Cabeçalhos */
    h1, h2, h3, h4, h5, h6 {{
        color: {COLOR_DARK_BLUE} !important;
        font-family: 'Helvetica Neue', sans-serif;
    }}
    
    /* Botões na Sidebar */
    .stSidebar .stButton > button {{
        background-color: transparent;
        color: white !important;
        border: 1px solid rgba(255,255,255,0.3);
        width: 100%;
        text-align: left;
        margin-bottom: 5px;
    }}
    
    .stSidebar .stButton > button:hover {{
        border-color: {COLOR_GOLD};
        color: {COLOR_GOLD} !important;
    }}

    /* Botões Principais (Dourados) */
    .main .stButton > button {{
        background-color: {COLOR_GOLD} !important;
        color: {COLOR_DARK_BLUE} !important;
        font-weight: bold;
        border: none;
        border-radius: 5px;
    }}

    /* Card Personalizado */
    .custom-card {{
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border-left: 5px solid {COLOR_GOLD};
        margin-bottom: 20px;
    }}
    
    .custom-card h3, .custom-card p {{
        color: {COLOR_DARK_BLUE} !important;
    }}

    /* Forçar cor preta em widgets específicos */
    .stMarkdown div p {{
        color: {COLOR_BLACK} !important;
    }}
    </style>
""", unsafe_allow_html=True)

# Inicialização do Estado de Sessão
if 'page' not in st.session_state:
    st.session_state.page = "Home"
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'messages' not in st.session_state:
    st.session_state.messages = []

# --- Sidebar de Navegação ---
st.sidebar.title("🧠 LPS")
st.sidebar.markdown("---")

if st.sidebar.button("🏠 Home"):
    st.session_state.page = "Home"
    st.rerun()

if st.sidebar.button("👤 Sobre"):
    st.session_state.page = "Sobre"
    st.rerun()

if st.sidebar.button("📚 LPS Curso"):
    st.session_state.page = "LPS Curso"
    st.rerun()

if st.sidebar.button("📊 LPSTest"):
    st.session_state.page = "LPSTest"
    st.rerun()

if st.sidebar.button("💬 LPSChat"):
    st.session_state.page = "LPSChat"
    st.rerun()

if st.sidebar.button("🤝 Mentoria"):
    st.session_state.page = "Mentoria"
    st.rerun()

st.sidebar.markdown("---")

# Área do Gestor
if not st.session_state.logged_in:
    st.sidebar.subheader("Área do Gestor")
    user = st.sidebar.text_input("Usuário")
    pw = st.sidebar.text_input("Senha", type="password")
    if st.sidebar.button("Entrar"):
        if user == "admin" and pw == "admin":
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.sidebar.error("Erro!")
else:
    st.sidebar.success("Logado")
    if st.sidebar.button("Sair"):
        st.session_state.logged_in = False
        st.rerun()

# --- Conteúdo Principal ---
page = st.session_state.page

if page == "Home":
    st.markdown("<div style='text-align: center; padding: 20px;'>", unsafe_allow_html=True)
    st.title("Transforme Sua Liderança com a Ciência do Inconsciente")
    st.markdown(f"<h3 style='color: {COLOR_GOLD} !important;'>Descubra como a psicanálise e a neurociência podem revolucionar sua capacidade de liderar</h3>", unsafe_allow_html=True)
    st.video("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    st.markdown("</div>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f'<div class="custom-card"><h3>Redução de Conflitos</h3><p>Entenda as dinâmicas ocultas que geram atritos.</p></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="custom-card"><h3>Menor Turnover</h3><p>Retenha talentos compreendendo necessidades humanas.</p></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="custom-card"><h3>Liderança Consciente</h3><p>Desenvolva uma visão sistêmica e autêntica.</p></div>', unsafe_allow_html=True)

elif page == "Sobre":
    st.title("Sobre a Plataforma")
    st.markdown(f"""
    <div class="custom-card">
    <h3>Viviane Nishiura</h3>
    <p><b>Psicóloga clínica</b>, formada pela Mackenzie e especialista pelo IPq-HC FMUSP.</p>
    <p>A Liderança Psicanalítica (LPS) une psicanálise e neurociência à gestão corporativa.</p>
    </div>
    """, unsafe_allow_html=True)
    st.image("https://placehold.co/800x400/0D3B66/F4D35E?text=Viviane+Nishiura+LPS")

elif page == "LPS Curso":
    st.title("LPS Curso")
    st.markdown("""
    ### Módulos do Programa:
    1. **Neurociência**
    2. **Inconsciente**
    3. **Transferência**
    4. **Autoconsciência**
    5. **Entendendo a Equipe**
    6. **Aplicação Prática**
    """)
    st.button("Inscrever-se")

elif page == "LPSTest":
    st.title("LPSTest")
    st.markdown('<div class="custom-card"><p>O <b>LPSTest</b> revela as forças inconscientes que moldam seu estilo de liderança.</p></div>', unsafe_allow_html=True)
    st.slider("Centralização", 0, 10, 5)
    st.button("Resultado")

elif page == "LPSChat":
    st.title("LPSChat")
    st.write("Análise de equipe via IA.")
    if prompt := st.chat_input("Diga algo..."):
        st.chat_message("user").write(prompt)
        st.chat_message("assistant").write("Análise psicanalítica processada...")

elif page == "Mentoria":
    st.title("Mentoria")
    st.write("Agende sua sessão individual.")
    st.date_input("Data")
    st.button("Agendar")
