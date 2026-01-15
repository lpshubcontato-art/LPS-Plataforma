import streamlit as st
import os
import streamlit.components.v1 as components

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
    }
    
    /* Estilização do Botão de Download: Dourado com texto Preto */
    .stDownloadButton>button {
        background-color: var(--accent-gold) !important;
        color: black !important;
        font-weight: bold !important;
        border-radius: 8px !important;
        border: 1px solid var(--primary-blue) !important;
    }
    
    .stDownloadButton>button:hover {
        background-color: #e5c654 !important;
        color: black !important;
    }

    div[data-testid="stExpander"] {
        border: 1px solid var(--primary-blue);
        border-radius: 8px;
        background-color: var(--light-gold);
    }

    div[data-testid="stExpander"] summary p {
        color: var(--primary-blue) !important;
        font-weight: bold !important;
        font-size: 1.1rem !important;
    }

    div[data-testid="stExpander"] summary svg {
        fill: var(--primary-blue) !important;
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

# Estrutura completa conforme roteiro técnico
MODULES = [
    {
        "id": 1, 
        "name": "Módulo 1: Neurociência da Liderança - químicos cerebrais, Círculo de Segurança", 
        "file": "attached_assets/Módulo_1_1768431876967.pdf", 
        "videos": ["https://vimeo.com/1154503073", "https://vimeo.com/1154503122", "https://vimeo.com/1154503201", "https://vimeo.com/1154503286", "https://vimeo.com/1154503332", "https://vimeo.com/1154502907", "https://vimeo.com/1154502997"]
    },
    {
        "id": 2, 
        "name": "Módulo 2: Mergulho no Inconsciente - Id, Ego, Superego, mecanismos de defesa", 
        "file": "attached_assets/Módulo_2_1768431876968.pdf", 
        "videos": ["https://vimeo.com/1154504282", "https://vimeo.com/1154503918", "https://vimeo.com/1154503996", "https://vimeo.com/1154504129", "https://vimeo.com/1154504216", "https://vimeo.com/1154504054"]
    },
    {
        "id": 3, 
        "name": "Módulo 3: Relações e Transferência - dinâmicas líder-liderado, manejo de contratransferência", 
        "file": "attached_assets/Módulo_3_1768431876969.pdf", 
        "videos": ["https://vimeo.com/1154508629", "https://vimeo.com/1154508577", "https://vimeo.com/1154508688", "https://vimeo.com/1154508745", "https://vimeo.com/1154508530"]
    },
    {
        "id": 4, 
        "name": "Módulo 4: Autoconsciência - seu arquétipo de liderança", 
        "file": "attached_assets/Módulo_5_1768431876971.pdf", 
        "videos": ["https://vimeo.com/1154510241", "https://vimeo.com/1154510404", "https://vimeo.com/1154510309"]
    },
    {
        "id": 5, 
        "name": "Módulo 5: Entendendo a Equipe - assessment dos funcionários, papéis grupais de Bion", 
        "file": "attached_assets/Módulo_6_1768431876972.pdf", 
        "videos": ["https://vimeo.com/1154510682", "https://vimeo.com/1154510710", "https://vimeo.com/1154510729", "https://vimeo.com/1154510816"]
    },
    {
        "id": 6, 
        "name": "Módulo 6: Aplicação Prática - casos reais, plano de ação personalizado", 
        "file": "attached_assets/Módulo_7_1768431876973.pdf", 
        "videos": ["https://vimeo.com/1154511020", "https://vimeo.com/1154511064"]
    },
    {
        "id": 7, 
        "name": "Módulo 7: Conclusão e Próximos Passos", 
        "file": "attached_assets/introdução_1768431876966.pdf", # Usando intro como referência final
        "videos": ["https://vimeo.com/1154502544", "https://vimeo.com/1154502598", "https://vimeo.com/1154502492"]
    }
]

# Sidebar
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

# Conteúdo
page = st.session_state.page
if page == "Home":
    st.title("Liderança Psicanalítica")
    vimeo_video("https://vimeo.com/1154502544")
    st.markdown(f'<a href="{WHATSAPP_URL}" target="_blank"><button style="background-color:#25D366; color:white; border:none; padding:12px 24px; border-radius:8px; cursor:pointer; font-weight:bold; font-size:16px; margin-top:10px;">Falar com a Consultora no WhatsApp</button></a>', unsafe_allow_html=True)

elif page == "LPS Curso":
    st.title("🎓 Programa LPS")
    for mod in MODULES:
        with st.expander(f"{mod['name']}"):
            for i, v_url in enumerate(mod['videos'], 1):
                st.write(f"**Parte {i}:**")
                vimeo_video(v_url)
            st.write("---")
            if os.path.exists(mod['file']):
                with open(mod['file'], "rb") as f:
                    st.download_button(
                        label=f"⬇️ Baixar Material de Apoio (PDF)",
                        data=f,
                        file_name=os.path.basename(mod['file']),
                        mime="application/pdf",
                        key=f"dl_v3_{mod['id']}"
                    )

elif page == "LPSTest":
    st.title("📝 LPSTest")
    st.markdown(f'<a href="{WHATSAPP_URL}" target="_blank"><button style="background-color:#25D366; color:white; border:none; padding:10px 20px; border-radius:5px; cursor:pointer; font-weight:bold;">Solicitar Acesso no WhatsApp</button></a>', unsafe_allow_html=True)

elif page == "Sobre":
    st.title("Sobre Viviane Nishiura")

elif page == "Mentoria":
    st.title("📞 Contato")
    st.write(f"E-mail: {OFFICIAL_EMAIL}")
    st.markdown(f'<a href="{WHATSAPP_URL}" target="_blank"><button style="background-color:#25D366; color:white; border:none; padding:12px 24px; border-radius:8px; cursor:pointer; font-weight:bold;">WhatsApp</button></a>', unsafe_allow_html=True)
