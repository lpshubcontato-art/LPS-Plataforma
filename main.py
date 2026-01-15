import streamlit as st
import os
import streamlit.components.v1 as components
from PIL import Image

# Configuração da Página - Tema LPS
st.set_page_config(
    page_title="Liderança Psicanalítica",
    page_icon="🧠",
    layout="wide"
)

# Estilização Customizada
st.markdown("""
    <style>
    :root {
        --primary-blue: #0D3B66;
        --accent-gold: #F4D35E;
        --bg-gray: #F5F5F5;
        --light-gold: #FFF9E6;
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
        width: 100%;
    }
    
    .stDownloadButton>button {
        background-color: var(--accent-gold) !important;
        color: black !important;
        font-weight: bold !important;
        border-radius: 8px !important;
        border: 1px solid var(--primary-blue) !important;
    }
    
    div[data-testid="stExpander"] {
        border: 1px solid var(--primary-blue);
        border-radius: 8px;
        background-color: var(--light-gold);
    }

    div[data-testid="stExpander"] summary p {
        color: var(--primary-blue) !important;
        font-weight: bold !important;
    }

    [data-testid="stSidebar"] {
        background-color: white;
        border-right: 1px solid #e0e0e0;
    }

    .logo-container {
        display: flex;
        justify-content: center;
        padding: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)

def vimeo_video(url):
    video_id = url.split('/')[-1]
    embed_url = f"https://player.vimeo.com/video/{video_id}"
    components.iframe(embed_url, height=450, scrolling=False)

if 'page' not in st.session_state:
    st.session_state.page = "Home"

WHATSAPP_URL = "https://wa.me/5511971419453"
OFFICIAL_EMAIL = "contato@liderancapsicanalitica.com"
LOGO_PATH = "attached_assets/logotipo_1768443722848.jpeg"

# Sidebar
with st.sidebar:
    if os.path.exists(LOGO_PATH):
        st.image(LOGO_PATH, use_container_width=True)
    
    st.title("LPS Hub")
    
    if st.button("🏠 Home"):
        st.session_state.page = "Home"
        st.rerun()
    if st.button("🎓 LPS Curso"):
        st.session_state.page = "LPS Curso"
        st.rerun()
    if st.button("📝 LPSTest"):
        st.session_state.page = "LPSTest"
        st.rerun()
    if st.button("💬 LPSChat"):
        st.session_state.page = "LPSChat"
        st.rerun()
    if st.button("📅 Mentoria"):
        st.session_state.page = "Mentoria"
        st.rerun()
    if st.button("👤 Sobre"):
        st.session_state.page = "Sobre"
        st.rerun()

# Conteúdo Principal
page = st.session_state.page

if page == "Home":
    if os.path.exists(LOGO_PATH):
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image(LOGO_PATH, use_container_width=True)
            
    st.title("Transforme Sua Liderança com a Ciência do Inconsciente")
    st.subheader("Descubra como a neurociência e a psicanálise podem revolucionar sua capacidade de liderar e influenciar equipes.")
    
    vimeo_video("https://vimeo.com/1154502544")
    
    st.markdown(f'<a href="{WHATSAPP_URL}" target="_blank"><button style="background-color:#25D366; color:white; border:none; padding:12px 24px; border-radius:8px; cursor:pointer; font-weight:bold; font-size:16px; margin-top:10px; width:auto;">Falar com a Consultora no WhatsApp</button></a>', unsafe_allow_html=True)

elif page == "LPS Curso":
    st.title("🎓 Programa LPS")
    
    modules = [
        {"id": 1, "name": "Módulo 1: Neurociência da Liderança - químicos cerebrais, Círculo de Segurança", "file": "attached_assets/Módulo_1_1768431876967.pdf", "videos": ["https://vimeo.com/1154503073", "https://vimeo.com/1154503122", "https://vimeo.com/1154503201", "https://vimeo.com/1154503286", "https://vimeo.com/1154503332", "https://vimeo.com/1154502907", "https://vimeo.com/1154502997"]},
        {"id": 2, "name": "Módulo 2: Mergulho no Inconsciente - Id, Ego, Superego, mecanismos de defesa", "file": "attached_assets/Módulo_2_1768431876968.pdf", "videos": ["https://vimeo.com/1154504282", "https://vimeo.com/1154503918", "https://vimeo.com/1154503996", "https://vimeo.com/1154504129", "https://vimeo.com/1154504216", "https://vimeo.com/1154504054"]},
        {"id": 3, "name": "Módulo 3: Relações e Transferência - dinâmicas líder-liderado, manejo de contratransferência", "file": "attached_assets/Módulo_3_1768431876969.pdf", "videos": ["https://vimeo.com/1154508629", "https://vimeo.com/1154508577", "https://vimeo.com/1154508688", "https://vimeo.com/1154508745", "https://vimeo.com/1154508530"]},
        {"id": 4, "name": "Módulo 4: Autoconsciência - seu arquétipo de liderança", "file": "attached_assets/Módulo_5_1768431876971.pdf", "videos": ["https://vimeo.com/1154510241", "https://vimeo.com/1154510404", "https://vimeo.com/1154510309"]},
        {"id": 5, "name": "Módulo 5: Entendendo a Equipe - assessment dos funcionários, papéis grupais de Bion", "file": "attached_assets/Módulo_6_1768431876972.pdf", "videos": ["https://vimeo.com/1154510682", "https://vimeo.com/1154510710", "https://vimeo.com/1154510729", "https://vimeo.com/1154510816"]},
        {"id": 6, "name": "Módulo 6: Aplicação Prática - casos reais, plano de ação personalizado", "file": "attached_assets/Módulo_7_1768431876973.pdf", "videos": ["https://vimeo.com/1154511020", "https://vimeo.com/1154511064"]},
        {"id": 7, "name": "Módulo 7: Conclusão e Próximos Passos", "file": "attached_assets/introdução_1768431876966.pdf", "videos": ["https://vimeo.com/1154502544", "https://vimeo.com/1154502598", "https://vimeo.com/1154502492"]}
    ]

    for mod in modules:
        with st.expander(mod['name']):
            for i, v_url in enumerate(mod['videos'], 1):
                st.write(f"**Parte {i}:**")
                vimeo_video(v_url)
            
            st.write("---")
            if os.path.exists(mod['file']):
                with open(mod['file'], "rb") as f:
                    st.download_button(
                        label="⬇️ Baixar Material de Apoio (PDF)",
                        data=f,
                        file_name=os.path.basename(mod['file']),
                        mime="application/pdf",
                        key=f"dl_{mod['id']}"
                    )

elif page == "LPSTest":
    st.title("📝 LPSTest")
    st.info("Área de Testes em Breve")
    st.write("Nesta seção, gestores e equipes terão acesso a ferramentas de assessment validadas para mapeamento comportamental e psicanalítico.")

elif page == "LPSChat":
    st.title("💬 LPSChat")
    st.info("Mapeamento de Equipe via IA")
    st.write("Nossa Inteligência Artificial ajudará você a analisar dinâmicas de grupo e perfis individuais com base na metodologia LPS.")

elif page == "Mentoria":
    st.title("📅 Mentoria")
    st.write("Agende suas sessões de mentoria síncrona com Viviane Nishiura.")
    st.markdown(f'<a href="{WHATSAPP_URL}" target="_blank"><button style="background-color:#25D366; color:white; border:none; padding:12px 24px; border-radius:8px; cursor:pointer; font-weight:bold; font-size:16px;">Agendar via WhatsApp</button></a>', unsafe_allow_html=True)

elif page == "Sobre":
    st.title("👤 Sobre Viviane Nishiura")
    st.write("""
    **Viviane Nishiura** é Psicóloga clínica formada pela **Universidade Mackenzie** e especialista pelo **Instituto de Psiquiatria do Hospital das Clínicas da Faculdade de Medicina da USP (IPq-HC FMUSP)**.
    
    Com mais de 28 anos de experiência em Recursos Humanos e Desenvolvimento Organizacional, Viviane fundou a metodologia **Liderança Psicanalítica (LPS)** para integrar a profundidade da psicanálise com as descobertas da neurociência no ambiente corporativo.
    """)
    st.write(f"Contato: {OFFICIAL_EMAIL}")
