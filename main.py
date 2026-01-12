import streamlit as st
import pandas as pd

# Configuração da Página - Tema padrão
st.set_page_config(
    page_title="Liderança Psicanalítica",
    page_icon="🧠",
    layout="wide"
)

# Inicialização do Estado de Sessão para Navegação e Funcionalidades
if 'page' not in st.session_state:
    st.session_state.page = "Home"
if 'invite_sent' not in st.session_state:
    st.session_state.invite_sent = False
if 'show_employee_form' not in st.session_state:
    st.session_state.show_employee_form = False

# --- Sidebar de Navegação ---
st.sidebar.title("LPS")

if st.sidebar.button("Home"):
    st.session_state.page = "Home"
    st.session_state.show_employee_form = False
    st.rerun()

if st.sidebar.button("Sobre"):
    st.session_state.page = "Sobre"
    st.session_state.show_employee_form = False
    st.rerun()

if st.sidebar.button("LPS Curso"):
    st.session_state.page = "LPS Curso"
    st.session_state.show_employee_form = False
    st.rerun()

if st.sidebar.button("LPSTest"):
    st.session_state.page = "LPSTest"
    st.session_state.show_employee_form = False
    st.rerun()

if st.sidebar.button("LPSChat"):
    st.session_state.page = "LPSChat"
    st.session_state.show_employee_form = False
    st.rerun()

if st.sidebar.button("Mentoria"):
    st.session_state.page = "Mentoria"
    st.session_state.show_employee_form = False
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
    
    st.write("Deseja expandir os conhecimentos da sua equipe?")
    if st.button("Solicitar Acessos Adicionais", type="primary"):
        st.session_state.page = "Mentoria"
        st.rerun()

elif page == "LPSTest":
    st.title("LPSTest: Descubra os perfis e mova as peças como um jogo")
    st.write("""
    O LPSTest revela as forças inconscientes que moldam seu estilo de liderança. 
    Esta ferramenta ajuda gestores a resolver conflitos, alocar tarefas de forma mais estratégica 
    e compreender as peças do tabuleiro organizacional com clareza.
    """)
    
    st.divider()
    
    st.subheader("Área do Gestor")
    if st.button("Gerar Link para Funcionário"):
        st.session_state.show_employee_form = True

    if st.session_state.show_employee_form:
        with st.form("employee_invite_form"):
            email = st.text_input("E-mail do Funcionário")
            submit = st.form_submit_button("Enviar Convite", type="primary")
            if submit:
                if email:
                    st.session_state.invite_sent = True
                    st.session_state.show_employee_form = False
                    st.rerun()
                else:
                    st.error("Por favor, insira um e-mail válido.")

    if st.session_state.invite_sent:
        st.success("Convite enviado com sucesso!")
        st.info("Aviso: O resultado será enviado por e-mail ao funcionário e ficará disponível no dashboard do gestor assim que concluído.")
        if st.button("Enviar outro convite"):
            st.session_state.invite_sent = False
            st.session_state.show_employee_form = True
            st.rerun()

    st.divider()
    
    with st.form("lps_test_form"):
        st.subheader("Seu Assessment de Liderança")
        st.write("Responda ao formulário abaixo para sua autoavaliação:")
        q1 = st.slider("Quanto você centraliza decisões?", 0, 10, 5)
        q2 = st.slider("Como você lida com conflitos?", 0, 10, 5)
        st.form_submit_button("Enviar Minhas Respostas", type="primary")

elif page == "LPSChat":
    st.title("LPSChat")
    st.write("Área da Inteligência Artificial para análise de equipe.")
    st.chat_input("Digite sua mensagem...")

elif page == "Mentoria":
    st.title("Mentoria e Contato")
    st.write("Informações sobre agendamento e sessões individuais.")
    
    with st.form("contact_form"):
        st.write("Solicite acessos adicionais ou agende uma mentoria:")
        st.text_input("Nome")
        st.text_input("E-mail")
        st.text_area("Mensagem")
        st.form_submit_button("Enviar Solicitação", type="primary")
