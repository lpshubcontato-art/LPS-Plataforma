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
- **Managers**: Register/login, see full sidebar with course and team management
- **Employees**: Access via unique token URL (?token=xxx), see only Assessment page

### Database Tables
- **users**: id, email, password_hash, name, user_type, created_at
- **managers**: id, user_id, session_id, name, email, profile data, created_at
- **employees**: id, manager_id, link_token, slot_number, profile data, bion_role
- **course_progress**: id, user_id, progress_data, updated_at

### LPSChat AI Integration
- **Model**: OpenAI gpt-4o-mini
- **Context**: System prompt includes manager profile, employee profiles with Bion roles
- **Concepts**: Bion roles, Transferência/Contratransferência, Tarefa Real
- **Behavior**: Analyzes team dynamics, suggests interventions based on psychoanalytic concepts

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