import streamlit as st
import os
import sqlite3
import uuid
import json
import hashlib
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import streamlit.components.v1 as components
from datetime import datetime
import google.generativeai as genai
import io
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.pdfgen import canvas

# ==========================================
# EMAIL CONFIGURATION (SMTP)
# ==========================================
# Configure these values in Streamlit secrets or environment variables
# Go to: Secrets tab -> Add the following keys:
#   SMTP_HOST = "smtp.gmail.com"  (or your email provider)
#   SMTP_PORT = "587"
#   SMTP_USER = "your-email@gmail.com"
#   SMTP_PASSWORD = "your-app-password"
#   SMTP_FROM_NAME = "Liderança Psicanalítica"
#   SMTP_FROM_EMAIL = "your-email@gmail.com"
# ==========================================

def get_smtp_config():
    """Get SMTP configuration from secrets or environment"""
    try:
        return {
            'host': st.secrets.get("SMTP_HOST", os.environ.get("SMTP_HOST", "")),
            'port': int(st.secrets.get("SMTP_PORT", os.environ.get("SMTP_PORT", "587"))),
            'user': st.secrets.get("SMTP_USER", os.environ.get("SMTP_USER", "")),
            'password': st.secrets.get("SMTP_PASSWORD", os.environ.get("SMTP_PASSWORD", "")),
            'from_name': st.secrets.get("SMTP_FROM_NAME", os.environ.get("SMTP_FROM_NAME", "Liderança Psicanalítica")),
            'from_email': st.secrets.get("SMTP_FROM_EMAIL", os.environ.get("SMTP_FROM_EMAIL", ""))
        }
    except:
        return None

def is_email_configured():
    """Check if email is properly configured"""
    config = get_smtp_config()
    if not config:
        return False
    return bool(config['host'] and config['user'] and config['password'] and config['from_email'])

def send_email(to_email, subject, html_content):
    """Send email using SMTP configuration"""
    if not is_email_configured():
        print(f"[EMAIL] SMTP not configured. Would send to: {to_email}")
        print(f"[EMAIL] Subject: {subject}")
        return False, "SMTP não configurado"
    
    config = get_smtp_config()
    
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = f"{config['from_name']} <{config['from_email']}>"
        msg['To'] = to_email
        
        html_part = MIMEText(html_content, 'html', 'utf-8')
        msg.attach(html_part)
        
        with smtplib.SMTP(config['host'], config['port']) as server:
            server.starttls()
            server.login(config['user'], config['password'])
            server.sendmail(config['from_email'], to_email, msg.as_string())
        
        return True, "Email enviado com sucesso"
    except Exception as e:
        print(f"[EMAIL ERROR] {str(e)}")
        return False, str(e)

def send_employee_result_email(employee_name, employee_email, dominant_profile, secondary_profile, bion_role, manager_name):
    """Send assessment result to employee"""
    subject = "Seu Perfil LPS: Insights sobre sua Lideranca e Comportamento"
    
    result_text = f"{dominant_profile} + {secondary_profile} ({bion_role})"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: Arial, sans-serif; background-color: #f5f5f5; margin: 0; padding: 20px; }}
            .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 10px; overflow: hidden; }}
            .header {{ background-color: #0D3B66; color: white; padding: 30px; text-align: center; }}
            .header h1 {{ margin: 0; color: #F4D35E; }}
            .content {{ padding: 30px; line-height: 1.7; color: #333; }}
            .result-box {{ background: linear-gradient(135deg, #0D3B66, #1a5490); color: white; padding: 25px; border-radius: 10px; text-align: center; margin: 25px 0; }}
            .result-box h2 {{ margin: 0; color: #F4D35E; font-size: 1.6rem; }}
            .signature {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; }}
            .footer {{ background-color: #f5f5f5; padding: 20px; text-align: center; font-size: 0.9rem; color: #666; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Lideranca Psicanalitica</h1>
                <p>Seu Perfil LPS</p>
            </div>
            <div class="content">
                <p>Ola, <strong>{employee_name}</strong>!</p>
                
                <p>Voce acaba de concluir o LPSTest, uma etapa fundamental na sua jornada de desenvolvimento dentro da Plataforma LPS.</p>
                
                <p>A analise do seu perfil combina os fundamentos da Psicanalise com as descobertas da Neurociencia para mapear nao apenas suas habilidades tecnicas, mas as forcas invisiveis e os mecanismos de defesa que moldam como voce se relaciona com sua equipe e seus lideres.</p>
                
                <div class="result-box">
                    <p style="margin: 0 0 10px 0; font-size: 0.9rem; color: #ccc;">Seu Resultado Principal:</p>
                    <h2>{result_text}</h2>
                </div>
                
                <p>Compreender o funcionamento do seu "eu" profissional e o primeiro passo para uma lideranca consciente e um ambiente psicologicamente seguro.</p>
                
                <p>O seu gestor ja recebeu o mapeamento completo e, em breve, voces poderao discutir estrategias de alocacao e desenvolvimento baseadas nesses dados estrategicos.</p>
                
                <div class="signature">
                    <p>Atenciosamente,<br><strong>Viviane Nishiura & Equipe LPS</strong></p>
                </div>
            </div>
            <div class="footer">
                <p>Este e um e-mail automatico da Plataforma LPS.</p>
                <p>Lideranca Psicanalitica - Transformando gestores em lideres conscientes.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return send_email(employee_email, subject, html_content)

def send_manager_notification_email(manager_email, manager_name, employee_name, employee_profile, bion_role):
    """Notify manager when an employee completes assessment"""
    subject = f"Novo Assessment Concluído - {employee_name}"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: Arial, sans-serif; background-color: #f5f5f5; margin: 0; padding: 20px; }}
            .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 10px; overflow: hidden; }}
            .header {{ background-color: #0D3B66; color: white; padding: 30px; text-align: center; }}
            .header h1 {{ margin: 0; color: #F4D35E; }}
            .content {{ padding: 30px; }}
            .alert-box {{ background-color: #d4edda; border-left: 4px solid #28a745; padding: 15px; border-radius: 5px; margin: 20px 0; }}
            .employee-card {{ background: #f8f9fa; padding: 20px; border-radius: 10px; margin: 20px 0; }}
            .bion-badge {{ display: inline-block; background-color: #F4D35E; color: #0D3B66; padding: 8px 16px; border-radius: 15px; font-weight: bold; }}
            .cta-button {{ display: inline-block; background-color: #0D3B66; color: white; padding: 15px 30px; border-radius: 25px; text-decoration: none; font-weight: bold; margin-top: 20px; }}
            .footer {{ background-color: #f5f5f5; padding: 20px; text-align: center; font-size: 0.9rem; color: #666; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Liderança Psicanalítica</h1>
                <p>Notificação de Assessment</p>
            </div>
            <div class="content">
                <p>Olá <strong>{manager_name}</strong>,</p>
                
                <div class="alert-box">
                    <strong>Novo membro mapeado!</strong> {employee_name} completou o LPSTest.
                </div>
                
                <div class="employee-card">
                    <h3 style="margin-top: 0; color: #0D3B66;">{employee_name}</h3>
                    <p><strong>Perfil:</strong> {employee_profile}</p>
                    <span class="bion-badge">{bion_role}</span>
                </div>
                
                <p>Acesse sua área de gestor para ver o mapeamento completo da equipe e os insights da IA sobre a dinâmica do grupo.</p>
                
                <p style="text-align: center;">
                    <a href="#" class="cta-button">Acessar Dashboard</a>
                </p>
            </div>
            <div class="footer">
                <p>Este é um e-mail automático da Plataforma LPS.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return send_email(manager_email, subject, html_content)

def send_welcome_email(user_email, user_name, password):
    """Send welcome email with login credentials (triggered manually after payment confirmation)"""
    subject = "Acesso Liberado - Liderança Psicanalítica"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: Arial, sans-serif; background-color: #f5f5f5; margin: 0; padding: 20px; }}
            .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 10px; overflow: hidden; }}
            .header {{ background-color: #0D3B66; color: white; padding: 30px; text-align: center; }}
            .header h1 {{ margin: 0; color: #F4D35E; }}
            .content {{ padding: 30px; }}
            .credentials-box {{ background: linear-gradient(135deg, #0D3B66, #1a5490); color: white; padding: 25px; border-radius: 10px; margin: 20px 0; }}
            .credentials-box h3 {{ margin-top: 0; color: #F4D35E; }}
            .credential-item {{ background: rgba(255,255,255,0.1); padding: 10px 15px; border-radius: 5px; margin: 10px 0; }}
            .credential-label {{ font-size: 0.9rem; opacity: 0.8; }}
            .credential-value {{ font-size: 1.1rem; font-weight: bold; }}
            .cta-button {{ display: inline-block; background-color: #F4D35E; color: #0D3B66; padding: 15px 30px; border-radius: 25px; text-decoration: none; font-weight: bold; margin-top: 20px; }}
            .features {{ background: #f8f9fa; padding: 20px; border-radius: 10px; margin: 20px 0; }}
            .feature-item {{ padding: 8px 0; border-bottom: 1px solid #e0e0e0; }}
            .feature-item:last-child {{ border-bottom: none; }}
            .footer {{ background-color: #f5f5f5; padding: 20px; text-align: center; font-size: 0.9rem; color: #666; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Bem-vindo(a) ao LPS!</h1>
                <p>Seu acesso foi liberado</p>
            </div>
            <div class="content">
                <p>Olá <strong>{user_name}</strong>,</p>
                <p>Parabéns! Seu pagamento foi confirmado e seu acesso à plataforma Liderança Psicanalítica está liberado.</p>
                
                <div class="credentials-box">
                    <h3>Seus Dados de Acesso</h3>
                    <div class="credential-item">
                        <div class="credential-label">E-mail:</div>
                        <div class="credential-value">{user_email}</div>
                    </div>
                    <div class="credential-item">
                        <div class="credential-label">Senha:</div>
                        <div class="credential-value">{password}</div>
                    </div>
                </div>
                
                <p><strong>Importante:</strong> Recomendamos que você altere sua senha após o primeiro acesso.</p>
                
                <div class="features">
                    <h4 style="margin-top: 0; color: #0D3B66;">O que você terá acesso:</h4>
                    <div class="feature-item">Curso completo com 6 módulos de Liderança Psicanalítica</div>
                    <div class="feature-item">LPSTest - Assessment de perfil de liderança</div>
                    <div class="feature-item">Gestão de Equipe - Mapeie até 4 colaboradores</div>
                    <div class="feature-item">LPSChat - Consultor de IA especializado</div>
                    <div class="feature-item">Acesso à mentoria com Viviane Nishiura</div>
                </div>
                
                <p style="text-align: center;">
                    <a href="#" class="cta-button">Acessar a Plataforma</a>
                </p>
            </div>
            <div class="footer">
                <p>Dúvidas? Entre em contato via WhatsApp.</p>
                <p>Liderança Psicanalítica - Transformando gestores em líderes conscientes.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return send_email(user_email, subject, html_content)

# Definir diretório de trabalho como local do script
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Configuração da Página - Tema LPS
st.set_page_config(
    page_title="Plataforma LPS",
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
    
    # Get manager info for email notification
    c.execute("""SELECT m.name, m.email, m.user_id FROM employees e 
                 JOIN managers m ON e.manager_id = m.id 
                 WHERE e.link_token = ?""", (token,))
    manager_info = c.fetchone()
    manager_name = manager_info[0] if manager_info else "Seu Gestor"
    manager_email = manager_info[1] if manager_info else None
    
    # Update employee record
    c.execute("""UPDATE employees SET name = ?, email = ?, profile_dominant = ?, profile_secondary = ?, 
                 profile_details = ?, bion_role = ?, completed = 1 WHERE link_token = ?""",
              (name, email, dominant, secondary, json.dumps(details), bion_role, token))
    conn.commit()
    conn.close()
    
    # Send email to employee with their result
    send_employee_result_email(name, email, dominant, secondary, bion_role, manager_name)
    
    # Send notification to manager
    if manager_email:
        employee_profile = f"{dominant} + {secondary}"
        send_manager_notification_email(manager_email, manager_name, name, employee_profile, bion_role)

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

# Course Progress Functions
def get_course_progress(user_id):
    """Get course progress for a user"""
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT progress_data FROM course_progress WHERE user_id = ?", (user_id,))
    result = c.fetchone()
    conn.close()
    if result and result[0]:
        return json.loads(result[0])
    return {}

def save_course_progress(user_id, progress_data):
    """Save course progress for a user"""
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT id FROM course_progress WHERE user_id = ?", (user_id,))
    existing = c.fetchone()
    if existing:
        c.execute("UPDATE course_progress SET progress_data = ?, updated_at = CURRENT_TIMESTAMP WHERE user_id = ?",
                  (json.dumps(progress_data), user_id))
    else:
        progress_id = str(uuid.uuid4())
        c.execute("INSERT INTO course_progress (id, user_id, progress_data) VALUES (?, ?, ?)",
                  (progress_id, user_id, json.dumps(progress_data)))
    conn.commit()
    conn.close()

def get_module_completion_status(user_id):
    """Get completion status for each module"""
    progress = get_course_progress(user_id)
    module_status = {}
    for mod in MODULES_DATA:
        module_lessons = [f"m{mod['id']}_v{v_idx}" for v_idx in range(len(mod['videos']))]
        completed = sum(1 for lesson in module_lessons if progress.get(lesson, False))
        total = len(module_lessons)
        module_status[mod['id']] = {
            'name': mod['name'],
            'completed': completed,
            'total': total,
            'percentage': (completed / total * 100) if total > 0 else 0
        }
    return module_status

def is_course_completed(user_id):
    """Check if user has completed all theoretical modules (first 5 modules)"""
    module_status = get_module_completion_status(user_id)
    theoretical_modules = [1, 2, 3, 4, 5]  # First 5 modules are theoretical
    for mod_id in theoretical_modules:
        if mod_id in module_status and module_status[mod_id]['percentage'] < 100:
            return False
    return True

def get_assessment_stats(manager_id):
    """Get assessment statistics for a manager"""
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM employees WHERE manager_id = ? AND completed = 1", (manager_id,))
    applied = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM employees WHERE manager_id = ?", (manager_id,))
    total_slots = c.fetchone()[0]
    conn.close()
    max_employees = 4  # Package limit
    remaining = max(0, max_employees - applied)  # Remaining based on completed assessments
    return {
        'applied': applied,
        'remaining': remaining,
        'total_slots': total_slots,
        'max_employees': max_employees
    }

def get_ai_insights(manager_id, user_id):
    """Generate AI insights about the team"""
    employees = get_manager_employees(manager_id)
    manager_profile = get_manager_profile_by_user(user_id)
    
    insights = []
    
    # Check if manager has taken the assessment
    if not manager_profile or not manager_profile.get('dominant'):
        insights.append({
            'type': 'warning',
            'message': 'Complete seu LPSTest para receber insights personalizados sobre sua liderança.'
        })
    
    # Check team size
    completed_employees = [e for e in employees if e[10] == 1]  # completed column
    if len(completed_employees) == 0:
        insights.append({
            'type': 'info',
            'message': 'Envie os links de assessment para sua equipe para começar a receber insights.'
        })
    elif len(completed_employees) < 3:
        insights.append({
            'type': 'info',
            'message': f'Você tem {len(completed_employees)} funcionário(s) mapeado(s). Mapeie mais membros para análises mais completas.'
        })
    else:
        # Analyze Bion roles distribution
        bion_roles = [e[9] for e in completed_employees if e[9]]  # bion_role column
        if bion_roles:
            role_counts = {}
            for role in bion_roles:
                role_counts[role] = role_counts.get(role, 0) + 1
            
            most_common = max(role_counts, key=role_counts.get)
            if role_counts[most_common] > len(bion_roles) / 2:
                insights.append({
                    'type': 'alert',
                    'message': f'Concentração de papéis: {role_counts[most_common]} membros com papel "{most_common}". Considere diversificar.'
                })
            else:
                insights.append({
                    'type': 'success',
                    'message': 'Boa diversidade de papéis na equipe! Isso favorece a dinâmica grupal.'
                })
    
    return insights[:3]  # Return max 3 insights

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
    
    .module-card {
        background: white;
        border: 2px solid var(--accent-gold);
        border-radius: 15px;
        padding: 1.5rem;
        text-align: center;
        transition: transform 0.2s, box-shadow 0.2s;
        cursor: pointer;
        height: 100%;
    }
    
    .module-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(13, 59, 102, 0.2);
    }
    
    .module-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
    }
    
    .module-title {
        color: var(--primary-blue);
        font-size: 1.1rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    
    .module-desc {
        color: #666;
        font-size: 0.9rem;
        line-height: 1.4;
    }
    
    .whatsapp-float {
        position: fixed;
        bottom: 25px;
        right: 25px;
        background-color: #25D366;
        color: white;
        border-radius: 50px;
        padding: 15px 25px;
        font-weight: bold;
        text-decoration: none;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        z-index: 9999;
        display: flex;
        align-items: center;
        gap: 10px;
        transition: transform 0.2s;
    }
    
    .whatsapp-float:hover {
        transform: scale(1.05);
        color: white;
    }
    
    .header-bar {
        background: linear-gradient(135deg, var(--primary-blue) 0%, #1a5490 100%);
        padding: 1rem 2rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin: -1rem -1rem 1rem -1rem;
        border-radius: 0 0 15px 15px;
    }
    
    .header-logo {
        display: flex;
        align-items: center;
        gap: 15px;
    }
    
    .header-title {
        color: var(--accent-gold);
        font-size: 1.5rem;
        font-weight: bold;
        margin: 0;
    }
    
    .btn-area-aluno {
        background-color: var(--accent-gold);
        color: var(--primary-blue);
        border: none;
        padding: 10px 25px;
        border-radius: 25px;
        font-weight: bold;
        cursor: pointer;
        transition: transform 0.2s;
    }
    
    .btn-area-aluno:hover {
        transform: scale(1.05);
    }
    
    .hero-section {
        background: linear-gradient(135deg, var(--primary-blue) 0%, #1a5490 100%);
        padding: 3rem 2rem;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .hero-title {
        color: var(--accent-gold);
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    
    .hero-subtitle {
        color: white;
        font-size: 1.2rem;
        margin-bottom: 1.5rem;
    }
    
    .restricted-modal {
        background: linear-gradient(135deg, #0D3B66 0%, #1a5490 100%);
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        border: 3px solid var(--accent-gold);
    }
    
    .restricted-title {
        color: var(--accent-gold);
        font-size: 1.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    
    .restricted-text {
        color: white;
        font-size: 1.1rem;
        margin-bottom: 1.5rem;
    }
    
    .nav-menu {
        display: flex;
        gap: 10px;
        flex-wrap: wrap;
        justify-content: center;
        margin-bottom: 1rem;
    }
    
    .nav-btn {
        background: transparent;
        border: none;
        color: var(--primary-blue);
        font-weight: 600;
        padding: 8px 15px;
        cursor: pointer;
        border-radius: 20px;
        transition: all 0.2s;
    }
    
    .nav-btn:hover {
        background-color: var(--light-gold);
    }
    
    .nav-btn.active {
        background-color: var(--primary-blue);
        color: white;
    }
    
    .btn-entrar {
        background-color: var(--accent-gold) !important;
        color: var(--primary-blue) !important;
        font-weight: bold !important;
        border-radius: 25px !important;
        padding: 10px 25px !important;
    }
    
    .section-title {
        color: var(--primary-blue);
        font-size: 2rem;
        font-weight: bold;
        text-align: center;
        margin: 2rem 0 1rem 0;
        border-bottom: 3px solid var(--accent-gold);
        padding-bottom: 0.5rem;
    }
    
    .about-card {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        border-left: 5px solid var(--accent-gold);
        margin: 1rem 0;
    }
    
    .solution-card {
        background: linear-gradient(135deg, var(--primary-blue) 0%, #1a5490 100%);
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        color: white;
    }
    
    .solution-title {
        color: var(--accent-gold);
        font-size: 1.3rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    
    .cta-button {
        display: inline-block;
        background-color: var(--accent-gold);
        color: var(--primary-blue);
        padding: 12px 30px;
        border-radius: 30px;
        font-weight: bold;
        text-decoration: none;
        margin-top: 1rem;
        transition: transform 0.2s;
    }
    
    .cta-button:hover {
        transform: scale(1.05);
        color: var(--primary-blue);
    }
    
    .paywall-box {
        background: linear-gradient(135deg, #0D3B66 0%, #1a5490 100%);
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        border: 3px solid var(--accent-gold);
        margin: 1rem 0;
    }
    
    .paywall-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
    }
    
    .paywall-title {
        color: var(--accent-gold);
        font-size: 1.5rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    
    .paywall-text {
        color: white;
        font-size: 1rem;
        margin-bottom: 1rem;
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
if 'section' not in st.session_state:
    st.session_state.section = "home"
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
if 'show_login_modal' not in st.session_state:
    st.session_state.show_login_modal = False
if 'selected_module' not in st.session_state:
    st.session_state.selected_module = None

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
    {"id": 1, "name": "Módulo 1: Neurociência da Liderança", "description": "Entenda como o cérebro processa decisões e aprenda a usar a neurociência para liderar com mais eficácia.", "icon": "🧠", "file": "attached_assets/Módulo_1_1768431876967.pdf", "videos": ["https://vimeo.com/1154503073", "https://vimeo.com/1154503122", "https://vimeo.com/1154503201"]},
    {"id": 2, "name": "Módulo 2: Mergulho no Inconsciente", "description": "Explore as camadas profundas da mente e descubra como padrões inconscientes influenciam sua liderança.", "icon": "🌊", "file": "attached_assets/Módulo_2_1768431876968.pdf", "videos": ["https://vimeo.com/1154504282", "https://vimeo.com/1154503918"]},
    {"id": 3, "name": "Módulo 3: Relações e Transferência", "description": "Compreenda as dinâmicas de transferência e contratransferência nas relações profissionais.", "icon": "🔄", "file": "attached_assets/Módulo_3_1768431876969.pdf", "videos": ["https://vimeo.com/1154508629", "https://vimeo.com/1154508577"]},
    {"id": 4, "name": "Módulo 4: Autoconsciência", "description": "Desenvolva autoconhecimento profundo e identifique seus gatilhos emocionais como líder.", "icon": "🪞", "file": "attached_assets/Módulo_5_1768431876971.pdf", "videos": ["https://vimeo.com/1154510241"]},
    {"id": 5, "name": "Módulo 5: Entendendo a Equipe", "description": "Aprenda a mapear perfis e dinâmicas grupais usando conceitos psicanalíticos.", "icon": "👥", "file": "attached_assets/Módulo_6_1768431876972.pdf", "videos": ["https://vimeo.com/1154510682"]},
    {"id": 6, "name": "Módulo 6: Aplicação Prática", "description": "Coloque em prática as ferramentas psicanalíticas no dia a dia da liderança.", "icon": "🛠️", "file": "attached_assets/Módulo_7_1768431876973.pdf", "videos": ["https://vimeo.com/1154511020"]}
]

# Check for employee token in URL (takes priority over auth)
query_params = st.query_params
is_employee_access = False

# Token in URL - set session state
if 'token' in query_params:
    st.session_state.employee_token = query_params['token']
    st.session_state.page = "EmployeeAssessment"
    is_employee_access = True

# Token already in session state - maintain employee access lock
if st.session_state.get('employee_token') and not st.session_state.get('authenticated'):
    st.session_state.page = "EmployeeAssessment"
    is_employee_access = True

# Floating WhatsApp Button (appears on all pages)
st.markdown(f'''
    <a href="{WHATSAPP_URL}" target="_blank" class="whatsapp-float">
        <span style="font-size: 1.5rem;">💬</span>
        Falar com Consultor
    </a>
''', unsafe_allow_html=True)

# Navigation Menu Sections
MENU_SECTIONS = ["Sobre", "Curso", "LPSTest", "LPSChat", "Mentoria", "Soluções", "Contato"]

# Public Header with Navigation Menu
def render_public_header():
    # Logo and Title Row
    col1, col2, col3 = st.columns([1, 4, 1])
    with col1:
        if os.path.exists(LOGO_PATH):
            st.image(LOGO_PATH, width=100)
    with col2:
        st.markdown("""
            <h1 style="color: #0D3B66; font-size: 2rem; margin: 0; text-align: center;">
                Liderança Psicanalítica
            </h1>
        """, unsafe_allow_html=True)
    with col3:
        if st.session_state.authenticated:
            st.markdown(f"""
                <div style="background-color: #0D3B66; color: #F4D35E; padding: 10px 20px; border-radius: 25px; text-align: center; font-weight: bold;">
                    👤 {st.session_state.user['name'][:12]}
                </div>
            """, unsafe_allow_html=True)
            if st.button("Minha Área", key="btn_dashboard", use_container_width=True):
                st.session_state.page = "Dashboard"
                st.rerun()
        else:
            if st.button("Entrar", key="button-entrar", use_container_width=True):
                st.session_state.page = "Login"
                st.rerun()
    
    # Navigation Menu using selectbox for reliability
    st.write("")
    current = st.session_state.section
    
    # Create styled navigation tabs
    nav_options = ["home"] + [s.lower() for s in MENU_SECTIONS]
    nav_labels = ["Home"] + MENU_SECTIONS
    
    # Display current section indicator
    current_idx = nav_options.index(current) if current in nav_options else 0
    
    # Use columns for navigation buttons with visual feedback
    nav_cols = st.columns(len(nav_labels))
    for idx, (opt, label) in enumerate(zip(nav_options, nav_labels)):
        with nav_cols[idx]:
            is_active = (current == opt)
            btn_style = "primary" if is_active else "secondary"
            if st.button(label, key=f"nav_{opt}_btn", use_container_width=True, type=btn_style if is_active else "secondary"):
                st.session_state.section = opt
                st.session_state.show_login_modal = False
                st.rerun()
    
    st.write("---")

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
        
        st.write("")
        if st.button("⬅️ Voltar para Vitrine", key="back_to_vitrine", use_container_width=True):
            st.session_state.page = "Vitrine"
            st.rerun()
        
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
            st.session_state.page = "Home"
            st.session_state.section = "home"
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

def get_profile_tendency(profile):
    """Return the leadership tendency for a given profile."""
    tendencies = {
        "Protetor": "acolhimento e cuidado da equipe",
        "Contenedor": "estabilidade emocional e gestao de crises",
        "Narciso Estrategico": "inspiracao e motivacao da equipe",
        "Estruturador": "organizacao e controle de processos",
        "Espelho Emocional": "empatia e validacao emocional",
        "Observador Reflexivo": "analise profunda e decisoes ponderadas"
    }
    return tendencies.get(profile, "desenvolvimento da equipe")

# ==========================================
# PDF EXPORT FUNCTIONS
# ==========================================

def create_pdf_styles():
    """Create custom styles for PDF reports with LPS branding."""
    styles = getSampleStyleSheet()
    
    # Title style
    styles.add(ParagraphStyle(
        name='LPSTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=HexColor('#0D3B66'),
        alignment=TA_CENTER,
        spaceAfter=20
    ))
    
    # Subtitle style
    styles.add(ParagraphStyle(
        name='LPSSubtitle',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=HexColor('#F4D35E'),
        alignment=TA_CENTER,
        spaceAfter=15
    ))
    
    # Section header
    styles.add(ParagraphStyle(
        name='LPSSection',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=HexColor('#0D3B66'),
        spaceAfter=10,
        spaceBefore=15
    ))
    
    # Body text
    styles.add(ParagraphStyle(
        name='LPSBody',
        parent=styles['Normal'],
        fontSize=11,
        textColor=HexColor('#333333'),
        alignment=TA_JUSTIFY,
        spaceAfter=8
    ))
    
    # Info text
    styles.add(ParagraphStyle(
        name='LPSInfo',
        parent=styles['Normal'],
        fontSize=10,
        textColor=HexColor('#666666'),
        alignment=TA_LEFT
    ))
    
    return styles

def create_pdf_header_table():
    """Create a styled header table with LPS logo and branding."""
    logo_path = "attached_assets/logotipo_1768443722848.jpeg"
    
    # Check if logo exists
    if os.path.exists(logo_path):
        logo = Image(logo_path, width=1.2*inch, height=1.2*inch)
        header_data = [[
            logo,
            Paragraph("<font color='white' size='14'><b>Lideranca Psicanalitica</b></font><br/><font color='#F4D35E' size='10'>Viviane Nishiura & Equipe LPS</font>", getSampleStyleSheet()['Normal'])
        ]]
    else:
        # Fallback to text-based header if logo not found
        header_data = [[
            Paragraph("<font color='#F4D35E' size='28'><b>LPS</b></font>", getSampleStyleSheet()['Normal']),
            Paragraph("<font color='white' size='12'>Lideranca Psicanalitica<br/><font size='9'>Viviane Nishiura & Equipe</font></font>", getSampleStyleSheet()['Normal'])
        ]]
    
    header_table = Table(header_data, colWidths=[1.5*inch, 4*inch])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), HexColor('#0D3B66')),
        ('TEXTCOLOR', (0, 0), (0, 0), HexColor('#F4D35E')),
        ('TEXTCOLOR', (1, 0), (1, 0), HexColor('#FFFFFF')),
        ('ALIGN', (0, 0), (0, 0), 'CENTER'),
        ('ALIGN', (1, 0), (1, 0), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ('BOX', (0, 0), (-1, -1), 1, HexColor('#0D3B66')),
    ]))
    return header_table

def generate_team_pdf_report(manager_name, employees_data, include_date=True):
    """Generate a PDF report with team assessment results."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.75*inch, bottomMargin=0.75*inch)
    styles = create_pdf_styles()
    elements = []
    
    # Styled header with LPS branding
    elements.append(create_pdf_header_table())
    elements.append(Spacer(1, 20))
    
    # Report title
    elements.append(Paragraph("Relatorio da Equipe", styles['LPSSection']))
    elements.append(Spacer(1, 20))
    
    # Manager info
    date_str = datetime.now().strftime("%d/%m/%Y") if include_date else ""
    elements.append(Paragraph(f"<b>Gestor:</b> {manager_name}", styles['LPSInfo']))
    elements.append(Paragraph(f"<b>Data:</b> {date_str}", styles['LPSInfo']))
    elements.append(Spacer(1, 20))
    
    # Table header
    table_data = [["Nome", "E-mail", "Perfil Dominante", "Perfil Secundario", "Papel de Bion"]]
    
    # Add employee data
    for emp in employees_data:
        if emp[10] == 1:  # completed
            emp_name = emp[4] or f'Funcionario {emp[3]}'
            table_data.append([
                emp_name,
                emp[5] or "N/A",
                emp[6] or "N/A",
                emp[7] or "N/A",
                emp[9] or "N/A"
            ])
    
    if len(table_data) > 1:
        table = Table(table_data, colWidths=[1.3*inch, 1.6*inch, 1.2*inch, 1.2*inch, 1.2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#0D3B66')),
            ('TEXTCOLOR', (0, 0), (-1, 0), HexColor('#FFFFFF')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), HexColor('#F5F5F5')),
            ('GRID', (0, 0), (-1, -1), 1, HexColor('#CCCCCC')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [HexColor('#FFFFFF'), HexColor('#F5F5F5')])
        ]))
        elements.append(table)
    else:
        elements.append(Paragraph("Nenhum funcionario completou o assessment ainda.", styles['LPSBody']))
    
    # Footer
    elements.append(Spacer(1, 30))
    elements.append(Paragraph("_" * 60, styles['LPSInfo']))
    elements.append(Paragraph("Gerado pela Plataforma LPS - Lideranca Psicanalitica", styles['LPSInfo']))
    elements.append(Paragraph("Viviane Nishiura & Equipe LPS", styles['LPSInfo']))
    
    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()

def generate_individual_pdf_report(employee_data, manager_name):
    """Generate a PDF report for an individual employee."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.75*inch, bottomMargin=0.75*inch)
    styles = create_pdf_styles()
    elements = []
    
    emp_name = employee_data[4] or f'Funcionario {employee_data[3]}'
    
    # Styled header with LPS branding
    elements.append(create_pdf_header_table())
    elements.append(Spacer(1, 20))
    
    # Report title
    elements.append(Paragraph("Relatorio Individual de Assessment", styles['LPSSection']))
    elements.append(Spacer(1, 15))
    
    # Employee info
    elements.append(Paragraph(f"<b>Funcionario:</b> {emp_name}", styles['LPSInfo']))
    elements.append(Paragraph(f"<b>E-mail:</b> {employee_data[5] or 'N/A'}", styles['LPSInfo']))
    elements.append(Paragraph(f"<b>Gestor:</b> {manager_name}", styles['LPSInfo']))
    elements.append(Paragraph(f"<b>Data:</b> {datetime.now().strftime('%d/%m/%Y')}", styles['LPSInfo']))
    elements.append(Spacer(1, 25))
    
    # Profile section
    elements.append(Paragraph("Perfil de Lideranca", styles['LPSSection']))
    elements.append(Paragraph(f"<b>Perfil Dominante:</b> {employee_data[6] or 'N/A'}", styles['LPSBody']))
    elements.append(Paragraph(f"<b>Perfil Secundario:</b> {employee_data[7] or 'N/A'}", styles['LPSBody']))
    elements.append(Spacer(1, 15))
    
    # Bion role section
    elements.append(Paragraph("Dinamica Grupal (Bion)", styles['LPSSection']))
    bion_role = employee_data[9] or 'N/A'
    elements.append(Paragraph(f"<b>Papel de Bion:</b> {bion_role}", styles['LPSBody']))
    
    # Bion role description
    bion_descriptions = {
        "Porta-voz": "Expressa o que o grupo sente mas nao consegue dizer. Captam tensoes inconscientes do grupo.",
        "Bode Expiatorio": "Absorve projecoes negativas do grupo. Frequentemente culpado por problemas sistemicos.",
        "Dependente": "Busca protecao constante no lider, evita autonomia. Requer contencao e orientacao.",
        "Lider de Luta-Fuga": "Reativo a ameacas reais ou imaginarias, mobiliza o grupo para ataque ou fuga.",
        "Sabotador Silencioso": "Resiste passivamente as mudancas. Concordancia superficial, boicote sutil."
    }
    if bion_role in bion_descriptions:
        elements.append(Paragraph(f"<i>{bion_descriptions[bion_role]}</i>", styles['LPSBody']))
    
    # Footer
    elements.append(Spacer(1, 40))
    elements.append(Paragraph("_" * 60, styles['LPSInfo']))
    elements.append(Paragraph("Gerado pela Plataforma LPS - Lideranca Psicanalitica", styles['LPSInfo']))
    elements.append(Paragraph("Viviane Nishiura & Equipe LPS", styles['LPSInfo']))
    
    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()

def generate_ai_analysis_pdf(manager_name, analysis_text, employees_data):
    """Generate a PDF report from AI analysis with LPS branding."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.75*inch, bottomMargin=0.75*inch)
    styles = create_pdf_styles()
    elements = []
    
    # Styled header with LPS branding
    elements.append(create_pdf_header_table())
    elements.append(Spacer(1, 20))
    
    # Report title
    elements.append(Paragraph("Analise de IA - Dinamicas de Equipe", styles['LPSSection']))
    elements.append(Spacer(1, 15))
    
    # Manager info
    elements.append(Paragraph(f"<b>Gestor:</b> {manager_name}", styles['LPSInfo']))
    elements.append(Paragraph(f"<b>Data da Analise:</b> {datetime.now().strftime('%d/%m/%Y as %H:%M')}", styles['LPSInfo']))
    elements.append(Spacer(1, 20))
    
    # Team summary
    elements.append(Paragraph("Composicao da Equipe Analisada", styles['LPSSection']))
    completed_count = sum(1 for emp in employees_data if emp[10] == 1)
    elements.append(Paragraph(f"<b>Funcionarios mapeados:</b> {completed_count}", styles['LPSBody']))
    
    # Bion distribution
    bion_roles = {}
    for emp in employees_data:
        if emp[10] == 1 and emp[9]:
            bion_roles[emp[9]] = bion_roles.get(emp[9], 0) + 1
    if bion_roles:
        elements.append(Paragraph("<b>Distribuicao de Papeis de Bion:</b>", styles['LPSBody']))
        for role, count in bion_roles.items():
            elements.append(Paragraph(f"  - {role}: {count} funcionario(s)", styles['LPSBody']))
    
    elements.append(Spacer(1, 20))
    
    # AI Analysis
    elements.append(Paragraph("Analise da Consultora de IA", styles['LPSSection']))
    
    # Split analysis into paragraphs
    paragraphs = analysis_text.split('\n\n')
    for para in paragraphs:
        if para.strip():
            clean_para = para.replace('\n', ' ').strip()
            clean_para = clean_para.replace('**', '')
            clean_para = clean_para.replace('*', '')
            elements.append(Paragraph(clean_para, styles['LPSBody']))
            elements.append(Spacer(1, 5))
    
    # Footer
    elements.append(Spacer(1, 30))
    elements.append(Paragraph("_" * 60, styles['LPSInfo']))
    elements.append(Paragraph("Analise gerada pela LPSChat - Consultora de IA em Psicanalise e Neurociencia", styles['LPSInfo']))
    elements.append(Paragraph("Plataforma LPS - Viviane Nishiura & Equipe LPS", styles['LPSInfo']))
    
    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()

def generate_team_chart(employees_data, manager_name):
    """Generate a team profile distribution chart as PNG."""
    # Count profiles
    profile_counts = {}
    bion_counts = {}
    
    for emp in employees_data:
        if emp[10] == 1:  # completed
            # Count dominant profiles
            if emp[6]:
                profile_counts[emp[6]] = profile_counts.get(emp[6], 0) + 1
            # Count Bion roles
            if emp[9]:
                bion_counts[emp[9]] = bion_counts.get(emp[9], 0) + 1
    
    if not profile_counts and not bion_counts:
        return None
    
    # Create figure with two subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle(f'Perfil da Equipe - {manager_name}', fontsize=16, color='#0D3B66', fontweight='bold')
    
    # Colors matching LPS brand
    colors_profile = ['#0D3B66', '#1a4f7a', '#2d6a9f', '#4080b5', '#5596c9', '#6aabdc']
    colors_bion = ['#F4D35E', '#e6c54e', '#d9b83e', '#ccab2e', '#bf9e1e', '#b2910e']
    
    # Profile distribution pie chart
    if profile_counts:
        labels1 = list(profile_counts.keys())
        sizes1 = list(profile_counts.values())
        ax1.pie(sizes1, labels=labels1, colors=colors_profile[:len(labels1)], autopct='%1.0f%%', startangle=90)
        ax1.set_title('Perfis de Lideranca', fontsize=12, color='#0D3B66')
    else:
        ax1.text(0.5, 0.5, 'Sem dados', ha='center', va='center')
        ax1.set_title('Perfis de Lideranca', fontsize=12, color='#0D3B66')
    
    # Bion roles bar chart
    if bion_counts:
        labels2 = list(bion_counts.keys())
        sizes2 = list(bion_counts.values())
        bars = ax2.barh(labels2, sizes2, color=colors_bion[:len(labels2)])
        ax2.set_xlabel('Quantidade')
        ax2.set_title('Papeis de Bion', fontsize=12, color='#0D3B66')
        ax2.set_xlim(0, max(sizes2) + 1)
        for bar, size in zip(bars, sizes2):
            ax2.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2, str(size), va='center')
    else:
        ax2.text(0.5, 0.5, 'Sem dados', ha='center', va='center')
        ax2.set_title('Papeis de Bion', fontsize=12, color='#0D3B66')
    
    plt.tight_layout()
    
    # Save to buffer
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    buffer.seek(0)
    return buffer.getvalue()

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

# Render Paywall Box
def render_paywall():
    st.markdown("""
        <div class="paywall-box">
            <div class="paywall-icon">🔒</div>
            <div class="paywall-title">Conteúdo Exclusivo para Alunos</div>
            <div class="paywall-text">
                Liberação apenas após confirmação de pagamento.<br>
                Entre em contato para adquirir seu acesso.
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("👤 Já sou aluno - Entrar", use_container_width=True, key="paywall_login"):
            st.session_state.page = "Login"
            st.rerun()
    with col2:
        st.markdown(f"""
            <a href="{WHATSAPP_URL}" target="_blank" class="cta-button" style="display: block; text-align: center; background-color: #25D366; color: white;">
                💬 Comprar Curso
            </a>
        """, unsafe_allow_html=True)

# GLOBAL EMPLOYEE ACCESS GUARD - Force employees to stay on EmployeeAssessment
# This runs before every page render to prevent any navigation
if is_employee_access and page != "EmployeeAssessment":
    st.session_state.page = "EmployeeAssessment"
    page = "EmployeeAssessment"

# Pages
if page == "Home":
    # Public landing page with sections
    render_public_header()
    
    current_section = st.session_state.section
    
    # HOME SECTION - Hero
    if current_section == "home":
        # Hero Section
        st.markdown("""
            <div class="hero-section">
                <div class="hero-title">Transforme Sua Liderança com a Ciência do Inconsciente</div>
                <div class="hero-subtitle">
                    Uma metodologia inovadora que une <strong>Psicanálise</strong> e <strong>Neurociência</strong><br>
                    para desenvolver líderes mais conscientes, empáticos e eficazes.
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Video Intro
        st.write("")
        vimeo_video("https://vimeo.com/1154502544")
        
        # Features
        st.write("---")
        st.markdown("### Por Que Escolher o LPS?")
        
        feat_cols = st.columns(3)
        with feat_cols[0]:
            st.markdown("""
                <div style="text-align: center; padding: 1rem;">
                    <div style="font-size: 2.5rem;">🧠</div>
                    <h4 style="color: #0D3B66;">Neurociência + Psicanálise</h4>
                    <p style="color: #666;">Metodologia única que une ciência do cérebro com análise profunda do comportamento.</p>
                </div>
            """, unsafe_allow_html=True)
        with feat_cols[1]:
            st.markdown("""
                <div style="text-align: center; padding: 1rem;">
                    <div style="font-size: 2.5rem;">📊</div>
                    <h4 style="color: #0D3B66;">Assessment Completo</h4>
                    <p style="color: #666;">Descubra seu perfil de liderança e mapeie sua equipe com ferramentas exclusivas.</p>
                </div>
            """, unsafe_allow_html=True)
        with feat_cols[2]:
            st.markdown("""
                <div style="text-align: center; padding: 1rem;">
                    <div style="font-size: 2.5rem;">💬</div>
                    <h4 style="color: #0D3B66;">IA Consultora</h4>
                    <p style="color: #666;">Converse com a LPSChat para receber insights personalizados sobre sua equipe.</p>
                </div>
            """, unsafe_allow_html=True)
        
        # CTA
        st.write("")
        cta_cols = st.columns([1, 2, 1])
        with cta_cols[1]:
            st.markdown(f"""
                <a href="{WHATSAPP_URL}" target="_blank" class="cta-button" style="display: block; text-align: center; font-size: 1.2rem;">
                    💬 Comprar Curso / Solicitar Orçamento
                </a>
            """, unsafe_allow_html=True)
    
    # SOBRE SECTION
    elif current_section == "sobre":
        st.markdown('<div class="section-title">Sobre o Programa LPS</div>', unsafe_allow_html=True)
        
        st.markdown("""
            <div class="about-card">
                <h3 style="color: #0D3B66;">O que é Liderança Psicanalítica?</h3>
                <p>A Liderança Psicanalítica é uma abordagem inovadora que integra conceitos da psicanálise com práticas de gestão moderna. 
                Desenvolvida por <strong>Viviane Nishiura</strong>, esta metodologia ajuda líderes a compreenderem as dinâmicas 
                inconscientes que influenciam suas equipes e tomadas de decisão.</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
            <div class="about-card">
                <h3 style="color: #0D3B66;">Quem é Viviane Nishiura?</h3>
                <p>Psicóloga clínica e consultora organizacional com mais de 15 anos de experiência em desenvolvimento de líderes. 
                Especialista em psicanálise aplicada às organizações, Viviane criou o método LPS para ajudar gestores 
                a transformarem suas relações de trabalho através do autoconhecimento.</p>
            </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 1])
        with col1:
            st.markdown(f"""
                <a href="{WHATSAPP_URL}" target="_blank" class="cta-button" style="display: block; text-align: center;">
                    💬 Falar com a Consultora
                </a>
            """, unsafe_allow_html=True)
    
    # CURSO SECTION - Module Cards with Paywall
    elif current_section == "curso":
        st.markdown('<div class="section-title">Programa de Formação LPS</div>', unsafe_allow_html=True)
        st.write("6 módulos completos para transformar sua liderança")
        st.write("")
        
        # Module Cards Grid - 2 rows of 3
        row1 = st.columns(3)
        for idx, col in enumerate(row1):
            if idx < len(MODULES_DATA):
                mod = MODULES_DATA[idx]
                with col:
                    st.markdown(f"""
                        <div class="module-card">
                            <div class="module-icon">{mod['icon']}</div>
                            <div class="module-title">{mod['name'].split(': ')[1]}</div>
                            <div class="module-desc">{mod['description']}</div>
                        </div>
                    """, unsafe_allow_html=True)
                    if st.button("Ver Conteúdo", key=f"btn_mod_{mod['id']}", use_container_width=True):
                        st.session_state.selected_module = mod['id']
                        if not st.session_state.authenticated:
                            st.session_state.show_login_modal = True
                            st.rerun()
                        else:
                            st.session_state.page = "LPS Curso"
                            st.rerun()
        
        st.write("")
        row2 = st.columns(3)
        for idx, col in enumerate(row2):
            mod_idx = idx + 3
            if mod_idx < len(MODULES_DATA):
                mod = MODULES_DATA[mod_idx]
                with col:
                    st.markdown(f"""
                        <div class="module-card">
                            <div class="module-icon">{mod['icon']}</div>
                            <div class="module-title">{mod['name'].split(': ')[1]}</div>
                            <div class="module-desc">{mod['description']}</div>
                        </div>
                    """, unsafe_allow_html=True)
                    if st.button("Ver Conteúdo", key=f"btn_mod_{mod['id']}", use_container_width=True):
                        st.session_state.selected_module = mod['id']
                        if not st.session_state.authenticated:
                            st.session_state.show_login_modal = True
                            st.rerun()
                        else:
                            st.session_state.page = "LPS Curso"
                            st.rerun()
        
        # Paywall Modal
        if st.session_state.show_login_modal:
            st.write("")
            render_paywall()
            if st.button("Fechar", key="close_modal"):
                st.session_state.show_login_modal = False
                st.rerun()
        
        # CTA
        st.write("---")
        cta_cols = st.columns([1, 2, 1])
        with cta_cols[1]:
            st.markdown(f"""
                <a href="{WHATSAPP_URL}" target="_blank" class="cta-button" style="display: block; text-align: center; font-size: 1.1rem;">
                    💬 Comprar Curso Completo
                </a>
            """, unsafe_allow_html=True)
    
    # LPSTEST SECTION - Preview with Paywall
    elif current_section == "lpstest":
        st.markdown('<div class="section-title">LPSTest - Assessment de Liderança</div>', unsafe_allow_html=True)
        
        st.markdown("""
            <div class="about-card">
                <h3 style="color: #0D3B66;">Descubra Seu Perfil de Liderança</h3>
                <p>O LPSTest é um assessment exclusivo com <strong>48 questões</strong> desenvolvidas para mapear 
                seu perfil de liderança através de 6 dimensões psicanalíticas:</p>
                <ul style="color: #666;">
                    <li><strong>Autoridade</strong> - Como você exerce e percebe sua autoridade</li>
                    <li><strong>Contenção</strong> - Sua capacidade de manter a calma em crises</li>
                    <li><strong>Narcisismo</strong> - Sua relação com reconhecimento e validação</li>
                    <li><strong>Estrutura</strong> - Sua necessidade de controle e organização</li>
                    <li><strong>Relação</strong> - Suas dinâmicas de transferência com a equipe</li>
                    <li><strong>Reflexão</strong> - Sua capacidade de autoconhecimento</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
            <div style="text-align: center; padding: 2rem;">
                <div style="font-size: 4rem;">📊</div>
                <h3 style="color: #0D3B66;">Receba Seu Perfil Híbrido</h3>
                <p style="color: #666;">Ao completar o assessment, você recebe um relatório com seu perfil dominante, 
                perfil secundário e papel grupal segundo Bion.</p>
            </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.authenticated:
            if st.button("Fazer o LPSTest Agora", use_container_width=True, type="primary"):
                st.session_state.page = "LPSTest"
                st.rerun()
        else:
            render_paywall()
    
    # LPSCHAT SECTION - Preview with Paywall
    elif current_section == "lpschat":
        st.markdown('<div class="section-title">LPSChat - Consultor de IA</div>', unsafe_allow_html=True)
        
        st.markdown("""
            <div class="about-card">
                <h3 style="color: #0D3B66;">Sua Consultora Psicanalítica 24/7</h3>
                <p>O LPSChat é uma inteligência artificial treinada com os conceitos da metodologia LPS. 
                Ela tem acesso ao seu perfil e da sua equipe, oferecendo:</p>
                <ul style="color: #666;">
                    <li>Análise das dinâmicas grupais da sua equipe</li>
                    <li>Identificação de padrões de transferência</li>
                    <li>Sugestões de intervenções baseadas em Bion</li>
                    <li>Orientações para gestão de conflitos</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
            <div style="background-color: #F5F5F5; padding: 1.5rem; border-radius: 10px; margin: 1rem 0;">
                <p style="color: #666; font-style: italic;">"Minha equipe está em conflito constante. O João parece 
                sempre ser culpado por tudo. Como posso intervir?"</p>
                <p style="color: #0D3B66; margin-top: 1rem;"><strong>LPSChat:</strong> Pelo que descreve, João pode 
                estar assumindo o papel de <em>Bode Expiatório</em> do grupo - uma dinâmica comum quando há ansiedade 
                não processada. Sugiro focar na <em>Tarefa Real</em> para resgatar a racionalidade...</p>
            </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.authenticated:
            if st.button("Acessar LPSChat", use_container_width=True, type="primary"):
                st.session_state.page = "LPSChat"
                st.rerun()
        else:
            render_paywall()
    
    # MENTORIA SECTION
    elif current_section == "mentoria":
        st.markdown('<div class="section-title">Mentoria Individual</div>', unsafe_allow_html=True)
        
        st.markdown("""
            <div class="about-card">
                <h3 style="color: #0D3B66;">Acompanhamento Personalizado</h3>
                <p>Sessões individuais com Viviane Nishiura para aprofundar seu desenvolvimento como líder psicanalítico:</p>
                <ul style="color: #666;">
                    <li>Análise do seu perfil LPSTest</li>
                    <li>Supervisão de casos da sua equipe</li>
                    <li>Desenvolvimento de estratégias personalizadas</li>
                    <li>Acompanhamento mensal do seu progresso</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
            <div style="text-align: center; margin-top: 2rem;">
                <a href="{WHATSAPP_URL}" target="_blank" class="cta-button" style="font-size: 1.2rem;">
                    📅 Agendar Mentoria
                </a>
            </div>
        """, unsafe_allow_html=True)
    
    # SOLUÇÕES SECTION
    elif current_section == "soluções":
        st.markdown('<div class="section-title">Soluções Corporativas</div>', unsafe_allow_html=True)
        
        sol_cols = st.columns(2)
        with sol_cols[0]:
            st.markdown("""
                <div class="solution-card">
                    <div class="solution-title">Treinamento In-Company</div>
                    <p>Formação completa para sua equipe de líderes com conteúdo personalizado para sua empresa.</p>
                </div>
            """, unsafe_allow_html=True)
        with sol_cols[1]:
            st.markdown("""
                <div class="solution-card">
                    <div class="solution-title">Consultoria Organizacional</div>
                    <p>Diagnóstico e intervenção em dinâmicas grupais problemáticas na sua organização.</p>
                </div>
            """, unsafe_allow_html=True)
        
        st.write("")
        sol_cols2 = st.columns(2)
        with sol_cols2[0]:
            st.markdown("""
                <div class="solution-card">
                    <div class="solution-title">Assessment de Equipes</div>
                    <p>Mapeamento completo de perfis e dinâmicas da sua equipe com relatório executivo.</p>
                </div>
            """, unsafe_allow_html=True)
        with sol_cols2[1]:
            st.markdown("""
                <div class="solution-card">
                    <div class="solution-title">Palestras e Workshops</div>
                    <p>Eventos sobre liderança psicanalítica para convenções e encontros corporativos.</p>
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown(f"""
            <div style="text-align: center; margin-top: 2rem;">
                <a href="{WHATSAPP_URL}" target="_blank" class="cta-button" style="font-size: 1.2rem;">
                    💼 Solicitar Orçamento
                </a>
            </div>
        """, unsafe_allow_html=True)
    
    # CONTATO SECTION
    elif current_section == "contato":
        st.markdown('<div class="section-title">Entre em Contato</div>', unsafe_allow_html=True)
        
        st.markdown("""
            <div style="text-align: center; padding: 2rem;">
                <div style="font-size: 4rem;">📱</div>
                <h3 style="color: #0D3B66;">Fale Diretamente Conosco</h3>
                <p style="color: #666; font-size: 1.1rem;">
                    Tire suas dúvidas, solicite orçamentos ou agende sua mentoria.<br>
                    Atendimento personalizado via WhatsApp.
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
            <div style="text-align: center;">
                <a href="{WHATSAPP_URL}" target="_blank" style="display: inline-block; background-color: #25D366; color: white; padding: 20px 50px; border-radius: 50px; font-weight: bold; font-size: 1.3rem; text-decoration: none;">
                    💬 Iniciar Conversa no WhatsApp
                </a>
            </div>
        """, unsafe_allow_html=True)
        
        st.write("")
        st.markdown("""
            <div style="text-align: center; color: #666; margin-top: 2rem;">
                <p><strong>E-mail:</strong> contato@liderancapsicanalitica.com.br</p>
                <p><strong>Instagram:</strong> @liderancapsicanalitica</p>
            </div>
        """, unsafe_allow_html=True)

elif page == "Login":
    render_login_page()

elif page == "Dashboard":
    # Authenticated user dashboard
    if not st.session_state.authenticated:
        st.session_state.page = "Home"
        st.rerun()
    
    render_public_header()
    
    # Get manager data
    manager_data = get_manager_by_user(st.session_state.user['id'])
    user_id = st.session_state.user['id']
    manager_id = manager_data['id'] if manager_data else None
    
    st.markdown(f"<h2 style='color: #0D3B66;'>Bem-vindo(a), {st.session_state.user['name']}!</h2>", unsafe_allow_html=True)
    
    # Dashboard CSS
    st.markdown("""
        <style>
        .dashboard-card {
            background: white;
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            border-left: 4px solid #F4D35E;
            margin-bottom: 1rem;
        }
        .dashboard-card h3 {
            color: #0D3B66;
            margin: 0 0 1rem 0;
            font-size: 1.1rem;
        }
        .progress-module {
            display: flex;
            align-items: center;
            margin-bottom: 0.5rem;
        }
        .progress-module-name {
            flex: 1;
            font-size: 0.9rem;
            color: #333;
        }
        .progress-module-bar {
            flex: 2;
            background: #e0e0e0;
            border-radius: 10px;
            height: 8px;
            margin: 0 10px;
        }
        .progress-module-fill {
            background: linear-gradient(90deg, #0D3B66, #F4D35E);
            height: 100%;
            border-radius: 10px;
            transition: width 0.3s ease;
        }
        .progress-module-percent {
            font-size: 0.85rem;
            color: #666;
            min-width: 40px;
            text-align: right;
        }
        .stat-box {
            text-align: center;
            padding: 1rem;
            background: #f8f9fa;
            border-radius: 8px;
        }
        .stat-number {
            font-size: 2rem;
            font-weight: bold;
            color: #0D3B66;
        }
        .stat-label {
            font-size: 0.85rem;
            color: #666;
        }
        .insight-item {
            padding: 0.75rem;
            margin-bottom: 0.5rem;
            border-radius: 8px;
            font-size: 0.9rem;
        }
        .insight-warning {
            background: #fff3cd;
            border-left: 3px solid #ffc107;
        }
        .insight-info {
            background: #cce5ff;
            border-left: 3px solid #0d6efd;
        }
        .insight-alert {
            background: #f8d7da;
            border-left: 3px solid #dc3545;
        }
        .insight-success {
            background: #d4edda;
            border-left: 3px solid #28a745;
        }
        .mentoring-btn {
            display: inline-block;
            background: linear-gradient(135deg, #0D3B66, #1a5490);
            color: white;
            padding: 15px 30px;
            border-radius: 25px;
            text-decoration: none;
            font-weight: bold;
            text-align: center;
            margin-top: 1rem;
        }
        .mentoring-btn:hover {
            opacity: 0.9;
            color: white;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Main Dashboard Grid
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Course Progress Card
        st.markdown("<div class='dashboard-card'><h3>Progresso do Curso</h3>", unsafe_allow_html=True)
        
        module_status = get_module_completion_status(user_id)
        total_completed = 0
        total_lessons = 0
        
        for mod_id, status in module_status.items():
            total_completed += status['completed']
            total_lessons += status['total']
            percentage = int(status['percentage'])
            st.markdown(f"""
                <div class='progress-module'>
                    <span class='progress-module-name'>{status['name'][:25]}...</span>
                    <div class='progress-module-bar'>
                        <div class='progress-module-fill' style='width: {percentage}%'></div>
                    </div>
                    <span class='progress-module-percent'>{percentage}%</span>
                </div>
            """, unsafe_allow_html=True)
        
        overall_progress = (total_completed / total_lessons * 100) if total_lessons > 0 else 0
        st.markdown(f"<p style='text-align: center; margin-top: 1rem; color: #0D3B66; font-weight: bold;'>Progresso Total: {overall_progress:.0f}%</p></div>", unsafe_allow_html=True)
        
        # AI Insights Card
        if manager_id:
            st.markdown("<div class='dashboard-card'><h3>Insights da IA sobre sua Equipe</h3>", unsafe_allow_html=True)
            
            insights = get_ai_insights(manager_id, user_id)
            if insights:
                for insight in insights:
                    insight_class = f"insight-{insight['type']}"
                    icon = {'warning': 'O', 'info': 'i', 'alert': '!', 'success': '✓'}.get(insight['type'], 'i')
                    st.markdown(f"<div class='insight-item {insight_class}'>{insight['message']}</div>", unsafe_allow_html=True)
            else:
                st.markdown("<p style='color: #666;'>Nenhum insight disponível ainda. Complete o LPSTest e mapeie sua equipe.</p>", unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        # Assessment Stats Card
        if manager_id:
            st.markdown("<div class='dashboard-card'><h3>Gestão de LPSTest</h3>", unsafe_allow_html=True)
            
            stats = get_assessment_stats(manager_id)
            
            stat_cols = st.columns(2)
            with stat_cols[0]:
                st.markdown(f"""
                    <div class='stat-box'>
                        <div class='stat-number'>{stats['applied']}</div>
                        <div class='stat-label'>Aplicados</div>
                    </div>
                """, unsafe_allow_html=True)
            with stat_cols[1]:
                st.markdown(f"""
                    <div class='stat-box'>
                        <div class='stat-number'>{stats['remaining']}</div>
                        <div class='stat-label'>Restantes</div>
                    </div>
                """, unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        # Mentoring Card
        st.markdown("<div class='dashboard-card'><h3>Mentoria Individual</h3>", unsafe_allow_html=True)
        st.markdown("<p style='font-size: 0.9rem; color: #666;'>Agende uma sessão exclusiva com Viviane Nishiura para aprofundar seus insights de liderança.</p>", unsafe_allow_html=True)
        st.markdown(f"""
            <a href='{WHATSAPP_URL}' target='_blank' class='mentoring-btn' data-testid='button-agendar-mentoria'>
                Agendar Mentoria
            </a>
        """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.write("---")
    
    # Quick Access Buttons
    st.markdown("<h4 style='color: #0D3B66;'>Acesso Rápido</h4>", unsafe_allow_html=True)
    dash_cols = st.columns(4)
    with dash_cols[0]:
        if st.button("Curso", key="btn-dash-curso", use_container_width=True):
            st.session_state.page = "LPS Curso"
            st.rerun()
    with dash_cols[1]:
        if st.button("LPSTest", key="btn-dash-test", use_container_width=True):
            st.session_state.page = "LPSTest"
            st.rerun()
    with dash_cols[2]:
        if st.button("Equipe", key="btn-dash-equipe", use_container_width=True):
            st.session_state.page = "TeamManagement"
            st.rerun()
    with dash_cols[3]:
        # LPSChat with access control
        course_completed = is_course_completed(user_id)
        if course_completed:
            if st.button("LPSChat", key="btn-dash-chat", use_container_width=True):
                st.session_state.page = "LPSChat"
                st.rerun()
        else:
            if st.button("LPSChat (Bloqueado)", key="btn-dash-chat-locked", use_container_width=True, disabled=True):
                pass
            st.caption("Complete os módulos teóricos para liberar")
    
    st.write("---")
    
    # Admin section (only for administrators)
    admin_col1, admin_col2 = st.columns([3, 1])
    with admin_col1:
        if st.button("Sair", key="btn-logout", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.user = None
            st.session_state.manager_data = None
            st.session_state.page = "Home"
            st.rerun()
    with admin_col2:
        if st.button("Admin", key="btn-admin", use_container_width=True):
            st.session_state.page = "AdminEmail"
            st.rerun()

elif page == "LPS Curso":
    if not st.session_state.authenticated:
        st.session_state.page = "Login"
        st.rerun()
    
    st.title("Programa LPS")
    
    # Load progress from database
    user_id = st.session_state.user['id']
    db_progress = get_course_progress(user_id)
    if db_progress:
        st.session_state.progress = db_progress
    
    total_lessons = sum(len(m['videos']) for m in MODULES_DATA)
    completed_lessons = sum(1 for v in st.session_state.progress.values() if v)
    
    # Overall progress bar
    st.markdown(f"<p style='color: #0D3B66; font-weight: bold;'>Progresso Geral: {completed_lessons}/{total_lessons} aulas concluídas</p>", unsafe_allow_html=True)
    st.progress(completed_lessons / total_lessons if total_lessons > 0 else 0)
    
    st.write("---")
    
    for mod in MODULES_DATA:
        with st.expander(mod['name']):
            for v_idx, v_url in enumerate(mod['videos']):
                lesson_id = f"m{mod['id']}_v{v_idx}"
                vimeo_video(v_url)
                new_value = st.checkbox("Concluí esta aula", value=st.session_state.progress.get(lesson_id, False), key=lesson_id)
                if new_value != st.session_state.progress.get(lesson_id, False):
                    st.session_state.progress[lesson_id] = new_value
                    save_course_progress(user_id, st.session_state.progress)
            if os.path.exists(mod['file']):
                with open(mod['file'], "rb") as f:
                    st.download_button("Material de Apoio", f, os.path.basename(mod['file']), key=f"dl_{mod['id']}")

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
    st.title("Gestao de Equipe")
    
    manager_data = st.session_state.manager_data
    if not manager_data:
        st.error("Dados do gestor nao encontrados. Por favor, faca login novamente.")
    else:
        manager_id = manager_data['id']
        manager_profile = manager_data if manager_data.get('dominant') else None
        
        # Get employees data first
        employees = get_manager_employees(manager_id)
        
        # Initialize session state for showing links
        if 'show_employee_links' not in st.session_state:
            st.session_state.show_employee_links = False
        
        has_existing_links = len(employees) > 0
        
        # Create tabs for organization
        tab_convite, tab_resultados = st.tabs(["Gerar Convites", "Resultados da Equipe"])
        
        with tab_convite:
            # Show Manager Profile First
            if manager_profile:
                st.markdown(f"""
                    <div class="result-card" style="margin-bottom: 20px;">
                        <div class="profile-title">Seu Perfil (Gestor)</div>
                        <p style="text-align: center; font-size: 1.3rem;"><strong>{manager_profile['dominant']} + {manager_profile['secondary']}</strong></p>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.warning("Complete seu LPSTest primeiro para ver a comparacao com sua equipe.")
            
            st.write("---")
            st.subheader("Gerar Link de Convite para Equipe")
            
            if not st.session_state.show_employee_links and not has_existing_links:
                st.markdown("""
                    <div style='background-color: #e8f4f8; padding: 1.5rem; border-radius: 8px; margin-bottom: 1rem;'>
                        <p style='margin: 0; color: #0D3B66;'>
                            <strong>Como funciona:</strong> Clique no botao abaixo para gerar links unicos para ate 4 funcionarios. 
                            Envie cada link por WhatsApp ou e-mail. Ao clicar, eles responderao o assessment e voce recebera os resultados aqui.
                        </p>
                    </div>
                """, unsafe_allow_html=True)
                
                if st.button("Gerar Link de Convite para Equipe", key="btn-generate-team-links", use_container_width=True, type="primary"):
                    for slot in range(1, 5):
                        generate_employee_link(manager_id, slot)
                    st.session_state.show_employee_links = True
                    st.rerun()
            else:
                st.session_state.show_employee_links = True
                
                st.markdown("""
                    <div style='background-color: #d4edda; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;'>
                        <p style='margin: 0; color: #155724;'>
                            Links gerados! Copie cada link e envie para o funcionario correspondente.
                        </p>
                    </div>
                """, unsafe_allow_html=True)
                
                base_url = get_app_url()
                cols = st.columns(4)
                
                for i, col in enumerate(cols):
                    with col:
                        slot = i + 1
                        token = generate_employee_link(manager_id, slot)
                        full_link = f"{base_url}?token={token}" if base_url else f"?token={token}"
                        
                        slot_employee = next((e for e in employees if e[3] == slot), None)
                        
                        if slot_employee and slot_employee[10] == 1:
                            st.markdown(f"**{slot_employee[4] or 'Funcionario ' + str(slot)}**")
                            st.success("Concluido")
                        else:
                            st.markdown(f"**Funcionario {slot}**")
                            st.code(full_link, language=None)
                            if slot_employee:
                                st.caption("Aguardando resposta")
                            else:
                                st.caption("Copie e envie")
        
        with tab_resultados:
            st.subheader("Resultados da Equipe")
            
            if employees:
                completed_count = sum(1 for e in employees if e[10] == 1)
                manager_name = st.session_state.user['name'] if st.session_state.user else "Gestor"
                
                st.metric("Respostas Recebidas", f"{completed_count}/4")
                
                if completed_count > 0:
                    st.markdown("#### Exportar Relatorios")
                    
                    col_csv, col_pdf, col_chart = st.columns(3)
                    
                    with col_csv:
                        csv_data = "Nome,E-mail,Perfil Dominante,Perfil Secundario,Papel de Bion\n"
                        for emp in employees:
                            if emp[10] == 1:
                                emp_name = emp[4] or f'Funcionario {emp[3]}'
                                csv_data += f'"{emp_name}","{emp[5]}","{emp[6]}","{emp[7]}","{emp[9]}"\n'
                        
                        st.download_button(
                            label="Baixar CSV",
                            data=csv_data,
                            file_name="resultados_equipe_lps.csv",
                            mime="text/csv",
                            use_container_width=True
                        )
                    
                    with col_pdf:
                        pdf_data = generate_team_pdf_report(manager_name, employees)
                        st.download_button(
                            label="Baixar PDF",
                            data=pdf_data,
                            file_name="relatorio_equipe_lps.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
                    
                    with col_chart:
                        chart_data = generate_team_chart(employees, manager_name)
                        if chart_data:
                            st.download_button(
                                label="Baixar Grafico",
                                data=chart_data,
                                file_name="grafico_perfil_equipe.png",
                                mime="image/png",
                                use_container_width=True
                            )
                    
                    st.write("---")
                    
                    # Display team chart preview
                    st.markdown("#### Grafico do Perfil da Equipe")
                    chart_preview = generate_team_chart(employees, manager_name)
                    if chart_preview:
                        st.image(chart_preview, use_container_width=True)
                
                if manager_profile and completed_count > 0:
                    st.markdown(f"""
                        <div style="background-color: #0D3B66; color: white; padding: 10px; border-radius: 8px; margin: 20px 0 10px 0;">
                            <strong>Comparacao:</strong> Seu perfil ({manager_profile['dominant']}) vs Equipe
                        </div>
                    """, unsafe_allow_html=True)
                
                # Only show completed employees in results tab
                completed_employees = [emp for emp in employees if emp[10] == 1]
                
                if completed_employees:
                    for emp in completed_employees:
                        emp_name = emp[4] or f'Funcionario {emp[3]}'
                        
                        with st.container():
                            col_info, col_csv_ind, col_pdf_ind = st.columns([4, 1, 1])
                            
                            with col_info:
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
                            
                            with col_csv_ind:
                                individual_csv = f"Nome,E-mail,Perfil Dominante,Perfil Secundario,Papel de Bion\n"
                                individual_csv += f'"{emp_name}","{emp[5]}","{emp[6]}","{emp[7]}","{emp[9]}"\n'
                                
                                safe_name = emp_name.replace(" ", "_").lower()[:20]
                                st.download_button(
                                    label="CSV",
                                    data=individual_csv,
                                    file_name=f"resultado_{safe_name}.csv",
                                    mime="text/csv",
                                    key=f"download_csv_{emp[0]}"
                                )
                            
                            with col_pdf_ind:
                                individual_pdf = generate_individual_pdf_report(emp, manager_name)
                                st.download_button(
                                    label="PDF",
                                    data=individual_pdf,
                                    file_name=f"resultado_{safe_name}.pdf",
                                    mime="application/pdf",
                                    key=f"download_pdf_{emp[0]}"
                                )
                else:
                    st.info("Nenhum funcionario respondeu ainda. Os resultados aparecerao aqui assim que completarem o assessment.")
            else:
                st.info("Nenhum convite gerado ainda. Va para a aba 'Gerar Convites' para criar links.")

elif page == "EmployeeAssessment":
    token = st.session_state.employee_token
    employee = get_employee_by_token(token)
    
    if not employee:
        st.error("Link invalido ou expirado.")
        st.markdown("""
            <div style='text-align: center; padding: 2rem;'>
                <p>Se você recebeu este link do seu gestor, entre em contato para solicitar um novo link.</p>
            </div>
        """, unsafe_allow_html=True)
    elif employee[10] == 1:  # already completed - Thank You page
        st.markdown("""
            <div style='text-align: center; padding: 2rem;'>
                <h1 style='color: #0D3B66;'>Obrigado pela participacao!</h1>
            </div>
        """, unsafe_allow_html=True)
        st.markdown(f"""
            <div class="result-card" style="max-width: 600px; margin: 0 auto;">
                <div class="profile-title">Seu Perfil foi Registrado</div>
                <p style="text-align: center; font-size: 1.4rem;"><strong>{employee[6]} + {employee[7]}</strong></p>
                <div style="background-color: #F4D35E; padding: 10px; border-radius: 20px; text-align: center; margin: 15px auto; max-width: 200px;">
                    <strong style="color: #0D3B66;">{employee[9]}</strong>
                </div>
                <p style="text-align: center; font-size: 0.95rem; color: #666; margin-top: 20px;">
                    Seu resultado foi salvo e enviado para seu e-mail ({employee[5]}).
                </p>
                <p style="text-align: center; font-size: 0.9rem; color: #888; margin-top: 10px;">
                    Seu gestor recebera uma notificacao e podera discutir estrategias de desenvolvimento com voce em breve.
                </p>
            </div>
        """, unsafe_allow_html=True)
        st.markdown("""
            <div style='text-align: center; margin-top: 2rem; padding: 1rem; background-color: #f5f5f5; border-radius: 10px;'>
                <p style='color: #666; margin: 0;'>Voce pode fechar esta pagina. Obrigado por participar do LPS!</p>
            </div>
        """, unsafe_allow_html=True)
    else:
        # Assessment Form - clean page for employees
        st.markdown("""
            <div style='text-align: center; margin-bottom: 1rem;'>
                <h1 style='color: #0D3B66;'>LPSTest - Assessment de Equipe</h1>
                <p style='color: #666;'>Responda as afirmacoes abaixo de forma honesta. Seus resultados individuais sao confidenciais.</p>
            </div>
        """, unsafe_allow_html=True)
        
        with st.form("employee_assessment"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Seu Nome Completo", placeholder="Maria Silva")
            with col2:
                email = st.text_input("Seu E-mail (recebera seu resultado)", placeholder="maria@email.com")
            
            st.write("---")
            responses = render_assessment_form("employee")
            submit = st.form_submit_button("Concluir Avaliacao", use_container_width=True)
            
            if submit:
                if not name or not email:
                    st.error("Preencha seu nome e e-mail.")
                else:
                    dominant, secondary, details, bion_role, _ = calculate_profile(responses)
                    save_employee_result(token, name, email, dominant, secondary, details, bion_role)
                    st.balloons()
                    st.rerun()

elif page == "LPSChat":
    if not st.session_state.authenticated:
        st.session_state.page = "Login"
        st.rerun()
    
    # PRIVACY: Only managers can access - employees are blocked globally
    # Access control: check if theoretical modules are completed
    user_id = st.session_state.user['id']
    course_completed = is_course_completed(user_id)
    
    # Custom chat styling with brand colors
    st.markdown("""
        <style>
        .chat-header {
            background: linear-gradient(135deg, #0D3B66 0%, #1a4f7a 100%);
            color: white;
            padding: 2rem;
            border-radius: 15px;
            margin-bottom: 1.5rem;
            text-align: center;
            box-shadow: 0 4px 15px rgba(13, 59, 102, 0.3);
        }
        .chat-header h1 {
            color: #F4D35E;
            margin: 0;
            font-size: 2rem;
        }
        .chat-header p {
            color: rgba(255,255,255,0.9);
            margin: 0.5rem 0 0 0;
        }
        .chat-container {
            background: #f8f9fa;
            border-radius: 15px;
            padding: 1.5rem;
            border: 2px solid #e9ecef;
        }
        .example-questions {
            background: linear-gradient(135deg, rgba(244, 211, 94, 0.15) 0%, rgba(244, 211, 94, 0.05) 100%);
            border: 1px solid #F4D35E;
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
        }
        .example-questions h4 {
            color: #0D3B66;
            margin: 0 0 1rem 0;
        }
        .example-q {
            background: white;
            padding: 0.75rem 1rem;
            border-radius: 8px;
            margin: 0.5rem 0;
            border-left: 3px solid #F4D35E;
            color: #333;
            font-style: italic;
            cursor: pointer;
            transition: all 0.2s;
        }
        .example-q:hover {
            background: #fffef5;
            transform: translateX(5px);
        }
        .team-context-card {
            background: white;
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            border: 1px solid #e0e0e0;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        }
        .team-context-card h4 {
            color: #0D3B66;
            margin: 0 0 1rem 0;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid #F4D35E;
        }
        .team-member {
            display: flex;
            align-items: center;
            padding: 0.75rem;
            background: #f8f9fa;
            border-radius: 8px;
            margin: 0.5rem 0;
        }
        .team-member-icon {
            width: 40px;
            height: 40px;
            background: #0D3B66;
            color: #F4D35E;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-right: 1rem;
            font-weight: bold;
        }
        .bion-badge {
            background: #F4D35E;
            color: #0D3B66;
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
            margin-left: auto;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Chat header with brand styling
    st.markdown("""
        <div class="chat-header">
            <h1>LPSChat</h1>
            <p>Consultora de IA em Psicanalise e Neurociencia aplicada a Lideranca</p>
        </div>
    """, unsafe_allow_html=True)
    
    if not course_completed:
        st.warning("Acesso Temporario Bloqueado")
        st.markdown("""
            <div style='background-color: #fff3cd; padding: 2rem; border-radius: 10px; border-left: 4px solid #ffc107;'>
                <h3 style='color: #856404; margin-top: 0;'>Complete os modulos teoricos para liberar o LPSChat</h3>
                <p style='color: #856404;'>
                    O acesso ao consultor de IA e liberado apos a conclusao dos 5 primeiros modulos do curso.
                    Isso garante que voce tenha a base teorica necessaria para aproveitar ao maximo as analises da IA.
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        # Show progress
        module_status = get_module_completion_status(user_id)
        st.markdown("<h4 style='color: #0D3B66; margin-top: 2rem;'>Seu progresso nos modulos teoricos:</h4>", unsafe_allow_html=True)
        
        theoretical_modules = [1, 2, 3, 4, 5]
        for mod_id in theoretical_modules:
            if mod_id in module_status:
                status = module_status[mod_id]
                progress_pct = int(status['percentage'])
                if progress_pct == 100:
                    st.markdown(f"[Completo] **{status['name']}**: {progress_pct}%")
                else:
                    st.markdown(f"[Em andamento] **{status['name']}**: {progress_pct}%")
        
        st.write("---")
        if st.button("Ir para o Curso", key="btn-goto-curso"):
            st.session_state.page = "LPS Curso"
            st.rerun()
    else:
        # Initialize chat history
        if 'chat_messages' not in st.session_state:
            st.session_state.chat_messages = []
        
        # Get manager and employee data for context
        manager_data = st.session_state.manager_data
        user_name = st.session_state.user['name'] if st.session_state.user else "Gestor"
        
        # Fetch complete employees data from database
        employees_context = ""
        employees_list_display = []
        team_dynamics_analysis = ""
        
        if manager_data:
            employees = get_manager_employees(manager_data['id'])
            if employees:
                employees_list = []
                bion_roles_count = {}
                
                for emp in employees:
                    if emp[10] == 1:  # completed
                        emp_name = emp[4] or f'Funcionario {emp[3]}'
                        dominant = emp[6] or "N/A"
                        secondary = emp[7] or "N/A"
                        bion_role = emp[9] or "N/A"
                        
                        # Track Bion roles for team dynamics
                        if bion_role and bion_role != "N/A":
                            bion_roles_count[bion_role] = bion_roles_count.get(bion_role, 0) + 1
                        
                        emp_info = f"""- Nome: {emp_name}
  Perfil Dominante: {dominant}
  Perfil Secundario: {secondary}
  Papel de Bion (dinamica grupal): {bion_role}
  Email: {emp[5] or 'N/A'}"""
                        employees_list.append(emp_info)
                        employees_list_display.append({
                            'name': emp_name,
                            'dominant': dominant,
                            'secondary': secondary,
                            'bion': bion_role
                        })
                
                if employees_list:
                    employees_context = "\n\n".join(employees_list)
                    
                    # Generate team dynamics summary
                    dynamics_parts = []
                    if bion_roles_count:
                        dynamics_parts.append(f"Distribuicao de Papeis de Bion na equipe: {bion_roles_count}")
                        
                        # Identify potential risks
                        if bion_roles_count.get('Bode Expiatorio', 0) > 0:
                            dynamics_parts.append("ALERTA: Ha um Bode Expiatorio na equipe - risco de projecoes negativas")
                        if bion_roles_count.get('Sabotador Silencioso', 0) > 0:
                            dynamics_parts.append("ATENCAO: Ha um Sabotador Silencioso - resistencia passiva as mudancas")
                        if bion_roles_count.get('Lider de Luta-Fuga', 0) > 1:
                            dynamics_parts.append("RISCO: Multiplos Lideres de Luta-Fuga podem gerar conflitos de poder")
                    
                    team_dynamics_analysis = "\n".join(dynamics_parts)
        
        # Manager profile context with details
        manager_profile = ""
        if manager_data and manager_data.get('dominant'):
            manager_profile = f"""Perfil do Gestor:
- Perfil Dominante: {manager_data['dominant']}
- Perfil Secundario: {manager_data['secondary']}
- Implicacoes: O gestor com perfil {manager_data['dominant']} tende a liderar com foco em {get_profile_tendency(manager_data['dominant'])}"""
        
        # Enhanced system prompt with Psychoanalysis and Neuroscience
        system_prompt = f"""Voce e uma CONSULTORA ESPECIALISTA em Psicanalise e Neurociencia aplicada a Lideranca, desenvolvida pela metodologia LPS de Viviane Nishiura.

PAPEL E IDENTIDADE:
- Voce e uma consultora senior com profundo conhecimento em psicanalise de grupos (Bion, Pichon-Riviere) e neurociencia organizacional
- Sua funcao e ajudar gestores a compreender as dinamicas inconscientes de suas equipes
- Voce analisa padroes de comportamento, identificando papeis inconscientes e arquetipos
- PRIVACIDADE: Seus insights sao EXCLUSIVOS para o gestor - nunca compartilhados com funcionarios

============ DADOS DA EQUIPE (CONFIDENCIAL) ============

GESTOR:
Nome: {user_name}
{manager_profile if manager_profile else "O gestor ainda nao completou o LPSTest."}

FUNCIONARIOS DA EQUIPE:
{employees_context if employees_context else "Nenhum funcionario completou o assessment ainda."}

ANALISE AUTOMATICA DA DINAMICA GRUPAL:
{team_dynamics_analysis if team_dynamics_analysis else "Dados insuficientes para analise de dinamica."}

============ BASE TEORICA ============

1. PAPEIS DE BION (Dinamica Grupal Inconsciente):
- Porta-voz: Expressa o que o grupo sente mas nao consegue dizer. Captam tensoes inconscientes.
- Bode Expiatorio: Absorve projecoes negativas do grupo. Frequentemente culpado por problemas sistemicos.
- Dependente: Busca protecao constante no lider, evita autonomia. Requer contencao.
- Lider de Luta-Fuga: Reativo a ameacas reais ou imaginarias, mobiliza o grupo para ataque ou fuga.
- Sabotador Silencioso: Resiste passivamente as mudancas. Concordancia superficial, boicote sutil.

2. NEUROCIENCIA DA LIDERANCA:
- Sistema Limbico: Emocoes primitivas (medo, raiva) podem sequestrar o cortex pre-frontal em situacoes de estresse
- Neuronios Espelho: Lideres regulam emocionalmente suas equipes - a calma ou ansiedade sao "contagiosas"
- Cortisol vs Oxitocina: Ambientes de ameaca elevam cortisol (paralisia); seguranca psicologica libera oxitocina (cooperacao)
- Amigdala: O "detector de ameacas" dispara em conflitos interpessoais - funcionarios em modo de defesa

3. TRANSFERENCIA E CONTRATRANSFERENCIA:
- Transferencia: Funcionarios projetam no lider figuras parentais (pai protetor, mae acolhedora, autoridade punitiva)
- Contratransferencia: Reacoes emocionais do lider as projecoes (irritacao inexplicavel, fadiga, bloqueio)
- Neurociencia: A amigdala do lider reage as projecoes antes da consciencia - por isso lideres "sentem" antes de "pensar"

4. TAREFA REAL vs REGRESSAO EMOCIONAL:
- Quando ha ansiedade grupal, o grupo REGRIDE para padroes primitivos (ataque, fuga, dependencia)
- A TAREFA REAL (objetivo concreto do trabalho) ancora o grupo na racionalidade
- Pergunte sempre: "Qual e a tarefa que voces precisam entregar?" para retirar o grupo da regressao

5. PERFIS DE LIDERANCA E SEUS ARQUETIPOS:
- Protetor: Acolhe mas pode absorver demais (risco de burnout)
- Contenedor: Mantem calma em crises, metaboliza ansiedade grupal
- Narciso Estrategico: Inspira e motiva, mas precisa de validacao constante
- Estruturador: Organiza e da forma, mas pode controlar demais
- Espelho Emocional: Reflete e valida emocoes, mas pode ser afetado
- Observador Reflexivo: Analisa profundamente, mas pode hesitar na acao

6. ADEQUACAO DE PERFIS A FUNCOES:
- Cargos de Lideranca Operacional: Estruturador ou Contenedor
- Cargos Criativos: Narciso Estrategico ou Espelho Emocional
- Cargos de Mediacao/RH: Protetor ou Espelho Emocional
- Cargos Analiticos: Observador Reflexivo
- Gestao de Crises: Contenedor ou Lider de Luta-Fuga (canalizado)

============ INSTRUCOES DE RESPOSTA ============

1. SEMPRE analise os dados REAIS da equipe do gestor (acima)
2. Identifique papeis inconscientes e arquetipos nos funcionarios
3. Mapeie pontos de CONFLITO potencial entre perfis incompativeis
4. Identifique SINERGIAS entre perfis complementares
5. Sugira adequacao de perfis para cargos especificos quando perguntado
6. Use conceitos de neurociencia para explicar comportamentos (ex: "O cortisol elevado dele explica a reatividade")
7. Identifique padroes de TRANSFERENCIA na relacao gestor-funcionario
8. Sempre termine sugerindo foco na TAREFA REAL para resolver regressoes
9. Seja empatica mas direta nas recomendacoes
10. Use portugues brasileiro

FORMATO DE RESPOSTA:
- Inicie com uma analise breve da situacao
- Use os dados reais da equipe para fundamentar
- Ofereca insights psicoanaliticos e neurocientificos
- Termine com recomendacoes praticas de intervencao"""

        # Display team context card
        if employees_list_display:
            st.markdown('<div class="team-context-card">', unsafe_allow_html=True)
            st.markdown('<h4>Sua Equipe Mapeada</h4>', unsafe_allow_html=True)
            for emp in employees_list_display:
                initial = emp['name'][0].upper() if emp['name'] else "?"
                st.markdown(f"""
                    <div class="team-member">
                        <div class="team-member-icon">{initial}</div>
                        <div>
                            <strong>{emp['name']}</strong><br>
                            <small style="color: #666;">{emp['dominant']} + {emp['secondary']}</small>
                        </div>
                        <span class="bion-badge">{emp['bion']}</span>
                    </div>
                """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("Nenhum funcionario completou o assessment ainda. Gere links de convite na area de Equipe.")
        
        # Example questions section
        st.markdown("""
            <div class="example-questions">
                <h4>Exemplos de perguntas que voce pode fazer:</h4>
                <div class="example-q">"Quais sao as principais dinamicas de transferencia no meu time?"</div>
                <div class="example-q">"Como posso melhorar a produtividade deste grupo?"</div>
                <div class="example-q">"Existe algum Bode Expiatorio na minha equipe?"</div>
                <div class="example-q">"Qual funcionario seria mais adequado para liderar o novo projeto?"</div>
                <div class="example-q">"Por que me sinto tao irritado com o Joao? (contratransferencia)"</div>
                <div class="example-q">"Como lidar com a resistencia passiva da Maria?"</div>
            </div>
        """, unsafe_allow_html=True)
        
        # Chat container
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        
        # Display chat history with custom styling
        for message in st.session_state.chat_messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Chat input
        if prompt := st.chat_input("Descreva a situacao da sua equipe ou faca uma pergunta..."):
            # Add user message to history
            st.session_state.chat_messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Generate AI response
            with st.chat_message("assistant"):
                with st.spinner("Analisando dinamicas da equipe..."):
                    try:
                        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
                        model = genai.GenerativeModel('gemini-1.5-flash')
                        
                        # Build conversation history for Gemini
                        chat_history = f"{system_prompt}\n\n"
                        for msg in st.session_state.chat_messages:
                            role = "Gestor" if msg["role"] == "user" else "Consultora LPS"
                            chat_history += f"{role}: {msg['content']}\n\n"
                        
                        response = model.generate_content(chat_history)
                        
                        assistant_message = response.text
                        st.markdown(assistant_message)
                        st.session_state.chat_messages.append({"role": "assistant", "content": assistant_message})
                    
                    except Exception as e:
                        error_msg = str(e)
                        if "GOOGLE_API_KEY" in error_msg or "API key" in error_msg.lower():
                            st.error("Chave da API do Google Gemini nao configurada. Configure GOOGLE_API_KEY nos secrets.")
                        else:
                            st.error(f"Erro ao conectar com a IA: {error_msg}")
        
        # Export and Clear buttons with styling
        if st.session_state.chat_messages:
            # Get the last AI response for export
            last_ai_response = ""
            for msg in reversed(st.session_state.chat_messages):
                if msg["role"] == "assistant":
                    last_ai_response = msg["content"]
                    break
            
            col1, col2, col3 = st.columns([1, 1, 1])
            
            with col1:
                if last_ai_response and employees_list_display:
                    # Generate PDF from last AI analysis
                    analysis_pdf = generate_ai_analysis_pdf(
                        user_name,
                        last_ai_response,
                        employees if manager_data else []
                    )
                    st.download_button(
                        label="Exportar Analise (PDF)",
                        data=analysis_pdf,
                        file_name=f"analise_ia_lps_{datetime.now().strftime('%Y%m%d')}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
            
            with col2:
                if st.button("Limpar Conversa", key="btn-clear-chat", use_container_width=True):
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
    st.title("Sobre Viviane Nishiura")
    st.write("Viviane Nishiura é psicóloga clínica e consultora de liderança.")

elif page == "AdminEmail":
    # Admin page for sending welcome emails after payment confirmation
    if not st.session_state.authenticated:
        st.session_state.page = "Login"
        st.rerun()
    
    st.title("Administração - Envio de E-mails")
    
    # Check if email is configured
    if is_email_configured():
        st.success("SMTP configurado corretamente")
    else:
        st.warning("SMTP não configurado. Configure as credenciais nas variáveis de ambiente ou secrets.")
        st.markdown("""
        **Configuração necessária:**
        - `SMTP_HOST` - Servidor SMTP (ex: smtp.gmail.com)
        - `SMTP_PORT` - Porta (ex: 587)
        - `SMTP_USER` - E-mail de envio
        - `SMTP_PASSWORD` - Senha do app
        - `SMTP_FROM_NAME` - Nome do remetente
        - `SMTP_FROM_EMAIL` - E-mail do remetente
        """)
    
    st.write("---")
    
    # Send Welcome Email Section
    st.subheader("Enviar E-mail de Boas-Vindas (Acesso Liberado)")
    st.write("Use este formulário para liberar o acesso de um novo aluno após confirmação de pagamento via WhatsApp.")
    
    with st.form("welcome_email_form"):
        col1, col2 = st.columns(2)
        with col1:
            new_user_name = st.text_input("Nome completo do aluno", placeholder="Maria Silva")
            new_user_email = st.text_input("E-mail do aluno", placeholder="maria@email.com")
        with col2:
            new_user_password = st.text_input("Senha temporária", placeholder="senha123", help="O aluno receberá esta senha no e-mail")
            create_account = st.checkbox("Criar conta automaticamente", value=True, help="Se marcado, cria a conta do aluno no sistema")
        
        submit = st.form_submit_button("Enviar E-mail de Boas-Vindas", use_container_width=True)
        
        if submit:
            if new_user_name and new_user_email and new_user_password:
                can_send_email = True
                
                # Create account if requested
                if create_account:
                    user_id, error = register_user(new_user_email, new_user_password, new_user_name)
                    if error:
                        st.error(f"Erro ao criar conta: {error}")
                        st.info("E-mail de boas-vindas não foi enviado. Corrija o erro acima ou desmarque 'Criar conta automaticamente' para reenviar credenciais existentes.")
                        can_send_email = False
                    else:
                        st.success(f"Conta criada com sucesso para {new_user_name}")
                
                # Only send welcome email if account was created successfully or we're not creating a new account
                if can_send_email:
                    success, message = send_welcome_email(new_user_email, new_user_name, new_user_password)
                    if success:
                        st.success(f"E-mail de boas-vindas enviado para {new_user_email}")
                    else:
                        st.warning(f"E-mail não enviado: {message}")
            else:
                st.error("Preencha todos os campos obrigatórios")
    
    st.write("---")
    
    # Test Email Section
    st.subheader("Testar Configuração de E-mail")
    test_email = st.text_input("E-mail para teste", placeholder="seu-email@teste.com")
    if st.button("Enviar E-mail de Teste"):
        if test_email:
            success, message = send_email(
                test_email, 
                "Teste de Configuração - LPS", 
                "<h1>Teste de E-mail</h1><p>Se você recebeu este e-mail, a configuração SMTP está funcionando corretamente.</p>"
            )
            if success:
                st.success("E-mail de teste enviado com sucesso!")
            else:
                st.error(f"Erro ao enviar: {message}")
        else:
            st.warning("Digite um e-mail para teste")
