# NOVA: Project Intelligence Platform

NOVA is an project intelligence platform that transforms unstructured project documents into actionable, searchable knowledge.

Built during a 24-hour hackathon, NOVA helps teams understand project decisions, responsibilities, deadlines, risks, and newly added information without manually searching through large collections of documents.

## 🚀 Features

- **AI-powered document processing**
  - Extracts structured project insights from unstructured documents.
  - Supports CSV, DOCX, EML, Markdown, PDF, TXT, and XLSX files.

- **Project Memory**
  - Centralizes important project decisions, owners, deadlines, commitments, risks, and sources.
  - Provides a dashboard for quickly understanding project status.

- **Ask NOVA**
  - Natural-language question answering powered by Google Gemini.
  - Answers questions using the project's processed knowledge rather than relying solely on general AI knowledge.
  - Identifies conflicting information instead of silently inventing or choosing facts.

- **New Information**
  - Allows users to add new project information directly from the dashboard.
  - Newly added information becomes available to NOVA when answering questions.

- **Persistent Storage**
  - Uses Supabase/PostgreSQL to persist newly added project information.
  - Includes a local JSON fallback so the application can continue operating if the database is unavailable.

- **Interactive Dashboard**
  - Displays project memory, decisions, actions, risks, sources, and timeline information.
  - Includes an interactive chat interface for Ask NOVA.

## 🛠️ Tech Stack
- **Backend**
- Python
- Flask
- Flask-CORS
-**AI**
- Google Gemini
- Grounded question answering
- Structured project insight extraction
-**Data & Storage**
- Supabase
- PostgreSQL
- JSON fallback storage
-**Document Processing**
- PDF
- DOCX
- XLSX
- CSV
- EML
- Markdown
- TXT
-**Frontend**
- HTML
- CSS
- JavaScript
-**Development**
- Git
- GitHub
- Python virtual environment
  - Provides API health/status feedback.

