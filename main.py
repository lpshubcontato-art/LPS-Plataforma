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
    
    .result-card {
        background-color: white;
        padding: 2rem;
        border-radius: 12px;
        border: 3px solid var(--accent-gold);
        margin-top: 1rem;
    }
    
    .profile-title {
        color: var(--primary-blue);
        font-size: 1.8rem;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

def vimeo_video(url):
    video_id = url.split('/')[-1]
    embed_url = f"https://player.vimeo.com/video/{video_id}"
    components.iframe(embed_url, height=450, scrolling=False)

# Inicialização do Estado de Sessão
if 'page' not in st.session_state:
    st.session_state.page = "Home"
if 'progress' not in st.session_state:
    st.session_state.progress = {}
if 'assessment_results' not in st.session_state:
    st.session_state.assessment_results = None

WHATSAPP_URL = "https://wa.me/5511971419453"
OFFICIAL_EMAIL = "contato@liderancapsicanalitica.com"
LOGO_PATH = "attached_assets/logotipo_1768443722848.jpeg"

# Banco de Dados de Perfis (Amostra dos 30 perfis conforme documentos)
PROFILES_DB = {
    "🛡 Protetor": {
        "🧠 Observador Reflexivo": {
            "forcas": "✔ Inspira confiança e acolhimento. ✔ Capacidade de análise emocional e previsão de conflitos. ✔ Toma decisões considerando o impacto humano.",
            "riscos": "⚠ Pode absorver emocionalmente os problemas do time. ⚠ Pode hesitar diante de decisões duras por empatia excessiva.",
            "reflexoes": "➡ Estabeleça limites claros entre você e a equipe. ➡ Reserve tempo para ação, não apenas para análise."
        },
        "🔥 Narciso Estratégico": {
            "forcas": "✔ Inspira pertencimento e admiração. ✔ Gera lealdade por meio da conexão emocional. ✔ Sabe como influenciar com afeto e presença.",
            "riscos": "⚠ Pode depender demais da validação externa. ⚠ Corre risco de evitar feedbacks duros para manter o carinho do time.",
            "reflexoes": "➡ Trabalhe a construção da sua autoridade sem depender do afeto. ➡ Lembre-se: cuidar também é confrontar quando necessário."
        }
    },
    "🎭 Relacional Reativo": {
        "👑 Idealista Exigente": {
            "forcas": "✔ Extrema habilidade diplomática e de leitura de ambiente. ✔ Capacidade de criar conexões e harmonia rapidamente. ✔ Sensibilidade às necessidades emocionais.",
            "riscos": "⚠ Dificuldade em tomar decisões firmes ou impopulares. ⚠ Tendência a evitar feedbacks negativos.",
            "reflexoes": "➡ Como equilibrar a busca por harmonia com a necessidade de clareza e firmeza? ➡ Sua identidade depende da aprovação?"
        }
    }
}

MODULES_DATA = [
    {"id": 1, "name": "Módulo 1: Neurociência da Liderança - químicos cerebrais, Círculo de Segurança", "file": "attached_assets/Módulo_1_1768431876967.pdf", "videos": ["https://vimeo.com/1154503073", "https://vimeo.com/1154503122", "https://vimeo.com/1154503201", "https://vimeo.com/1154503286", "https://vimeo.com/1154503332", "https://vimeo.com/1154502907", "https://vimeo.com/1154502997"]},
    {"id": 2, "name": "Módulo 2: Mergulho no Inconsciente - Id, Ego, Superego, mecanismos de defesa", "file": "attached_assets/Módulo_2_1768431876968.pdf", "videos": ["https://vimeo.com/1154504282", "https://vimeo.com/1154503918", "https://vimeo.com/1154503996", "https://vimeo.com/1154504129", "https://vimeo.com/1154504216", "https://vimeo.com/1154504054"]},
    {"id": 3, "name": "Módulo 3: Relações e Transferência - dinâmicas líder-liderado, manejo de contratransferência", "file": "attached_assets/Módulo_3_1768431876969.pdf", "videos": ["https://vimeo.com/1154508629", "https://vimeo.com/1154508577", "https://vimeo.com/1154508688", "https://vimeo.com/1154508745", "https://vimeo.com/1154508530"]},
    {"id": 4, "name": "Módulo 4: Autoconsciência - seu arquétipo de liderança", "file": "attached_assets/Módulo_5_1768431876971.pdf", "videos": ["https://vimeo.com/1154510241", "https://vimeo.com/1154510404", "https://vimeo.com/1154510309"]},
    {"id": 5, "name": "Módulo 5: Entendendo a Equipe - assessment dos funcionários, papéis grupais de Bion", "file": "attached_assets/Módulo_6_1768431876972.pdf", "videos": ["https://vimeo.com/1154510682", "https://vimeo.com/1154510710", "https://vimeo.com/1154510729", "https://vimeo.com/1154510816"]},
    {"id": 6, "name": "Módulo 6: Aplicação Prática - casos reais, plano de ação personalizado", "file": "attached_assets/Módulo_7_1768431876973.pdf", "videos": ["https://vimeo.com/1154511020", "https://vimeo.com/1154511064"]},
    {"id": 7, "name": "Módulo 7: Conclusão e Próximos Passos", "file": "attached_assets/introdução_1768431876966.pdf", "videos": ["https://vimeo.com/1154502544", "https://vimeo.com/1154502598", "https://vimeo.com/1154502492"]}
]

total_lessons = sum(len(m['videos']) for m in MODULES_DATA)
completed_lessons = sum(1 for v in st.session_state.progress.values() if v)
course_completed = completed_lessons >= total_lessons

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
    st.write("---")
    st.markdown(f'[💬 Suporte e Orçamento]({WHATSAPP_URL})')

page = st.session_state.page

if page == "Home":
    st.markdown("""
        <div style="display: flex; align-items: center; justify-content: center; gap: 15px; margin-top: -50px; margin-bottom: 30px;">
            <img src="https://raw.githubusercontent.com/user-attachments/assets/650e41f0-410a-428a-8531-18e47854694b" style="width: 60px;">
            <h1 style="color: #0D3B66; margin: 0; font-size: 2.2rem;">Plataforma de Liderança Psicanalítica (LPS)</h1>
        </div>
    """, unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; color: #0D3B66;'>Transforme Sua Liderança com a Ciência do Inconsciente</h2>", unsafe_allow_html=True)
    vimeo_video("https://vimeo.com/1154502544")
    st.markdown(f'<div style="text-align: center;"><a href="{WHATSAPP_URL}" target="_blank"><button style="background-color:#25D366; color:white; border:none; padding:12px 24px; border-radius:8px; cursor:pointer; font-weight:bold; font-size:16px; margin-top:20px; width:auto;">Falar com a Consultora no WhatsApp</button></a></div>', unsafe_allow_html=True)

elif page == "LPS Curso":
    st.title("🎓 Programa LPS")
    st.progress(completed_lessons / total_lessons if total_lessons > 0 else 0)
    for mod in MODULES_DATA:
        with st.expander(mod['name']):
            for v_idx, v_url in enumerate(mod['videos']):
                lesson_id = f"m{mod['id']}_v{v_idx}"
                vimeo_video(v_url)
                st.session_state.progress[lesson_id] = st.checkbox("Concluí esta aula", value=st.session_state.progress.get(lesson_id, False), key=lesson_id)
            if os.path.exists(mod['file']):
                with open(mod['file'], "rb") as f:
                    st.download_button("⬇️ Baixar Material", f, os.path.basename(mod['file']), key=f"dl_{mod['id']}")

elif page == "LPSTest":
    st.title("📝 LPSTest Assessment")
    if course_completed:
        st.write("O LPSTest revela as forças inconscientes que moldam seu estilo de liderança.")
        
        with st.form("assessment_form"):
            st.subheader("Assessment de Liderança")
            blocks = ["Autoridade", "Contenção", "Narcisismo", "Estrutura", "Relação", "Reflexão"]
            block_scores = {}
            for block in blocks:
                block_scores[block] = st.slider(f"Pontuação para {block}", 1, 40, 20)
            
            if st.form_submit_button("Gerar Meu Perfil Dominante"):
                sorted_scores = sorted(block_scores.items(), key=lambda x: x[1], reverse=True)
                dominant = sorted_scores[0][0]
                secondary = sorted_scores[1][0]
                
                # Mapeamento para nomes do DB (Exemplo simplificado)
                db_dominant = "🛡 Protetor" if dominant == "Relação" else "🎭 Relacional Reativo"
                db_secondary = "🧠 Observador Reflexivo" if secondary == "Reflexão" else "🔥 Narciso Estratégico"
                
                st.session_state.assessment_results = {
                    "dominant": db_dominant,
                    "secondary": db_secondary,
                    "details": PROFILES_DB.get(db_dominant, {}).get(db_secondary, {
                        "forcas": "Perfis híbridos personalizados conforme análise.",
                        "riscos": "Aguarde análise completa da consultora.",
                        "reflexoes": "Considere agendar uma mentoria síncrona."
                    })
                }
        
        if st.session_state.assessment_results:
            res = st.session_state.assessment_results
            st.markdown(f"""
                <div class="result-card">
                    <div class="profile-title">Seu Perfil: {res['dominant']} + {res['secondary']}</div>
                    <hr>
                    <h4 style="color: #0D3B66;">Forças:</h4>
                    <p>{res['details']['forcas']}</p>
                    <h4 style="color: #0D3B66;">Riscos:</h4>
                    <p>{res['details']['riscos']}</p>
                    <h4 style="color: #0D3B66;">Reflexões para Desenvolvimento:</h4>
                    <p>{res['details']['reflexoes']}</p>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.error("🔒 Conclua o curso para liberar o assessment.")

elif page == "LPSChat":
    st.title("💬 LPSChat")
    if course_completed:
        st.chat_input("Descreva sua equipe...")
    else:
        st.error("🔒 Conclua o curso para liberar o chat.")

elif page == "Mentoria":
    st.title("📅 Mentoria")
    if course_completed:
        st.markdown(f'<a href="{WHATSAPP_URL}" target="_blank"><button style="background-color:#25D366; color:white; border:none; padding:12px 24px; border-radius:8px; cursor:pointer; font-weight:bold; font-size:16px;">Agendar Mentoria</button></a>', unsafe_allow_html=True)
    else:
        st.error("🔒 Conclua o curso para liberar a mentoria.")

elif page == "Sobre":
    st.title("👤 Sobre")
    st.write("Viviane Nishiura - Psicóloga clínica e especialista em Transtornos de Personalidade.")
