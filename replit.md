# Liderança Psicanalítica (LPS)

## Overview

This is a Streamlit-based Python application for "Liderança Psicanalítica" (Psychoanalytic Leadership). The application features a custom-styled interface using the LPS brand colors (Navy Blue #0D3B66 and Gold #F4D35E).

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Current Application (Python/Streamlit)
- **Framework**: Streamlit for rapid Python web application development
- **Entry Point**: `main.py` serves as the application entry
- **Styling**: Custom CSS embedded in Streamlit for brand theming
- **Server**: Runs on port 5000 with Streamlit's built-in server
- **Database**: SQLite (lps_data.db) with users, managers, employees, course_progress tables

### Authentication System
- **Password Hashing**: bcrypt with 12 rounds for secure credential storage
- **Legacy Support**: verify_password() handles both bcrypt and legacy SHA-256 hashes
- **Auto-Upgrade**: upgrade_password_hash() migrates SHA-256 to bcrypt on login
- **Session Management**: Streamlit session_state for authenticated sessions
- **User Types**: Managers (full access via login) and Employees (token-based access)
- **Session Variables**: authenticated, user (id/name/email), manager_data, login_mode

### Data Isolation (Multitenancy)
- **Ownership Validation**: validate_manager_ownership(user_id, manager_id) checks manager belongs to user
- **Secure Access**: get_secure_manager_employees(user_id, manager_id) wraps all data access
- **Protected Functions**: TeamManagement, LPSChat, and AI insights use secure functions
- **Isolation Guarantee**: Managers can only see their own team data

### Access Control
- **Public Visitors**: Can view the Home page with sections (Sobre, Curso, LPSTest, LPSChat, Mentoria, Soluções, Contato)
- **Managers**: Register/login via "Entrar" button, access Dashboard with course progress and team management
- **Employees**: Access via unique token URL (?token=xxx), see only Assessment page
- **Content Gating**: Protected content shows paywall message "Conteúdo exclusivo para alunos. Liberação apenas após confirmação de pagamento"
- **LPSChat Access**: Only available after completing all course modules and having active payment

### Page Structure
- **Home**: Public landing page with hero section and navigation menu (8 sections)
- **Login**: Authentication page accessible via "Entrar" button
- **Dashboard**: Manager area with course progress bar, assessment stats, AI insights, mentoring CTA
- **LPS Curso**: Full course content with 8 modules (Introduction + 7 Modules), progress saved to database
- **LPSTest**: Leadership assessment (70 questions in 7 blocks, 7-axis radar chart, Bion role mapping)
- **TeamManagement**: Tabbed interface with "Gerar Convites" (link generation) and "Resultados da Equipe" (completed results + CSV exports)
- **LPSChat**: AI consultant (gated behind theoretical module completion)
- **EmployeeAssessment**: Token-based employee assessment page with Thank You page after completion

### Employee Access Guard
- **Global Protection**: Runs before every page render to force employees to stay on EmployeeAssessment
- **Token Persistence**: Employee token stored in session_state prevents navigation to other pages
- **Sidebar Hidden**: Employees see a clean page with no sidebar/navigation
- **Thank You Page**: Displays after assessment completion with profile summary

### Dashboard Features (Manager Area)
- **Course Progress**: Visual progress bars for each of 8 modules with overall percentage
- **Assessment Stats**: Counter showing "Aplicados" vs "Restantes" (4-employee package limit)
- **AI Insights**: Automated alerts about team (Bion role distribution, manager profile status)
- **Mentoring CTA**: Button to schedule with Viviane Nishiura via WhatsApp
- **Quick Access**: Buttons to Curso, LPSTest, Equipe, LPSChat (locked until course complete)

### Guia e Suporte (Support Materials)
- **Manager's Guide PDF**: Downloadable PDF with complete LPS methodology
- **Guide Contents**:
  - Como interpretar seu Perfil: Explanation of unconscious archetypes
  - Mapeamento de Equipe: How to use LPSTest to reduce turnover and conflicts
  - Uso Estratégico do LPSChat: How to ask the right questions to get insights about group roles
  - Passo a Passo da Mentoria: How to schedule and what to prepare for sessions with Viviane
- **WhatsApp Support**: Direct link to contact support team

### Profile System (PROFILES_DB)
- **42 Profile Combinations**: 7 archetypes × 6 secondary profiles each
- **Archetypes**: 🛡 Protetor, 🧱 Contenedor, 🔥 Narciso Estratégico, 🏗 Estruturador, 🪞 Espelho Emocional, 🧠 Observador Reflexivo, 🎭 Relacional Reativo
- **Each Combination Contains**: Forças (strengths), Riscos (risks), Recomendações (recommendations)

### Radar Chart Visualization
- **7 Axes**: Autoridade Interna, Contenção Emocional, Narcisismo/Reconhecimento, Estrutura/Ordem, Relação/Empatia, Reflexão/Observação, Relacional Reativo
- **Data Source**: Assessment responses aggregated by block (max 50 points per block, 10 questions × 5 points)
- **Normalization**: Percentages 0-100% for visual display
- **Colors**: Navy Blue (#0D3B66) fill, Gold (#F4D35E) markers

### Assessment Response Storage
- **Table**: assessment_responses
- **Storage**: Each individual response (1-5) saved for future AI analysis
- **Functions**: save_assessment_responses() for storage, get_assessment_block_sums() for retrieval
- **Types**: Both managers and employees store responses

### Database Tables
- **users**: id, email, password_hash, name, user_type, created_at
- **managers**: id, user_id, session_id, name, email, profile data, created_at
- **employees**: id, manager_id, link_token, slot_number, profile data, bion_role, consent_given, consent_date
- **course_progress**: id, user_id, progress_data, updated_at
- **assessment_responses**: id, respondent_id, respondent_type, block_name, question_index, question_text, response_value

### Database Backup System
- **Backup Directory**: backups/ folder with timestamped SQLite copies
- **Auto-Backup**: auto_backup_on_startup() creates daily backups on application start
- **Retention**: cleanup_old_backups() keeps the 5 newest backups, removes oldest
- **Restore**: restore_from_backup() allows recovery to any available checkpoint
- **Sorting**: Uses numeric timestamps for correct chronological ordering

### LGPD Compliance
- **Privacy Page**: Dedicated page explaining data collection, processing, and user rights
- **Footer Link**: Privacy link accessible from all pages
- **Consent Capture**: Checkbox in employee assessment form, required before submission
- **Atomic Save**: Consent and assessment results saved together in single transaction
- **User Rights**: Access, correction, deletion, and portability rights documented

### LPSChat AI Integration ("Analytical Brain")
- **Model**: Google Gemini (gemini-1.5-flash)
- **Role**: Consultora especialista em Psicanálise e Neurociência aplicada à Liderança
- **Data Access**: Loads complete employee assessment data from SQLite (profiles, Bion roles, emails)
- **Privacy**: Only managers can access - employees blocked by global guard
- **Methodology Integrated**:
  - Kernberg: Rational leader characteristics (intelligence, integrity, object relations, healthy narcissism, healthy paranoid attitude)
  - Bion: Basic Assumptions (Dependency, Fight-Flight, Pairing) vs Work Group
  - Sinek: Circle of Safety with EDSO chemicals (Endorphin, Dopamine, Serotonin, Oxytocin)
  - Neuroscience: Cortisol vs Oxytocin, Amygdala, Mirror Neurons, Prefrontal Cortex
  - Transference & Countertransference dynamics
- **Capabilities**:
  - Identify unconscious roles and archetypes in team members
  - Map conflict points and synergies between employees
  - Suggest profile-to-role adequacy for specific positions
  - Explain transference/countertransference dynamics
  - Apply neuroscience concepts (cortisol, amygdala, mirror neurons)
- **Concepts**: Bion roles, Transferência/Contratransferência, Tarefa Real, Neurociência organizacional
- **Interface**: Elegant blue (#0D3B66) and gold (#F4D35E) themed chat with team context cards and example questions
- **API Key**: Uses st.secrets["GOOGLE_API_KEY"] for authentication

### Export System
- **PDF Generation**: Uses ReportLab library with custom LPS branding
- **Logo Integration**: Official LPS logo (attached_assets/logotipo_1768443722848.jpeg) in PDF header
- **PDF Types**:
  - Team Report: Complete team assessment with employee table and Bion role distribution
  - Individual Report: Single employee profile with detailed assessment results
  - AI Analysis Report: LPSChat conversation insights with team composition
- **Chart Export**: Matplotlib PNG with pie/bar charts showing profile distribution
- **CSV Export**: Team data in spreadsheet format
- **Export Locations**:
  - Team Management "Resultados da Equipe" tab: CSV, PDF, and Chart buttons
  - Individual employee cards: CSV and PDF buttons
  - LPSChat: "Exportar Analise (PDF)" button for AI insights

### Automated Email System
- **SMTP Configuration**: Uses placeholders for later configuration (SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, SMTP_FROM_NAME, SMTP_FROM_EMAIL)
- **Email Triggers**:
  - Employee completes assessment → Employee receives result email + Manager receives notification
  - Admin sends welcome email → New user receives login credentials after payment confirmation
- **AdminEmail Page**: Accessible via Dashboard "Admin" button for:
  - Sending welcome emails with login credentials
  - Creating user accounts automatically
  - Testing SMTP configuration
- **Security**: Employees only receive their own results; admin functions require authenticated manager

### Legacy/Dormant TypeScript Stack
The repository contains configuration for a full-stack TypeScript application that is not currently active:
- **Frontend**: React with Vite, TypeScript, Tailwind CSS, and shadcn/ui components
- **Backend**: Express.js server with session management
- **Database**: PostgreSQL with Drizzle ORM
- **Build System**: esbuild for server bundling, Vite for client

### Directory Structure Pattern
```
client/src/     - React frontend components (dormant)
server/         - Express backend (dormant)
shared/         - Shared schemas and types
migrations/     - Database migrations
```

### Design Decisions
1. **Streamlit over React**: Currently using Streamlit for simpler Python-based development, likely for rapid prototyping or data-focused features
2. **Brand Consistency**: Custom CSS ensures visual consistency with LPS branding regardless of framework

## External Dependencies

### Active Dependencies (Python)
- **Streamlit**: Web application framework
- **Pandas**: Data manipulation (imported in main.py)

### Configured but Dormant (TypeScript)
- **PostgreSQL**: Database (requires DATABASE_URL environment variable)
- **Drizzle ORM**: Database schema management and queries
- **shadcn/ui + Radix**: Component library for React
- **TanStack Query**: Data fetching and caching
- **Express Session**: Server-side session management with connect-pg-simple
- **Various integrations**: OpenAI, Stripe, Nodemailer, Google Generative AI (bundled in build script)

### Environment Variables Required
- `DATABASE_URL`: PostgreSQL connection string (for TypeScript stack activation)