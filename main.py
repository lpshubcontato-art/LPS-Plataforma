import streamlit as st
import pandas as pd

# Configuração da Página
st.set_page_config(
    page_title="Liderança Psicanalítica",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo Global Simplificado e Direto
st.markdown("""
    <style>
    /* Fundo da Página */
    .stApp {
        background-color: #F5F5F5 !important;
    }
    
    /* Texto Principal */
    .stApp, .stApp p, .stApp li, .stApp label {
        color: #0D3B66 !important;
    }
    
    /* Títulos */
    h1, h2, h3, h4, h5, h6 {
        color: #0D3B66 !important;
    }

    /* ESTILO DOS BOTÕES - REQUISIÇÃO EXPLICITA */
    div.stButton > button {
        background-color: #0D3B66 !important;
        color: white !important;
        border-radius: 8px !important;
        border: none !important;
        padding: 0.5rem 1rem !important;
        width: 100% !important;
        display: block !important;
    }

    /* EFEITO HOVER */
    div.stButton > button:hover {
        background-color: #F4D35E !important;
        color: #0D3B66 !important;
    }

    /* Ajustes na Sidebar */
    [data-testid="stSidebar"] {
        background-color: #0D3B66 !important;
    }
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    /* Botões na Sidebar seguem o mesmo padrão */
    [data-testid="stSidebar"] div.stButton > button {
        background-color: transparent !important;
        border: 1px solid rgba(255,255,255,0.3) !important;
    }
    [data-testid="stSidebar"] div.stButton > button:hover {
        background-color: #F4D35E !important;
        color: #0D3B66 !important;
    }
    </style>
""", unsafe_allow_html=True)

# Inicialização do Estado de Sessão
if 'page' not in st.session_state:
    st.session_state.page = "Home"

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

# --- Conteúdo Principal ---
page = st.session_state.page

if page == "Home":
    st.title("Transforme Sua Liderança com a Ciência do Inconsciente")
    st.subheader("Descubra como a psicanálise e a neurociência podem revolucionar sua capacidade de liderar")
    st.video("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("**Redução de Conflitos**\n\nEntenda as dinâmicas ocultas.")
    with col2:
        st.info("**Menor Turnover**\n\nRetenha talentos humanos.")
    with col3:
        st.info("**Liderança Consciente**\n\nVisão sistêmica e autêntica.")

elif page == "Sobre":
    st.title("Sobre a Plataforma")
    st.markdown("### Viviane Nishiura")
    st.write("**Psicóloga clínica**, formada pela Mackenzie e especialista pelo IPq-HC FMUSP.")
    st.write("A Liderança Psicanalítica (LPS) une psicanálise e neurociência à gestão corporativa.")

elif page == "LPS Curso":
    st.title("LPS Curso")
    st.markdown("""
    1. **Neurociência**
    2. **Inconsciente**
    3. **Transferência**
    4. **Autoconsciência**
    5. **Entendendo a Equipe**
    6. **Aplicação Prática**
    """)
    st.button("Inscrever-se no Curso")

elif page == "LPSTest":
    st.title("LPSTest")
    st.write("O LPSTest revela as forças inconscientes que moldam seu estilo de liderança.")
    st.button("Iniciar Teste")

elif page == "LPSChat":
    st.title("LPSChat")
    st.write("Área da Inteligência Artificial para análise de equipe.")
    st.chat_input("Descreva a situação da equipe...")

elif page == "Mentoria":
    st.title("Mentoria")
    st.write("Informações sobre agendamento e sessões individuais.")
    st.button("Solicitar Agendamento")
