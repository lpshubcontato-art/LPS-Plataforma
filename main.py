import streamlit as st
import pandas as pd
import os

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

# URL do WhatsApp Oficial
WHATSAPP_URL = "https://wa.me/5511971419453"
OFFICIAL_EMAIL = "contato@liderancapsicanalitica.com"

# Mapeamento de Módulos e PDFs
MODULES = [
    {"id": 1, "name": "Neurociência", "file": "attached_assets/Módulo_1_1768431876967.pdf"},
    {"id": 2, "name": "Psicanálise", "file": "attached_assets/Módulo_2_1768431876968.pdf"},
    {"id": 3, "name": "Transferência", "file": "attached_assets/Módulo_3_1768431876969.pdf"},
    {"id": 4, "name": "Inconsciente Coletivo", "file": "attached_assets/Módulo_4_1768431876970.pdf"},
    {"id": 5, "name": "Autoconsciência", "file": "attached_assets/Módulo_5_1768431876971.pdf"},
    {"id": 6, "name": "Mapeamento da Equipe", "file": "attached_assets/Módulo_6_1768431876972.pdf"},
]

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
    
    # Botão de WhatsApp visível abaixo do vídeo
    st.markdown(f'<a href="{WHATSAPP_URL}" target="_blank"><button style="background-color:#25D366; color:white; border:none; padding:12px 24px; border-radius:8px; cursor:pointer; font-weight:bold; font-size:16px; margin-top:10px;">Falar com a Consultora no WhatsApp</button></a>', unsafe_allow_html=True)
    
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
    st.info("Todas as opções de compra estão vinculadas à realização do Curso LPS")
    
    st.write("Explore os módulos do programa e baixe o material de apoio:")
    
    for mod in MODULES:
        with st.expander(f"Módulo {mod['id']}: {mod['name']}"):
            st.write(f"Conteúdo detalhado do Módulo {mod['id']}.")
            if os.path.exists(mod['file']):
                with open(mod['file'], "rb") as f:
                    st.download_button(
                        label=f"Baixar Material de Apoio (PDF) - Módulo {mod['id']}",
                        data=f,
                        file_name=f"LPS_Modulo_{mod['id']}_{mod['name'].replace(' ', '_')}.pdf",
                        mime="application/pdf",
                        key=f"dl_{mod['id']}"
                    )
            else:
                st.warning("Arquivo PDF não encontrado no servidor.")
    
    st.markdown(f'<a href="{WHATSAPP_URL}" target="_blank"><button style="background-color:#25D366; color:white; border:none; padding:10px 20px; border-radius:5px; cursor:pointer; font-weight:bold;">Falar com a Consultora no WhatsApp</button></a>', unsafe_allow_html=True)

elif page == "LPSTest":
    st.title("LPSTest: Descubra os perfis e mova as peças como um jogo")
    st.write("""
    O LPSTest revela as forças inconscientes que moldam seu estilo de liderança. 
    Esta ferramenta ajuda gestores a resolver conflitos, alocar tarefas de forma mais estratégica 
    e compreender as peças do tabuleiro organizacional com clareza.
    """)
    
    st.markdown(f'<a href="{WHATSAPP_URL}" target="_blank"><button style="background-color:#25D366; color:white; border:none; padding:10px 20px; border-radius:5px; cursor:pointer; font-weight:bold;">Solicitar Acessos via WhatsApp</button></a>', unsafe_allow_html=True)

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
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Informações de Contato")
        st.write(f"📞 WhatsApp: +55 11 97141-9453")
        st.write(f"📧 E-mail: {OFFICIAL_EMAIL}")
    
    with col2:
        with st.form("contact_form"):
            st.subheader("Envie uma mensagem")
            st.text_input("Nome")
            st.text_input("E-mail")
            st.text_area("Mensagem")
            st.form_submit_button("Enviar Solicitação", type="primary")
    
    st.markdown("---")
    st.write("Fale conosco agora mesmo:")
    st.markdown(f'<a href="{WHATSAPP_URL}" target="_blank"><button style="background-color:#25D366; color:white; border:none; padding:12px 24px; border-radius:8px; cursor:pointer; font-weight:bold; font-size:16px;">Falar com a Consultora no WhatsApp</button></a>', unsafe_allow_html=True)
