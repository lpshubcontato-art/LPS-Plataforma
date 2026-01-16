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
- **Password Hashing**: SHA-256 for credential storage
- **Session Management**: Streamlit session_state for authenticated sessions
- **User Types**: Managers (full access via login) and Employees (token-based access)
- **Session Variables**: authenticated, user (id/name/email), manager_data, login_mode

### Access Control
- **Public Visitors**: Can view the Home page with sections (Sobre, Curso, LPSTest, LPSChat, Mentoria, Soluções, Contato)
- **Managers**: Register/login via "Entrar" button, access Dashboard with course progress and team management
- **Employees**: Access via unique token URL (?token=xxx), see only Assessment page
- **Content Gating**: Protected content shows paywall message "Conteúdo exclusivo para alunos. Liberação apenas após confirmação de pagamento"
- **LPSChat Access**: Only available after completing 5 theoretical modules (first 5 of 6)

### Page Structure
- **Home**: Public landing page with hero section and navigation menu (8 sections)
- **Login**: Authentication page accessible via "Entrar" button
- **Dashboard**: Manager area with course progress bar, assessment stats, AI insights, mentoring CTA
- **LPS Curso**: Full course content with 6 modules, progress saved to database
- **LPSTest**: Leadership assessment (48 questions, Bion role mapping)
- **TeamManagement**: Tabbed interface with "Gerar Convites" (link generation) and "Resultados da Equipe" (completed results + CSV exports)
- **LPSChat**: AI consultant (gated behind theoretical module completion)
- **EmployeeAssessment**: Token-based employee assessment page with Thank You page after completion

### Employee Access Guard
- **Global Protection**: Runs before every page render to force employees to stay on EmployeeAssessment
- **Token Persistence**: Employee token stored in session_state prevents navigation to other pages
- **Sidebar Hidden**: Employees see a clean page with no sidebar/navigation
- **Thank You Page**: Displays after assessment completion with profile summary

### Dashboard Features (Manager Area)
- **Course Progress**: Visual progress bars for each of 6 modules with overall percentage
- **Assessment Stats**: Counter showing "Aplicados" vs "Restantes" (4-employee package limit)
- **AI Insights**: Automated alerts about team (Bion role distribution, manager profile status)
- **Mentoring CTA**: Button to schedule with Viviane Nishiura via WhatsApp
- **Quick Access**: Buttons to Curso, LPSTest, Equipe, LPSChat (locked until course complete)

### Database Tables
- **users**: id, email, password_hash, name, user_type, created_at
- **managers**: id, user_id, session_id, name, email, profile data, created_at
- **employees**: id, manager_id, link_token, slot_number, profile data, bion_role
- **course_progress**: id, user_id, progress_data, updated_at

### LPSChat AI Integration
- **Model**: Google Gemini (gemini-1.5-flash)
- **Role**: Consultora especialista em Psicanálise e Neurociência aplicada à Liderança
- **Data Access**: Loads complete employee assessment data from SQLite (profiles, Bion roles, emails)
- **Privacy**: Only managers can access - employees blocked by global guard
- **Capabilities**:
  - Identify unconscious roles and archetypes in team members
  - Map conflict points and synergies between employees
  - Suggest profile-to-role adequacy for specific positions
  - Explain transference/countertransference dynamics
  - Apply neuroscience concepts (cortisol, amygdala, mirror neurons)
- **Concepts**: Bion roles, Transferência/Contratransferência, Tarefa Real, Neurociência organizacional
- **Interface**: Elegant blue (#0D3B66) and gold (#F4D35E) themed chat with team context cards and example questions
- **API Key**: Uses st.secrets["GOOGLE_API_KEY"] for authentication

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