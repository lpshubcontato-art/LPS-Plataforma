import streamlit as st
import os
import sqlite3
import uuid
import json
import hashlib
import bcrypt
import smtplib
import shutil
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import streamlit.components.v1 as components
from datetime import datetime, timedelta
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
            .header {{ background-color: #18738c; color: white; padding: 30px; text-align: center; }}
            .header h1 {{ margin: 0; color: #d19f09; }}
            .content {{ padding: 30px; line-height: 1.7; color: #333; }}
            .result-box {{ background: linear-gradient(135deg, #18738c, #1a5490); color: white; padding: 25px; border-radius: 10px; text-align: center; margin: 25px 0; }}
            .result-box h2 {{ margin: 0; color: #d19f09; font-size: 1.6rem; }}
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
                
                <p>Voce acaba de concluir o LPTest, uma etapa fundamental na sua jornada de desenvolvimento dentro da Plataforma LPS.</p>
                
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
            .header {{ background-color: #18738c; color: white; padding: 30px; text-align: center; }}
            .header h1 {{ margin: 0; color: #d19f09; }}
            .content {{ padding: 30px; }}
            .alert-box {{ background-color: #d4edda; border-left: 4px solid #28a745; padding: 15px; border-radius: 5px; margin: 20px 0; }}
            .employee-card {{ background: #f8f9fa; padding: 20px; border-radius: 10px; margin: 20px 0; }}
            .bion-badge {{ display: inline-block; background-color: #d19f09; color: #18738c; padding: 8px 16px; border-radius: 15px; font-weight: bold; }}
            .cta-button {{ display: inline-block; background-color: #18738c; color: white; padding: 15px 30px; border-radius: 25px; text-decoration: none; font-weight: bold; margin-top: 20px; }}
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
                    <strong>Novo membro mapeado!</strong> {employee_name} completou o LPTest.
                </div>
                
                <div class="employee-card">
                    <h3 style="margin-top: 0; color: #18738c;">{employee_name}</h3>
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
            .header {{ background-color: #18738c; color: white; padding: 30px; text-align: center; }}
            .header h1 {{ margin: 0; color: #d19f09; }}
            .content {{ padding: 30px; }}
            .credentials-box {{ background: linear-gradient(135deg, #18738c, #1a5490); color: white; padding: 25px; border-radius: 10px; margin: 20px 0; }}
            .credentials-box h3 {{ margin-top: 0; color: #d19f09; }}
            .credential-item {{ background: rgba(255,255,255,0.1); padding: 10px 15px; border-radius: 5px; margin: 10px 0; }}
            .credential-label {{ font-size: 0.9rem; opacity: 0.8; }}
            .credential-value {{ font-size: 1.1rem; font-weight: bold; }}
            .cta-button {{ display: inline-block; background-color: #d19f09; color: #18738c; padding: 15px 30px; border-radius: 25px; text-decoration: none; font-weight: bold; margin-top: 20px; }}
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
                    <h4 style="margin-top: 0; color: #18738c;">O que você terá acesso:</h4>
                    <div class="feature-item">Curso completo com 8 modulos de Lideranca Psicanalitica</div>
                    <div class="feature-item">LPTest - Assessment de perfil de liderança</div>
                    <div class="feature-item">Gestão de Equipe - Mapeie até 4 colaboradores</div>
                    <div class="feature-item">LPChat - Consultor de IA especializado</div>
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

# Password hashing functions using bcrypt
def hash_password(password):
    """Hash password using bcrypt for secure storage."""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(password, hashed):
    """Verify password against hash. Supports bcrypt and legacy SHA-256."""
    # Check if it's a bcrypt hash (starts with $2b$, $2a$, or $2y$)
    if hashed.startswith('$2'):
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
        except Exception:
            return False
    else:
        # Legacy SHA-256 hash support for existing users
        legacy_hash = hashlib.sha256(password.encode()).hexdigest()
        return legacy_hash == hashed

def upgrade_password_hash(user_id, password):
    """Upgrade legacy SHA-256 hash to bcrypt."""
    new_hash = hash_password(password)
    conn = sqlite3.connect('lps_data.db')
    c = conn.cursor()
    c.execute("UPDATE users SET password_hash = ? WHERE id = ?", (new_hash, user_id))
    conn.commit()
    conn.close()
    return new_hash

# Database Backup System
BACKUP_DIR = "backups"
MAX_BACKUPS = 5  # Keep last 5 backups

def ensure_backup_dir():
    """Ensure backup directory exists."""
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)

def create_database_backup():
    """Create a backup of the SQLite database."""
    ensure_backup_dir()
    
    db_path = 'lps_data.db'
    if not os.path.exists(db_path):
        return None
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_filename = f"lps_data_backup_{timestamp}.db"
    backup_path = os.path.join(BACKUP_DIR, backup_filename)
    
    try:
        # Use shutil to copy the database file
        shutil.copy2(db_path, backup_path)
        
        # Cleanup old backups (keep only MAX_BACKUPS most recent)
        cleanup_old_backups()
        
        return backup_path
    except Exception as e:
        print(f"Backup error: {e}")
        return None

def cleanup_old_backups():
    """Remove old backups, keeping only the most recent ones."""
    ensure_backup_dir()
    
    backups = []
    for f in os.listdir(BACKUP_DIR):
        if f.startswith('lps_data_backup_') and f.endswith('.db'):
            backup_path = os.path.join(BACKUP_DIR, f)
            backups.append((backup_path, os.path.getmtime(backup_path)))
    
    # Sort by modification time (newest first)
    backups.sort(key=lambda x: x[1], reverse=True)
    
    # Remove old backups beyond MAX_BACKUPS
    for backup_path, _ in backups[MAX_BACKUPS:]:
        try:
            os.remove(backup_path)
        except Exception:
            pass

def restore_from_backup(backup_filename):
    """Restore database from a backup file."""
    backup_path = os.path.join(BACKUP_DIR, backup_filename)
    
    if not os.path.exists(backup_path):
        return False, "Arquivo de backup nao encontrado"
    
    try:
        # Create backup of current db before restoring
        current_backup = create_database_backup()
        
        # Restore
        shutil.copy2(backup_path, 'lps_data.db')
        return True, f"Banco restaurado com sucesso. Backup anterior: {current_backup}"
    except Exception as e:
        return False, f"Erro ao restaurar: {e}"

def get_available_backups():
    """Get list of available backups."""
    ensure_backup_dir()
    
    backups = []
    for f in os.listdir(BACKUP_DIR):
        if f.startswith('lps_data_backup_') and f.endswith('.db'):
            backup_path = os.path.join(BACKUP_DIR, f)
            size_mb = os.path.getsize(backup_path) / (1024 * 1024)
            mod_timestamp = os.path.getmtime(backup_path)
            mod_time = datetime.fromtimestamp(mod_timestamp)
            backups.append({
                'filename': f,
                'size_mb': round(size_mb, 2),
                'created': mod_time.strftime('%d/%m/%Y %H:%M:%S'),
                'timestamp': mod_timestamp  # Keep numeric timestamp for sorting
            })
    
    # Sort by timestamp (newest first) - using numeric timestamp for correct ordering
    backups.sort(key=lambda x: x['timestamp'], reverse=True)
    return backups

def auto_backup_on_startup():
    """Create an automatic backup when the application starts."""
    ensure_backup_dir()
    
    # Check if we already have a backup today
    today = datetime.now().strftime('%Y%m%d')
    for f in os.listdir(BACKUP_DIR):
        if f.startswith(f'lps_data_backup_{today}'):
            return None  # Already have today's backup
    
    # Create new backup
    return create_database_backup()

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
        consent_given INTEGER DEFAULT 0,
        consent_date TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (manager_id) REFERENCES managers(id)
    )''')
    
    # Migration: Add consent columns if they don't exist
    c.execute("PRAGMA table_info(employees)")
    columns = [col[1] for col in c.fetchall()]
    if 'consent_given' not in columns:
        c.execute("ALTER TABLE employees ADD COLUMN consent_given INTEGER DEFAULT 0")
    if 'consent_date' not in columns:
        c.execute("ALTER TABLE employees ADD COLUMN consent_date TIMESTAMP")
    
    # Course progress table
    c.execute('''CREATE TABLE IF NOT EXISTS course_progress (
        id TEXT PRIMARY KEY,
        user_id TEXT,
        progress_data TEXT,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )''')
    
    # Payments table for subscription/access control
    c.execute('''CREATE TABLE IF NOT EXISTS payments (
        id TEXT PRIMARY KEY,
        user_id TEXT,
        plan_type TEXT DEFAULT 'basic',
        status TEXT DEFAULT 'pending',
        amount REAL,
        payment_date TIMESTAMP,
        expiry_date TIMESTAMP,
        payment_method TEXT,
        transaction_id TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )''')
    
    # AI Chat logs table
    c.execute('''CREATE TABLE IF NOT EXISTS ai_chat_logs (
        id TEXT PRIMARY KEY,
        user_id TEXT,
        manager_id TEXT,
        message_type TEXT,
        message_content TEXT,
        response_content TEXT,
        tokens_used INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (manager_id) REFERENCES managers(id)
    )''')
    
    # Mentorship scheduling table
    c.execute('''CREATE TABLE IF NOT EXISTS mentorship_sessions (
        id TEXT PRIMARY KEY,
        user_id TEXT,
        manager_id TEXT,
        session_date TIMESTAMP,
        session_type TEXT DEFAULT 'individual',
        status TEXT DEFAULT 'scheduled',
        notes TEXT,
        meeting_link TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (manager_id) REFERENCES managers(id)
    )''')
    
    # Assessment responses table - stores each individual response (1-5) for future AI analysis
    c.execute('''CREATE TABLE IF NOT EXISTS assessment_responses (
        id TEXT PRIMARY KEY,
        respondent_id TEXT,
        respondent_type TEXT,
        block_name TEXT,
        question_index INTEGER,
        question_text TEXT,
        response_value INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    conn.commit()
    conn.close()

init_db()

# Run automatic backup on startup (once per day)
auto_backup_on_startup()

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
        # Upgrade legacy SHA-256 hash to bcrypt on successful login
        if not result[1].startswith('$2'):
            upgrade_password_hash(result[0], password)
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

def get_manager_by_id(manager_id):
    """Get manager info by manager ID."""
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT id, user_id, name, email, profile_dominant, profile_secondary FROM managers WHERE id = ?", (manager_id,))
    result = c.fetchone()
    conn.close()
    if result:
        return {
            "id": result[0],
            "user_id": result[1],
            "name": result[2],
            "email": result[3],
            "dominant": result[4],
            "secondary": result[5]
        }
    return None

def validate_manager_ownership(user_id, manager_id):
    """Validate that the manager_id belongs to the user_id (multitenancy check)."""
    if not user_id or not manager_id:
        return False
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT id FROM managers WHERE id = ? AND user_id = ?", (manager_id, user_id))
    result = c.fetchone()
    conn.close()
    return result is not None

def get_secure_manager_employees(user_id, manager_id):
    """Get employees for a manager with ownership validation (multitenancy safe)."""
    if not validate_manager_ownership(user_id, manager_id):
        return []
    return get_manager_employees(manager_id)

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

def save_employee_consent(token):
    """Save employee consent to database with timestamp."""
    conn = get_db()
    c = conn.cursor()
    c.execute("""UPDATE employees SET consent_given = 1, consent_date = ? 
                 WHERE link_token = ?""", (datetime.now(), token))
    conn.commit()
    conn.close()
    return True

def get_employee_consent(token):
    """Check if employee has given consent."""
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT consent_given FROM employees WHERE link_token = ?", (token,))
    result = c.fetchone()
    conn.close()
    if result:
        return result[0] == 1
    return False

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

def get_assessment_block_sums(respondent_id, respondent_type="manager"):
    """Calculate block sums from saved assessment responses for radar chart."""
    conn = get_db()
    c = conn.cursor()
    c.execute("""SELECT block_name, SUM(response_value) as block_sum
                 FROM assessment_responses 
                 WHERE respondent_id = ? AND respondent_type = ?
                 GROUP BY block_name""", (respondent_id, respondent_type))
    results = c.fetchall()
    conn.close()
    
    if not results:
        return None
    
    block_sums = {}
    for row in results:
        block_sums[row[0]] = row[1]
    return block_sums

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

def get_user_payment_status(user_id):
    """Check if user has an active payment/subscription"""
    conn = get_db()
    c = conn.cursor()
    c.execute("""SELECT id, plan_type, status, expiry_date 
                 FROM payments 
                 WHERE user_id = ? AND status = 'active'
                 ORDER BY created_at DESC LIMIT 1""", (user_id,))
    result = c.fetchone()
    conn.close()
    
    if result:
        # Check if payment is still valid (not expired)
        if result[3]:  # expiry_date
            try:
                # Use fromisoformat for robust parsing (handles microseconds)
                expiry = datetime.fromisoformat(result[3]) if isinstance(result[3], str) else result[3]
            except (ValueError, TypeError):
                # Fallback: try common format without microseconds
                try:
                    expiry = datetime.strptime(result[3], '%Y-%m-%d %H:%M:%S')
                except:
                    expiry = datetime.now()  # Safe fallback
            if expiry > datetime.now():
                return {'active': True, 'plan': result[1], 'expiry': result[3]}
        else:
            # No expiry date = lifetime access
            return {'active': True, 'plan': result[1], 'expiry': None}
    
    return {'active': False, 'plan': None, 'expiry': None}

def activate_user_payment(user_id, plan_type='premium', amount=997.0, days_valid=365):
    """Activate a payment for a user (called after WhatsApp confirmation)"""
    conn = get_db()
    c = conn.cursor()
    payment_id = str(uuid.uuid4())
    payment_date = datetime.now()
    expiry_date = payment_date + timedelta(days=days_valid)
    
    c.execute("""INSERT INTO payments (id, user_id, plan_type, status, amount, payment_date, expiry_date, payment_method)
                 VALUES (?, ?, ?, 'active', ?, ?, ?, 'whatsapp')""",
              (payment_id, user_id, plan_type, amount, payment_date, expiry_date))
    conn.commit()
    conn.close()
    return payment_id

def can_access_premium_features(user_id):
    """Check if user can access premium features (LPChat, Mentoria)
    Requires: Active payment AND completed theoretical course modules"""
    payment_status = get_user_payment_status(user_id)
    course_completed = is_course_completed(user_id)
    
    return {
        'can_access': payment_status['active'] and course_completed,
        'payment_active': payment_status['active'],
        'course_completed': course_completed,
        'plan': payment_status['plan'],
        'message': get_access_message(payment_status['active'], course_completed)
    }

def get_access_message(payment_active, course_completed):
    """Generate appropriate message for access status"""
    if not payment_active:
        return "Acesso liberado após confirmação de pagamento via WhatsApp."
    if not course_completed:
        return "Complete os módulos teóricos do curso para liberar este recurso."
    return None

def log_ai_chat(user_id, manager_id, message_type, message_content, response_content, tokens_used=0):
    """Log AI chat interactions"""
    conn = get_db()
    c = conn.cursor()
    log_id = str(uuid.uuid4())
    c.execute("""INSERT INTO ai_chat_logs (id, user_id, manager_id, message_type, message_content, response_content, tokens_used)
                 VALUES (?, ?, ?, ?, ?, ?, ?)""",
              (log_id, user_id, manager_id, message_type, message_content, response_content, tokens_used))
    conn.commit()
    conn.close()
    return log_id

def get_ai_insights(manager_id, user_id):
    """Generate AI insights about the team with multitenancy validation"""
    # Use secure function to validate ownership
    employees = get_secure_manager_employees(user_id, manager_id)
    manager_profile = get_manager_profile_by_user(user_id)
    
    insights = []
    
    # Check if manager has taken the assessment
    if not manager_profile or not manager_profile.get('dominant'):
        insights.append({
            'type': 'warning',
            'message': 'Complete seu LPTest para receber insights personalizados sobre sua liderança.'
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
    @import url('https://fonts.googleapis.com/css2?family=Open+Sans:wght@400;600;700;800&family=Ubuntu:wght@300;400;500;700&display=swap');
    
    :root {
        --primary-blue: #18738c;
        --accent-gold: #d19f09;
        --bg-gray: #F5F5F5;
        --light-gold: #FFF9E6;
    }
    
    .main { background-color: var(--bg-gray); }
    h1, h2, h3 { 
        color: var(--primary-blue) !important;
        font-family: 'Open Sans', sans-serif !important;
    }
    body, p, span, div, label {
        font-family: 'Ubuntu', sans-serif !important;
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
        background: linear-gradient(135deg, #18738c 0%, #1a5490 100%);
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
        background: linear-gradient(135deg, #18738c 0%, #1a5490 100%);
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
LOGO_PATH = "attached_assets/logotipo_2__1768529013163.jpeg"

# Definições das questões do Assessment (8 por bloco)
ASSESSMENT_QUESTIONS = {
    "Bloco 1 – Autoridade Interna e Autoimagem": [
        "Sinto que a equipe me observa de forma idealizada.",
        "Tenho clareza sobre minhas forças e fraquezas como líder.",
        "Me sinto desconfortável quando sou admirado demais.",
        "Prefiro manter minha imagem emocionalmente neutra no ambiente.",
        "Às vezes, não sei se sou respeitado ou apenas temido.",
        "Quando recebo críticas, demoro a me recuperar internamente.",
        "Me esforço para parecer emocionalmente estável, mesmo quando não estou.",
        "A percepção da equipe sobre mim influencia minhas decisões."
    ],
    "Bloco 2 – Contenção Emocional do Grupo": [
        "Em situações de crise, sou o primeiro a manter a calma.",
        "Sei conter a ansiedade coletiva mesmo sem dizer uma palavra.",
        "Percebo rapidamente quando a equipe está emocionalmente instável.",
        "Eu sou, muitas vezes, o 'termômetro emocional' do time.",
        "Me preocupo com o impacto emocional das mudanças.",
        "Sei como evitar que o pânico da equipe tome conta.",
        "Tenho habilidade para resgatar a racionalidade do grupo.",
        "Sinto que absorvo emocionalmente o clima da equipe."
    ],
    "Bloco 3 – Narcisismo e Reconhecimento": [
        "Me incomodo quando não sou reconhecido pelo meu esforço.",
        "Gosto de ser o centro das atenções nas reuniões.",
        "A opinião da liderança acima de mim afeta meu desempenho.",
        "Sinto frustração quando minha equipe não valida minhas decisões.",
        "Preciso de reconhecimento frequente para me manter motivado.",
        "Evito demonstrar insegurança para não comprometer minha autoridade.",
        "Comparo minha liderança com a de outros colegas frequentemente.",
        "Às vezes exagero meu valor para manter respeito."
    ],
    "Bloco 4 – Estrutura e Lógica de Tarefa": [
        "Preciso de metas e estruturas bem definidas para funcionar.",
        "Me incomodo com mudanças frequentes nas prioridades.",
        "Gosto de controlar todos os processos para evitar erros.",
        "Tenho dificuldade em delegar quando há risco de falhas.",
        "Acredito que sem controle, as pessoas tendem ao caos.",
        "Prefiro manter a equipe ocupada, mesmo que sem urgência.",
        "Me estresso com prazos mal definidos.",
        "Costumo antecipar problemas antes que eles ocorram."
    ],
    "Bloco 5 – Relação com a Equipe e Projeções": [
        "Já senti que alguém da equipe me via como uma figura parental.",
        "Em alguns momentos, sou tratado com hostilidade sem motivo aparente.",
        "Já notei que membros da equipe projetam em mim expectativas irreais.",
        "Alguns funcionários me fazem sentir como se eu fosse o 'culpado' de tudo.",
        "Tenho dificuldade em me distanciar emocionalmente de alguns colaboradores.",
        "Preciso manter uma certa 'armadura' para não ser afetado pela equipe.",
        "Costumo internalizar conflitos mesmo quando não são meus.",
        "Às vezes, me sinto em uma posição emocionalmente isolada."
    ],
    "Bloco 6 – Reflexão, Crítica e Autoconsciência": [
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

BLOCK_SHORT_NAMES = {
    "Bloco 1 – Autoridade Interna e Autoimagem": "Autoridade",
    "Bloco 2 – Contenção Emocional do Grupo": "Contenção",
    "Bloco 3 – Narcisismo e Reconhecimento": "Narcisismo",
    "Bloco 4 – Estrutura e Lógica de Tarefa": "Estrutura",
    "Bloco 5 – Relação com a Equipe e Projeções": "Relação",
    "Bloco 6 – Reflexão, Crítica e Autoconsciência": "Reflexão"
}

BLOCK_TO_PROFILE = {
    "Bloco 5 – Relação com a Equipe e Projeções": "🛡 Protetor",
    "Bloco 2 – Contenção Emocional do Grupo": "🧱 Contenedor",
    "Bloco 3 – Narcisismo e Reconhecimento": "🔥 Narciso Estratégico",
    "Bloco 4 – Estrutura e Lógica de Tarefa": "🏗 Estruturador",
    "Bloco 1 – Autoridade Interna e Autoimagem": "🪞 Espelho Emocional",
    "Bloco 6 – Reflexão, Crítica e Autoconsciência": "🧠 Observador Reflexivo"
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
            "forcas": "✔ Cria ambientes emocionalmente estáveis. ✔ Protege o time com sistemas e processos claros. ✔ Excelente para liderar equipes em ambientes caóticos.",
            "riscos": "⚠ Pode se tornar rígido(a) demais tentando 'salvar' todos. ⚠ Pode controlar excessivamente para evitar conflitos.",
            "recomendacoes": "➡ Confie mais na maturidade emocional do time. ➡ Flexibilize regras quando perceber crescimento autônomo."
        },
        "🧱 Contenedor": {
            "forcas": "✔ Equilíbrio emocional impressionante. ✔ Alta capacidade de empatia sem perder o centro. ✔ Inspira respeito e lealdade.",
            "riscos": "⚠ Pode assumir a responsabilidade emocional de todos. ⚠ Pode ser visto como 'pai' ou 'mãe', gerando dependência excessiva.",
            "recomendacoes": "➡ Incentive autonomia emocional na equipe. ➡ Crie momentos de autorreflexão para não se sobrecarregar."
        },
        "🪞 Espelho Emocional": {
            "forcas": "✔ Capacidade ímpar de adaptação ao grupo. ✔ Constrói confiança e acolhimento rapidamente. ✔ Sensível às dinâmicas invisíveis da equipe.",
            "riscos": "⚠ Pode perder autenticidade tentando corresponder a todas as expectativas. ⚠ Pode se frustrar com rejeições ou incompreensões sutis.",
            "recomendacoes": "➡ Mantenha contato com sua identidade, além da imagem percebida. ➡ Fortaleça a liderança com base em valores, não só em aceitação."
        }
    },
    "🧱 Contenedor": {
        "🛡 Protetor": {
            "forcas": "✔ Regula emoções do grupo com estabilidade. ✔ Transmite confiança emocional e acolhimento. ✔ Excelente para liderar momentos de crise ou transformação.",
            "riscos": "⚠ Pode atrair dependência emocional dos colaboradores. ⚠ Pode evitar confrontos para manter a harmonia.",
            "recomendacoes": "➡ Incentive responsabilidade emocional na equipe. ➡ Lembre-se: firmeza também é uma forma de cuidado."
        },
        "🔥 Narciso Estratégico": {
            "forcas": "✔ Mistura inteligência emocional com carisma. ✔ Inspira e acalma ao mesmo tempo. ✔ Alta performance em contextos de tensão.",
            "riscos": "⚠ Pode internalizar tensões em silêncio até esgotar-se. ⚠ Pode buscar reconhecimento como forma de compensar o peso de conter tudo.",
            "recomendacoes": "➡ Divida responsabilidades emocionais. ➡ Cultive o reconhecimento interno, não só o externo."
        },
        "🧠 Observador Reflexivo": {
            "forcas": "✔ Altíssimo nível de percepção emocional e racional. ✔ Sabe esperar o momento certo de agir. ✔ Traz clareza e estabilidade para grupos confusos.",
            "riscos": "⚠ Pode se distanciar demais do grupo tentando manter neutralidade. ⚠ Pode cair em análise excessiva e postergar decisões importantes.",
            "recomendacoes": "➡ Confie no seu timing emocional e decida com coragem. ➡ Mantenha-se presente mesmo quando estiver processando internamente."
        },
        "🏗 Estruturador": {
            "forcas": "✔ Excelente para liderar ambientes de caos e incerteza. ✔ Gera segurança por meio de sistemas claros e postura firme. ✔ Constrói uma cultura emocionalmente sólida.",
            "riscos": "⚠ Pode se tornar inflexível com processos ou resistir a mudanças. ⚠ Pode achar que 'segurar tudo' é seu papel, sem delegar.",
            "recomendacoes": "➡ Desenvolva flexibilidade estratégica. ➡ Ensine sua equipe a segurar junto com você — não sozinho(a)."
        },
        "🪞 Espelho Emocional": {
            "forcas": "✔ Capacidade empática refinada. ✔ Leitura intuitiva das emoções do grupo. ✔ Inspira confiança e conexão não verbal.",
            "riscos": "⚠ Pode internalizar dores que não são suas. ⚠ Pode moldar seu comportamento em excesso para evitar desarmonia.",
            "recomendacoes": "➡ Cuide da sua identidade enquanto cuida dos outros. ➡ Use sua empatia como ferramenta, não como identidade central."
        }
    },
    "🔥 Narciso Estratégico": {
        "🛡 Protetor": {
            "forcas": "✔ Mobiliza com empatia e energia. ✔ Cria laços emocionais com facilidade. ✔ Inspira performance e pertencimento.",
            "riscos": "⚠ Pode se sentir sobrecarregado(a) por expectativas emocionais da equipe. ⚠ Pode adiar confrontos difíceis para preservar a imagem carinhosa.",
            "recomendacoes": "➡ Equilibre empatia com assertividade. ➡ Reforce sua autoridade para além da simpatia."
        },
        "🧱 Contenedor": {
            "forcas": "✔ Presença forte e magnética. ✔ Sabe conter o caos emocional da equipe com calma, liderando com presença e impacto. ✔ Impõe respeito e mobiliza corações.",
            "riscos": "⚠ Pode internalizar tensões em silêncio até esgotar-se. ⚠ Pode buscar reconhecimento para compensar o peso de conter tudo.",
            "recomendacoes": "➡ Divida responsabilidades emocionais com a equipe. ➡ Cultive o reconhecimento interno, não só o externo."
        },
        "🧠 Observador Reflexivo": {
            "forcas": "✔ Combinação de profundidade intelectual com carisma. ✔ Excelente comunicador estratégico. ✔ Habilidade de ler o ambiente e adaptar a abordagem para máxima influência.",
            "riscos": "⚠ Risco de usar a inteligência para manipular ou justificar ações egoístas. ⚠ A autoanálise pode focar apenas em otimizar a imagem.",
            "recomendacoes": "➡ Use sua capacidade de análise para construir relações mais genuínas. ➡ Separe seu valor da admiração que recebe."
        },
        "🏗 Estruturador": {
            "forcas": "✔ Combina energia carismática com organização metódica. ✔ Transforma visão em processos claros. ✔ Motiva a equipe enquanto mantém o controle.",
            "riscos": "⚠ Pode usar a estrutura para controlar e manter a centralidade. ⚠ Pode resistir a delegar para não perder o holofote.",
            "recomendacoes": "➡ Deixe a equipe brilhar também. ➡ Use a estrutura para empoderar, não para controlar."
        },
        "🪞 Espelho Emocional": {
            "forcas": "✔ Carisma adaptável e leitura refinada do ambiente. ✔ Conecta-se facilmente com diferentes públicos. ✔ Usa a percepção social para influenciar positivamente.",
            "riscos": "⚠ Pode se perder entre a imagem que projeta e quem realmente é. ⚠ Vulnerável à manipulação por buscar aprovação excessiva.",
            "recomendacoes": "➡ Mantenha uma âncora interna de valores além da aprovação. ➡ Reflita sobre suas motivações mais profundas."
        }
    },
    "🏗 Estruturador": {
        "🛡 Protetor": {
            "forcas": "✔ Une firmeza com sensibilidade. ✔ A equipe se sente segura porque você oferece direção, clareza e acolhimento. ✔ Protege através da organização.",
            "riscos": "⚠ Pode se tornar rígido(a) tentando 'salvar' todos. ⚠ Pode controlar excessivamente para evitar conflitos.",
            "recomendacoes": "➡ Confie mais na maturidade emocional do time. ➡ Flexibilize regras quando perceber crescimento autônomo."
        },
        "🧱 Contenedor": {
            "forcas": "✔ Líder de ferro com coração equilibrado. ✔ Organiza para proteger, cria rotinas para estabilizar. ✔ Conduz com tranquilidade firme.",
            "riscos": "⚠ Pode se tornar inflexível com processos. ⚠ Pode achar que 'segurar tudo' é seu papel, sem delegar.",
            "recomendacoes": "➡ Desenvolva flexibilidade estratégica. ➡ Ensine sua equipe a segurar junto com você."
        },
        "🔥 Narciso Estratégico": {
            "forcas": "✔ Combina visão estratégica com presença marcante. ✔ Usa a estrutura para amplificar seu impacto. ✔ Inspira confiança pela competência e carisma.",
            "riscos": "⚠ Pode usar a estrutura para manter controle e centralidade. ⚠ Pode resistir a mudanças que ameacem sua posição.",
            "recomendacoes": "➡ Deixe a equipe brilhar também. ➡ Use sua influência para desenvolver outros líderes."
        },
        "🧠 Observador Reflexivo": {
            "forcas": "✔ Excepcional capacidade de análise sistêmica e pensamento estratégico. ✔ Criação de estruturas lógicas, eficientes e otimizadas. ✔ Tomada de decisão baseada em dados e análise crítica.",
            "riscos": "⚠ Risco extremo de paralisia por análise, buscando a solução 'perfeita'. ⚠ Pode parecer excessivamente técnico ou desconectado da realidade prática.",
            "recomendacoes": "➡ Integre a intuição e o fator humano em suas análises. ➡ Torne-se mais confortável com a incerteza e a adaptação."
        },
        "🪞 Espelho Emocional": {
            "forcas": "✔ Cria processos que promovem colaboração e minimizam atritos. ✔ Comunica regras de forma clara e diplomática. ✔ Ambiente organizado, previsível e com baixo conflito.",
            "riscos": "⚠ Pode criar regras para evitar conversas difíceis. ⚠ Pode sacrificar agilidade em nome da harmonia e ordem.",
            "recomendacoes": "➡ Use a clareza dos processos para abordar conflitos de forma construtiva. ➡ Equilibre ordem com flexibilidade."
        }
    },
    "🪞 Espelho Emocional": {
        "🛡 Protetor": {
            "forcas": "✔ Capacidade ímpar de adaptação e acolhimento. ✔ Percebe e responde às necessidades emocionais da equipe. ✔ Constrói conexões profundas e segurança psicológica.",
            "riscos": "⚠ Pode perder autenticidade tentando corresponder a expectativas. ⚠ Pode se frustrar com rejeições sutis.",
            "recomendacoes": "➡ Mantenha contato com sua identidade, além da imagem percebida. ➡ Fortaleça a liderança com base em valores."
        },
        "🧱 Contenedor": {
            "forcas": "✔ Absorve o ambiente como uma esponja refinada. ✔ Sensibilidade rara para o emocional coletivo. ✔ Atua como espelho silencioso da equipe.",
            "riscos": "⚠ Pode internalizar dores que não são suas. ⚠ Pode moldar comportamento em excesso para evitar desarmonia.",
            "recomendacoes": "➡ Cuide da sua identidade enquanto cuida dos outros. ➡ Use empatia como ferramenta, não como identidade central."
        },
        "🔥 Narciso Estratégico": {
            "forcas": "✔ Carisma adaptável e leitura refinada do ambiente. ✔ Conecta-se facilmente com diferentes públicos. ✔ Usa a percepção social para influenciar positivamente.",
            "riscos": "⚠ Pode se perder entre a imagem que projeta e quem é. ⚠ Vulnerável à manipulação por buscar aprovação excessiva.",
            "recomendacoes": "➡ Mantenha uma âncora interna de valores. ➡ Reflita sobre suas motivações mais profundas."
        },
        "🏗 Estruturador": {
            "forcas": "✔ Cria processos que acomodam necessidades relacionais. ✔ Sensível para ajustar estruturas de forma diplomática. ✔ Liderança equilibrada, justa e cuidadosa.",
            "riscos": "⚠ Pode criar burocracia para evitar conversas difíceis. ⚠ Pode sacrificar agilidade em nome da harmonia.",
            "recomendacoes": "➡ Use estrutura para abordar conflitos construtivamente. ➡ Equilibre ordem com flexibilidade e autenticidade."
        },
        "🧠 Observador Reflexivo": {
            "forcas": "✔ Excepcional inteligência emocional e interpessoal. ✔ Habilidade de ler entrelinhas e compreender motivações ocultas. ✔ Pode ser excelente coach ou mentor.",
            "riscos": "⚠ Risco de paralisia por análise nas relações. ⚠ Pode usar compreensão para evitar confrontos necessários.",
            "recomendacoes": "➡ Use sua compreensão para agir com coragem e autenticidade. ➡ Equilibre observação com expressão genuína."
        }
    },
    "🧠 Observador Reflexivo": {
        "🛡 Protetor": {
            "forcas": "✔ Inspira confiança e acolhimento. ✔ Capacidade de análise emocional e previsão de conflitos. ✔ Toma decisões considerando o impacto humano.",
            "riscos": "⚠ Pode absorver emocionalmente os problemas do time. ⚠ Pode hesitar diante de decisões duras por empatia excessiva.",
            "recomendacoes": "➡ Estabeleça limites claros entre você e a equipe. ➡ Reserve tempo para ação, não apenas para análise."
        },
        "🧱 Contenedor": {
            "forcas": "✔ Excepcional combinação de inteligência emocional e racional. ✔ Profunda estabilidade e capacidade de análise, mesmo sob pressão. ✔ Excelente em gerenciar crises e conflitos delicados.",
            "riscos": "⚠ Risco de distanciamento excessivo, parecendo frio ou analítico demais. ⚠ Pode intelectualizar excessivamente as emoções.",
            "recomendacoes": "➡ Compartilhe mais da sua humanidade sem perder sua força. ➡ Equilibre a observação com a participação ativa."
        },
        "🔥 Narciso Estratégico": {
            "forcas": "✔ Combinação de profundidade intelectual com carisma. ✔ Excelente comunicador estratégico, capaz de persuadir com lógica e emoção. ✔ Capaz de gerar admiração tanto pelo conteúdo quanto pela forma.",
            "riscos": "⚠ Risco de cinismo ou de usar a inteligência para manipular. ⚠ Pode se tornar excessivamente calculista.",
            "recomendacoes": "➡ Use sua inteligência a serviço da conexão genuína e do propósito maior. ➡ Separe seu valor da admiração que recebe."
        },
        "🏗 Estruturador": {
            "forcas": "✔ Excepcional capacidade de análise sistêmica e pensamento estratégico. ✔ Criação de estruturas lógicas e otimizadas. ✔ Liderança percebida como altamente inteligente e metódica.",
            "riscos": "⚠ Risco extremo de paralisia por análise. ⚠ Pode supervalorizar a lógica, negligenciando fatores humanos e emocionais.",
            "recomendacoes": "➡ Integre a intuição, a emoção e o fator humano em suas análises. ➡ Torne-se mais confortável com a incerteza."
        },
        "🪞 Espelho Emocional": {
            "forcas": "✔ Excepcional inteligência emocional e interpessoal. ✔ Habilidade de ler entrelinhas e compreender motivações ocultas. ✔ Adapta-se às necessidades do grupo com consciência.",
            "riscos": "⚠ Risco de paralisia pela análise das relações. ⚠ Pode usar a compreensão para evitar confrontos ou manipular sutilmente.",
            "recomendacoes": "➡ Use sua compreensão para construir relações autênticas, mesmo que envolvam conflito. ➡ Equilibre a cabeça e o coração."
        }
    }
}

MODULES_DATA = [
    {
        "id": 0, 
        "name": "Introducao: A Jornada LPS", 
        "title": "A Jornada LPS", 
        "description": "Apresentacao da metodologia, boas-vindas da Viviane Nishiura e o mapa da jornada entre Neurociencia e Psicanalise. Conheca o caminho que vai transformar sua lideranca.", 
        "icon": "🚀", 
        "file": "attached_assets/introdução_1768431876966.pdf", 
        "videos": [
            "https://vimeo.com/1154502544",
            "https://vimeo.com/1154502598",
            "https://vimeo.com/1154502492"
        ]
    },
    {
        "id": 1, 
        "name": "Modulo 1: Neurociencia da Lideranca", 
        "title": "Neurociencia da Lideranca", 
        "description": "Foco em quimicos cerebrais (dopamina, ocitocina) e o Circulo de Seguranca. Entenda como o cerebro processa decisoes e aprenda a usar a neurociencia para liderar com mais eficacia.", 
        "icon": "🧠", 
        "file": "attached_assets/Módulo_1_1768431876967.pdf", 
        "videos": [
            "https://vimeo.com/1154503073",
            "https://vimeo.com/1154503122",
            "https://vimeo.com/1154503201",
            "https://vimeo.com/1154503286",
            "https://vimeo.com/1154503332",
            "https://vimeo.com/1154502907",
            "https://vimeo.com/1154502997"
        ]
    },
    {
        "id": 2, 
        "name": "Modulo 2: Mergulho no Inconsciente", 
        "title": "Mergulho no Inconsciente", 
        "description": "Estudo do Id, Ego, Superego e mecanismos de defesa. Explore as camadas profundas da mente e descubra como padroes inconscientes influenciam sua lideranca.", 
        "icon": "🌊", 
        "file": "attached_assets/Módulo_2_1768431876968.pdf", 
        "videos": [
            "https://vimeo.com/1154504282",
            "https://vimeo.com/1154503918",
            "https://vimeo.com/1154503996",
            "https://vimeo.com/1154504129",
            "https://vimeo.com/1154504216",
            "https://vimeo.com/1154504054"
        ]
    },
    {
        "id": 3, 
        "name": "Modulo 3: Relacoes e Transferencia", 
        "title": "Relacoes e Transferencia", 
        "description": "Dinamicas lider-liderado e manejo de contratransferencia. Compreenda as dinamicas de transferencia nas relacoes profissionais e como usa-las a seu favor.", 
        "icon": "🔄", 
        "file": "attached_assets/Módulo_3_1768431876969.pdf", 
        "videos": [
            "https://vimeo.com/1154508629",
            "https://vimeo.com/1154508577",
            "https://vimeo.com/1154508688",
            "https://vimeo.com/1154508745",
            "https://vimeo.com/1154508530"
        ]
    },
    {
        "id": 4, 
        "name": "Modulo 4: Autoconsciencia", 
        "title": "Autoconsciencia", 
        "description": "Identificacao do seu arquetipo de lideranca psicanalitica. Desenvolva autoconhecimento profundo e identifique seus gatilhos emocionais como lider.", 
        "icon": "🪞", 
        "file": "attached_assets/Módulo_4_1768431876970.pdf", 
        "videos": [
            "https://vimeo.com/1154509566",
            "https://vimeo.com/1154509679",
            "https://vimeo.com/1154509769",
            "https://vimeo.com/1154509511"
        ]
    },
    {
        "id": 5, 
        "name": "Modulo 5: Entendendo a Equipe", 
        "title": "Entendendo a Equipe", 
        "description": "Mapeamento com assessments e os papeis grupais de Bion. Aprenda a mapear perfis e dinamicas grupais usando conceitos psicanaliticos.", 
        "icon": "👥", 
        "file": "attached_assets/Módulo_5_1768431876971.pdf", 
        "videos": [
            "https://vimeo.com/1154510241",
            "https://vimeo.com/1154510404",
            "https://vimeo.com/1154510309"
        ]
    },
    {
        "id": 6, 
        "name": "Modulo 6: Aplicacao Pratica", 
        "title": "Aplicacao Pratica", 
        "description": "Analise de casos reais e construcao do plano de acao personalizado. Coloque em pratica as ferramentas psicanaliticas no dia a dia da lideranca.", 
        "icon": "🛠️", 
        "file": "attached_assets/Módulo_6_1768431876972.pdf", 
        "videos": [
            "https://vimeo.com/1154510682",
            "https://vimeo.com/1154510710",
            "https://vimeo.com/1154510729",
            "https://vimeo.com/1154510816"
        ]
    },
    {
        "id": 7, 
        "name": "Modulo 7: Lideranca de Alta Performance", 
        "title": "Lideranca de Alta Performance e Sustentabilidade", 
        "description": "Como manter os resultados a longo prazo, gestao da cultura organizacional e o fechamento do ciclo de desenvolvimento. Consolide sua transformacao como lider.", 
        "icon": "🏆", 
        "file": "attached_assets/Módulo_7_1768431876973.pdf", 
        "videos": [
            "https://vimeo.com/1154511020",
            "https://vimeo.com/1154511064"
        ]
    }
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

# Floating WhatsApp Button (appears on all pages) - Black text for readability
st.markdown(f'''
    <style>
    .whatsapp-float {{
        color: #000000 !important;
        font-weight: bold;
    }}
    </style>
    <a href="{WHATSAPP_URL}" target="_blank" class="whatsapp-float" style="color: #000000 !important;">
        <span style="font-size: 1.5rem;">💬</span>
        Falar com Consultor
    </a>
''', unsafe_allow_html=True)

# Navigation Menu Sections with Icons
MENU_SECTIONS = [
    {"key": "home", "label": "Home", "icon": "🏠"},
    {"key": "sobre", "label": "Sobre", "icon": "👤"},
    {"key": "curso", "label": "Curso", "icon": "📚"},
    {"key": "lpstest", "label": "LPTest", "icon": "🧠"},
    {"key": "lpschat", "label": "LPChat", "icon": "💬"},
    {"key": "mentoria", "label": "Mentoria", "icon": "📅"},
    {"key": "soluções", "label": "Soluções", "icon": "💼"},
    {"key": "insights", "label": "Insights", "icon": "📰"},
    {"key": "contato", "label": "Contato", "icon": "📧"}
]

# Sidebar Navigation - Uses unique keys per page context
def render_sidebar_navigation():
    # Use page context for unique widget keys
    page_ctx = st.session_state.get('page', 'Home')
    key_prefix = f"sb_{page_ctx}_"
    
    with st.sidebar:
        # Sidebar CSS styling - Premium Design
        st.markdown("""
            <style>
            /* Global page background */
            .stApp {
                background-color: #F5F5F5 !important;
            }
            .stApp > header {
                background-color: #F5F5F5 !important;
            }
            /* Main content text color */
            .stApp .stMarkdown p, .stApp .stMarkdown li, .stApp .stMarkdown span {
                color: #000000;
            }
            /* Sidebar styling */
            [data-testid="stSidebar"] {
                background-color: #18738c !important;
                padding-top: 0;
            }
            [data-testid="stSidebar"] > div:first-child {
                background-color: #18738c !important;
            }
            /* Sidebar buttons */
            [data-testid="stSidebar"] .stButton > button {
                background-color: transparent;
                color: #FFFFFF !important;
                border: none;
                text-align: left;
                padding: 1rem 1.25rem;
                font-size: 1.05rem;
                font-weight: 500;
                width: 100%;
                border-radius: 8px;
                margin-bottom: 0.5rem;
                transition: all 0.2s ease;
                white-space: nowrap;
            }
            [data-testid="stSidebar"] .stButton > button:hover {
                background-color: rgba(209, 159, 9, 0.25) !important;
                color: #d19f09 !important;
            }
            [data-testid="stSidebar"] .stButton > button[kind="primary"] {
                background-color: #d19f09 !important;
                color: #18738c !important;
                font-weight: bold;
            }
            [data-testid="stSidebar"] .stButton > button[kind="primary"]:hover {
                background-color: #e6c654 !important;
            }
            /* Logo container - Full width, no borders */
            .sidebar-logo-container {
                text-align: center;
                padding: 0;
                margin: 0;
                background-color: transparent;
            }
            .sidebar-logo-container img {
                width: 100% !important;
                max-width: 100% !important;
            }
            /* Remove top padding from sidebar */
            [data-testid="stSidebar"] > div:first-child > div:first-child {
                padding-top: 0 !important;
                margin-top: 0 !important;
            }
            /* Sidebar divider */
            .sidebar-divider {
                border-top: 1px solid rgba(255,255,255,0.15);
                margin: 1rem 0;
            }
            /* User badge */
            .user-badge {
                background-color: rgba(209, 159, 9, 0.15);
                border: 2px solid #d19f09;
                color: #d19f09;
                padding: 0.75rem 1rem;
                border-radius: 25px;
                text-align: center;
                font-weight: bold;
                margin-bottom: 1rem;
                font-size: 0.95rem;
            }
            /* Navigation label */
            .nav-section-label {
                color: #d19f09;
                font-size: 0.75rem;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 1px;
                padding-left: 1.25rem;
                margin-bottom: 0.75rem;
            }
            /* WhatsApp buttons - Black text */
            .whatsapp-float {
                color: #000000 !important;
            }
            a[href*="wa.me"], a[href*="whatsapp"] {
                color: #000000 !important;
            }
            </style>
        """, unsafe_allow_html=True)
        
        # Logo Only (Full Width, No Text Title)
        st.markdown('<div class="sidebar-logo-container">', unsafe_allow_html=True)
        if os.path.exists(LOGO_PATH):
            st.image(LOGO_PATH, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Login/User Section at Top
        if st.session_state.authenticated:
            st.markdown(f"""
                <div class="user-badge">{st.session_state.user['name']}</div>
            """, unsafe_allow_html=True)
            if st.button("Minha Area", key=f"{key_prefix}dashboard", use_container_width=True):
                st.session_state.page = "Dashboard"
                st.rerun()
            if st.button("Sair", key=f"{key_prefix}logout", use_container_width=True):
                st.session_state.authenticated = False
                st.session_state.user = None
                st.session_state.page = "Home"
                st.rerun()
        else:
            if st.button("Entrar", key=f"{key_prefix}login", use_container_width=True, type="primary"):
                st.session_state.page = "Login"
                st.rerun()
        
        st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)
        
        # Navigation Menu (no label - clean design)
        current = st.session_state.section
        for item in MENU_SECTIONS:
            is_active = (current == item["key"])
            btn_label = f"{item['icon']}   {item['label']}"
            if st.button(btn_label, key=f"{key_prefix}nav_{item['key']}", use_container_width=True, type="primary" if is_active else "secondary"):
                st.session_state.section = item["key"]
                st.session_state.show_login_modal = False
                st.rerun()
        
        # Footer in sidebar
        st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)
        st.markdown("""
            <p style="color: rgba(255,255,255,0.6); font-size: 0.7rem; text-align: center; padding: 0.5rem;">
                2026 Viviane Nishiura<br>
                Todos os direitos reservados
            </p>
        """, unsafe_allow_html=True)

# Public Header (simplified - navigation moved to sidebar)
def render_public_header():
    # Just show a clean header with page title
    st.markdown("""
        <div style="background: linear-gradient(135deg, #18738c 0%, #1a4f7a 100%); padding: 1.5rem; border-radius: 10px; margin-bottom: 1.5rem;">
            <h1 style="color: #d19f09; font-size: 1.8rem; margin: 0; text-align: center;">
                Liderança Psicanalítica
            </h1>
            <p style="color: rgba(255,255,255,0.8); text-align: center; margin: 0.5rem 0 0 0; font-size: 0.95rem;">
                Transforme sua gestão com Psicanálise e Neurociência
            </p>
        </div>
    """, unsafe_allow_html=True)

# Login Page Function
def render_login_page():
    st.markdown("""
        <style>
        .login-container {
            background-color: #18738c;
            padding: 3rem;
            border-radius: 15px;
            max-width: 450px;
            margin: 2rem auto;
            box-shadow: 0 8px 25px rgba(0,0,0,0.3);
        }
        .login-title {
            color: #d19f09;
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
            <h1 style="color: #18738c; font-size: 2.5rem; text-align: center; font-weight: bold; margin: 0.5rem 0;">
                Liderança Psicanalítica
            </h1>
            <div style="background-color: #18738c; padding: 1.5rem; border-radius: 15px; margin-top: 1rem;">
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
        if st.button("📝 LPTest", key="nav_test"):
            st.session_state.page = "LPTest"
            st.rerun()
        if st.button("👥 Gestão de Equipe", key="nav_team"):
            st.session_state.page = "TeamManagement"
            st.rerun()
        if st.button("💬 LPChat", key="nav_chat"):
            st.session_state.page = "LPChat"
            st.rerun()
        if st.button("📅 Mentoria", key="nav_mentoria"):
            st.session_state.page = "Mentoria"
            st.rerun()
        if st.button("👤 Sobre", key="nav_sobre"):
            st.session_state.page = "Sobre"
            st.rerun()
        if st.button("📚 Guia e Suporte", key="nav_guia"):
            st.session_state.page = "GuiaSuporte"
            st.rerun()
        st.write("---")
        st.markdown(f'[💬 Suporte via WhatsApp]({WHATSAPP_URL})')
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
        textColor=HexColor('#18738c'),
        alignment=TA_CENTER,
        spaceAfter=20
    ))
    
    # Subtitle style
    styles.add(ParagraphStyle(
        name='LPSSubtitle',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=HexColor('#d19f09'),
        alignment=TA_CENTER,
        spaceAfter=15
    ))
    
    # Section header
    styles.add(ParagraphStyle(
        name='LPSSection',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=HexColor('#18738c'),
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
            Paragraph("<font color='white' size='14'><b>Lideranca Psicanalitica</b></font><br/><font color='#d19f09' size='10'>Viviane Nishiura & Equipe LPS</font>", getSampleStyleSheet()['Normal'])
        ]]
    else:
        # Fallback to text-based header if logo not found
        header_data = [[
            Paragraph("<font color='#d19f09' size='28'><b>LPS</b></font>", getSampleStyleSheet()['Normal']),
            Paragraph("<font color='white' size='12'>Lideranca Psicanalitica<br/><font size='9'>Viviane Nishiura & Equipe</font></font>", getSampleStyleSheet()['Normal'])
        ]]
    
    header_table = Table(header_data, colWidths=[1.5*inch, 4*inch])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), HexColor('#18738c')),
        ('TEXTCOLOR', (0, 0), (0, 0), HexColor('#d19f09')),
        ('TEXTCOLOR', (1, 0), (1, 0), HexColor('#FFFFFF')),
        ('ALIGN', (0, 0), (0, 0), 'CENTER'),
        ('ALIGN', (1, 0), (1, 0), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ('BOX', (0, 0), (-1, -1), 1, HexColor('#18738c')),
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
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#18738c')),
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
    elements.append(Paragraph("Analise gerada pela LPChat - Consultora de IA em Psicanalise e Neurociencia", styles['LPSInfo']))
    elements.append(Paragraph("Plataforma LPS - Viviane Nishiura & Equipe LPS", styles['LPSInfo']))
    
    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()

def generate_manager_guide_pdf():
    """Generate the Manager's Guide PDF with LPS methodology."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.75*inch, bottomMargin=0.75*inch)
    styles = create_pdf_styles()
    elements = []
    
    # Styled header with LPS branding
    elements.append(create_pdf_header_table())
    elements.append(Spacer(1, 20))
    
    # Title
    elements.append(Paragraph("Manual do Gestor LPS", styles['LPSTitle']))
    elements.append(Paragraph("Guia Pratico para Lideranca Psicanalitica", styles['LPSInfo']))
    elements.append(Spacer(1, 30))
    
    # Section 1: Como interpretar seu Perfil
    elements.append(Paragraph("1. Como Interpretar seu Perfil", styles['LPSSection']))
    elements.append(Spacer(1, 10))
    elements.append(Paragraph(
        "Seu perfil de lideranca revela seus arquetipos inconscientes dominantes - padroes de comportamento "
        "que operam abaixo da consciencia e influenciam como voce lidera sua equipe.",
        styles['LPSBody']))
    elements.append(Spacer(1, 8))
    
    # Profile descriptions
    profiles = [
        ("Protetor", "Voce tende a acolher e cuidar da equipe. Seu ponto forte e criar ambientes seguros. "
         "Atencao: pode haver dificuldade em cobrar resultados ou dar feedbacks dificeis."),
        ("Contenedor", "Voce absorve tensoes do grupo e mantem estabilidade emocional. Essencial em crises. "
         "Atencao: risco de sobrecarga emocional e esgotamento."),
        ("Narciso Estrategico", "Voce inspira e motiva atraves de visao e carisma. Mobiliza a equipe para grandes objetivos. "
         "Atencao: pode centralizar demais e dificultar a autonomia."),
        ("Estruturador", "Voce organiza processos e garante previsibilidade. Equipes bem estruturadas. "
         "Atencao: rigidez excessiva pode inibir criatividade e inovacao."),
        ("Espelho Emocional", "Voce valida emocoes e cria conexao empatica. Equipes se sentem ouvidas. "
         "Atencao: pode absorver problemas alheios e perder objetividade."),
        ("Observador Reflexivo", "Voce analisa profundamente antes de agir. Decisoes ponderadas e estrategicas. "
         "Atencao: pode parecer distante ou demorar demais para decidir.")
    ]
    
    for name, desc in profiles:
        elements.append(Paragraph(f"<b>{name}:</b> {desc}", styles['LPSBody']))
        elements.append(Spacer(1, 5))
    
    elements.append(Spacer(1, 20))
    
    # Section 2: Mapeamento de Equipe
    elements.append(Paragraph("2. Mapeamento de Equipe", styles['LPSSection']))
    elements.append(Spacer(1, 10))
    elements.append(Paragraph(
        "O LPTest mapeia os perfis inconscientes de sua equipe, permitindo entender dinamicas grupais "
        "que impactam produtividade, conflitos e turnover.",
        styles['LPSBody']))
    elements.append(Spacer(1, 8))
    
    elements.append(Paragraph("<b>Como usar para reduzir turnover:</b>", styles['LPSBody']))
    elements.append(Paragraph(
        "- Identifique funcionarios cujo perfil nao se adequa ao cargo atual", styles['LPSBody']))
    elements.append(Paragraph(
        "- Realoque pessoas com base em suas tendencias naturais", styles['LPSBody']))
    elements.append(Paragraph(
        "- Crie pares complementares (ex: Estruturador + Criativo)", styles['LPSBody']))
    elements.append(Spacer(1, 8))
    
    elements.append(Paragraph("<b>Como usar para reduzir conflitos:</b>", styles['LPSBody']))
    elements.append(Paragraph(
        "- Identifique Bodes Expiatorios e proteja-os de projecoes negativas", styles['LPSBody']))
    elements.append(Paragraph(
        "- Reconheca Porta-Vozes como sensores do clima organizacional", styles['LPSBody']))
    elements.append(Paragraph(
        "- Transforme Lideres de Luta-Fuga em agentes de mudanca construtiva", styles['LPSBody']))
    
    elements.append(Spacer(1, 20))
    
    # Section 3: Uso Estratégico do LPChat
    elements.append(Paragraph("3. Uso Estrategico do LPChat", styles['LPSSection']))
    elements.append(Spacer(1, 10))
    elements.append(Paragraph(
        "O LPChat e sua consultora de IA especializada em psicanalise e neurociencia aplicada a lideranca. "
        "Para obter os melhores insights, faca perguntas especificas sobre sua equipe.",
        styles['LPSBody']))
    elements.append(Spacer(1, 8))
    
    elements.append(Paragraph("<b>Perguntas recomendadas:</b>", styles['LPSBody']))
    questions = [
        "Quais conflitos inconscientes podem surgir entre [Funcionario A] e [Funcionario B]?",
        "Qual funcionario seria ideal para liderar o projeto X, considerando os perfis mapeados?",
        "Como posso dar feedback construtivo para um Dependente sem gerar mais dependencia?",
        "Quais dinamicas de transferencia podem estar afetando minha relacao com a equipe?",
        "Como aplicar conceitos de neurociencia para reduzir o estresse no time?"
    ]
    for q in questions:
        elements.append(Paragraph(f"- {q}", styles['LPSBody']))
    
    elements.append(Spacer(1, 20))
    
    # Section 4: Passo a Passo da Mentoria
    elements.append(Paragraph("4. Passo a Passo da Mentoria", styles['LPSSection']))
    elements.append(Spacer(1, 10))
    elements.append(Paragraph(
        "A mentoria com Viviane Nishiura e o momento de aprofundar sua jornada de lideranca consciente. "
        "Prepare-se adequadamente para maximizar os resultados.",
        styles['LPSBody']))
    elements.append(Spacer(1, 8))
    
    elements.append(Paragraph("<b>Antes da sessao:</b>", styles['LPSBody']))
    elements.append(Paragraph("1. Revise seu perfil de lideranca no Dashboard", styles['LPSBody']))
    elements.append(Paragraph("2. Analise os resultados do mapeamento de equipe", styles['LPSBody']))
    elements.append(Paragraph("3. Identifique 2-3 desafios especificos que deseja abordar", styles['LPSBody']))
    elements.append(Paragraph("4. Anote situacoes concretas para discutir", styles['LPSBody']))
    elements.append(Spacer(1, 8))
    
    elements.append(Paragraph("<b>Durante a sessao:</b>", styles['LPSBody']))
    elements.append(Paragraph("- Compartilhe abertamente seus desafios", styles['LPSBody']))
    elements.append(Paragraph("- Pergunte sobre padroes inconscientes que nao consegue ver", styles['LPSBody']))
    elements.append(Paragraph("- Solicite exercicios praticos para aplicar no dia-a-dia", styles['LPSBody']))
    elements.append(Spacer(1, 8))
    
    elements.append(Paragraph("<b>Como agendar:</b>", styles['LPSBody']))
    elements.append(Paragraph(
        "Acesse o menu 'Mentoria' no Dashboard ou envie mensagem via WhatsApp para agendar sua sessao.",
        styles['LPSBody']))
    
    # Footer
    elements.append(Spacer(1, 30))
    elements.append(Paragraph("_" * 60, styles['LPSInfo']))
    elements.append(Paragraph("Plataforma LPS - Lideranca Psicanalitica", styles['LPSInfo']))
    elements.append(Paragraph("Viviane Nishiura & Equipe LPS", styles['LPSInfo']))
    elements.append(Paragraph(f"Versao: {datetime.now().strftime('%m/%Y')}", styles['LPSInfo']))
    
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
    fig.suptitle(f'Perfil da Equipe - {manager_name}', fontsize=16, color='#18738c', fontweight='bold')
    
    # Colors matching LPS brand
    colors_profile = ['#18738c', '#1a4f7a', '#2d6a9f', '#4080b5', '#5596c9', '#6aabdc']
    colors_bion = ['#d19f09', '#e6c54e', '#d9b83e', '#ccab2e', '#bf9e1e', '#b2910e']
    
    # Profile distribution pie chart
    if profile_counts:
        labels1 = list(profile_counts.keys())
        sizes1 = list(profile_counts.values())
        ax1.pie(sizes1, labels=labels1, colors=colors_profile[:len(labels1)], autopct='%1.0f%%', startangle=90)
        ax1.set_title('Perfis de Lideranca', fontsize=12, color='#18738c')
    else:
        ax1.text(0.5, 0.5, 'Sem dados', ha='center', va='center')
        ax1.set_title('Perfis de Lideranca', fontsize=12, color='#18738c')
    
    # Bion roles bar chart
    if bion_counts:
        labels2 = list(bion_counts.keys())
        sizes2 = list(bion_counts.values())
        bars = ax2.barh(labels2, sizes2, color=colors_bion[:len(labels2)])
        ax2.set_xlabel('Quantidade')
        ax2.set_title('Papeis de Bion', fontsize=12, color='#18738c')
        ax2.set_xlim(0, max(sizes2) + 1)
        for bar, size in zip(bars, sizes2):
            ax2.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2, str(size), va='center')
    else:
        ax2.text(0.5, 0.5, 'Sem dados', ha='center', va='center')
        ax2.set_title('Papeis de Bion', fontsize=12, color='#18738c')
    
    plt.tight_layout()
    
    # Save to buffer
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    buffer.seek(0)
    return buffer.getvalue()

def generate_radar_chart(block_sums, profile_name=""):
    """Generate a radar chart showing the 6 axes of the assessment."""
    import numpy as np
    
    # Define the 6 axes with short names
    categories = [
        'Autoridade\nInterna',
        'Contencao\nEmocional',
        'Narcisismo\nReconhecimento',
        'Estrutura\nOrdem',
        'Relacao\nEmpatia',
        'Reflexao\nObservacao'
    ]
    
    # Map full block names to short names for data extraction
    block_keys = [
        "Bloco 1 – Autoridade Interna e Autoimagem",
        "Bloco 2 – Contenção Emocional do Grupo",
        "Bloco 3 – Narcisismo e Reconhecimento",
        "Bloco 4 – Estrutura e Lógica de Tarefa",
        "Bloco 5 – Relação com a Equipe e Projeções",
        "Bloco 6 – Reflexão, Crítica e Autoconsciência"
    ]
    
    # Get values (max is 40 for each block - 8 questions x 5 points)
    values = []
    for key in block_keys:
        val = block_sums.get(key, 24)  # Default to midpoint if not found
        # Normalize to percentage (0-100)
        normalized = (val / 40) * 100
        values.append(normalized)
    
    # Number of variables
    N = len(categories)
    
    # Compute angle for each category
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    values_plot = values + [values[0]]  # Complete the loop
    angles += angles[:1]  # Complete the loop
    
    # Create figure
    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
    
    # Plot data
    ax.fill(angles, values_plot, color='#18738c', alpha=0.25)
    ax.plot(angles, values_plot, color='#18738c', linewidth=2)
    
    # Add markers
    ax.scatter(angles[:-1], values, color='#d19f09', s=100, zorder=5)
    
    # Set category labels
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, size=10, color='#18738c')
    
    # Set y-axis limits
    ax.set_ylim(0, 100)
    ax.set_yticks([20, 40, 60, 80, 100])
    ax.set_yticklabels(['20%', '40%', '60%', '80%', '100%'], size=8, color='gray')
    
    # Title
    title = f'Perfil de Lideranca: {profile_name}' if profile_name else 'Perfil de Lideranca'
    ax.set_title(title, size=14, color='#18738c', fontweight='bold', pad=20)
    
    # Style
    ax.grid(True, color='gray', linestyle='-', linewidth=0.5, alpha=0.5)
    ax.spines['polar'].set_color('#18738c')
    
    # Save to buffer
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    buffer.seek(0)
    return buffer.getvalue()

def save_assessment_responses(respondent_id, respondent_type, responses):
    """Save each individual response (1-5) to the database for future AI analysis."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    for block_name, questions in ASSESSMENT_QUESTIONS.items():
        for q_idx, question_text in enumerate(questions):
            response_key = f"{block_name}_{q_idx}"
            response_value = responses.get(response_key, 3)
            
            response_id = str(uuid.uuid4())
            c.execute("""INSERT INTO assessment_responses 
                        (id, respondent_id, respondent_type, block_name, question_index, question_text, response_value)
                        VALUES (?, ?, ?, ?, ?, ?, ?)""",
                     (response_id, respondent_id, respondent_type, block_name, q_idx, question_text, response_value))
    
    conn.commit()
    conn.close()

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
    
    # Convert full block names to short names for Bion classification
    short_block_sums = {}
    for full_name, value in block_sums.items():
        short_name = BLOCK_SHORT_NAMES.get(full_name, full_name)
        short_block_sums[short_name] = value
    
    bion_role = classify_bion_role(short_block_sums)
    
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
            <a href="{WHATSAPP_URL}" target="_blank" class="cta-button" style="display: block; text-align: center; background-color: #25D366; color: #000000;">
                💬 Comprar Curso
            </a>
        """, unsafe_allow_html=True)

# PDF Generation Functions with LPS Branding
def generate_individual_pdf(employee_data, manager_name=""):
    """Generate individual employee PDF report with LPS branding."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.75*inch, bottomMargin=0.75*inch)
    
    # Colors
    navy_blue = HexColor('#18738c')
    gold = HexColor('#d19f09')
    light_gray = HexColor('#F5F5F5')
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'LPSTitle',
        parent=styles['Title'],
        fontName='Helvetica-Bold',
        fontSize=18,
        textColor=navy_blue,
        alignment=TA_CENTER,
        spaceAfter=20
    )
    subtitle_style = ParagraphStyle(
        'LPSSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=14,
        textColor=navy_blue,
        spaceAfter=10,
        spaceBefore=15
    )
    body_style = ParagraphStyle(
        'LPSBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        textColor=HexColor('#333333'),
        alignment=TA_JUSTIFY,
        spaceAfter=8
    )
    
    elements = []
    
    # Title
    elements.append(Paragraph("Liderança Psicanalítica - Laudo Individual", title_style))
    elements.append(Spacer(1, 20))
    
    # Employee Info Table
    name = employee_data.get('name', 'Não informado')
    email = employee_data.get('email', 'Não informado')
    profile_dom = employee_data.get('profile_dominant', 'Não realizado')
    profile_sec = employee_data.get('profile_secondary', 'Não realizado')
    bion_role = employee_data.get('bion_role', 'Não classificado')
    
    info_data = [
        ['Nome:', name],
        ['Email:', email],
        ['Perfil Dominante:', profile_dom],
        ['Perfil Secundário:', profile_sec],
        ['Papel de Bion:', bion_role]
    ]
    
    info_table = Table(info_data, colWidths=[2*inch, 4*inch])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), light_gray),
        ('TEXTCOLOR', (0, 0), (0, -1), navy_blue),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, navy_blue),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 20))
    
    # Profile Details
    profile_details = employee_data.get('profile_details', {})
    if profile_details:
        elements.append(Paragraph("Análise do Perfil", subtitle_style))
        
        if 'forcas' in profile_details:
            elements.append(Paragraph("<b>Forças:</b>", body_style))
            elements.append(Paragraph(profile_details['forcas'], body_style))
        
        if 'riscos' in profile_details:
            elements.append(Paragraph("<b>Riscos:</b>", body_style))
            elements.append(Paragraph(profile_details['riscos'], body_style))
        
        if 'recomendacoes' in profile_details:
            elements.append(Paragraph("<b>Recomendações:</b>", body_style))
            elements.append(Paragraph(profile_details['recomendacoes'], body_style))
    
    # Footer
    elements.append(Spacer(1, 30))
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=9,
        textColor=HexColor('#666666'),
        alignment=TA_CENTER
    )
    elements.append(Paragraph(f"Relatório gerado em {datetime.now().strftime('%d/%m/%Y %H:%M')}", footer_style))
    elements.append(Paragraph("Liderança Psicanalítica - Todos os direitos reservados", footer_style))
    
    doc.build(elements)
    buffer.seek(0)
    return buffer

def generate_team_pdf(employees_list, manager_name=""):
    """Generate team PDF report with all employees."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.75*inch, bottomMargin=0.75*inch)
    
    # Colors
    navy_blue = HexColor('#18738c')
    gold = HexColor('#d19f09')
    light_gray = HexColor('#F5F5F5')
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'LPSTitle',
        parent=styles['Title'],
        fontName='Helvetica-Bold',
        fontSize=18,
        textColor=navy_blue,
        alignment=TA_CENTER,
        spaceAfter=20
    )
    subtitle_style = ParagraphStyle(
        'LPSSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=14,
        textColor=navy_blue,
        spaceAfter=10,
        spaceBefore=15
    )
    
    elements = []
    
    # Title
    elements.append(Paragraph("Liderança Psicanalítica - Relatório da Equipe", title_style))
    if manager_name:
        elements.append(Paragraph(f"Gestor: {manager_name}", ParagraphStyle(
            'ManagerName',
            parent=styles['Normal'],
            fontSize=12,
            textColor=navy_blue,
            alignment=TA_CENTER
        )))
    elements.append(Spacer(1, 20))
    
    # Team Summary Table
    elements.append(Paragraph("Membros da Equipe", subtitle_style))
    
    # Table headers
    table_data = [['Nome', 'Perfil Dominante', 'Perfil Secundário', 'Papel de Bion']]
    
    for emp in employees_list:
        name = emp.get('name', 'Não informado')
        profile_dom = emp.get('profile_dominant', '-')
        profile_sec = emp.get('profile_secondary', '-')
        bion_role = emp.get('bion_role', '-')
        table_data.append([name, profile_dom, profile_sec, bion_role])
    
    team_table = Table(table_data, colWidths=[1.8*inch, 1.8*inch, 1.8*inch, 1.5*inch])
    team_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), navy_blue),
        ('TEXTCOLOR', (0, 0), (-1, 0), HexColor('#FFFFFF')),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), light_gray),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, navy_blue),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ]))
    elements.append(team_table)
    elements.append(Spacer(1, 20))
    
    # Bion Role Distribution
    bion_counts = {}
    for emp in employees_list:
        role = emp.get('bion_role', 'Não classificado')
        if role and role != '-':
            bion_counts[role] = bion_counts.get(role, 0) + 1
    
    if bion_counts:
        elements.append(Paragraph("Distribuição de Papéis de Bion", subtitle_style))
        dist_data = [[role, str(count)] for role, count in bion_counts.items()]
        dist_table = Table(dist_data, colWidths=[4*inch, 1*inch])
        dist_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), light_gray),
            ('TEXTCOLOR', (0, 0), (0, -1), navy_blue),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, navy_blue),
            ('ALIGN', (1, 0), (1, -1), 'CENTER'),
        ]))
        elements.append(dist_table)
    
    # Footer
    elements.append(Spacer(1, 30))
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=9,
        textColor=HexColor('#666666'),
        alignment=TA_CENTER
    )
    elements.append(Paragraph(f"Relatório gerado em {datetime.now().strftime('%d/%m/%Y %H:%M')}", footer_style))
    elements.append(Paragraph("Liderança Psicanalítica - Todos os direitos reservados", footer_style))
    
    doc.build(elements)
    buffer.seek(0)
    return buffer

def generate_csv_data(employees_list):
    """Generate CSV string from employee data."""
    import csv
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Headers
    writer.writerow(['Nome', 'Email', 'Perfil Dominante', 'Perfil Secundário', 'Papel de Bion', 'Data'])
    
    for emp in employees_list:
        writer.writerow([
            emp.get('name', ''),
            emp.get('email', ''),
            emp.get('profile_dominant', ''),
            emp.get('profile_secondary', ''),
            emp.get('bion_role', ''),
            emp.get('created_at', '')
        ])
    
    return output.getvalue()

def generate_team_pdf_report(manager_name, employees):
    """Generate team PDF report from employee tuple list."""
    # Convert tuples to dict format for the PDF generator
    employees_list = []
    for emp in employees:
        if emp[10] == 1:  # completed
            employees_list.append({
                'name': emp[4] or f'Funcionario {emp[3]}',
                'email': emp[5] or '',
                'profile_dominant': emp[6] or '',
                'profile_secondary': emp[7] or '',
                'bion_role': emp[9] or ''
            })
    
    return generate_team_pdf(employees_list, manager_name).getvalue()

def generate_individual_pdf_report(employee_tuple, manager_name=""):
    """Generate individual PDF report from employee tuple."""
    employee_data = {
        'name': employee_tuple[4] or f'Funcionario {employee_tuple[3]}',
        'email': employee_tuple[5] or '',
        'profile_dominant': employee_tuple[6] or '',
        'profile_secondary': employee_tuple[7] or '',
        'bion_role': employee_tuple[9] or '',
        'profile_details': json.loads(employee_tuple[8]) if employee_tuple[8] else {}
    }
    
    return generate_individual_pdf(employee_data, manager_name).getvalue()

# GLOBAL EMPLOYEE ACCESS GUARD - Force employees to stay on EmployeeAssessment
# This runs before every page render to prevent any navigation
if is_employee_access and page != "EmployeeAssessment":
    st.session_state.page = "EmployeeAssessment"
    page = "EmployeeAssessment"

# Pages
if page == "Home":
    # Public landing page with sections
    render_sidebar_navigation()
    render_public_header()
    
    current_section = st.session_state.section
    
    # HOME SECTION - Hero
    if current_section == "home":
        # Banner 1 - Hero Section (Azure background)
        st.markdown("""
            <div style="background-color: #18738c; padding: 4rem 2rem; border-radius: 15px; margin-bottom: 2rem; text-align: center;">
                <h1 style="color: white; font-size: 3rem; margin: 0; font-family: 'Open Sans', sans-serif; font-weight: 800;">
                    Lideranca Psicanalitica
                </h1>
                <p style="color: #d19f09; font-size: 1.5rem; margin-top: 1rem; font-family: 'Ubuntu', sans-serif;">
                    A ciencia por tras da gestao de pessoas
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        # Video Intro
        st.write("")
        vimeo_video("https://vimeo.com/1154882598")
        
        # Banner 2 - Second Hero (Yellow accent)
        st.markdown("""
            <div style="background: linear-gradient(135deg, #d19f09 0%, #e6b82e 100%); padding: 3rem 2rem; border-radius: 15px; margin: 2rem 0; text-align: center;">
                <h2 style="color: #18738c; font-size: 2.2rem; margin: 0; font-family: 'Open Sans', sans-serif; font-weight: 700;">
                    Transforme sua Lideranca
                </h2>
                <p style="color: #18738c; font-size: 1.2rem; margin-top: 1rem; font-family: 'Ubuntu', sans-serif; opacity: 0.9;">
                    Entenda as dinamicas invisiveis que travam sua equipe
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        # Features
        st.write("---")
        st.markdown("### Por Que Escolher o LPS?")
        
        feat_cols = st.columns(3)
        with feat_cols[0]:
            st.markdown("""
                <div style="text-align: center; padding: 1rem; background-color: #f8f9fa; border-radius: 10px; border: 2px solid #18738c;">
                    <div style="width: 60px; height: 60px; margin: 0 auto 1rem; background-color: #18738c; border-radius: 50%; display: flex; align-items: center; justify-content: center;">
                        <span style="color: white; font-weight: bold; font-size: 1.5rem;">N+P</span>
                    </div>
                    <h4 style="color: #18738c;">Neurociencia + Psicanalise</h4>
                    <p style="color: #666;">Metodologia unica que une ciencia do cerebro com analise profunda do comportamento.</p>
                </div>
            """, unsafe_allow_html=True)
        with feat_cols[1]:
            st.markdown("""
                <div style="text-align: center; padding: 1rem; background-color: #f8f9fa; border-radius: 10px; border: 2px solid #18738c;">
                    <div style="width: 60px; height: 60px; margin: 0 auto 1rem; background-color: #d19f09; border-radius: 50%; display: flex; align-items: center; justify-content: center;">
                        <span style="color: white; font-weight: bold; font-size: 1.2rem;">48Q</span>
                    </div>
                    <h4 style="color: #18738c;">Assessment Completo</h4>
                    <p style="color: #666;">Descubra seu perfil de lideranca e mapeie sua equipe com ferramentas exclusivas.</p>
                </div>
            """, unsafe_allow_html=True)
        with feat_cols[2]:
            st.markdown("""
                <div style="text-align: center; padding: 1rem; background-color: #f8f9fa; border-radius: 10px; border: 2px solid #18738c;">
                    <div style="width: 60px; height: 60px; margin: 0 auto 1rem; background-color: #18738c; border-radius: 50%; display: flex; align-items: center; justify-content: center;">
                        <span style="color: white; font-weight: bold; font-size: 1.2rem;">IA</span>
                    </div>
                    <h4 style="color: #18738c;">IA Consultora</h4>
                    <p style="color: #666;">Converse com a LPChat para receber insights personalizados sobre sua equipe.</p>
                </div>
            """, unsafe_allow_html=True)
        
        # CTA
        st.write("")
        cta_cols = st.columns([1, 2, 1])
        with cta_cols[1]:
            st.markdown(f"""
                <a href="{WHATSAPP_URL}" target="_blank" class="cta-button" style="display: block; text-align: center; font-size: 1.2rem;">
                    Comprar Curso / Solicitar Orcamento
                </a>
            """, unsafe_allow_html=True)
    
    # SOBRE SECTION
    elif current_section == "sobre":
        st.markdown('<div class="section-title">Sobre o Programa LPS</div>', unsafe_allow_html=True)
        
        st.markdown("""
            <div class="about-card">
                <h3 style="color: #18738c;">O que é Liderança Psicanalítica?</h3>
                <p>A Liderança Psicanalítica é uma abordagem inovadora que integra conceitos da psicanálise com práticas de gestão moderna. 
                Desenvolvida por <strong>Viviane Nishiura</strong>, esta metodologia ajuda líderes a compreenderem as dinâmicas 
                inconscientes que influenciam suas equipes e tomadas de decisão.</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
            <div class="about-card">
                <h3 style="color: #18738c;">Quem é Viviane Nishiura?</h3>
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
        st.markdown('<div class="section-title">Programa de Formacao LPS</div>', unsafe_allow_html=True)
        st.markdown('<p style="text-align: center; color: #000000; font-size: 1.1rem; margin-bottom: 2rem;">6 modulos completos para transformar sua lideranca</p>', unsafe_allow_html=True)
        
        # Premium Module Card CSS
        st.markdown("""
            <style>
            .premium-module-card {
                background-color: #18738c;
                border-radius: 12px;
                padding: 1.5rem;
                margin-bottom: 1rem;
                min-height: 280px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.15);
                transition: transform 0.2s ease, box-shadow 0.2s ease;
            }
            .premium-module-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 8px 25px rgba(0,0,0,0.25);
            }
            .premium-module-icon {
                font-size: 2.5rem;
                text-align: center;
                margin-bottom: 0.75rem;
            }
            .premium-module-title {
                color: #d19f09;
                font-size: 1.15rem;
                font-weight: bold;
                text-align: center;
                margin-bottom: 0.75rem;
            }
            .premium-module-desc {
                color: #FFFFFF;
                font-size: 0.9rem;
                line-height: 1.5;
                text-align: center;
            }
            </style>
        """, unsafe_allow_html=True)
        
        # Module Cards Grid - 2 rows of 4 for 8 modules
        row1 = st.columns(4)
        for idx, col in enumerate(row1):
            if idx < len(MODULES_DATA):
                mod = MODULES_DATA[idx]
                with col:
                    st.markdown(f"""
                        <div class="premium-module-card">
                            <div class="premium-module-icon">{mod['icon']}</div>
                            <div class="premium-module-title">{mod['title']}</div>
                            <div class="premium-module-desc">{mod['description']}</div>
                        </div>
                    """, unsafe_allow_html=True)
                    if st.button("Saiba Mais", key=f"btn_mod_{mod['id']}", use_container_width=True):
                        if not st.session_state.authenticated:
                            st.session_state.show_login_modal = True
                            st.rerun()
                        else:
                            st.session_state.selected_module = mod['id']
                            st.session_state.page = "LPS Curso"
                            st.rerun()
        
        st.write("")
        row2 = st.columns(4)
        for idx, col in enumerate(row2):
            mod_idx = idx + 4
            if mod_idx < len(MODULES_DATA):
                mod = MODULES_DATA[mod_idx]
                with col:
                    st.markdown(f"""
                        <div class="premium-module-card">
                            <div class="premium-module-icon">{mod['icon']}</div>
                            <div class="premium-module-title">{mod['title']}</div>
                            <div class="premium-module-desc">{mod['description']}</div>
                        </div>
                    """, unsafe_allow_html=True)
                    if st.button("Saiba Mais", key=f"btn_mod_{mod['id']}", use_container_width=True):
                        if not st.session_state.authenticated:
                            st.session_state.show_login_modal = True
                            st.rerun()
                        else:
                            st.session_state.selected_module = mod['id']
                            st.session_state.page = "LPS Curso"
                            st.rerun()
        
        # Paywall Modal for non-logged users
        if st.session_state.show_login_modal:
            st.write("")
            st.markdown(f"""
                <div style="background-color: #fff3cd; padding: 2rem; border-radius: 10px; border-left: 4px solid #d19f09; margin: 1rem 0;">
                    <h3 style="color: #18738c; margin-top: 0;">Conteudo Exclusivo para Alunos</h3>
                    <p style="color: #333;">O acesso ao curso completo e liberado apos a confirmacao do pagamento. Entre em contato via WhatsApp para adquirir seu acesso.</p>
                    <a href="{WHATSAPP_URL}" target="_blank" style="display: inline-block; background-color: #25D366; color: #000000; padding: 0.75rem 2rem; border-radius: 25px; text-decoration: none; font-weight: bold; margin-top: 0.5rem;">
                        Falar com Consultor
                    </a>
                </div>
            """, unsafe_allow_html=True)
            if st.button("Fechar", key="close_modal"):
                st.session_state.show_login_modal = False
                st.rerun()
        
        # CTA
        st.write("---")
        cta_cols = st.columns([1, 2, 1])
        with cta_cols[1]:
            st.markdown(f"""
                <a href="{WHATSAPP_URL}" target="_blank" class="cta-button" style="display: block; text-align: center; font-size: 1.1rem; background-color: #d19f09; color: #18738c;">
                    Comprar Curso Completo
                </a>
            """, unsafe_allow_html=True)
    
    # LPSTEST SECTION - Preview with Paywall
    elif current_section == "lpstest":
        st.markdown('<div class="section-title">LPTest - Assessment de Liderança</div>', unsafe_allow_html=True)
        
        st.markdown("""
            <div class="about-card">
                <h3 style="color: #18738c;">Descubra Seu Perfil de Liderança</h3>
                <p>O LPTest é um assessment exclusivo com <strong>48 questões</strong> desenvolvidas para mapear 
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
                <h3 style="color: #18738c;">Receba Seu Perfil Híbrido</h3>
                <p style="color: #666;">Ao completar o assessment, você recebe um relatório com seu perfil dominante, 
                perfil secundário e papel grupal segundo Bion.</p>
            </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.authenticated:
            if st.button("Fazer o LPTest Agora", use_container_width=True, type="primary"):
                st.session_state.page = "LPTest"
                st.rerun()
        else:
            render_paywall()
    
    # LPSCHAT SECTION - Preview with Paywall
    elif current_section == "lpschat":
        st.markdown('<div class="section-title">LPChat - Consultor de IA</div>', unsafe_allow_html=True)
        
        st.markdown("""
            <div class="about-card">
                <h3 style="color: #18738c;">Sua Consultora Psicanalítica 24/7</h3>
                <p>O LPChat é uma inteligência artificial treinada com os conceitos da metodologia LPS. 
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
                <p style="color: #18738c; margin-top: 1rem;"><strong>LPChat:</strong> Pelo que descreve, João pode 
                estar assumindo o papel de <em>Bode Expiatório</em> do grupo - uma dinâmica comum quando há ansiedade 
                não processada. Sugiro focar na <em>Tarefa Real</em> para resgatar a racionalidade...</p>
            </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.authenticated:
            if st.button("Acessar LPChat", use_container_width=True, type="primary"):
                st.session_state.page = "LPChat"
                st.rerun()
        else:
            render_paywall()
    
    # MENTORIA SECTION
    elif current_section == "mentoria":
        st.markdown('<div class="section-title">Mentoria Individual</div>', unsafe_allow_html=True)
        
        st.markdown("""
            <div class="about-card">
                <h3 style="color: #18738c;">Acompanhamento Personalizado</h3>
                <p>Sessões individuais com Viviane Nishiura para aprofundar seu desenvolvimento como líder psicanalítico:</p>
                <ul style="color: #666;">
                    <li>Análise do seu perfil LPTest</li>
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
    
    # INSIGHTS/BLOG SECTION (SEO)
    elif current_section == "insights":
        st.markdown('<div class="section-title">Insights de Lideranca</div>', unsafe_allow_html=True)
        st.markdown("""
            <p style="text-align: center; color: #666; margin-bottom: 2rem;">
                Artigos e conteudos semanais sobre Psicanalise, Neurociencia e Lideranca Consciente
            </p>
        """, unsafe_allow_html=True)
        
        # Featured Articles
        blog_posts = [
            {
                "title": "Os 5 Arquetipos Inconscientes que Todo Lider Possui",
                "excerpt": "Descubra como padroes ocultos influenciam suas decisoes e o comportamento da sua equipe. Aprenda a identificar seu arquetipo dominante.",
                "category": "Psicanalise",
                "date": "Janeiro 2025"
            },
            {
                "title": "Neurociencia do Estresse: Como o Cortisol Afeta sua Lideranca",
                "excerpt": "Entenda os mecanismos cerebrais por tras do estresse cronico e como gestores podem criar ambientes que promovem produtividade.",
                "category": "Neurociencia",
                "date": "Janeiro 2025"
            },
            {
                "title": "Transferencia e Contratransferencia no Ambiente Corporativo",
                "excerpt": "Por que alguns funcionarios 'ativam' reacoes intensas em voce? A resposta esta nas dinamicas inconscientes de transferencia.",
                "category": "Psicanalise",
                "date": "Dezembro 2024"
            },
            {
                "title": "Como Reduzir Turnover com Mapeamento de Perfis",
                "excerpt": "Estudo de caso: empresa reduziu rotatividade em 40% apos aplicar LPTest e realocar funcionarios por perfil.",
                "category": "Gestao",
                "date": "Dezembro 2024"
            },
            {
                "title": "Os Papeis de Bion: Entenda as Dinamicas Ocultas do Seu Time",
                "excerpt": "Porta-voz, Bode Expiatorio, Lider de Luta-Fuga... Descubra quem esta exercendo cada papel na sua equipe.",
                "category": "Dinamica Grupal",
                "date": "Novembro 2024"
            },
            {
                "title": "Neuronios-Espelho e Empatia: A Base Neurologica da Lideranca",
                "excerpt": "Como seu cerebro 'espelha' emocoes da equipe e por que isso e crucial para liderar com autenticidade.",
                "category": "Neurociencia",
                "date": "Novembro 2024"
            }
        ]
        
        cols = st.columns(2)  # Initialize columns outside loop
        for i, post in enumerate(blog_posts):
            if i % 2 == 0:
                cols = st.columns(2)
            
            with cols[i % 2]:
                category_color = {
                    "Psicanalise": "#18738c",
                    "Neurociencia": "#28a745",
                    "Gestao": "#d19f09",
                    "Dinamica Grupal": "#6c757d"
                }.get(post["category"], "#18738c")
                
                st.markdown(f"""
                    <div style="background: white; border-radius: 10px; padding: 1.5rem; margin-bottom: 1rem; box-shadow: 0 2px 8px rgba(0,0,0,0.1); border-left: 4px solid {category_color};">
                        <span style="background: {category_color}; color: white; padding: 3px 10px; border-radius: 15px; font-size: 0.75rem; margin-bottom: 0.5rem; display: inline-block;">{post['category']}</span>
                        <h3 style="color: #18738c; margin: 0.5rem 0; font-size: 1.1rem;">{post['title']}</h3>
                        <p style="color: #666; font-size: 0.9rem; margin-bottom: 0.5rem;">{post['excerpt']}</p>
                        <span style="color: #999; font-size: 0.8rem;">{post['date']}</span>
                    </div>
                """, unsafe_allow_html=True)
        
        st.markdown(f"""
            <div style="text-align: center; margin-top: 2rem; padding: 2rem; background: linear-gradient(135deg, #18738c 0%, #1a4f7a 100%); border-radius: 15px;">
                <h3 style="color: #d19f09; margin-bottom: 1rem;">Receba Conteudos Semanais</h3>
                <p style="color: white; margin-bottom: 1.5rem;">Insights exclusivos sobre lideranca psicanalitica direto no seu WhatsApp</p>
                <a href="{WHATSAPP_URL}" target="_blank" style="display: inline-block; background-color: #25D366; color: #000000; padding: 12px 30px; border-radius: 25px; text-decoration: none; font-weight: bold;">
                    Receber Insights
                </a>
            </div>
        """, unsafe_allow_html=True)
    
    # CONTATO SECTION
    elif current_section == "contato":
        st.markdown('<div class="section-title">Entre em Contato</div>', unsafe_allow_html=True)
        
        st.markdown("""
            <div style="text-align: center; padding: 2rem;">
                <div style="font-size: 4rem;">📱</div>
                <h3 style="color: #18738c;">Fale Diretamente Conosco</h3>
                <p style="color: #666; font-size: 1.1rem;">
                    Tire suas dúvidas, solicite orçamentos ou agende sua mentoria.<br>
                    Atendimento personalizado via WhatsApp.
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
            <div style="text-align: center;">
                <a href="{WHATSAPP_URL}" target="_blank" style="display: inline-block; background-color: #25D366; color: #000000; padding: 20px 50px; border-radius: 50px; font-weight: bold; font-size: 1.3rem; text-decoration: none;">
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
    
    render_sidebar_navigation()
    render_public_header()
    
    # Get manager data
    manager_data = get_manager_by_user(st.session_state.user['id'])
    user_id = st.session_state.user['id']
    manager_id = manager_data['id'] if manager_data else None
    
    st.markdown(f"<h2 style='color: #18738c;'>Bem-vindo(a), {st.session_state.user['name']}!</h2>", unsafe_allow_html=True)
    
    # Dashboard CSS
    st.markdown("""
        <style>
        .dashboard-card {
            background: white;
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            border-left: 4px solid #d19f09;
            margin-bottom: 1rem;
        }
        .dashboard-card h3 {
            color: #18738c;
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
            background: linear-gradient(90deg, #18738c, #d19f09);
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
            color: #18738c;
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
            background: linear-gradient(135deg, #18738c, #1a5490);
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
        st.markdown(f"<p style='text-align: center; margin-top: 1rem; color: #18738c; font-weight: bold;'>Progresso Total: {overall_progress:.0f}%</p></div>", unsafe_allow_html=True)
        
        # Radar Chart Card - Manager Profile
        manager_profile = get_manager_profile_by_user(user_id)
        if manager_profile:
            st.markdown("<div class='dashboard-card'><h3>Seu Perfil de Lideranca</h3>", unsafe_allow_html=True)
            
            # Try to get block sums from assessment responses
            block_sums = get_assessment_block_sums(user_id, "manager")
            if block_sums:
                profile_name = f"{manager_profile['dominant']} + {manager_profile['secondary']}"
                radar_chart = generate_radar_chart(block_sums, profile_name)
                if radar_chart:
                    st.image(radar_chart, use_container_width=True)
                    st.markdown(f"""
                        <div style='text-align: center; padding: 1rem; background: #f8f9fa; border-radius: 8px; margin-top: 1rem;'>
                            <strong style='color: #18738c;'>Perfil Dominante:</strong> {manager_profile['dominant']}<br>
                            <strong style='color: #18738c;'>Perfil Secundario:</strong> {manager_profile['secondary']}
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                    <div style='text-align: center; padding: 1rem;'>
                        <strong style='color: #18738c;'>{manager_profile['dominant']} + {manager_profile['secondary']}</strong>
                        <p style='color: #666; font-size: 0.9rem; margin-top: 0.5rem;'>Refaca o LPTest para visualizar seu grafico radar</p>
                    </div>
                """, unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
        
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
                st.markdown("<p style='color: #666;'>Nenhum insight disponível ainda. Complete o LPTest e mapeie sua equipe.</p>", unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        # Assessment Stats Card
        if manager_id:
            st.markdown("<div class='dashboard-card'><h3>Gestão de LPTest</h3>", unsafe_allow_html=True)
            
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
    
    # Team Chart Preview (if team is mapped)
    if manager_id:
        employees = get_secure_manager_employees(user_id, manager_id)
        completed_employees = [e for e in employees if e[10] == 1]
        if len(completed_employees) >= 2:
            st.markdown("<div class='dashboard-card'><h3>Mapeamento da Equipe</h3>", unsafe_allow_html=True)
            manager_name = st.session_state.user['name'] if st.session_state.user else "Gestor"
            chart_data = generate_team_chart(employees, manager_name)
            if chart_data:
                st.image(chart_data, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
    
    st.write("---")
    
    # Quick Access Buttons
    st.markdown("<h4 style='color: #18738c;'>Acesso Rápido</h4>", unsafe_allow_html=True)
    dash_cols = st.columns(4)
    with dash_cols[0]:
        if st.button("Curso", key="btn-dash-curso", use_container_width=True):
            st.session_state.page = "LPS Curso"
            st.rerun()
    with dash_cols[1]:
        if st.button("LPTest", key="btn-dash-test", use_container_width=True):
            st.session_state.page = "LPTest"
            st.rerun()
    with dash_cols[2]:
        if st.button("Equipe", key="btn-dash-equipe", use_container_width=True):
            st.session_state.page = "TeamManagement"
            st.rerun()
    with dash_cols[3]:
        # LPChat with access control
        course_completed = is_course_completed(user_id)
        if course_completed:
            if st.button("LPChat", key="btn-dash-chat", use_container_width=True):
                st.session_state.page = "LPChat"
                st.rerun()
        else:
            if st.button("LPChat (Bloqueado)", key="btn-dash-chat-locked", use_container_width=True, disabled=True):
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
    st.markdown(f"<p style='color: #18738c; font-weight: bold;'>Progresso Geral: {completed_lessons}/{total_lessons} aulas concluídas</p>", unsafe_allow_html=True)
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

elif page == "LPTest":
    if not st.session_state.authenticated:
        st.session_state.page = "Login"
        st.rerun()
    st.title("📝 LPTest Assessment - Seu Perfil")
    
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
        if st.button("🔄 Refazer LPTest"):
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
                
                # Save individual responses for future AI analysis
                save_assessment_responses(user_id, "manager", responses)
                
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
        user_id = st.session_state.user['id']
        manager_profile = manager_data if manager_data.get('dominant') else None
        
        # Get employees data first with multitenancy validation
        employees = get_secure_manager_employees(user_id, manager_id)
        
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
                st.warning("Complete seu LPTest primeiro para ver a comparacao com sua equipe.")
            
            st.write("---")
            st.subheader("Gerar Link de Convite para Equipe")
            
            if not st.session_state.show_employee_links and not has_existing_links:
                st.markdown("""
                    <div style='background-color: #e8f4f8; padding: 1.5rem; border-radius: 8px; margin-bottom: 1rem;'>
                        <p style='margin: 0; color: #18738c;'>
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
                        <div style="background-color: #18738c; color: white; padding: 10px; border-radius: 8px; margin: 20px 0 10px 0;">
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
                                        <h4 style="color: #18738c; margin:0;">{emp_name}</h4>
                                        <p><strong>Perfil:</strong> {emp[6]} + {emp[7]}</p>
                                        <span class="bion-badge">{emp[9]}</span>
                                        <p style="font-size: 0.9rem; color: #666; margin-top:10px;">
                                            {BION_DESCRIPTIONS.get(emp[9], '')}
                                        </p>
                                        <p style="font-size: 0.85rem; color: #18738c; margin-top: 8px;">
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
                <h1 style='color: #18738c;'>Obrigado pela participacao!</h1>
            </div>
        """, unsafe_allow_html=True)
        st.markdown(f"""
            <div class="result-card" style="max-width: 600px; margin: 0 auto;">
                <div class="profile-title">Seu Perfil foi Registrado</div>
                <p style="text-align: center; font-size: 1.4rem;"><strong>{employee[6]} + {employee[7]}</strong></p>
                <div style="background-color: #d19f09; padding: 10px; border-radius: 20px; text-align: center; margin: 15px auto; max-width: 200px;">
                    <strong style="color: #18738c;">{employee[9]}</strong>
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
                <h1 style='color: #18738c;'>LPTest - Assessment de Equipe</h1>
                <p style='color: #666;'>Responda as afirmacoes abaixo de forma honesta. Seus resultados individuais sao confidenciais.</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Check consent from database (persistent storage)
        consent_given = get_employee_consent(token)
        
        # Single unified form with consent + assessment
        # Consent is validated and saved atomically with assessment results
        with st.form("employee_assessment"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Seu Nome Completo", placeholder="Maria Silva")
            with col2:
                email = st.text_input("Seu E-mail (recebera seu resultado)", placeholder="maria@email.com")
            
            st.write("---")
            
            # Show consent terms if not yet consented
            if not consent_given:
                st.markdown("""
                    <div style="background-color: #f8f9fa; padding: 1.5rem; border-radius: 10px; border-left: 4px solid #18738c; margin-bottom: 1.5rem;">
                        <h4 style="color: #18738c; margin-top: 0;">Termo de Consentimento - LGPD</h4>
                        <p style="color: #333; font-size: 0.9rem;">Ao concluir esta avaliacao, voce aceita que:</p>
                        <ul style="color: #333; font-size: 0.85rem;">
                            <li>Seus dados serao utilizados exclusivamente para fins de desenvolvimento profissional</li>
                            <li>Os resultados serao compartilhados com seu gestor para analise de perfil de equipe</li>
                            <li>Seus dados sao protegidos por sigilo e nao serao compartilhados com terceiros</li>
                            <li>Voce pode solicitar a exclusao dos seus dados a qualquer momento</li>
                        </ul>
                    </div>
                """, unsafe_allow_html=True)
                consent = st.checkbox("Aceito que meus dados sejam processados para este mapeamento de perfil profissional", key="consent_checkbox")
            else:
                consent = True  # Already consented
            
            st.write("---")
            responses = render_assessment_form("employee")
            submit = st.form_submit_button("Concluir Avaliacao", use_container_width=True)
            
            if submit:
                # Validation
                if not name or not email:
                    st.error("Preencha seu nome e e-mail.")
                elif not consent:
                    st.error("Voce precisa aceitar os termos de consentimento para continuar.")
                else:
                    # Atomic operation: save consent (if new) + save results
                    if not consent_given:
                        save_employee_consent(token)
                    
                    # Calculate and save results
                    dominant, secondary, details, bion_role, block_sums = calculate_profile(responses)
                    save_employee_result(token, name, email, dominant, secondary, details, bion_role)
                    
                    # Save individual responses for future AI analysis
                    employee_id = employee[0]  # Get employee ID
                    save_assessment_responses(employee_id, "employee", responses)
                    
                    # Send email notifications (if SMTP configured)
                    # Get manager info for notification
                    manager_id = employee[1]
                    manager_info = get_manager_by_id(manager_id)
                    if manager_info:
                        manager_name = manager_info.get('name', 'Gestor')
                        manager_email = manager_info.get('email', '')
                        
                        # Send result to employee
                        send_employee_result_email(name, email, dominant, secondary, bion_role, manager_name)
                        
                        # Notify manager
                        if manager_email:
                            send_manager_notification_email(manager_email, manager_name, name, f"{dominant} + {secondary}", bion_role)
                    
                    st.balloons()
                    st.rerun()

elif page == "LPChat":
    if not st.session_state.authenticated:
        st.session_state.page = "Login"
        st.rerun()
    
    # PRIVACY: Only managers can access - employees are blocked globally
    # Access control: check payment status AND course completion
    user_id = st.session_state.user['id']
    access_status = can_access_premium_features(user_id)
    course_completed = access_status['course_completed']
    
    # Custom chat styling with brand colors
    st.markdown("""
        <style>
        .chat-header {
            background: linear-gradient(135deg, #18738c 0%, #1a4f7a 100%);
            color: white;
            padding: 2rem;
            border-radius: 15px;
            margin-bottom: 1.5rem;
            text-align: center;
            box-shadow: 0 4px 15px rgba(13, 59, 102, 0.3);
        }
        .chat-header h1 {
            color: #d19f09;
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
            background: linear-gradient(135deg, rgba(209, 159, 9, 0.15) 0%, rgba(209, 159, 9, 0.05) 100%);
            border: 1px solid #d19f09;
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
        }
        .example-questions h4 {
            color: #18738c;
            margin: 0 0 1rem 0;
        }
        .example-q {
            background: white;
            padding: 0.75rem 1rem;
            border-radius: 8px;
            margin: 0.5rem 0;
            border-left: 3px solid #d19f09;
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
            color: #18738c;
            margin: 0 0 1rem 0;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid #d19f09;
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
            background: #18738c;
            color: #d19f09;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-right: 1rem;
            font-weight: bold;
        }
        .bion-badge {
            background: #d19f09;
            color: #18738c;
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
            <h1>LPChat</h1>
            <p>Consultora de IA em Psicanalise e Neurociencia aplicada a Lideranca</p>
        </div>
    """, unsafe_allow_html=True)
    
    if not access_status['can_access']:
        st.warning("Acesso Bloqueado")
        
        # Show different message based on what's missing
        if not access_status['payment_active']:
            st.markdown(f"""
                <div style='background-color: #f8d7da; padding: 2rem; border-radius: 10px; border-left: 4px solid #dc3545;'>
                    <h3 style='color: #721c24; margin-top: 0;'>Conteudo Exclusivo para Alunos</h3>
                    <p style='color: #721c24;'>
                        O acesso ao LPChat e liberado apos a confirmacao do pagamento.
                        Entre em contato via WhatsApp para adquirir seu acesso.
                    </p>
                    <a href="{WHATSAPP_URL}" target="_blank" style="display: inline-block; background-color: #25D366; color: #000000; padding: 0.75rem 2rem; border-radius: 25px; text-decoration: none; font-weight: bold; margin-top: 1rem;">
                        Falar com Suporte
                    </a>
                </div>
            """, unsafe_allow_html=True)
        elif not access_status['course_completed']:
            st.markdown("""
                <div style='background-color: #fff3cd; padding: 2rem; border-radius: 10px; border-left: 4px solid #ffc107;'>
                    <h3 style='color: #856404; margin-top: 0;'>Complete os modulos teoricos para liberar o LPChat</h3>
                    <p style='color: #856404;'>
                        O acesso ao consultor de IA e liberado apos a conclusao dos 5 primeiros modulos do curso.
                        Isso garante que voce tenha a base teorica necessaria para aproveitar ao maximo as analises da IA.
                    </p>
                </div>
            """, unsafe_allow_html=True)
            
            # Show progress
            module_status = get_module_completion_status(user_id)
            st.markdown("<h4 style='color: #18738c; margin-top: 2rem;'>Seu progresso nos modulos teoricos:</h4>", unsafe_allow_html=True)
            
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
            user_id = st.session_state.user['id']
            employees = get_secure_manager_employees(user_id, manager_data['id'])
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
- Voce e uma consultora senior com profundo conhecimento em psicanalise de grupos (Bion, Kernberg, Pichon-Riviere) e neurociencia organizacional
- Sua funcao e ajudar gestores a compreender as dinamicas inconscientes de suas equipes
- Voce analisa padroes de comportamento, identificando papeis inconscientes e arquetipos
- Voce aplica o conceito de Circulo de Seguranca (Sinek) para avaliar o ambiente emocional
- PRIVACIDADE: Seus insights sao EXCLUSIVOS para o gestor - nunca compartilhados com funcionarios

============ DADOS DA EQUIPE (CONFIDENCIAL) ============

GESTOR:
Nome: {user_name}
{manager_profile if manager_profile else "O gestor ainda nao completou o LPTest."}

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

4.1 PRESSUPOSTOS BASICOS DE BION:
- Grupo de Trabalho: envolvido com a tarefa real, focado na realizacao
- Grupo de Suposicao Basica: fantasias inconscientes que atrapalham a tarefa
  * Dependencia: grupo espera que o lider seja onipotente e tenha todas as respostas (mae idealizada)
  * Luta e Fuga: grupo projeta o mal para fora, prepara-se para lutar ou fugir (irreflexivo, so acao)
  * Acasalamento: crenca de que um messias salvador surgira (defesa contra odio e destrutividade)

4.2 CIRCULO DE SEGURANCA (SINEK):
- EDSO: Endorfina, Dopamina (individuais) + Serotonina, Oxitocina (coletivos)
- Ambiente seguro: baixo Cortisol, alta Oxitocina = cooperacao e confianca
- Ambiente toxico: alto Cortisol = modo de sobrevivencia, paralisia, conflitos
- O lider CRIA o circulo de seguranca, protegendo a equipe de ameacas externas
- Quando o circulo esta forte: funcionarios tomam riscos, inovam, colaboram
- Quando o circulo esta fraco: funcionarios se protegem, competem, escondem erros

4.3 KERNBERG - CARACTERISTICAS DO LIDER RACIONAL:
- Inteligencia
- Honestidade e incorruptibilidade
- Capacidade de estabelecer relacoes objetais profundas
- Narcisismo sadio (para nao depender excessivamente da aprovacao)
- Atitude paranoide sadia (alerta aos perigos da corrupcao e regressao)

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
    
    render_sidebar_navigation()
    render_public_header()
    
    # Access control for Mentoria
    user_id = st.session_state.user['id']
    access_status = can_access_premium_features(user_id)
    
    st.markdown("""
        <div style="text-align: center; margin-bottom: 2rem;">
            <h1 style="color: #18738c;">Mentoria com Viviane Nishiura</h1>
            <p style="color: #666;">Sessoes individuais para aprofundar sua jornada de lideranca consciente</p>
        </div>
    """, unsafe_allow_html=True)
    
    if not access_status['can_access']:
        # Show paywall
        if not access_status['payment_active']:
            st.markdown(f"""
                <div style='background-color: #f8d7da; padding: 2rem; border-radius: 10px; border-left: 4px solid #dc3545; margin-bottom: 2rem;'>
                    <h3 style='color: #721c24; margin-top: 0;'>Conteudo Exclusivo para Alunos</h3>
                    <p style='color: #721c24;'>
                        O agendamento de mentoria e liberado apos a confirmacao do pagamento.
                        Entre em contato via WhatsApp para adquirir seu acesso.
                    </p>
                    <a href="{WHATSAPP_URL}" target="_blank" style="display: inline-block; background-color: #25D366; color: #000000; padding: 0.75rem 2rem; border-radius: 25px; text-decoration: none; font-weight: bold; margin-top: 1rem;">
                        Falar com Suporte
                    </a>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
                <div style='background-color: #fff3cd; padding: 2rem; border-radius: 10px; border-left: 4px solid #ffc107; margin-bottom: 2rem;'>
                    <h3 style='color: #856404; margin-top: 0;'>Complete o curso para liberar a Mentoria</h3>
                    <p style='color: #856404;'>
                        O acesso a mentoria e liberado apos a conclusao dos modulos teoricos do curso.
                        Isso garante uma base solida para aproveitar ao maximo sua sessao.
                    </p>
                </div>
            """, unsafe_allow_html=True)
            if st.button("Ir para o Curso", key="mentoria-goto-curso"):
                st.session_state.page = "LPS Curso"
                st.rerun()
    else:
        # Full mentoria content for paying users
        st.markdown("""
            <div class="about-card">
                <h3 style="color: #18738c;">O que esperar da Mentoria</h3>
                <ul>
                    <li><strong>Sessao individual de 1 hora</strong> com Viviane Nishiura</li>
                    <li>Analise aprofundada do seu perfil de lideranca</li>
                    <li>Discussao sobre dinamicas de equipe e conflitos inconscientes</li>
                    <li>Estrategias praticas baseadas em psicanalise e neurociencia</li>
                    <li>Acompanhamento personalizado para seu desenvolvimento</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
            <div class="about-card">
                <h3 style="color: #18738c;">Como se preparar</h3>
                <ol>
                    <li>Revise seu perfil de lideranca no Dashboard</li>
                    <li>Analise os resultados do mapeamento de equipe</li>
                    <li>Identifique 2-3 desafios especificos que deseja abordar</li>
                    <li>Anote situacoes concretas para discutir</li>
                </ol>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
            <div style="background: linear-gradient(135deg, #18738c 0%, #1a4f7a 100%); padding: 2rem; border-radius: 15px; text-align: center; margin-top: 2rem;">
                <h2 style="color: #d19f09; margin-bottom: 1rem;">Agende sua Sessao</h2>
                <p style="color: white; margin-bottom: 1.5rem;">Entre em contato via WhatsApp para agendar sua mentoria individual.</p>
                <a href="{WHATSAPP_URL}" target="_blank" style="display: inline-block; background-color: #25D366; color: #000000; padding: 1rem 3rem; border-radius: 25px; text-decoration: none; font-weight: bold; font-size: 1.1rem;">
                    Agendar Mentoria
                </a>
            </div>
        """, unsafe_allow_html=True)

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

elif page == "GuiaSuporte":
    # Guide and Support page for managers - Authentication required
    if not st.session_state.authenticated:
        st.session_state.page = "Login"
        st.rerun()
    
    render_sidebar_navigation()
    render_public_header()
    
    st.markdown("""
        <div style="text-align: center; margin-bottom: 2rem;">
            <h1 style="color: #18738c;">Guia e Suporte</h1>
            <p style="color: #666;">Materiais de apoio para maximizar sua experiencia com a plataforma LPS</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Download Manual Button
    st.markdown("""
        <div style="background: linear-gradient(135deg, #18738c 0%, #1a4f7a 100%); padding: 2rem; border-radius: 15px; margin-bottom: 2rem; text-align: center;">
            <h2 style="color: #d19f09; margin-bottom: 1rem;">Manual do Gestor LPS</h2>
            <p style="color: white; margin-bottom: 1.5rem;">Guia completo com tudo que voce precisa saber para aplicar a Lideranca Psicanalitica na sua equipe.</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Generate and offer PDF download
    pdf_data = generate_manager_guide_pdf()
    st.download_button(
        label="📥 Baixar Manual do Gestor (PDF)",
        data=pdf_data,
        file_name="Manual_do_Gestor_LPS.pdf",
        mime="application/pdf",
        use_container_width=True,
        type="primary"
    )
    
    st.write("---")
    
    # Section 1: Como interpretar seu Perfil
    st.markdown("""
        <div class="about-card">
            <h3 style="color: #18738c;">1. Como Interpretar seu Perfil</h3>
            <p>Seu perfil de lideranca revela seus <strong>arquetipos inconscientes dominantes</strong> - padroes de comportamento 
            que operam abaixo da consciencia e influenciam como voce lidera sua equipe.</p>
            <p>Os 6 perfis de lideranca do LPS sao:</p>
            <ul>
                <li><strong>Protetor:</strong> Acolhimento e cuidado da equipe</li>
                <li><strong>Contenedor:</strong> Estabilidade emocional e gestao de crises</li>
                <li><strong>Narciso Estrategico:</strong> Inspiracao e motivacao atraves de visao</li>
                <li><strong>Estruturador:</strong> Organizacao e controle de processos</li>
                <li><strong>Espelho Emocional:</strong> Empatia e validacao emocional</li>
                <li><strong>Observador Reflexivo:</strong> Analise profunda e decisoes ponderadas</li>
            </ul>
            <p><em>Cada perfil tem seus pontos fortes e areas de atencao. O LPTest mostra seu perfil dominante e secundario.</em></p>
        </div>
    """, unsafe_allow_html=True)
    
    # Section 2: Mapeamento de Equipe
    st.markdown("""
        <div class="about-card">
            <h3 style="color: #18738c;">2. Mapeamento de Equipe</h3>
            <p>O LPTest mapeia os perfis inconscientes de sua equipe, permitindo entender dinamicas grupais 
            que impactam produtividade, conflitos e turnover.</p>
            <h4 style="color: #18738c;">Como usar para reduzir turnover:</h4>
            <ul>
                <li>Identifique funcionarios cujo perfil nao se adequa ao cargo atual</li>
                <li>Realoque pessoas com base em suas tendencias naturais</li>
                <li>Crie pares complementares (ex: Estruturador + Criativo)</li>
            </ul>
            <h4 style="color: #18738c;">Como usar para reduzir conflitos:</h4>
            <ul>
                <li>Identifique <strong>Bodes Expiatorios</strong> e proteja-os de projecoes negativas</li>
                <li>Reconheca <strong>Porta-Vozes</strong> como sensores do clima organizacional</li>
                <li>Transforme <strong>Lideres de Luta-Fuga</strong> em agentes de mudanca construtiva</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)
    
    # Section 3: Uso Estratégico do LPChat
    st.markdown("""
        <div class="about-card">
            <h3 style="color: #18738c;">3. Uso Estrategico do LPChat</h3>
            <p>O LPChat e sua <strong>consultora de IA especializada</strong> em psicanalise e neurociencia aplicada a lideranca. 
            Para obter os melhores insights, faca perguntas especificas sobre sua equipe.</p>
            <h4 style="color: #18738c;">Perguntas recomendadas:</h4>
            <ul>
                <li>"Quais conflitos inconscientes podem surgir entre [Funcionario A] e [Funcionario B]?"</li>
                <li>"Qual funcionario seria ideal para liderar o projeto X, considerando os perfis mapeados?"</li>
                <li>"Como posso dar feedback construtivo para um Dependente sem gerar mais dependencia?"</li>
                <li>"Quais dinamicas de transferencia podem estar afetando minha relacao com a equipe?"</li>
                <li>"Como aplicar conceitos de neurociencia para reduzir o estresse no time?"</li>
            </ul>
            <p><em>Dica: Quanto mais especifica a pergunta, melhor sera a resposta da IA.</em></p>
        </div>
    """, unsafe_allow_html=True)
    
    # Section 4: Passo a Passo da Mentoria
    st.markdown(f"""
        <div class="about-card">
            <h3 style="color: #18738c;">4. Passo a Passo da Mentoria</h3>
            <p>A mentoria com <strong>Viviane Nishiura</strong> e o momento de aprofundar sua jornada de lideranca consciente. 
            Prepare-se adequadamente para maximizar os resultados.</p>
            <h4 style="color: #18738c;">Antes da sessao:</h4>
            <ol>
                <li>Revise seu perfil de lideranca no Dashboard</li>
                <li>Analise os resultados do mapeamento de equipe</li>
                <li>Identifique 2-3 desafios especificos que deseja abordar</li>
                <li>Anote situacoes concretas para discutir</li>
            </ol>
            <h4 style="color: #18738c;">Durante a sessao:</h4>
            <ul>
                <li>Compartilhe abertamente seus desafios</li>
                <li>Pergunte sobre padroes inconscientes que nao consegue ver</li>
                <li>Solicite exercicios praticos para aplicar no dia-a-dia</li>
            </ul>
            <h4 style="color: #18738c;">Como agendar:</h4>
            <p>Acesse o menu <strong>Mentoria</strong> no Dashboard ou envie mensagem via 
            <a href="{WHATSAPP_URL}" target="_blank" style="color: #18738c;">WhatsApp</a> para agendar sua sessao.</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Contact Support
    st.markdown(f"""
        <div style="background-color: #f5f5f5; padding: 1.5rem; border-radius: 10px; text-align: center; margin-top: 2rem;">
            <h3 style="color: #18738c;">Precisa de Ajuda?</h3>
            <p>Entre em contato com nossa equipe via WhatsApp para suporte personalizado.</p>
            <a href="{WHATSAPP_URL}" target="_blank" style="display: inline-block; background-color: #25D366; color: #000000; padding: 0.75rem 2rem; border-radius: 25px; text-decoration: none; font-weight: bold;">
                Falar com Suporte
            </a>
        </div>
    """, unsafe_allow_html=True)

elif page == "Privacy":
    # Privacy and Terms page
    st.markdown('<div class="section-title">Privacidade e Termos de Uso</div>', unsafe_allow_html=True)
    
    st.markdown("""
        <div class="about-card">
            <h3 style="color: #18738c;">Politica de Privacidade - LGPD</h3>
            <p>A Plataforma LPS (Lideranca Psicanalitica) esta comprometida com a protecao dos dados pessoais de todos os usuarios, 
            em conformidade com a Lei Geral de Protecao de Dados (LGPD - Lei 13.709/2018).</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
        <div class="about-card">
            <h3 style="color: #18738c;">Dados Coletados</h3>
            <p><strong>Para Gestores:</strong></p>
            <ul style="color: #333;">
                <li>Nome completo e e-mail para autenticacao</li>
                <li>Resultados do assessment de perfil de lideranca</li>
                <li>Progresso no curso e modulos acessados</li>
            </ul>
            <p><strong>Para Funcionarios:</strong></p>
            <ul style="color: #333;">
                <li>Nome e e-mail (opcional)</li>
                <li>Respostas do assessment de perfil</li>
                <li>Resultado do mapeamento de perfil e papel de Bion</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
        <div class="about-card">
            <h3 style="color: #18738c;">Finalidade do Tratamento</h3>
            <p>Os dados coletados sao utilizados <strong>exclusivamente</strong> para:</p>
            <ul style="color: #333;">
                <li>Desenvolvimento profissional e autoconhecimento dos participantes</li>
                <li>Geracao de insights sobre dinamicas de equipe para gestores</li>
                <li>Personalizacao da experiencia de aprendizagem</li>
                <li>Comunicacoes relacionadas ao programa LPS</li>
            </ul>
            <p style="color: #18738c;"><strong>Os dados NUNCA serao vendidos, compartilhados com terceiros ou utilizados para fins comerciais alem do programa.</strong></p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
        <div class="about-card">
            <h3 style="color: #18738c;">Sigilo e Confidencialidade</h3>
            <p>Todos os resultados de assessment sao tratados com <strong>sigilo absoluto</strong>:</p>
            <ul style="color: #333;">
                <li>Funcionarios: Seus resultados sao visiveis apenas para o gestor que enviou o convite</li>
                <li>Gestores: Tem acesso somente aos dados de seus proprios funcionarios</li>
                <li>Isolamento de dados: Cada gestor tem seu ambiente isolado, sem acesso a dados de outros gestores</li>
                <li>Criptografia: Senhas sao armazenadas com criptografia bcrypt de alta seguranca</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
        <div class="about-card">
            <h3 style="color: #18738c;">Direitos do Usuario (LGPD)</h3>
            <p>Voce tem direito a:</p>
            <ul style="color: #333;">
                <li><strong>Acesso:</strong> Solicitar copia de todos os seus dados</li>
                <li><strong>Correcao:</strong> Retificar dados incorretos ou desatualizados</li>
                <li><strong>Exclusao:</strong> Solicitar a remocao de seus dados do sistema</li>
                <li><strong>Portabilidade:</strong> Receber seus dados em formato estruturado</li>
                <li><strong>Revogacao:</strong> Retirar seu consentimento a qualquer momento</li>
            </ul>
            <p>Para exercer esses direitos, entre em contato via WhatsApp.</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
        <div class="about-card">
            <h3 style="color: #18738c;">Termos de Uso</h3>
            <p>Ao utilizar a Plataforma LPS, voce concorda que:</p>
            <ul style="color: #333;">
                <li>Os conteudos do curso sao protegidos por direitos autorais</li>
                <li>O acesso e pessoal e intransferivel</li>
                <li>Nao e permitido compartilhar materiais ou credenciais de acesso</li>
                <li>Os resultados de assessment sao para uso interno de desenvolvimento profissional</li>
                <li>A plataforma reserva-se o direito de suspender acessos em caso de violacao</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
        <div class="about-card">
            <h3 style="color: #18738c;">Contato</h3>
            <p>Para duvidas sobre privacidade e protecao de dados:</p>
            <p><strong>Responsavel:</strong> Viviane Nishiura</p>
            <p><strong>E-mail:</strong> contato@liderancapsicanalitica.com.br</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
        <div style="text-align: center; margin-top: 2rem;">
            <p style="color: #666; font-size: 0.9rem;">Ultima atualizacao: Janeiro/2026</p>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("Voltar para Home", key="btn-privacy-home", use_container_width=True):
        st.session_state.page = "Home"
        st.rerun()

# Footer for all pages (except employee assessment)
if not is_employee_access:
    st.markdown(f"""
        <div style="margin-top: 3rem; padding: 1.5rem; background-color: #f5f5f5; border-radius: 8px; text-align: center;">
            <p style="margin: 0 0 10px 0; color: #666; font-size: 0.9rem;">
                Lideranca Psicanalitica - Viviane Nishiura & Equipe
            </p>
            <a href="{WHATSAPP_URL}" target="_blank" style="display: inline-flex; align-items: center; gap: 8px; padding: 10px 25px; background-color: #25D366; color: white; border-radius: 25px; text-decoration: none; font-weight: bold; font-size: 0.95rem;">
                Fale Conosco no WhatsApp
            </a>
        </div>
    """, unsafe_allow_html=True)
    
    # Privacy link button
    col_footer = st.columns([3, 1, 3])
    with col_footer[1]:
        if st.button("Privacidade e Termos", key="footer-privacy-link", use_container_width=True):
            st.session_state.page = "Privacy"
            st.rerun()
