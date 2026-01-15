import streamlit as st
import os
import sqlite3
import uuid
import json
import hashlib
import streamlit.components.v1 as components
from datetime import datetime
import google.generativeai as genai

# Configuração da Página - Tema LPS
st.set_page_config(
    page_title="Liderança Psicanalítica",
    page_icon="🧠",
    layout="wide"
)

# Password hashing functions
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, hashed):
    return hash_password(password) == hashed

# Database Setup
def init_db():
    conn = sqlite3.connect('lps_data.db')
    c = conn.cursor()
    
    # Users table for authentication
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        email TEXT UNIQUE,
        password_hash TEXT,
        name TEXT,
        user_type TEXT DEFAULT 'manager',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Managers table
    c.execute('''CREATE TABLE IF NOT EXISTS managers (
        id TEXT PRIMARY KEY,
        user_id TEXT,
        session_id TEXT,
        name TEXT,
        email TEXT,
        profile_dominant TEXT,
        profile_secondary TEXT,
        profile_details TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )''')
    
    # Migration: Add user_id column to managers if it doesn't exist
    c.execute("PRAGMA table_info(managers)")
    columns = [col[1] for col in c.fetchall()]
    if 'user_id' not in columns:
        c.execute("ALTER TABLE managers ADD COLUMN user_id TEXT")
    
    # Employees table
    c.execute('''CREATE TABLE IF NOT EXISTS employees (
        id TEXT PRIMARY KEY,
        manager_id TEXT,
        link_token TEXT UNIQUE,
        slot_number INTEGER,
        name TEXT,
        email TEXT,
        profile_dominant TEXT,
        profile_secondary TEXT,
        profile_details TEXT,
        bion_role TEXT,
        completed INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (manager_id) REFERENCES managers(id)
    )''')
    
    # Course progress table
    c.execute('''CREATE TABLE IF NOT EXISTS course_progress (
        id TEXT PRIMARY KEY,
        user_id TEXT,
        progress_data TEXT,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )''')
    
    conn.commit()
    conn.close()

init_db()

# Authentication functions
def register_user(email, password, name):
    conn = get_db()
    c = conn.cursor()
    try:
        user_id = str(uuid.uuid4())
        password_hash = hash_password(password)
        c.execute("INSERT INTO users (id, email, password_hash, name) VALUES (?, ?, ?, ?)",
                  (user_id, email.lower(), password_hash, name))
        manager_id = str(uuid.uuid4())
        c.execute("INSERT INTO managers (id, user_id, email, name) VALUES (?, ?, ?, ?)",
                  (manager_id, user_id, email.lower(), name))
        conn.commit()
        conn.close()
        return user_id, None
    except sqlite3.IntegrityError:
        conn.close()
        return None, "E-mail já cadastrado."

def authenticate_user(email, password):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT id, password_hash, name FROM users WHERE email = ?", (email.lower(),))
    result = c.fetchone()
    conn.close()
    if result and verify_password(password, result[1]):
        return {"id": result[0], "name": result[2], "email": email.lower()}
    return None

def get_manager_by_user(user_id):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT id, profile_dominant, profile_secondary, profile_details FROM managers WHERE user_id = ?", (user_id,))
    result = c.fetchone()
    conn.close()
    if result:
        return {
            "id": result[0],
            "dominant": result[1],
            "secondary": result[2],
            "details": json.loads(result[3]) if result[3] else {}
        }
    return None

def get_db():
    return sqlite3.connect('lps_data.db')

def generate_employee_link(manager_id, slot_number):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT link_token FROM employees WHERE manager_id = ? AND slot_number = ?", (manager_id, slot_number))
    result = c.fetchone()
    if result:
        conn.close()
        return result[0]
    token = str(uuid.uuid4())[:8]
    employee_id = str(uuid.uuid4())
    c.execute("INSERT INTO employees (id, manager_id, link_token, slot_number) VALUES (?, ?, ?, ?)", 
              (employee_id, manager_id, token, slot_number))
    conn.commit()
    conn.close()
    return token

def save_manager_profile(user_id, dominant, secondary, details):
    conn = get_db()
    c = conn.cursor()
    c.execute("""UPDATE managers SET profile_dominant = ?, profile_secondary = ?, profile_details = ? 
                 WHERE user_id = ?""", (dominant, secondary, json.dumps(details), user_id))
    conn.commit()
    conn.close()

def get_manager_employees(manager_id):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM employees WHERE manager_id = ? ORDER BY slot_number", (manager_id,))
    employees = c.fetchall()
    conn.close()
    return employees

def save_employee_result(token, name, email, dominant, secondary, details, bion_role):
    conn = get_db()
    c = conn.cursor()
    c.execute("""UPDATE employees SET name = ?, email = ?, profile_dominant = ?, profile_secondary = ?, 
                 profile_details = ?, bion_role = ?, completed = 1 WHERE link_token = ?""",
              (name, email, dominant, secondary, json.dumps(details), bion_role, token))
    conn.commit()
    conn.close()

def get_employee_by_token(token):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM employees WHERE link_token = ?", (token,))
    employee = c.fetchone()
    conn.close()
    return employee

def get_manager_profile_by_user(user_id):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT profile_dominant, profile_secondary, profile_details FROM managers WHERE user_id = ?", (user_id,))
    result = c.fetchone()
    conn.close()
    if result and result[0]:
        return {
            "dominant": result[0],
            "secondary": result[1],
            "details": json.loads(result[2]) if result[2] else {}
        }
    return None

def get_app_url():
    """Get the current app URL for generating employee links"""
    try:
        # Try to get from environment or use a default pattern
        replit_url = os.environ.get('REPLIT_DEV_DOMAIN', '')
        if replit_url:
            return f"https://{replit_url}"
        # Fallback for production
        replit_slug = os.environ.get('REPL_SLUG', '')
        replit_owner = os.environ.get('REPL_OWNER', '')
        if replit_slug and replit_owner:
            return f"https://{replit_slug}.{replit_owner}.repl.co"
    except:
        pass
    return ""

# Estilização Customizada
st.markdown("""
    <style>
    :root {
        --primary-blue: #0D3B66;
        --accent-gold: #F4D35E;
        --bg-gray: #F5F5F5;
        --light-gold: #FFF9E6;
    }
    
    .main { background-color: var(--bg-gray); }
    h1, h2, h3 { color: var(--primary-blue) !important; }
    
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

    .employee-card {
        background-color: white;
        padding: 1.5rem;
        border-radius: 10px;
        border: 2px solid var(--accent-gold);
        margin: 10px 0;
    }

    .link-box {
        background-color: var(--light-gold);
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid var(--primary-blue);
        font-family: monospace;
        word-break: break-all;
    }

    .bion-badge {
        background-color: var(--primary-blue);
        color: white;
        padding: 5px 12px;
        border-radius: 15px;
        font-size: 0.9rem;
        display: inline-block;
        margin-top: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

def vimeo_video(url):
    video_id = url.split('/')[-1]
    embed_url = f"https://player.vimeo.com/video/{video_id}"
    components.iframe(embed_url, height=450, scrolling=False)

# Inicialização do Estado de Sessão
if 'page' not in st.session_state:
    st.session_state.page = "Login"
if 'progress' not in st.session_state:
    st.session_state.progress = {}
if 'assessment_results' not in st.session_state:
    st.session_state.assessment_results = None
if 'employee_token' not in st.session_state:
    st.session_state.employee_token = None
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user' not in st.session_state:
    st.session_state.user = None
if 'manager_data' not in st.session_state:
    st.session_state.manager_data = None
if 'login_mode' not in st.session_state:
    st.session_state.login_mode = "login"
if 'show_test_form' not in st.session_state:
    st.session_state.show_test_form = False

WHATSAPP_URL = "https://wa.me/5511971419453"
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
        "Alguns funcionários me fazem sentir como se eu fosse o 'culpado' de tudo.",
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

BLOCK_TO_PROFILE = {
    "Relação": "🛡 Protetor",
    "Contenção": "🧱 Contenedor",
    "Narcisismo": "🔥 Narciso Estratégico",
    "Estrutura": "🏗 Estruturador",
    "Autoridade": "🪞 Espelho Emocional",
    "Reflexão": "🧠 Observador Reflexivo"
}

# Mapeamento de Papéis de Bion baseado nas respostas
def classify_bion_role(block_sums):
    """
    Classifica o papel grupal segundo Bion:
    - Porta-voz: Alta Autoridade + Alta Reflexão (expressa o que o grupo sente)
    - Bode Expiatório: Alta Relação + Baixa Contenção (absorve projeções negativas)
    - Dependente: Alta Contenção + Baixa Autoridade (busca proteção no líder)
    - Líder de Luta-Fuga: Alto Narcisismo + Alta Estrutura (reativo a ameaças)
    - Sabotador Silencioso: Alta Estrutura + Baixa Reflexão (resiste passivamente)
    """
    autoridade = block_sums.get("Autoridade", 24)
    contencao = block_sums.get("Contenção", 24)
    narcisismo = block_sums.get("Narcisismo", 24)
    estrutura = block_sums.get("Estrutura", 24)
    relacao = block_sums.get("Relação", 24)
    reflexao = block_sums.get("Reflexão", 24)
    
    # Thresholds
    high = 30
    low = 20
    
    if autoridade >= high and reflexao >= high:
        return "🎤 Porta-voz"
    elif relacao >= high and contencao <= low:
        return "🐐 Bode Expiatório"
    elif contencao >= high and autoridade <= low:
        return "🤝 Dependente"
    elif narcisismo >= high and estrutura >= high:
        return "⚔️ Líder de Luta-Fuga"
    elif estrutura >= high and reflexao <= low:
        return "🔇 Sabotador Silencioso"
    else:
        return "⚖️ Neutro/Adaptável"

BION_DESCRIPTIONS = {
    "🎤 Porta-voz": "Expressa verbalmente o que o grupo sente mas não consegue dizer. Canaliza tensões coletivas.",
    "🐐 Bode Expiatório": "Absorve projeções negativas do grupo. Frequentemente culpado por falhas sistêmicas.",
    "🤝 Dependente": "Busca proteção e direção no líder. Evita autonomia e delega responsabilidade emocional.",
    "⚔️ Líder de Luta-Fuga": "Reativo a ameaças reais ou imaginárias. Mobiliza o grupo para atacar ou fugir.",
    "🔇 Sabotador Silencioso": "Resiste passivamente às mudanças. Cumpre tarefas sem engajamento emocional.",
    "⚖️ Neutro/Adaptável": "Perfil equilibrado. Adapta-se às necessidades do grupo sem assumir papel fixo."
}

PROFILES_DB = {
    "🛡 Protetor": {
        "🧠 Observador Reflexivo": {
            "forcas": "✔ Inspira confiança e acolhimento. ✔ Capacidade de análise emocional e previsão de conflitos.",
            "riscos": "⚠ Pode absorver emocionalmente os problemas do time. ⚠ Pode hesitar diante de decisões duras.",
            "recomendacoes": "➡ Estabeleça limites claros. ➡ Reserve tempo para ação, não apenas análise."
        },
        "🔥 Narciso Estratégico": {
            "forcas": "✔ Inspira pertencimento e admiração. ✔ Gera lealdade por conexão emocional.",
            "riscos": "⚠ Pode depender demais da validação externa. ⚠ Evita feedbacks duros.",
            "recomendacoes": "➡ Construa autoridade sem depender do afeto. ➡ Cuidar também é confrontar."
        }
    }
}

MODULES_DATA = [
    {"id": 1, "name": "Módulo 1: Neurociência da Liderança", "file": "attached_assets/Módulo_1_1768431876967.pdf", "videos": ["https://vimeo.com/1154503073", "https://vimeo.com/1154503122", "https://vimeo.com/1154503201"]},
    {"id": 2, "name": "Módulo 2: Mergulho no Inconsciente", "file": "attached_assets/Módulo_2_1768431876968.pdf", "videos": ["https://vimeo.com/1154504282", "https://vimeo.com/1154503918"]},
    {"id": 3, "name": "Módulo 3: Relações e Transferência", "file": "attached_assets/Módulo_3_1768431876969.pdf", "videos": ["https://vimeo.com/1154508629", "https://vimeo.com/1154508577"]},
    {"id": 4, "name": "Módulo 4: Autoconsciência", "file": "attached_assets/Módulo_5_1768431876971.pdf", "videos": ["https://vimeo.com/1154510241"]},
    {"id": 5, "name": "Módulo 5: Entendendo a Equipe", "file": "attached_assets/Módulo_6_1768431876972.pdf", "videos": ["https://vimeo.com/1154510682"]},
    {"id": 6, "name": "Módulo 6: Aplicação Prática", "file": "attached_assets/Módulo_7_1768431876973.pdf", "videos": ["https://vimeo.com/1154511020"]},
    {"id": 7, "name": "Módulo 7: Conclusão", "file": "attached_assets/introdução_1768431876966.pdf", "videos": ["https://vimeo.com/1154502544"]}
]

# Check for employee token in URL (takes priority over auth)
query_params = st.query_params
is_employee_access = False
if 'token' in query_params:
    st.session_state.employee_token = query_params['token']
    st.session_state.page = "EmployeeAssessment"
    is_employee_access = True

# Login Page Function
def render_login_page():
    st.markdown("""
        <style>
        .login-container {
            background-color: #0D3B66;
            padding: 3rem;
            border-radius: 15px;
            max-width: 450px;
            margin: 2rem auto;
            box-shadow: 0 8px 25px rgba(0,0,0,0.3);
        }
        .login-title {
            color: #F4D35E;
            font-size: 1.5rem;
            text-align: center;
            margin-bottom: 1rem;
            font-weight: bold;
        }
        .welcome-text {
            color: white;
            text-align: center;
            font-size: 1.1rem;
            margin-bottom: 2rem;
            font-style: italic;
        }
        </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if os.path.exists(LOGO_PATH):
            st.image(LOGO_PATH, width=150)
        
        st.markdown("""
            <h1 style="color: #0D3B66; font-size: 2.5rem; text-align: center; font-weight: bold; margin: 0.5rem 0;">
                Liderança Psicanalítica
            </h1>
            <div style="background-color: #0D3B66; padding: 1.5rem; border-radius: 15px; margin-top: 1rem;">
                <p class="welcome-text">Transforme Sua Liderança com a Ciência do Inconsciente</p>
            </div>
        """, unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["Entrar", "Cadastrar"])
        
        with tab1:
            with st.form("login_form"):
                email = st.text_input("E-mail", key="login_email", placeholder="seu@email.com")
                password = st.text_input("Senha", type="password", key="login_password")
                submit = st.form_submit_button("Entrar", use_container_width=True)
                
                if submit:
                    if email and password:
                        user = authenticate_user(email, password)
                        if user:
                            st.session_state.authenticated = True
                            st.session_state.user = user
                            st.session_state.manager_data = get_manager_by_user(user['id'])
                            st.session_state.page = "Home"
                            st.rerun()
                        else:
                            st.error("E-mail ou senha incorretos.")
                    else:
                        st.error("Preencha todos os campos.")
        
        with tab2:
            with st.form("register_form"):
                name = st.text_input("Nome Completo", key="reg_name")
                email = st.text_input("E-mail", key="reg_email", placeholder="seu@email.com")
                password = st.text_input("Senha", type="password", key="reg_password")
                password2 = st.text_input("Confirmar Senha", type="password", key="reg_password2")
                submit = st.form_submit_button("Criar Conta", use_container_width=True)
                
                if submit:
                    if not all([name, email, password, password2]):
                        st.error("Preencha todos os campos.")
                    elif password != password2:
                        st.error("As senhas não coincidem.")
                    elif len(password) < 6:
                        st.error("Senha deve ter no mínimo 6 caracteres.")
                    else:
                        user_id, error = register_user(email, password, name)
                        if user_id:
                            st.success("Conta criada! Faça login para continuar.")
                        else:
                            st.error(error)

# Sidebar (only for authenticated managers, not employees via token)
if st.session_state.authenticated and not is_employee_access:
    with st.sidebar:
        if os.path.exists(LOGO_PATH):
            st.image(LOGO_PATH, width=120)
        st.title("LPS Hub")
        if st.session_state.user:
            st.caption(f"Olá, {st.session_state.user['name']}")
        st.write("---")
        if st.button("🏠 Home", key="nav_home"):
            st.session_state.page = "Home"
            st.rerun()
        if st.button("🎓 LPS Curso", key="nav_curso"):
            st.session_state.page = "LPS Curso"
            st.rerun()
        if st.button("📝 LPSTest", key="nav_test"):
            st.session_state.page = "LPSTest"
            st.rerun()
        if st.button("👥 Gestão de Equipe", key="nav_team"):
            st.session_state.page = "TeamManagement"
            st.rerun()
        if st.button("💬 LPSChat", key="nav_chat"):
            st.session_state.page = "LPSChat"
            st.rerun()
        if st.button("📅 Mentoria", key="nav_mentoria"):
            st.session_state.page = "Mentoria"
            st.rerun()
        if st.button("👤 Sobre", key="nav_sobre"):
            st.session_state.page = "Sobre"
            st.rerun()
        st.write("---")
        st.markdown(f'[💬 Suporte]({WHATSAPP_URL})')
        st.write("---")
        if st.button("🚪 Sair", key="nav_logout"):
            st.session_state.authenticated = False
            st.session_state.user = None
            st.session_state.manager_data = None
            st.session_state.page = "Login"
            st.rerun()

page = st.session_state.page

# Assessment Form Component
def render_assessment_form(form_key, is_employee=False):
    responses = {}
    for block_name, questions in ASSESSMENT_QUESTIONS.items():
        st.markdown(f"### {block_name}")
        for i, q in enumerate(questions):
            st.markdown(f'<div class="question-text">{i+1}. {q}</div>', unsafe_allow_html=True)
            responses[f"{block_name}_{i}"] = st.select_slider(
                "Nota:",
                options=[1, 2, 3, 4, 5],
                value=3,
                key=f"{form_key}_{block_name}_{i}"
            )
        st.write("---")
    return responses

def calculate_profile(responses):
    block_sums = {}
    for block in ASSESSMENT_QUESTIONS.keys():
        block_sums[block] = sum(responses[f"{block}_{i}"] for i in range(8))
    
    sorted_blocks = sorted(block_sums.items(), key=lambda x: x[1], reverse=True)
    dom_key = sorted_blocks[0][0]
    sec_key = sorted_blocks[1][0]
    
    dominant_name = BLOCK_TO_PROFILE[dom_key]
    secondary_name = BLOCK_TO_PROFILE[sec_key]
    
    details = PROFILES_DB.get(dominant_name, {}).get(secondary_name, {
        "forcas": f"✔ Combinação de {dominant_name} e {secondary_name}.",
        "riscos": "⚠ Necessidade de vigília sobre dinâmicas da equipe.",
        "recomendacoes": "➡ Agende mentoria personalizada."
    })
    
    bion_role = classify_bion_role(block_sums)
    
    return dominant_name, secondary_name, details, bion_role, block_sums

# Pages
if page == "Login":
    render_login_page()

elif page == "Home":
    if not st.session_state.authenticated:
        st.session_state.page = "Login"
        st.rerun()
    st.markdown("<h1 style='text-align: center; color: #0D3B66;'>Plataforma de Liderança Psicanalítica (LPS)</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; color: #0D3B66;'>Transforme Sua Liderança com a Ciência do Inconsciente</h2>", unsafe_allow_html=True)
    vimeo_video("https://vimeo.com/1154502544")
    st.markdown(f'<div style="text-align: center;"><a href="{WHATSAPP_URL}" target="_blank"><button style="background-color:#25D366; color:white; border:none; padding:12px 24px; border-radius:8px; cursor:pointer; font-weight:bold;">Falar com a Consultora</button></a></div>', unsafe_allow_html=True)

elif page == "LPS Curso":
    if not st.session_state.authenticated:
        st.session_state.page = "Login"
        st.rerun()
    st.title("🎓 Programa LPS")
    total_lessons = sum(len(m['videos']) for m in MODULES_DATA)
    completed_lessons = sum(1 for v in st.session_state.progress.values() if v)
    st.progress(completed_lessons / total_lessons if total_lessons > 0 else 0)
    for mod in MODULES_DATA:
        with st.expander(mod['name']):
            for v_idx, v_url in enumerate(mod['videos']):
                lesson_id = f"m{mod['id']}_v{v_idx}"
                vimeo_video(v_url)
                st.session_state.progress[lesson_id] = st.checkbox("Concluí", value=st.session_state.progress.get(lesson_id, False), key=lesson_id)
            if os.path.exists(mod['file']):
                with open(mod['file'], "rb") as f:
                    st.download_button("⬇️ Material", f, os.path.basename(mod['file']), key=f"dl_{mod['id']}")

elif page == "LPSTest":
    if not st.session_state.authenticated:
        st.session_state.page = "Login"
        st.rerun()
    st.title("📝 LPSTest Assessment - Seu Perfil")
    
    # Check for existing saved profile from database
    saved_profile = get_manager_profile_by_user(st.session_state.user['id'])
    
    if saved_profile:
        st.success("✅ Seu perfil já está salvo! Você pode refazer o teste a qualquer momento.")
        st.markdown(f"""
            <div class="result-card">
                <div class="profile-title">Seu Perfil Atual: {saved_profile['dominant']} + {saved_profile['secondary']}</div>
                <div class="section-header">🧠 Forças</div>
                <p>{saved_profile['details'].get('forcas', 'Perfil calculado.')}</p>
                <div class="section-header">⚠ Riscos</div>
                <p>{saved_profile['details'].get('riscos', 'Agende mentoria para análise.')}</p>
                <div class="section-header">➡ Recomendações</div>
                <p>{saved_profile['details'].get('recomendacoes', 'Agende mentoria.')}</p>
            </div>
        """, unsafe_allow_html=True)
        st.write("---")
        if st.button("🔄 Refazer LPSTest"):
            st.session_state.show_test_form = True
            st.rerun()
    
    # Show form if no saved profile OR user wants to redo
    if not saved_profile or st.session_state.get('show_test_form', False):
        st.write("Responda às 48 afirmações. (1 = Discordo Totalmente, 5 = Concordo Totalmente)")
        
        with st.form("manager_assessment"):
            responses = render_assessment_form("manager")
            submit = st.form_submit_button("Gerar Meu Perfil de Liderança")
            
            if submit and st.session_state.user:
                dominant, secondary, details, bion_role, block_sums = calculate_profile(responses)
                user_id = st.session_state.user['id']
                save_manager_profile(user_id, dominant, secondary, details)
                st.session_state.manager_data = get_manager_by_user(user_id)
                st.session_state.show_test_form = False
                st.session_state.assessment_results = {
                    "dominant": dominant,
                    "secondary": secondary,
                    "details": details,
                    "bion_role": bion_role
                }
                st.rerun()
        
        if st.session_state.assessment_results:
            res = st.session_state.assessment_results
            st.markdown(f"""
                <div class="result-card">
                    <div class="profile-title">Resultado: {res['dominant']} + {res['secondary']}</div>
                    <div class="section-header">🧠 Forças</div>
                    <p>{res['details']['forcas']}</p>
                    <div class="section-header">⚠ Riscos</div>
                    <p>{res['details']['riscos']}</p>
                    <div class="section-header">➡ Recomendações</div>
                    <p>{res['details'].get('recomendacoes', 'Agende mentoria.')}</p>
                </div>
            """, unsafe_allow_html=True)

elif page == "TeamManagement":
    if not st.session_state.authenticated:
        st.session_state.page = "Login"
        st.rerun()
    st.title("👥 Gestão de Equipe")
    st.write("Gere links para seus colaboradores responderem ao assessment e veja o mapeamento completo.")
    
    manager_data = st.session_state.manager_data
    if not manager_data:
        st.error("Dados do gestor não encontrados. Por favor, faça login novamente.")
    else:
        manager_id = manager_data['id']
        manager_profile = manager_data if manager_data.get('dominant') else None
        
        # Show Manager Profile First
        if manager_profile:
            st.markdown(f"""
                <div class="result-card" style="margin-bottom: 20px;">
                    <div class="profile-title">👤 Seu Perfil (Gestor)</div>
                    <p style="text-align: center; font-size: 1.3rem;"><strong>{manager_profile['dominant']} + {manager_profile['secondary']}</strong></p>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("⚠️ Complete seu LPSTest primeiro para ver a comparação com sua equipe.")
        
        st.write("---")
        
        # Generate Links Section
        st.subheader("🔗 Gerar Links para Funcionários")
        st.write("Cada link é único. Copie e envie para cada colaborador.")
        
        base_url = get_app_url()
        cols = st.columns(4)
        
        for i, col in enumerate(cols):
            with col:
                slot = i + 1
                token = generate_employee_link(manager_id, slot)
                full_link = f"{base_url}?token={token}" if base_url else f"?token={token}"
                st.markdown(f"**Funcionário {slot}**")
                st.code(full_link, language=None)
                st.caption("Copie e envie este link")
        
        if not base_url:
            st.info("Copie o link e adicione a URL do seu app publicado na frente.")
        
        st.write("---")
        
        # Team Dashboard with Comparative View
        st.subheader("📊 Dashboard Comparativo da Equipe")
        employees = get_manager_employees(manager_id)
        
        if employees:
            completed_count = sum(1 for e in employees if e[10] == 1)
            st.metric("Respostas Recebidas", f"{completed_count}/4")
            
            # Comparative table header
            if manager_profile and completed_count > 0:
                st.markdown(f"""
                    <div style="background-color: #0D3B66; color: white; padding: 10px; border-radius: 8px; margin-bottom: 10px;">
                        <strong>Comparacao:</strong> Seu perfil ({manager_profile['dominant']}) vs Equipe
                    </div>
                """, unsafe_allow_html=True)
            
            for emp in employees:
                if emp[10] == 1:  # completed
                    emp_name = emp[4] or f'Funcionario {emp[3]}'
                    st.markdown(f"""
                        <div class="employee-card">
                            <h4 style="color: #0D3B66; margin:0;">{emp_name}</h4>
                            <p><strong>Perfil:</strong> {emp[6]} + {emp[7]}</p>
                            <span class="bion-badge">{emp[9]}</span>
                            <p style="font-size: 0.9rem; color: #666; margin-top:10px;">
                                {BION_DESCRIPTIONS.get(emp[9], '')}
                            </p>
                            <p style="font-size: 0.85rem; color: #0D3B66; margin-top: 8px;">
                                Resultado enviado para: {emp[5]}
                            </p>
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                        <div class="employee-card" style="opacity: 0.5;">
                            <h4 style="color: #0D3B66; margin:0;">Funcionario {emp[3]}</h4>
                            <p>Aguardando resposta...</p>
                        </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("Os links serao gerados automaticamente. Copie-os acima e envie para seus colaboradores.")

elif page == "EmployeeAssessment":
    token = st.session_state.employee_token
    employee = get_employee_by_token(token)
    
    if not employee:
        st.error("Link inválido ou expirado.")
    elif employee[10] == 1:  # already completed
        st.success("Você já respondeu ao assessment! Obrigado pela participação.")
        st.markdown(f"""
            <div class="result-card">
                <div class="profile-title">Seu Perfil Registrado</div>
                <p style="text-align: center;"><strong>{employee[6]} + {employee[7]}</strong></p>
                <p style="text-align: center; font-size: 0.9rem; color: #666;">
                    Seu resultado foi salvo e enviado para seu e-mail ({employee[5]}).
                </p>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.title("📝 Assessment de Equipe")
        st.write("Responda às afirmações abaixo de forma honesta. Seus resultados individuais são confidenciais.")
        
        with st.form("employee_assessment"):
            name = st.text_input("Seu Nome")
            email = st.text_input("Seu E-mail (receberá seu resultado individual)")
            st.write("---")
            responses = render_assessment_form("employee")
            submit = st.form_submit_button("Enviar Minhas Respostas")
            
            if submit:
                if not name or not email:
                    st.error("Preencha seu nome e e-mail.")
                else:
                    dominant, secondary, details, bion_role, _ = calculate_profile(responses)
                    save_employee_result(token, name, email, dominant, secondary, details, bion_role)
                    st.balloons()
                    st.success("Obrigado! Suas respostas foram salvas com sucesso.")
                    st.markdown(f"""
                        <div class="result-card">
                            <div class="profile-title">Seu Perfil de Liderança</div>
                            <p style="text-align: center; font-size: 1.5rem;"><strong>{dominant} + {secondary}</strong></p>
                            <div class="section-header">🧠 Suas Forças</div>
                            <p>{details['forcas']}</p>
                            <div class="section-header">⚠ Pontos de Atenção</div>
                            <p>{details['riscos']}</p>
                            <div class="section-header">➡ Recomendações</div>
                            <p>{details.get('recomendacoes', 'Participe da mentoria para aprofundar.')}</p>
                        </div>
                    """, unsafe_allow_html=True)
                    st.info(f"📧 Uma cópia deste resultado será enviada para {email}. Apenas você e seu gestor terão acesso ao mapeamento completo da equipe.")

elif page == "LPSChat":
    if not st.session_state.authenticated:
        st.session_state.page = "Login"
        st.rerun()
    
    st.title("💬 LPSChat - Consultor de Liderança Psicanalítica")
    st.write("Converse com a IA sobre sua equipe. Ela tem acesso aos perfis dos seus funcionários.")
    
    # Initialize chat history
    if 'chat_messages' not in st.session_state:
        st.session_state.chat_messages = []
    
    # Get manager and employee data for context
    manager_data = st.session_state.manager_data
    user_name = st.session_state.user['name'] if st.session_state.user else "Gestor"
    
    # Fetch employees data
    employees_context = ""
    if manager_data:
        employees = get_manager_employees(manager_data['id'])
        if employees:
            employees_list = []
            for emp in employees:
                if emp[10] == 1:  # completed
                    emp_info = f"- {emp[4] or 'Funcionário ' + str(emp[3])}: Perfil {emp[6]} + {emp[7]}, Papel de Bion: {emp[9]}"
                    employees_list.append(emp_info)
            if employees_list:
                employees_context = "\n".join(employees_list)
    
    # Manager profile context
    manager_profile = ""
    if manager_data and manager_data.get('dominant'):
        manager_profile = f"Perfil do Gestor: {manager_data['dominant']} + {manager_data['secondary']}"
    
    # System prompt with psychoanalytic concepts
    system_prompt = f"""Você é um consultor especialista em Liderança Psicanalítica, baseado na metodologia LPS de Viviane Nishiura.

CONTEXTO DO GESTOR:
Nome: {user_name}
{manager_profile if manager_profile else "O gestor ainda não completou o LPSTest."}

EQUIPE DO GESTOR:
{employees_context if employees_context else "Nenhum funcionário completou o assessment ainda."}

CONCEITOS-CHAVE QUE VOCÊ DEVE USAR:

1. PAPÉIS DE BION (Dinâmica Grupal):
- Porta-voz: Expressa o que o grupo sente mas não consegue dizer
- Bode Expiatório: Absorve projeções negativas do grupo
- Dependente: Busca proteção no líder, evita autonomia
- Líder de Luta-Fuga: Reativo a ameaças, mobiliza ataque ou fuga
- Sabotador Silencioso: Resiste passivamente às mudanças

2. TRANSFERÊNCIA E CONTRATRANSFERÊNCIA:
- Transferência: Quando funcionários projetam no líder expectativas de figuras parentais
- Contratransferência: Quando o líder reage emocionalmente às projeções (irritação, bloqueio, fadiga)
- Use esses conceitos para explicar POR QUE o líder se sente irritado ou bloqueado

3. TAREFA REAL vs REGRESSÃO EMOCIONAL:
- Quando o grupo está em regressão (ansiedade, conflito, paralisia), sugira SEMPRE focar na Tarefa Real
- A Tarefa Real é o objetivo concreto do trabalho que traz o grupo de volta à racionalidade
- Pergunte: "Qual é a tarefa que vocês precisam entregar?" para tirar o grupo da regressão

4. PERFIS DE LIDERANÇA:
- Protetor: Acolhe mas pode absorver demais
- Contenedor: Mantém calma em crises
- Narciso Estratégico: Inspira mas precisa de validação
- Estruturador: Organiza mas pode controlar demais
- Espelho Emocional: Reflete o grupo mas pode ser afetado
- Observador Reflexivo: Analisa mas pode hesitar

INSTRUÇÕES DE RESPOSTA:
- Analise sempre os dados reais da equipe do gestor
- Identifique riscos dinâmicos (ex: presença de Bode Expiatório)
- Sugira intervenções práticas baseadas nos conceitos psicanalíticos
- Sempre termine sugerindo foco na Tarefa Real para resolver regressões
- Seja empático mas direto nas recomendações
- Use português brasileiro"""

    # Display chat history
    for message in st.session_state.chat_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Descreva a situação da sua equipe ou faça uma pergunta..."):
        # Add user message to history
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate AI response
        with st.chat_message("assistant"):
            with st.spinner("Analisando..."):
                try:
                    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    
                    # Build conversation history for Gemini
                    chat_history = f"{system_prompt}\n\n"
                    for msg in st.session_state.chat_messages:
                        role = "Gestor" if msg["role"] == "user" else "Consultor"
                        chat_history += f"{role}: {msg['content']}\n\n"
                    
                    response = model.generate_content(chat_history)
                    
                    assistant_message = response.text
                    st.markdown(assistant_message)
                    st.session_state.chat_messages.append({"role": "assistant", "content": assistant_message})
                
                except Exception as e:
                    st.error(f"Erro ao conectar com a IA: {str(e)}")
    
    # Clear chat button
    if st.session_state.chat_messages:
        if st.button("🗑️ Limpar Conversa"):
            st.session_state.chat_messages = []
            st.rerun()

elif page == "Mentoria":
    if not st.session_state.authenticated:
        st.session_state.page = "Login"
        st.rerun()
    st.title("📅 Mentoria")
    st.markdown(f'<div style="text-align: center;"><a href="{WHATSAPP_URL}" target="_blank"><button style="background-color:#25D366; color:white; border:none; padding:12px 24px; border-radius:8px; cursor:pointer; font-weight:bold;">Agendar Mentoria</button></a></div>', unsafe_allow_html=True)

elif page == "Sobre":
    if not st.session_state.authenticated:
        st.session_state.page = "Login"
        st.rerun()
    st.title("👤 Sobre Viviane Nishiura")
    st.write("Viviane Nishiura é psicóloga clínica e consultora de liderança.")
