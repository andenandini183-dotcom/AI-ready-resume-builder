"""
File system and path manipulation utilities.
Handles filename sanitization, safe path operations, database backups, PDF text extraction, and text/JSON/PDF resume imports.
"""

import json
import re
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, Union

from app.config.settings import BACKUP_DIR, DATABASE_PATH, ensure_directories
from app.models.resume import Resume
from app.models.personal_info import PersonalInfo
from app.models.education import Education
from app.models.experience import Experience
from app.models.project import Project
from app.models.skill import Skill
from app.models.certification import Certification
from app.utils.formatting import format_date_range, clean_garbage_text
from app.utils.logger import logger


def sanitize_filename(filename: str, default_name: str = "resume") -> str:
    """Sanitizes strings for safe cross-platform file naming."""
    if not filename or not filename.strip():
        filename = default_name
        
    clean = re.sub(r"[^\w\s-]", "", filename.strip())
    clean = re.sub(r"[\s_]+", "_", clean)
    clean = clean.strip("_")
    
    return clean or default_name


def backup_database() -> Path:
    """Creates a timestamped backup copy of the SQLite database file."""
    ensure_directories()
    
    if not DATABASE_PATH.exists():
        logger.warning(f"Database file {DATABASE_PATH} does not exist yet. Backup skipped.")
        return BACKUP_DIR
        
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = BACKUP_DIR / f"resume_builder_backup_{timestamp}.db"
    
    try:
        shutil.copy2(DATABASE_PATH, backup_path)
        logger.info(f"Database backup created successfully: {backup_path}")
        return backup_path
    except Exception as e:
        logger.error(f"Failed to create database backup: {e}")
        raise e


def extract_text_from_pdf(pdf_path: Path) -> str:
    """Extracts raw text content from a PDF document using pypdf/PyPDF2/pdfplumber."""
    try:
        import pypdf
        reader = pypdf.PdfReader(pdf_path)
        text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
        if text.strip():
            logger.info(f"Extracted PDF text via pypdf from {pdf_path}")
            return text
    except Exception as e:
        logger.warning(f"pypdf extraction failed, trying PyPDF2: {e}")

    try:
        import PyPDF2
        reader = PyPDF2.PdfReader(pdf_path)
        text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
        if text.strip():
            logger.info(f"Extracted PDF text via PyPDF2 from {pdf_path}")
            return text
    except Exception as e:
        logger.warning(f"PyPDF2 extraction failed, trying pdfplumber: {e}")

    try:
        import pdfplumber
        with pdfplumber.open(pdf_path) as pdf:
            text = "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])
            if text.strip():
                logger.info(f"Extracted PDF text via pdfplumber from {pdf_path}")
                return text
    except Exception as e:
        logger.error(f"Failed to extract text from PDF {pdf_path}: {e}")

    return ""


def format_resume_to_text(resume: Resume) -> str:
    """Formats a Resume object into clean, human-readable structured text."""
    name = clean_garbage_text(resume.personal_info.full_name) or "Candidate Name"
    title = clean_garbage_text(resume.personal_info.title) or ""
    email = resume.personal_info.email or ""
    phone = resume.personal_info.phone or ""
    location = clean_garbage_text(resume.personal_info.location) or ""
    linkedin = resume.personal_info.linkedin or ""
    github = resume.personal_info.github or ""

    contact_parts = [p for p in [email, phone, location, linkedin, github] if p and p.strip()]
    contact = " | ".join(contact_parts)

    text = f"{name}\n"
    if title:
        text += f"{title}\n"
    if contact:
        text += f"{contact}\n"
    text += "\n"

    if resume.personal_info.summary:
        text += f"PROFESSIONAL SUMMARY:\n{clean_garbage_text(resume.personal_info.summary)}\n\n"

    if resume.experience:
        text += "WORK EXPERIENCE & INTERNSHIPS:\n"
        for exp in resume.experience:
            pos = clean_garbage_text(exp.position)
            comp = clean_garbage_text(exp.company)
            pos_comp = f"{pos} — {comp}" if comp else pos
            if exp.location:
                pos_comp += f" ({clean_garbage_text(exp.location)})"
            dates = format_date_range(exp.start_date, exp.end_date, exp.is_current)
            date_str = f" [{dates}]" if dates else ""
            text += f"{pos_comp}{date_str}\n"

            bullets = exp.get_responsibilities_list()
            if bullets:
                for b in bullets:
                    text += f"- {clean_garbage_text(b)}\n"
            elif exp.responsibilities:
                text += f"{clean_garbage_text(exp.responsibilities)}\n"
            text += "\n"

    if resume.education:
        text += "EDUCATION:\n"
        for edu in resume.education:
            deg = clean_garbage_text(edu.degree)
            inst = clean_garbage_text(edu.institution)
            field = clean_garbage_text(edu.field_of_study)
            if deg and field and field.lower() not in deg.lower():
                deg_str = f"{deg} in {field}"
            else:
                deg_str = deg or field or "Bachelor of Technology (B.Tech)"
            
            inst_deg = f"{deg_str} — {inst}" if inst else deg_str
            dates = format_date_range(edu.start_date, edu.end_date)
            date_str = f" [{dates}]" if dates else ""
            gpa_str = f" (GPA: {edu.gpa})" if edu.gpa else ""
            text += f"{inst_deg}{gpa_str}{date_str}\n"
            if edu.description:
                text += f"{clean_garbage_text(edu.description)}\n"
            text += "\n"

    if resume.projects:
        text += "KEY PROJECTS:\n"
        for proj in resume.projects:
            p_name = clean_garbage_text(proj.project_name)
            p_tech = clean_garbage_text(proj.technologies)
            tech = f" | Tech: {p_tech}" if p_tech else ""
            dates = format_date_range(proj.start_date, proj.end_date)
            date_str = f" [{dates}]" if dates else ""
            text += f"{p_name}{tech}{date_str}\n"

            if proj.description:
                text += f"{clean_garbage_text(proj.description)}\n"
            bullets = proj.get_contributions_list()
            for b in bullets:
                text += f"- {clean_garbage_text(b)}\n"
            if proj.project_url or proj.github_url:
                url = proj.project_url or proj.github_url
                text += f"Link: {url}\n"
            text += "\n"

    if resume.skills:
        text += "TECHNICAL SKILLS & COMPETENCIES:\n"
        skills_by_cat: Dict[str, List[str]] = {}
        for s in resume.skills:
            cat = clean_garbage_text(s.category) or "Technical Skills"
            if cat not in skills_by_cat:
                skills_by_cat[cat] = []
            skills_by_cat[cat].append(clean_garbage_text(s.skill_name))
        for cat, items in skills_by_cat.items():
            text += f"{cat}: " + ", ".join(items) + "\n"
        text += "\n"

    if resume.certifications:
        text += "CERTIFICATIONS & LICENSES:\n"
        for c in resume.certifications:
            c_name = clean_garbage_text(c.name)
            issuer = f" — {clean_garbage_text(c.issuing_organization)}" if c.issuing_organization else ""
            date_str = f" [{c.issue_date}]" if c.issue_date else ""
            text += f"{c_name}{issuer}{date_str}\n"

    return text.strip()


def parse_resume_import(file_path_or_content: Union[Path, str]) -> Resume:
    """Imports and parses resume data from a PDF file, JSON file, text file, or raw string."""
    text_content = ""

    is_existing_file = False
    file_path: Optional[Path] = None

    if isinstance(file_path_or_content, Path):
        file_path = file_path_or_content
        is_existing_file = file_path.exists()
    elif isinstance(file_path_or_content, str) and Path(file_path_or_content).exists():
        file_path = Path(file_path_or_content)
        is_existing_file = True

    if is_existing_file and file_path:
        suffix = file_path.suffix.lower()
        if suffix == ".pdf":
            text_content = extract_text_from_pdf(file_path)
        elif suffix == ".json":
            content_bytes = file_path.read_bytes()
            try:
                raw_json = content_bytes.decode("utf-8")
            except UnicodeDecodeError:
                raw_json = content_bytes.decode("latin-1")

            try:
                data = json.loads(raw_json)
                if isinstance(data, dict):
                    resume = Resume.from_dict(data)
                    resume.id = None
                    resume.personal_info.full_name = re.sub(r"^(name|full name|candidate name)[:\s-]+", "", resume.personal_info.full_name, flags=re.IGNORECASE).strip()
                    return resume
            except Exception as e:
                logger.warning(f"Could not parse file as JSON, falling back to text parsing: {e}")
                text_content = raw_json
        else:
            content_bytes = file_path.read_bytes()
            try:
                text_content = content_bytes.decode("utf-8")
            except UnicodeDecodeError:
                text_content = content_bytes.decode("latin-1")
    else:
        text_content = str(file_path_or_content)

    resume = Resume(title="Imported Resume")
    lines = [clean_garbage_text(line) for line in text_content.split("\n") if line.strip()]
    if not lines:
        return resume

    # 1. Contact Information Extraction
    email_match = re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text_content)
    if email_match:
        resume.personal_info.email = email_match.group(0)

    phone_match = re.search(r"\+?[0-9\s\-\(\)\.]{9,20}", text_content)
    if phone_match:
        resume.personal_info.phone = phone_match.group(0).strip()

    linkedin_match = re.search(r"(https?://)?(www\.)?linkedin\.com/in/[a-zA-Z0-9_-]+", text_content)
    if linkedin_match:
        resume.personal_info.linkedin = linkedin_match.group(0)

    github_match = re.search(r"(https?://)?(www\.)?github\.com/[a-zA-Z0-9_-]+", text_content)
    if github_match:
        resume.personal_info.github = github_match.group(0)

    # Name and Title from top lines
    first_few = lines[:5]
    name_candidates = []
    for l in first_few:
        clean_l = re.sub(r"^(name|full name|candidate name)[:\s-]+", "", l, flags=re.IGNORECASE).strip()
        clean_l = re.sub(r"[#\*_]", "", clean_l).strip()
        if clean_l and not "@" in clean_l and not re.search(r"\d{7,}", clean_l) and not clean_l.lower().startswith(("email", "phone", "summary", "profile", "contact", "http")):
            name_candidates.append(clean_l)

    if name_candidates:
        resume.personal_info.full_name = name_candidates[0].title()
        if len(name_candidates) > 1 and len(name_candidates[1]) < 60 and not any(kw in name_candidates[1].lower() for kw in ["summary", "experience", "education", "skills"]):
            resume.personal_info.title = name_candidates[1].title()

    # 2. Section Boundary Detection
    SECTION_KEYWORDS = {
        "summary": ["summary", "professional summary", "profile", "executive summary", "about me", "objective", "career objective"],
        "experience": ["work experience", "professional experience", "employment history", "work history", "experience", "employment", "career history", "relevant experience", "internships"],
        "education": ["education", "academic background", "academic history", "qualifications", "education & training", "education and training"],
        "projects": ["projects", "key projects", "technical projects", "personal projects", "portfolio", "notable projects"],
        "skills": ["skills", "technical skills", "core competencies", "competencies", "technologies", "skills & abilities", "areas of expertise", "expertise", "tools & technologies", "technical skills & competencies"],
        "certifications": ["certifications", "licenses", "certifications & licenses", "certifications and licenses", "courses", "credentials", "certifications & training"],
    }

    def identify_section_header(line: str) -> Optional[str]:
        clean = re.sub(r"^[#\*\-=\s]+", "", line).strip().rstrip(":").lower()
        if not clean or len(clean) > 40:
            return None
        for sec_type, kw_list in SECTION_KEYWORDS.items():
            for kw in kw_list:
                if clean == kw:
                    return sec_type
        return None

    sections: Dict[str, List[str]] = {}
    current_sec = "header"
    sections[current_sec] = []

    for line in lines:
        sec_match = identify_section_header(line)
        if sec_match:
            current_sec = sec_match
            if current_sec not in sections:
                sections[current_sec] = []
        else:
            sections[current_sec].append(line)

    # 3. Parse Extracted Sections
    if "summary" in sections and sections["summary"]:
        sum_lines = [l for l in sections["summary"] if not "@" in l and not l.lower().startswith(("name:", "email:", "phone:"))]
        resume.personal_info.summary = clean_garbage_text(" ".join(sum_lines))

    if "experience" in sections and sections["experience"]:
        exp_lines = sections["experience"]
        current_job: Optional[Experience] = None
        job_resp_lines: List[str] = []

        for l in exp_lines:
            is_job_header = False
            pos, comp = "", ""

            if re.search(r"\s+at\s+", l, flags=re.IGNORECASE):
                parts = re.split(r"\s+at\s+", l, maxsplit=1, flags=re.IGNORECASE)
                pos, comp = parts[0].strip(), parts[1].strip()
                is_job_header = True
            elif re.search(r"\s+[—–\|\-]\s+", l):
                parts = re.split(r"\s+[—–\|\-]\s+", l, maxsplit=1)
                if not parts[0].strip().startswith(("-", "*", "•")):
                    pos, comp = parts[0].strip(), parts[1].strip()
                    is_job_header = True

            if is_job_header:
                if current_job:
                    current_job.responsibilities = "\n".join(job_resp_lines).strip()
                    resume.experience.append(current_job)
                    job_resp_lines = []
                current_job = Experience(
                    company=re.sub(r"\s*\(.*?\)", "", comp).strip() or "Company",
                    position=pos or "Role",
                )
            else:
                if current_job:
                    job_resp_lines.append(l)
                else:
                    current_job = Experience(company="Company", position=l)

        if current_job:
            current_job.responsibilities = "\n".join(job_resp_lines).strip()
            resume.experience.append(current_job)

    if "education" in sections and sections["education"]:
        edu_lines = sections["education"]
        current_edu: Optional[Education] = None

        DEGREE_KEYWORDS = [
            "b.tech", "btech", "b tech", "bachelor of technology",
            "b.e", "b.e.", "be", "bachelor of engineering",
            "b.s", "b.s.", "bs", "bachelor of science",
            "b.a", "ba", "bachelor of arts",
            "m.tech", "mtech", "m tech", "master of technology",
            "m.s", "ms", "master of science",
            "bca", "mca", "mba", "ph.d", "phd", "diploma", "degree",
            "higher secondary", "intermediate", "high school"
        ]

        for l in edu_lines:
            clean_l = l.strip()
            if not clean_l:
                continue

            l_lower = clean_l.lower()
            if any(deg_kw in l_lower for deg_kw in DEGREE_KEYWORDS):
                if current_edu:
                    resume.education.append(current_edu)

                deg_text = clean_l
                inst_text = ""
                field_text = ""

                if re.search(r"\s+[—–\|\-]\s+", clean_l):
                    parts = re.split(r"\s+[—–\|\-]\s+", clean_l, maxsplit=1)
                    deg_text = parts[0].strip()
                    inst_text = parts[1].strip()
                elif re.search(r"\s+at\s+", clean_l, flags=re.IGNORECASE):
                    parts = re.split(r"\s+at\s+", clean_l, maxsplit=1, flags=re.IGNORECASE)
                    deg_text = parts[0].strip()
                    inst_text = parts[1].strip()

                if any(k in deg_text.lower() for k in ["btech", "b.tech", "b tech", "bachelor of technology"]):
                    deg_name = "Bachelor of Technology (B.Tech)"
                    if re.search(r"\s+in\s+", deg_text, flags=re.IGNORECASE):
                        parts = re.split(r"\s+in\s+", deg_text, maxsplit=1, flags=re.IGNORECASE)
                        field_text = parts[1].strip()
                elif re.search(r"\s+in\s+", deg_text, flags=re.IGNORECASE):
                    parts = re.split(r"\s+in\s+", deg_text, maxsplit=1, flags=re.IGNORECASE)
                    deg_name = parts[0].strip()
                    field_text = parts[1].strip()
                else:
                    deg_name = deg_text
                    field_text = ""

                current_edu = Education(
                    institution=inst_text or "University / College",
                    degree=deg_name,
                    field_of_study=field_text,
                )
            elif current_edu:
                if current_edu.institution == "University / College" and len(clean_l) < 70 and not re.search(r"\d{4}", clean_l):
                    current_edu.institution = clean_l
                else:
                    current_edu.description = (current_edu.description + "\n" + clean_l).strip()
            else:
                current_edu = Education(institution=clean_l, degree="Bachelor of Technology (B.Tech)")

        if current_edu:
            resume.education.append(current_edu)

    if "projects" in sections and sections["projects"]:
        proj_lines = sections["projects"]
        current_proj: Optional[Project] = None

        for l in proj_lines:
            clean_l = clean_garbage_text(l)
            if not clean_l:
                continue

            if re.search(r"\s*[—–\|\-]\s*", clean_l) or (not clean_l.startswith(("-", "*", "•")) and len(clean_l) < 55):
                if current_proj:
                    resume.projects.append(current_proj)
                p_name = clean_l
                p_tech = ""
                if re.search(r"\s*[—–\|\-]\s*", clean_l):
                    parts = re.split(r"\s*[—–\|\-]\s*", clean_l, maxsplit=1)
                    p_name, p_tech = parts[0].strip(), parts[1].strip()
                    p_tech = re.sub(r"^(tech|technologies)[:\s-]+", "", p_tech, flags=re.IGNORECASE).strip()

                p_name = re.sub(r"\(Tech:.*?\)", "", p_name, flags=re.IGNORECASE).strip()
                p_name = clean_garbage_text(p_name)
                current_proj = Project(project_name=p_name, technologies=clean_garbage_text(p_tech))
            elif current_proj:
                current_proj.key_contributions = (current_proj.key_contributions + "\n" + clean_l).strip()
            else:
                p_name = re.sub(r"\(Tech:.*?\)", "", clean_l, flags=re.IGNORECASE).strip()
                current_proj = Project(project_name=clean_garbage_text(p_name))

        if current_proj:
            resume.projects.append(current_proj)

    if "skills" in sections and sections["skills"]:
        sk_text = " ".join(sections["skills"])
        raw_skills = [s.strip() for s in re.split(r"[,;•\n|]", sk_text) if s.strip()]
        for sk in raw_skills[:25]:
            clean_sk = re.sub(r"^(skills|technical skills)[:\s-]+", "", sk, flags=re.IGNORECASE).strip()
            clean_sk = clean_garbage_text(clean_sk)
            if clean_sk and len(clean_sk) < 40 and not "@" in clean_sk and not clean_sk.lower().startswith("http"):
                resume.skills.append(Skill(skill_name=clean_sk.capitalize(), category="Technical Skills"))

    if "certifications" in sections and sections["certifications"]:
        cert_lines = sections["certifications"]
        for l in cert_lines:
            clean_l = clean_garbage_text(l)
            if clean_l and not clean_l.lower().startswith("certifications"):
                parts = re.split(r"\s*[—–\|\-]\s*", clean_l, maxsplit=1)
                c_name = parts[0].strip()
                c_issuer = parts[1].strip() if len(parts) > 1 else ""
                resume.certifications.append(Certification(name=c_name, issuing_organization=c_issuer))

    if not resume.personal_info.summary and lines:
        body_lines = [l for l in lines[2:] if not l.lower().startswith(("name:", "email:", "phone:")) and len(l) > 25]
        if body_lines:
            resume.personal_info.summary = clean_garbage_text(" ".join(body_lines[:3]))

    return resume


