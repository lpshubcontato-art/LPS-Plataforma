import streamlit as st
import pandas as pd
import os

# Configuração da Página - Tema LPS (Azul Marinho #0D3B66 e Dourado #F4D35E)
st.set_page_config(
    page_title="Liderança Psicanalítica",
    page_icon="🧠",
    layout="wide"
)

# Estilização Customizada para Cores Azul Marinho e Dourado
st.markdown("""
    <style>
    /* Azul Marinho #0D3B66 e Dourado #F4D35E */
    :root {
        --primary-blue: #0D3B66;
        --accent-gold: #F4D35E;
        --bg-gray: #F5F5F5;
    }
    
    .main {
        background-color: var(--bg-gray);
    }
    
    h1, h2, h3 {
        color: var(--primary-blue) !important;
    }
    
    .stButton>button {
        background-color: var(--primary-blue);
        color: white;
        border-radius: 8px;
        border: 2px solid var(--accent-gold);
    }
    
    .stDownloadButton>button {
        background-color: var(--accent-gold);
        color: var(--primary-blue);
        font-weight: bold;
        border-radius: 8px;
        border: none;
    }

    div[data-testid="stExpander"] {
        border: 1px solid var(--primary-blue);
        border-radius: 8px;
        background-color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# Inicialização do Estado de Sessão
if 'page' not in st.session_state:
    st.session_state.page = "Home"

# URL do WhatsApp Oficial
WHATSAPP_URL = "https://wa.me/5511971419453"
OFFICIAL_EMAIL = "contato@liderancapsicanalitica.com"

# Mapeamento de Módulos (8 Módulos conforme solicitado)
# Incluindo IDs fictícios do Vimeo para os vídeos (serão substituídos pelos reais do usuário)
MODULES = [
    {"id": 0, "name": "Introdução", "file": "attached_assets/introdução_1768431876966.pdf", "vimeo_id": "824804225"},
    {"id": 1, "name": "Neurociência", "file": "attached_assets/Módulo_1_1768431876967.pdf", "vimeo_id": "824804225"},
    {"id": 2, "name": "Psicanálise", "file": "attached_assets/Módulo_2_1768431876968.pdf", "vimeo_id": "824804225"},
    {"id": 3, "name": "Transferência", "file": "attached_assets/Módulo_3_1768431876969.pdf", "vimeo_id": "824804225"},
    {"id": 4, "name": "Inconsciente Coletivo", "file": "attached_assets/Módulo_4_1768431876970.pdf", "vimeo_id": "824804225"},
    {"id": 5, "name": "Autoconsciência", "file": "attached_assets/Módulo_5_1768431876971.pdf", "vimeo_id": "824804225"},
    {"id": 6, "name": "Mapeamento da Equipe", "file": "attached_assets/Módulo_6_1768431876972.pdf", "vimeo_id": "824804225"},
    {"id": 7, "name": "Interpretação dos Arquétipos", "file": "attached_assets/Módulo_7_1768431876973.pdf", "vimeo_id": "824804225"},
]

# --- Sidebar de Navegação ---
st.sidebar.title("LPS Platform")

if st.sidebar.button("🏠 Home"):
    st.session_state.page = "Home"
    st.rerun()

if st.sidebar.button("🎓 LPS Curso"):
    st.session_state.page = "LPS Curso"
    st.rerun()

if st.sidebar.button("📝 LPSTest"):
    st.session_state.page = "LPSTest"
    st.rerun()

if st.sidebar.button("👤 Sobre"):
    st.session_state.page = "Sobre"
    st.rerun()

if st.sidebar.button("📞 Contato"):
    st.session_state.page = "Mentoria"
    st.rerun()

# --- Conteúdo Principal ---
page = st.session_state.page

if page == "Home":
    st.title("Transforme Sua Liderança com a Ciência do Inconsciente")
    st.write("Bem-vindo à plataforma de Liderança Psicanalítica (LPS).")
    
    st.video("https://vimeo.com/824804225") # Vídeo de boas vindas
    
    st.markdown(f'<a href="{WHATSAPP_URL}" target="_blank"><button style="background-color:#25D366; color:white; border:none; padding:12px 24px; border-radius:8px; cursor:pointer; font-weight:bold; font-size:16px; margin-top:10px;">Falar com a Consultora no WhatsApp</button></a>', unsafe_allow_html=True)
    
    st.subheader("O que você encontrará aqui:")
    st.write("- **Metodologia Exclusiva**: Unindo neurociência e psicanálise.")
    st.write("- **Autoconhecimento**: Identificação de arquétipos de liderança.")
    st.write("- **Gestão Estratégica**: Ferramentas para mapeamento de equipe.")

elif page == "LPS Curso":
    st.title("🎓 Programa LPS: Módulos do Curso")
    st.info("Abaixo estão os 8 módulos que compõem sua jornada de liderança.")
    
    for mod in MODULES:
        with st.expander(f"Módulo {mod['id']}: {mod['name']}"):
            # Vídeo do Vimeo
            vimeo_url = f"https://vimeo.com/{mod['vimeo_id']}"
            st.video(vimeo_url)
            
            st.write(f"Material complementar para o {mod['name']}:")
            
            # Botão de Download PDF
            if os.path.exists(mod['file']):
                with open(mod['file'], "rb") as f:
                    st.download_button(
                        label=f"⬇️ Baixar PDF - {mod['name']}",
                        data=f,
                        file_name=f"LPS_{mod['name'].replace(' ', '_')}.pdf",
                        mime="application/pdf",
                        key=f"dl_mod_{mod['id']}"
                    )
            else:
                st.warning("Arquivo PDF em processamento.")

elif page == "LPSTest":
    st.title("📝 LPSTest Assessment")
    st.write("Realize o mapeamento de perfil e arquétipos.")
    st.markdown(f'<a href="{WHATSAPP_URL}" target="_blank"><button style="background-color:#25D366; color:white; border:none; padding:10px 20px; border-radius:5px; cursor:pointer; font-weight:bold;">Solicitar Acesso Completo no WhatsApp</button></a>', unsafe_allow_html=True)

elif page == "Sobre":
    st.title("Sobre Viviane Nishiura")
    st.write("Psicóloga clínica e especialista em comportamento organizacional.")

elif page == "Mentoria":
    st.title("📞 Contato e Mentoria")
    st.write(f"E-mail: {OFFICIAL_EMAIL}")
    st.write("WhatsApp: +55 11 97141-9453")
    st.markdown(f'<a href="{WHATSAPP_URL}" target="_blank"><button style="background-color:#25D366; color:white; border:none; padding:12px 24px; border-radius:8px; cursor:pointer; font-weight:bold;">Chamar no WhatsApp</button></a>', unsafe_allow_html=True)
