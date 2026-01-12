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

# Estado de Sessão para Login
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# --- Sidebar de Navegação ---
with st.sidebar:
    st.title("🧠 LPS")
    st.markdown("---")
    
    menu_options = ["Home", "Sobre", "LPS Curso", "LPSTest", "LPSChat", "Mentoria"]
    selection = st.radio("Navegação", menu_options, label_visibility="collapsed")
    
    st.markdown("---")
    
    # Botão de Login Simples
    if not st.session_state.logged_in:
        st.subheader("Área do Gestor")
        username = st.text_input("Usuário", key="login_user")
        password = st.text_input("Senha", type="password", key="login_pass")
        if st.button("Entrar"):
            if username == "admin" and password == "admin":  # Mock login
                st.session_state.logged_in = True
                st.success("Logado com sucesso!")
                time.sleep(1)
                st.rerun()
            else:
                st.error("Credenciais inválidas")
    else:
        st.success(f"Bem-vindo, Gestor!")
        if st.button("Sair"):
            st.session_state.logged_in = False
            st.rerun()

# --- Conteúdo Principal ---

if selection == "Home":
    st.markdown("<div style='text-align: center; padding: 50px;'>", unsafe_allow_html=True)
    st.title("Transforme Sua Liderança com a Ciência do Inconsciente")
    st.markdown(f"<h3 style='color: {COLOR_GOLD};'>Descubra como a psicanálise e a neurociência podem revolucionar sua capacidade de liderar</h3>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="custom-card">
            <h3>Redução de Conflitos</h3>
            <p>Entenda as dinâmicas ocultas que geram atritos e aprenda a mediá-los com eficácia.</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown(f"""
        <div class="custom-card">
            <h3>Menor Turnover</h3>
            <p>Retenha talentos através de uma gestão que compreende as necessidades humanas reais.</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown(f"""
        <div class="custom-card">
            <h3>Liderança Consciente</h3>
            <p>Desenvolva uma visão sistêmica e autêntica do seu papel como gestor.</p>
        </div>
        """, unsafe_allow_html=True)

elif selection == "Sobre":
    st.title("Sobre a Plataforma")
    st.write("""
    A Liderança Psicanalítica (LPS) é uma metodologia inovadora que une os conceitos da psicanálise e neurociência à gestão corporativa moderna.
    
    **Sobre a Fundadora:**
    Viviane Nishiura é Psicóloga clínica, formada pela Mackenzie e especialista pelo IPq-HC FMUSP. Com vasta experiência clínica e corporativa, ela desenvolveu o LPS para humanizar e potencializar a liderança.
    """)
    st.image("https://placehold.co/800x400/0D3B66/F4D35E?text=Viviane+Nishiura+LPS", caption="Viviane Nishiura - Liderança Psicanalítica")

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
        st.markdown(f"""
        <div class="custom-card" style="text-align: center;">
            <h2>R$ 1.997,00</h2>
            <p>ou 12x de R$ 199,70</p>
        </div>
        """, unsafe_allow_html=True)
        st.button("Inscrever-se Agora")

elif selection == "LPSTest":
    st.title("LPSTest: Análise de Perfil")
    st.markdown("#### O LPSTest revela as forças inconscientes que moldam seu estilo de liderança")
    st.write("Responda ao questionário abaixo para iniciar sua jornada de descoberta.")
    
    with st.expander("Iniciar Teste Rápido"):
        q1 = st.slider("Quanto você centraliza decisões?", 0, 10, 5)
        q2 = st.slider("Como você lida com conflitos?", 0, 10, 5)
        q3 = st.slider("Nível de abertura a novas ideias", 0, 10, 5)
        
        if st.button("Gerar Resultado"):
            score = (q1 + q2 + q3) / 3
            st.success("Análise concluída!")
            
            chart_data = pd.DataFrame({
                "Competência": ["Centralização", "Resolução", "Inovação"],
                "Nível": [q1, q2, q3]
            })
            st.bar_chart(chart_data, x="Competência", y="Nível")
            
            if score > 7:
                st.write("**Perfil:** Líder Visionário (Dominância do Ego)")
            elif score > 4:
                st.write("**Perfil:** Líder Mediador (Equilíbrio Superego)")
            else:
                st.write("**Perfil:** Líder Analítico (Foco no Id)")

elif selection == "LPSChat":
    st.title("LPSChat 🤖")
    st.write("Converse com nossa IA treinada em psicanálise corporativa.")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Digite sua dúvida sobre liderança..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            response = f"Interessante sua questão sobre '{prompt}'. Na visão da liderança psicanalítica, devemos olhar para o que não é dito. O que isso representa para o inconsciente da sua equipe?"
            st.markdown(response)
        
        st.session_state.messages.append({"role": "assistant", "content": response})

elif selection == "Mentoria":
    st.title("Mentoria Executiva")
    st.write("Agende uma sessão individual com nossos especialistas.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.date_input("Escolha uma data")
    with col2:
        st.time_input("Escolha um horário")
    
    st.button("Solicitar Agendamento")
