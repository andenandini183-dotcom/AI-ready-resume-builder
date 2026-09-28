# Desktop AI-Ready Resume Builder

A complete, production-ready desktop Resume Builder application built with **Python 3.x**, **Tkinter + ttk**, **SQLite**, and **ReportLab**. Designed with a modular clean-architecture layout ready for future AI/LLM integration.

---

## 🌟 Overview

The **Desktop AI-Ready Resume Builder** is a local desktop application that allows professionals to build, customize, optimize, and export high-quality resumes. It runs **100% offline**, requires **no external API keys**, and features a deterministic ATS analyzer, live real-time preview, template switching, delayed autosave, database backups, and professional PDF generation.

---

## ✨ Features

- **Polished Desktop UX**: Modern neutral workspace palette with slate navy navigation, crisp white cards, and responsive sidebar editor layout.
- **Full Offline Resume Management**: Create, edit, duplicate, search, rename, and delete resumes with automatic SQLite persistence.
- **6 Comprehensive Resume Sections**:
  1. Personal Information & Professional Summary
  2. Education History
  3. Work Experience (with bullet point managers for responsibilities & key achievements)
  4. Key Projects (tech stack tags, descriptions, live/github URLs)
  5. Skills & Competencies (grouped by category and proficiency)
  6. Certifications & Licenses
- **Real-Time Live Preview**: Dynamic preview panel rendered inside a scrollable container that updates live as you type.
- **4 Professional Design Templates**:
  - **Modern**: Clean 2-column layout with bold navy headers and royal blue accents.
  - **Professional**: Executive top-to-bottom corporate style with structured dividers.
  - **Minimal**: High-contrast, typography-focused layout with sleek gray borders.
  - **Creative**: Vibrant visual layout with purple header and highlight badges.
- **ReportLab PDF Generator**: Generates clean, multi-page A4 PDFs (`output/generated_resumes/John_Doe_Resume.pdf`) with clickable URLs, dynamic line wrapping, page numbers ("Page X of Y"), and no overlapping content.
- **Deterministic Offline ATS Analyzer**: Evaluates contact details, section completeness, action verb usage, keyword density, and formatting risks to produce a 0–100 ATS Score with actionable suggestions.
- **Debounced Autosave**: Saves changes automatically after editing pauses (configurable delay), displaying visual "Saving..." / "Saved" status indicators.
- **Database Snapshot Backups**: One-click local database backup to `data/backups/`.
- **Comprehensive Pytest Suite**: 100% passing automated test suite covering models, database repository CRUD, business services, ATS scoring, and PDF rendering.

---

## 🏗️ Architecture & Dependency Direction

The project strictly follows a **one-directional dependency flow**:

```text
main.py
   │
   ▼
UI Layer (app/ui/) ──► Navbar, Sidebar, Forms, Dashboard, Live Preview
   │
   ▼
Services Layer (app/services/) ──► ResumeService, ATSAnalyzer, PDFGenerator, TemplateService, ExportService
   │                                  │
   ▼                                  ▼
Models Layer (app/models/)        Templates Layer (app/templates/)
   │
   ▼
Repository Layer (app/database/)
   │
   ▼
SQLite Database (data/resume_builder.db)
```

### Architectural Safeguards
- **UI** contains no SQL or complex business logic.
- **Repository** encapsulates all database CRUD and parameterized queries.
- **Templates** receive structured resume data and contain no database or Tkinter dependencies.
- **Services** own business logic and remain usable independently of the GUI.

---

## 📁 Folder Structure

```text
resume_builder/
├── main.py                       # Application entry point
├── requirements.txt               # Third-party dependencies
├── README.md                      # Comprehensive documentation
├── .gitignore                     # Git ignore rules
├── .env.example                   # Environment configuration template
│
├── app/
│   ├── config/
│   │   └── settings.py            # Centralized settings, paths, & UI theme
│   ├── database/
│   │   ├── connection.py          # SQLite connection manager & foreign keys
│   │   ├── schema.py              # DDL scripts and table creation
│   │   └── repository.py          # Resume repository (CRUD, duplicate, backup)
│   ├── models/
│   │   ├── personal_info.py       # PersonalInfo dataclass
│   │   ├── education.py           # Education dataclass
│   │   ├── experience.py          # Experience dataclass
│   │   ├── project.py             # Project dataclass
│   │   ├── skill.py               # Skill dataclass
│   │   ├── certification.py       # Certification dataclass
│   │   └── resume.py              # Resume root aggregate dataclass
│   ├── services/
│   │   ├── template_service.py    # Template registry & switching
│   │   ├── pdf_generator.py       # ReportLab PDF document generator
│   │   ├── ats_analyzer.py        # Deterministic offline ATS analyzer
│   │   ├── export_service.py      # Export helper and PDF system viewer launch
│   │   └── resume_service.py      # Business service coordinator & AI hooks
│   ├── templates/
│   │   ├── base_template.py       # Abstract base template contract
│   │   ├── modern.py              # Modern template
│   │   ├── professional.py        # Professional template
│   │   ├── minimal.py             # Minimal template
│   │   └── creative.py            # Creative template
│   ├── ui/
│   │   ├── main_window.py         # Root Tkinter window & view router
│   │   ├── dashboard.py           # Main dashboard & resume cards
│   │   ├── resume_preview.py      # Live real-time preview panel
│   │   ├── components/            # Sidebar, Navbar, Buttons, Dialogs
│   │   └── forms/                 # Personal, Education, Experience, Projects, Skills, Certs
│   └── utils/
│       ├── logger.py              # App logger
│       ├── validators.py          # Input validators
│       ├── file_utils.py          # File sanitization & backups
│       └── formatting.py          # Date & text formatting
│
├── data/
│   ├── resume_builder.db          # SQLite production database
│   └── backups/                   # Timestamped database backups
├── output/
│   └── generated_resumes/         # Exported PDF files
└── tests/                         # Pytest automated test suite
    ├── test_models.py
    ├── test_repository.py
    ├── test_resume_service.py
    ├── test_ats_analyzer.py
    └── test_pdf_generator.py
```

---

## 💻 Requirements

- **Python 3.8+** (Tested on Python 3.14)
- **Tkinter** (Included with standard Python installations on Windows & macOS)
- **ReportLab** (`reportlab>=3.6.0`)
- **Pytest** (`pytest>=7.0.0`)

---

## 🚀 Quick Start & Installation

### 1. Clone or Open Workspace
Navigate to the root project directory:
```bash
cd resume
```

### 2. Set Up Virtual Environment (Optional but Recommended)
On Windows (PowerShell):
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

On macOS / Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run Application
```bash
python main.py
```

---

## 🗄️ Database Management

- **Location**: `data/resume_builder.db`
- **Auto-Initialization**: The database schema initializes automatically on first launch.
- **Cascading Deletes**: Deleting a resume automatically cleans up all associated child entries using foreign key constraints (`PRAGMA foreign_keys = ON;`).
- **Backups**: Database backups are saved with timestamped filenames in `data/backups/`.

---

## 📄 PDF Export

- Exported PDF resumes are saved in `output/generated_resumes/<Name>_Resume.pdf`.
- Supports clickable web URLs, custom margins, page numbering ("Page X of Y"), and clean multi-page wrapping.

---

## 📊 ATS Analyzer Engine

The ATS analyzer is **100% offline and deterministic**. It scores your resume across 5 key dimensions:
1. **Contact Information Completeness** (Full Name, Email, Phone, Location, Web URLs)
2. **Required Section Coverage** (Summary, Work Experience, Education, Skills, Projects, Certifications)
3. **Action Verb & Bullet Point Impact** (Verbs like *Led, Architected, Developed, Scaled*)
4. **Keyword Coverage & Density** (Detects industry technical and soft skill keywords)
5. **Length & Formatting Risk Check** (Word count benchmarking)

---

## 🧪 Running Tests

Run the complete automated test suite using pytest:
```bash
python -m pytest -v
```

---

## 🔮 Future AI Integration Architecture (Section 20)

`ResumeService` (`app/services/resume_service.py`) includes clean extension points designed to integrate future LLM/AI APIs without modifying UI or database layers:
- `ai_improve_bullet(bullet_text: str) -> str`: Bullet enhancement hook.
- `ai_generate_summary(resume: Resume) -> str`: Professional summary generation hook.
- `ai_match_job_description(resume: Resume, job_description: str) -> dict`: JD matching & keyword gap analysis hook.

---

## ❓ Troubleshooting

- **Tkinter Error on Linux**: If `tkinter` is missing, install it via system package manager:
  ```bash
  sudo apt-get install python3-tk
  ```
- **PDF Generation Error**: Ensure the output folder `output/generated_resumes/` is writable.
