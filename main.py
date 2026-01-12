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

# Estilos CSS Personalizados
st.markdown(f"""
    <style>
    /* Fundo Geral */
    .stApp {{
        background-color: {COLOR_GRAY};
    }}
    
    /* Sidebar */
    [data-testid="stSidebar"] {{
        background-color: {COLOR_DARK_BLUE};
    }}
    [data-testid="stSidebar"] * {{
        color: white !important;
    }}
    
    /* Títulos e Cabeçalhos */
    h1, h2, h3 {{
        color: {COLOR_DARK_BLUE};
        font-family: 'Helvetica Neue', sans-serif;
    }}
    
    /* Botões */
    .stButton > button {{
        background-color: {COLOR_GOLD};
        color: {COLOR_DARK_BLUE};
        font-weight: bold;
        border: none;
        border-radius: 5px;
        width: 100%;
    }}
    .stButton > button:hover {{
        background-color: #e0c255;
        color: {COLOR_DARK_BLUE};
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
    </style>
""", unsafe_allow_html=True)

# Inicialização do Estado de Sessão
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'page' not in st.session_state:
    st.session_state.page = "Home"
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Funções de navegação
def set_page(page_name):
    st.session_state.page = page_name

# --- Sidebar de Navegação ---
with st.sidebar:
    st.title("🧠 LPS")
    st.markdown("---")
    
    # Menu de Navegação usando botões para garantir funcionamento
    st.subheader("Menu")
    if st.button("🏠 Home", key="btn_home"): set_page("Home")
    if st.button("👤 Sobre", key="btn_sobre"): set_page("Sobre")
    if st.button("📚 LPS Curso", key="btn_curso"): set_page("LPS Curso")
    if st.button("📊 LPSTest", key="btn_test"): set_page("LPSTest")
    if st.button("💬 LPSChat", key="btn_chat"): set_page("LPSChat")
    if st.button("🤝 Mentoria", key="btn_mentoria"): set_page("Mentoria")
    
    st.markdown("---")
    
    # Área do Gestor
    if not st.session_state.logged_in:
        st.subheader("Área do Gestor")
        username = st.text_input("Usuário", key="login_user")
        password = st.text_input("Senha", type="password", key="login_pass")
        if st.button("Entrar", key="btn_login"):
            if username == "admin" and password == "admin":
                st.session_state.logged_in = True
                st.success("Logado com sucesso!")
                st.rerun()
            else:
                st.error("Credenciais inválidas")
    else:
        st.success(f"Bem-vindo, Gestor!")
        if st.button("Sair", key="btn_logout"):
            st.session_state.logged_in = False
            st.rerun()

# --- Conteúdo Principal ---
selection = st.session_state.page

if selection == "Home":
    st.markdown("<div style='text-align: center; padding: 20px;'>", unsafe_allow_html=True)
    st.title("Transforme Sua Liderança com a Ciência do Inconsciente")
    st.markdown(f"<h3 style='color: {COLOR_GOLD};'>Descubra como a psicanálise e a neurociência podem revolucionar sua capacidade de liderar</h3>", unsafe_allow_html=True)
    
    # Adicionando Vídeo (Placeholder do YouTube conforme solicitado)
    st.video("https://www.youtube.com/watch?v=dQw4w9WgXcQ") # Substituir pelo vídeo real do PDF
    st.markdown("</div>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""<div class="custom-card"><h3>Redução de Conflitos</h3><p>Entenda as dinâmicas ocultas que geram atritos e aprenda a mediá-los com eficácia.</p></div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""<div class="custom-card"><h3>Menor Turnover</h3><p>Retenha talentos através de uma gestão que compreende as necessidades humanas reais.</p></div>""", unsafe_allow_html=True)
    with col3:
        st.markdown(f"""<div class="custom-card"><h3>Liderança Consciente</h3><p>Desenvolva uma visão sistêmica e autêntica do seu papel como gestor.</p></div>""", unsafe_allow_html=True)

elif selection == "Sobre":
    st.title("Sobre a Plataforma")
    st.markdown(f"""
    <div class="custom-card">
    <h3>Viviane Nishiura</h3>
    <p><b>Psicóloga clínica</b>, formada pela Mackenzie e especialista pelo IPq-HC FMUSP.</p>
    <p>A Liderança Psicanalítica (LPS) é uma metodologia inovadora que une os conceitos da psicanálise e neurociência à gestão corporativa moderna. 
    Com vasta experiência clínica e corporativa, Viviane desenvolveu o LPS para humanizar e potencializar a liderança através da compreensão do inconsciente.</p>
    </div>
    """, unsafe_allow_html=True)
    st.image("https://placehold.co/800x400/0D3B66/F4D35E?text=Viviane+Nishiura+LPS", caption="Viviane Nishiura - Especialista em Liderança")

elif selection == "LPS Curso":
    st.title("LPS Curso: Módulos do Programa")
    st.info("Inscrições abertas para a próxima turma!")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("""
        ### Estrutura do Curso:
        1. **Neurociência:** As bases biológicas do comportamento e decisão.
        2. **Inconsciente:** O que motiva as ações além da superfície.
        3. **Transferência:** A dinâmica das relações entre líder e liderado.
        4. **Autoconsciência:** O mergulho do líder em sua própria psique.
        5. **Entendendo a Equipe:** Leitura de grupo e clima organizacional.
        6. **Aplicação Prática:** Transformando teoria em resultados reais.
        """)
    with col2:
        st.markdown(f"""<div class="custom-card" style="text-align: center;"><h2>R$ 1.997,00</h2><p>ou 12x de R$ 199,70</p></div>""", unsafe_allow_html=True)
        st.button("Quero me inscrever", key="btn_inscrever")

elif selection == "LPSTest":
    st.title("LPSTest: Assessments de Perfil")
    st.markdown("""
    <div class="custom-card">
    <p>O <b>LPSTest</b> revela as forças inconscientes que moldam seu estilo de liderança.</p>
    <p>Através de assessments baseados em psicanálise corporativa, identificamos padrões de comportamento, 
    mecanismos de defesa e potenciais de liderança que muitas vezes permanecem ocultos no dia a dia organizacional.</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.expander("Iniciar Assessment Rápido"):
        q1 = st.slider("Quanto você centraliza decisões?", 0, 10, 5)
        q2 = st.slider("Como você lida com conflitos?", 0, 10, 5)
        q3 = st.slider("Nível de abertura a novas ideias", 0, 10, 5)
        if st.button("Gerar Resultado", key="btn_result"):
            st.success("Análise concluída!")
            chart_data = pd.DataFrame({"Competência": ["Centralização", "Resolução", "Inovação"], "Nível": [q1, q2, q3]})
            st.bar_chart(chart_data, x="Competência", y="Nível")

elif selection == "LPSChat":
    st.title("LPSChat: Inteligência Artificial para Análise de Equipe")
    st.markdown("""
    <div class="custom-card">
    <p>Utilize nossa IA especializada para analisar dinâmicas de grupo, feedbacks e comportamentos da sua equipe sob a ótica da psicanálise.</p>
    </div>
    """, unsafe_allow_html=True)
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Descreva uma situação da sua equipe para análise..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            response = f"Analisando a situação '{prompt}' sob a ótica da transferência: parece haver um padrão de repetição inconsciente. Como a equipe reage à sua autoridade nesse momento?"
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

elif selection == "Mentoria":
    st.title("Mentoria e Agendamento")
    st.markdown("""
    <div class="custom-card">
    <h3>Sessões Individuais</h3>
    <p>Acelere seu desenvolvimento com acompanhamento personalizado focado nos seus desafios específicos de gestão.</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.date_input("Escolha uma data disponível")
    with col2:
        st.time_input("Escolha um horário")
    st.button("Solicitar Agendamento de Mentoria", key="btn_mentor")
