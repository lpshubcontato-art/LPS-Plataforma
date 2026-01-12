import streamlit as st
import pandas as pd

# Configuração da Página - Tema padrão
st.set_page_config(
    page_title="Liderança Psicanalítica",
    page_icon="🧠",
    layout="wide"
)

# Inicialização do Estado de Sessão para Navegação
if 'page' not in st.session_state:
    st.session_state.page = "Home"

# --- Sidebar de Navegação ---
st.sidebar.title("LPS")

if st.sidebar.button("Home"):
    st.session_state.page = "Home"
    st.rerun()

if st.sidebar.button("Sobre"):
    st.session_state.page = "Sobre"
    st.rerun()

if st.sidebar.button("LPS Curso"):
    st.session_state.page = "LPS Curso"
    st.rerun()

if st.sidebar.button("LPSTest"):
    st.session_state.page = "LPSTest"
    st.rerun()

if st.sidebar.button("LPSChat"):
    st.session_state.page = "LPSChat"
    st.rerun()

if st.sidebar.button("Mentoria"):
    st.session_state.page = "Mentoria"
    st.rerun()

# --- Conteúdo Principal ---
page = st.session_state.page

if page == "Home":
    st.title("Transforme Sua Liderança com a Ciência do Inconsciente")
    st.write("Descubra como a psicanálise e a neurociência podem revolucionar sua capacidade de liderar")
    
    # Placeholder de vídeo
    st.video("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    
    st.subheader("Benefícios")
    st.write("- **Redução de conflitos**: Entenda as dinâmicas ocultas.")
    st.write("- **Menor turnover**: Retenha talentos humanos.")
    st.write("- **Liderança consciente**: Visão sistêmica e autêntica.")

elif page == "Sobre":
    st.title("Sobre a Plataforma")
    st.subheader("Viviane Nishiura")
    st.write("Psicóloga clínica, formada pela Mackenzie e especialista pelo IPq-HC FMUSP.")
    st.write("A Liderança Psicanalítica (LPS) une psicanálise e neurociência à gestão corporativa moderna.")

elif page == "LPS Curso":
    st.title("LPS Curso")
    st.write("Módulos do Programa:")
    st.write("1. Neurociência")
    st.write("2. Inconsciente")
    st.write("3. Transferência")
    st.write("4. Autoconsciência")
    st.write("5. Entendendo a Equipe")
    st.write("6. Aplicação Prática")
    st.button("Inscrever-se no Curso", type="primary")

elif page == "LPSTest":
    st.title("LPSTest")
    st.write("O LPSTest revela as forças inconscientes que moldam seu estilo de liderança.")
    
    with st.form("lps_test_form"):
        st.write("Responda ao formulário abaixo:")
        q1 = st.slider("Quanto você centraliza decisões?", 0, 10, 5)
        q2 = st.slider("Como você lida com conflitos?", 0, 10, 5)
        st.form_submit_button("Enviar Respostas", type="primary")

elif page == "LPSChat":
    st.title("LPSChat")
    st.write("Área da Inteligência Artificial para análise de equipe.")
    st.chat_input("Digite sua mensagem...")

elif page == "Mentoria":
    st.title("Mentoria")
    st.write("Informações sobre agendamento e sessões individuais.")
    st.button("Solicitar Agendamento", type="primary")
