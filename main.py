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
        font-weight: bold;
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
        background-color: var(--light-gold);
        padding: 2.5rem;
        border-radius: 15px;
        border: 5px solid var(--accent-gold);
        margin-top: 1.5rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .profile-title {
        color: var(--primary-blue);
        font-size: 2.2rem;
        font-weight: 800;
        text-align: center;
        margin-bottom: 1rem;
    }

    .question-text {
        color: var(--primary-blue);
        font-weight: 600;
        margin-top: 15px;
        margin-bottom: 5px;
        font-size: 1.1rem;
    }

    .section-header {
        color: var(--primary-blue);
        border-bottom: 2px solid var(--accent-gold);
        padding-bottom: 5px;
        margin-top: 20px;
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

# Definições das questões do Assessment (8 por bloco)
ASSESSMENT_QUESTIONS = {
    "Autoridade": [
        "Sinto que a equipe me observa de forma idealizada.",
        "Tenho clareza sobre minhas forças e fraquezas como líder.",
        "Me sinto desconfortável quando sou admirado demais.",
        "Prefiro manter minha imagem emocionalmente neutra no ambiente.",
        "Às vezes, não sei se sou respeitado ou apenas temido.",
        "Quando recebo críticas, demoro a me recuperar internamente.",
        "Me esforço para parecer emocionalmente estável, mesmo quando não estou.",
        "A percepção da equipe sobre mim influencia minhas decisões."
    ],
    "Contenção": [
        "Em situações de crise, sou o primeiro a manter a calma.",
        "Sei conter a ansiedade coletiva mesmo sem dizer uma palavra.",
        "Percebo rapidamente quando a equipe está emocionalmente instável.",
        "Eu sou, muitas vezes, o 'termômetro emocional' do time.",
        "Me preocupo com o impacto emocional das mudanças.",
        "Sei como evitar que o pânico da equipe tome conta.",
        "Tenho habilidade para resgatar a racionalidade do grupo.",
        "Sinto que absorvo emocionalmente o clima da equipe."
    ],
    "Narcisismo": [
        "Me incomodo quando não sou reconhecido pelo meu esforço.",
        "Gosto de ser o centro das atenções nas reuniões.",
        "A opinião da liderança acima de mim afeta meu desempenho.",
        "Sinto frustração quando minha equipe não valida minhas decisões.",
        "Preciso de reconhecimento frequente para me manter motivado.",
        "Evito demonstrar insegurança para não comprometer minha autoridade.",
        "Comparo minha liderança com a de outros colegas frequentemente.",
        "Às vezes exagero meu valor para manter respeito."
    ],
    "Estrutura": [
        "Preciso de metas e estruturas bem definidas para funcionar.",
        "Me incomodo com mudanças frequentes nas prioridades.",
        "Gosto de controlar todos os processos para evitar erros.",
        "Tenho dificuldade em delegar quando há risco de falhas.",
        "Acredito que sem controle, as pessoas tendem ao caos.",
        "Prefiro manter a equipe ocupada, mesmo que sem urgência.",
        "Me estresso com prazos mal definidos.",
        "Costumo antecipar problemas antes que eles ocorram."
    ],
    "Relação": [
        "Já senti que alguém da equipe me via como uma figura parental.",
        "Em alguns momentos, sou tratado com hostilidade sem motivo aparente.",
        "Já notei que membros da equipe projetam em mim expectativas irreais.",
        "Alguns funcionários me fazem sentir como se eu fosse o 'culpado' of tudo.",
        "Tenho dificuldade em me distanciar emocionalmente de alguns colaboradores.",
        "Preciso manter uma certa 'armadura' para não ser afetado pela equipe.",
        "Costumo internalizar conflitos mesmo quando não são meus.",
        "Às vezes, me sinto em uma posição emocionalmente isolada."
    ],
    "Reflexão": [
        "Tenho facilidade em identificar minhas armadilhas emocionais.",
        "Costumo refletir profundamente antes de tomar decisões difíceis.",
        "Entendo como meu temperamento afeta meu estilo de liderança.",
        "Estou constantemente ajustando meu modo de liderar conforme o grupo.",
        "Levo em conta as dinâmicas inconscientes ao lidar com conflitos.",
        "Aceito ajuda externa quando percebo que estou emocionalmente sobrecarregado.",
        "Consigo separar crítica pessoal de crítica à minha liderança.",
        "Vejo a liderança como um processo psicológico, não só técnico."
    ]
}

# Mapeamento para nomes de exibição dos perfis
BLOCK_TO_PROFILE = {
    "Relação": "🛡 Protetor",
    "Contenção": "🧱 Contenedor",
    "Narcisismo": "🔥 Narciso Estratégico",
    "Estrutura": "🏗 Estruturador",
    "Autoridade": "🪞 Espelho Emocional",
    "Reflexão": "🧠 Observador Reflexivo"
}

# Expandindo o Banco de Dados para incluir mais perfis híbridos (Amostra dos 30 solicitados)
PROFILES_DB = {
    "🛡 Protetor": {
        "🧠 Observador Reflexivo": {
            "forcas": "✔ Inspira confiança e acolhimento. ✔ Capacidade de análise emocional e previsão de conflitos. ✔ Toma decisões considerando o impacto humano.",
            "riscos": "⚠ Pode absorver emocionalmente os problemas do time. ⚠ Pode hesitar diante de decisões duras por empatia excessiva.",
            "recomendacoes": "➡ Estabeleça limites claros entre você e a equipe. ➡ Reserve tempo para ação, não apenas para análise."
        },
        "🔥 Narciso Estratégico": {
            "forcas": "✔ Inspira pertencimento e admiração. ✔ Gera lealdade por meio da conexão emocional. ✔ Sabe como influenciar com afeto e presença.",
            "riscos": "⚠ Pode depender demais da validação externa. ⚠ Corre risco de evitar feedbacks duros para manter o carinho do time.",
            "recomendacoes": "➡ Trabalhe a construção da sua autoridade sem depender do afeto. ➡ Lembre-se: cuidar também é confrontar quando necessário."
        },
        "🏗 Estruturador": {
            "forcas": "✔ Cria ambientes emocionalmente estáveis. ✔ Protege o time com sistemas e processos claros.",
            "riscos": "⚠ Pode se tornar rígido demais. ⚠ Dificuldade em lidar com o imprevisto emocional.",
            "recomendacoes": "➡ Permita que a equipe falhe sob sua supervisão. ➡ Flexibilize as regras em momentos de alta criatividade."
        }
    },
    "🧱 Contenedor": {
        "🛡 Protetor": {
            "forcas": "✔ Equilíbrio emocional impressionante. ✔ Alta capacidade de conter a ansiedade do grupo.",
            "riscos": "⚠ Pode ser visto como frio ou distante se não calibrar a empatia. ⚠ Risco de sobrecarga por absorver o estresse alheio.",
            "recomendacoes": "➡ Pratique o desapego emocional após reuniões intensas. ➡ Delegue a gestão de conflitos menores."
        }
    },
    "🔥 Narciso Estratégico": {
        "🪞 Espelho Emocional": {
            "forcas": "✔ Carisma magnético. ✔ Capacidade de moldar a cultura organizacional através do exemplo.",
            "riscos": "⚠ Necessidade constante de holofotes. ⚠ Dificuldade em aceitar sucessos da equipe que não passem por ele.",
            "recomendacoes": "➡ Celebre as vitórias individuais do time sem se colocar no centro. ➡ Busque validação interna, não apenas externa."
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

# Conteúdo Principal
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
    total_lessons = sum(len(m['videos']) for m in MODULES_DATA)
    completed_lessons = sum(1 for v in st.session_state.progress.values() if v)
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
    st.write("Responda às 48 afirmações abaixo. Seja sincero com suas tendências automáticas.")
    
    with st.form("assessment_form"):
        responses = {}
        for block_name, questions in ASSESSMENT_QUESTIONS.items():
            st.markdown(f"### {block_name}")
            for i, q in enumerate(questions):
                st.markdown(f'<div class="question-text">{i+1}. {q}</div>', unsafe_allow_html=True)
                responses[f"{block_name}_{i}"] = st.select_slider(
                    "Sua resposta:",
                    options=[1, 2, 3, 4, 5],
                    value=3,
                    labels={1: "Discordo totalmente", 3: "Neutro", 5: "Concordo totalmente"},
                    key=f"q_{block_name}_{i}"
                )
            st.write("---")
        
        if st.form_submit_button("Gerar Meu Perfil de Liderança"):
            # Calculando somas por bloco
            block_sums = {}
            for block in ASSESSMENT_QUESTIONS.keys():
                block_sums[block] = sum(responses[f"{block}_{i}"] for i in range(8))
            
            sorted_blocks = sorted(block_sums.items(), key=lambda x: x[1], reverse=True)
            dom_key, dom_score = sorted_blocks[0]
            sec_key, sec_score = sorted_blocks[1]
            
            dominant_name = BLOCK_TO_PROFILE[dom_key]
            secondary_name = BLOCK_TO_PROFILE[sec_key]
            
            # Detalhes do Perfil
            details = PROFILES_DB.get(dominant_name, {}).get(secondary_name, {
                "forcas": f"✔ Combinação potente de {dominant_name} e {secondary_name}. ✔ Alta capacidade adaptativa.",
                "riscos": "⚠ Necessidade de vigília constante sobre as projeções da equipe.",
                "recomendacoes": "➡ Agende sua mentoria personalizada para detalhar este perfil híbrido."
            })
            
            st.session_state.assessment_results = {
                "dominant": dominant_name,
                "secondary": secondary_name,
                "details": details
            }
            st.rerun()
    
    if st.session_state.assessment_results:
        res = st.session_state.assessment_results
        st.markdown(f"""
            <div class="result-card">
                <div class="profile-title">Resultado: {res['dominant']} + {res['secondary']}</div>
                <div class="section-header">🧠 Forças do Arquétipo Híbrido</div>
                <p style="margin-top:10px;">{res['details']['forcas']}</p>
                <div class="section-header">⚠ Riscos e Pontos Cegos</div>
                <p style="margin-top:10px;">{res['details']['riscos']}</p>
                <div class="section-header">➡ Recomendações de Desenvolvimento</div>
                <p style="margin-top:10px;">{res['details'].get('recomendacoes', res['details'].get('reflexoes'))}</p>
            </div>
        """, unsafe_allow_html=True)
        st.info("💡 Este é um resumo técnico. O relatório completo é discutido na mentoria individual.")

elif page == "LPSChat":
    st.title("💬 LPSChat")
    st.chat_input("Descreva a situação da sua equipe para análise psicanalítica...")

elif page == "Mentoria":
    st.title("📅 Mentoria")
    st.markdown(f'<div style="text-align: center;"><a href="{WHATSAPP_URL}" target="_blank"><button style="background-color:#25D366; color:white; border:none; padding:12px 24px; border-radius:8px; cursor:pointer; font-weight:bold; font-size:16px;">Agendar Mentoria Síncrona</button></a></div>', unsafe_allow_html=True)

elif page == "Sobre":
    st.title("👤 Sobre Viviane Nishiura")
    st.write("Viviane Nishiura é psicóloga clínica e consultora de liderança com foco em psicanálise aplicada a grupos e instituições.")
