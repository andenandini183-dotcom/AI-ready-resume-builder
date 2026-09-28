"""
Deterministic Offline ATS Analyzer Engine & Job Description Tailoring Builder.
Evaluates contact details, section completeness, action verbs, keyword coverage, JD matching, and builds new tailored resumes.
"""

import re
from dataclasses import dataclass, field
from typing import List, Dict, Any, Set, Tuple, Optional
from app.models.resume import Resume
from app.models.personal_info import PersonalInfo
from app.models.education import Education
from app.models.experience import Experience
from app.models.project import Project
from app.models.skill import Skill
from app.models.certification import Certification

# High-impact professional action verbs
ACTION_VERBS = {
    "led", "developed", "architected", "engineered", "implemented", "designed",
    "managed", "created", "optimized", "scaled", "automated", "built", "orchestrated",
    "spearheaded", "directed", "formulated", "delivered", "deployed", "transformed",
    "reduced", "increased", "maximized", "streamlined", "accelerated", "pioneered"
}

# Industry standard tech & professional keywords
STANDARD_KEYWORDS = {
    "python", "sql", "git", "api", "rest", "docker", "agile", "aws", "cloud",
    "architecture", "linux", "ci/cd", "unit testing", "database", "communication",
    "problem solving", "leadership", "analytics", "scrum", "microservices"
}


@dataclass
class ATSResult:
    """Structured ATS Analysis Report Data Class."""
    score: int = 0
    critical_issues: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    detected_keywords: List[str] = field(default_factory=list)
    missing_keywords: List[str] = field(default_factory=list)
    section_analysis: Dict[str, bool] = field(default_factory=dict)
    word_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Converts ATS result to dictionary."""
        return {
            "score": self.score,
            "critical_issues": self.critical_issues,
            "warnings": self.warnings,
            "suggestions": self.suggestions,
            "detected_keywords": self.detected_keywords,
            "missing_keywords": self.missing_keywords,
            "section_analysis": self.section_analysis,
            "word_count": self.word_count,
        }


@dataclass
class JDATSResult:
    """Job Description ATS Match Result Data Class."""
    score: int = 0
    job_title_detected: str = "Target Role"
    matched_keywords: List[str] = field(default_factory=list)
    missing_keywords: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    total_jd_keywords: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "score": self.score,
            "match_percentage": self.score,
            "job_title_detected": self.job_title_detected,
            "matched_keywords": self.matched_keywords,
            "missing_keywords": self.missing_keywords,
            "recommendations": self.recommendations,
            "total_jd_keywords": self.total_jd_keywords,
        }


class ATSAnalyzer:
    """Deterministic offline ATS analyzer & Job Description matcher."""

    def analyze(self, resume: Resume) -> ATSResult:
        """Performs full deterministic ATS scan on resume model."""
        result = ATSResult()
        score_components = []

        # 1. Contact Information Completeness (20 points max)
        contact_score = 0
        p = resume.personal_info
        if p.full_name and p.full_name.strip():
            contact_score += 4
        else:
            result.critical_issues.append("Missing Full Name in contact details.")

        if p.email and "@" in p.email:
            contact_score += 4
        else:
            result.critical_issues.append("Missing or invalid Email address.")

        if p.phone and p.phone.strip():
            contact_score += 4
        else:
            result.warnings.append("Missing Phone Number.")

        if p.location and p.location.strip():
            contact_score += 4
        else:
            result.warnings.append("Missing Location (City, State/Country).")

        if p.linkedin or p.github or p.portfolio:
            contact_score += 4
        else:
            result.suggestions.append("Add a LinkedIn, GitHub, or Portfolio URL to boost recruiter visibility.")

        score_components.append(contact_score)

        # 2. Section Analysis (25 points max)
        section_status = {
            "Personal Information": bool(p.full_name and p.email),
            "Professional Summary": bool(p.summary and len(p.summary.strip()) > 30),
            "Work Experience": len(resume.experience) > 0,
            "Education": len(resume.education) > 0,
            "Skills": len(resume.skills) > 0,
            "Projects": len(resume.projects) > 0,
            "Certifications": len(resume.certifications) > 0,
        }
        result.section_analysis = section_status

        section_score = 0
        if section_status["Personal Information"]: section_score += 5
        if section_status["Professional Summary"]:
            section_score += 4
        else:
            result.suggestions.append("Add a compelling 2-3 sentence Professional Summary.")

        if section_status["Work Experience"]:
            section_score += 6
        else:
            result.critical_issues.append("No Work Experience entries added.")

        if section_status["Education"]:
            section_score += 5
        else:
            result.warnings.append("No Education history added.")

        if section_status["Skills"]:
            section_score += 5
        else:
            result.critical_issues.append("No Skills listed.")

        score_components.append(section_score)

        # 3. Action Verb & Bullet Point Analysis (25 points max)
        verb_count = 0
        total_bullets = 0
        all_text = [p.summary]

        for exp in resume.experience:
            bullets = exp.get_responsibilities_list() + exp.get_achievements_list()
            total_bullets += len(bullets)
            for b in bullets:
                all_text.append(b)
                words = b.lower().split()
                if words and words[0] in ACTION_VERBS:
                    verb_count += 1

        for proj in resume.projects:
            all_text.append(proj.description)
            bullets = proj.get_contributions_list()
            total_bullets += len(bullets)
            for b in bullets:
                all_text.append(b)

        bullet_score = 0
        if total_bullets >= 5:
            bullet_score += 15
        elif total_bullets > 0:
            bullet_score += 8
            result.warnings.append(f"Only {total_bullets} bullet points found. Aim for at least 5-10 strong bullet points across experience.")
        else:
            result.critical_issues.append("No bullet points found under Experience or Projects.")

        if verb_count >= 3:
            bullet_score += 10
        elif verb_count > 0:
            bullet_score += 5
            result.suggestions.append("Start more bullet points with strong action verbs (e.g., Developed, Led, Architected, Scaled).")
        else:
            result.suggestions.append("Use active power verbs to begin responsibility bullet points.")

        score_components.append(bullet_score)

        # 4. Keyword Analysis & Density (20 points max)
        full_text_str = " ".join([t for t in all_text if t]).lower()
        for sk in resume.skills:
            full_text_str += " " + sk.skill_name.lower()

        words_set = set(re.findall(r"\b[a-zA-Z/+-]+\b", full_text_str))
        detected = list(STANDARD_KEYWORDS.intersection(words_set))
        missing = list(STANDARD_KEYWORDS.difference(words_set))

        result.detected_keywords = sorted(detected)
        result.missing_keywords = sorted(missing[:6])

        keyword_score = min(20, len(detected) * 4)
        score_components.append(keyword_score)

        # 5. Length & Formatting Risk Check (10 points max)
        word_count = len(full_text_str.split())
        result.word_count = word_count
        length_score = 10

        if word_count < 100:
            length_score = 3
            result.warnings.append("Resume is very brief (< 100 words). Expand details for better ATS indexing.")
        elif word_count > 1000:
            length_score = 6
            result.warnings.append("Resume is very lengthy (> 1000 words). Try streamlining to 1-2 pages.")

        score_components.append(length_score)

        total_score = min(100, max(0, sum(score_components)))
        result.score = total_score
        return result

    def analyze_job_description(self, resume: Resume, job_description: str) -> JDATSResult:
        """Analyzes how well the resume matches a target Job Description."""
        res = JDATSResult()
        if not job_description or not job_description.strip():
            res.recommendations.append("Paste a target Job Description above to see tailored ATS match insights.")
            return res

        jd_clean = job_description.strip()

        # Extract job title from first line or common title patterns
        lines = [line.strip() for line in jd_clean.split("\n") if line.strip()]
        if lines:
            first_line = lines[0]
            if len(first_line) < 60 and not first_line.lower().startswith("about"):
                res.job_title_detected = first_line.title()

        # Extract keywords from JD using clean regex
        words = re.findall(r"\b[a-zA-Z][a-zA-Z0-9+#]*\b", jd_clean.lower())

        # Filter out common stop words and generic filler words
        stop_words = {
            "the", "and", "for", "with", "that", "this", "from", "you", "your", "will", "have",
            "are", "about", "work", "team", "experience", "role", "our", "ability", "must", "requirements",
            "responsibilities", "looking", "working", "strong", "knowledge", "skills", "such", "using",
            "align", "applications", "application", "powered", "required", "proficient", "tech", "technology",
            "build", "best", "used", "uses", "make", "help", "helps", "academic", "generator", "diagnostic",
            "assistant", "classification", "solution", "solutions", "overall", "target", "competencies",
            "degree", "field", "study", "description", "details", "level", "system", "systems", "project",
            "projects", "support", "across", "within", "plus", "years", "year", "good", "great", "high",
            "well", "needs", "need", "developed", "built", "implemented", "designed", "created", "managed"
        }
        jd_keywords = set([w for w in words if w not in stop_words and len(w) >= 3 and not w.isdigit()])

        if not jd_keywords:
            res.recommendations.append("Could not extract distinct keywords from JD. Please provide a more detailed posting.")
            return res

        res.total_jd_keywords = len(jd_keywords)

        # Extract resume full text
        resume_text_parts = [
            resume.personal_info.full_name,
            resume.personal_info.title,
            resume.personal_info.summary,
        ]
        for exp in resume.experience:
            resume_text_parts.extend([exp.company, exp.position, exp.responsibilities, exp.achievements])
        for edu in resume.education:
            resume_text_parts.extend([edu.institution, edu.degree, edu.field_of_study, edu.description])
        for proj in resume.projects:
            resume_text_parts.extend([proj.project_name, proj.description, proj.technologies, proj.key_contributions])
        for sk in resume.skills:
            resume_text_parts.extend([sk.skill_name, sk.category])

        resume_full_str = " ".join([t for t in resume_text_parts if t]).lower()
        resume_words = set(re.findall(r"\b[a-zA-Z][a-zA-Z0-9+#]*\b", resume_full_str))

        matched = sorted(list(jd_keywords.intersection(resume_words)))
        missing = sorted(list(jd_keywords.difference(resume_words)))

        res.matched_keywords = matched
        res.missing_keywords = missing

        # Calculate percentage
        if jd_keywords:
            raw_match = (len(matched) / len(jd_keywords)) * 100
            res.score = min(100, max(15, int(raw_match * 1.5)))  # Weighted score scaling
        else:
            res.score = 50

        # Build actionable recommendations
        if missing:
            top_missing = missing[:5]
            res.recommendations.append(f"Consider adding key target terms: {', '.join(top_missing)}.")
        if res.score < 70:
            res.recommendations.append("Click 'Build Tailored Resume' to automatically build a custom resume targeted for this role.")
        else:
            res.recommendations.append("Strong ATS match! Your resume incorporates most key target JD terms.")

        return res

    def tailor_resume_for_jd(self, resume: Resume, job_description: str) -> Tuple[Resume, JDATSResult]:
        """Automatically tailors the resume for the given job description."""
        jd_result = self.analyze_job_description(resume, job_description)

        # 1. Update Title if missing or generic
        if jd_result.job_title_detected and jd_result.job_title_detected != "Target Role":
            resume.personal_info.title = jd_result.job_title_detected

        # 2. Add missing keywords to Skills under "Job Tailored Skills"
        existing_skills = {s.skill_name.lower() for s in resume.skills}
        for kw in jd_result.missing_keywords[:6]:
            if kw.lower() not in existing_skills and len(kw) >= 3:
                new_skill = Skill(
                    skill_name=kw.capitalize(),
                    category="Job Tailored Skills",
                    proficiency="",
                )
                resume.skills.append(new_skill)
                existing_skills.add(kw.lower())

        # Re-run analysis on tailored resume
        updated_result = self.analyze_job_description(resume, job_description)
        return resume, updated_result

    def build_tailored_resume_from_jd(self, base_resume: Resume, job_description: str) -> Tuple[Resume, JDATSResult]:
        """Builds a BRAND NEW targeted Resume specifically tailored to the given Job Description and Candidate Details."""
        jd_result = self.analyze_job_description(base_resume, job_description)

        target_title = jd_result.job_title_detected if jd_result.job_title_detected != "Target Role" else (base_resume.personal_info.title or "Professional")
        new_resume_title = f"Tailored - {target_title}"

        # Create brand new tailored Resume object graph
        tailored = Resume(
            title=new_resume_title,
            template_name=base_resume.template_name or "modern",
        )

        # 1. Personal Info & Tailored Summary
        tailored.personal_info = PersonalInfo.from_dict(base_resume.personal_info.to_dict())
        tailored.personal_info.title = target_title

        matched_caps = [kw.capitalize() for kw in jd_result.matched_keywords[:4]]
        missing_caps = [kw.capitalize() for kw in jd_result.missing_keywords[:4]]
        top_keywords = ", ".join(matched_caps + missing_caps)

        if base_resume.personal_info.summary:
            clean_sum = base_resume.personal_info.summary.strip()
            if target_title.lower() not in clean_sum.lower():
                tailored.personal_info.summary = f"{clean_sum} Tailored for {target_title} positions, leveraging key proficiencies in {top_keywords}."
            else:
                tailored.personal_info.summary = clean_sum
        else:
            tailored.personal_info.summary = f"Results-driven {target_title} with proven background in {top_keywords}. Focused on building high-performance solutions and delivering scalable engineering outcomes."

        # 2. Copy Education
        tailored.education = [Education.from_dict(e.to_dict()) for e in base_resume.education]

        # 3. Work Experience
        tailored.experience = []
        for exp in base_resume.experience:
            exp_copy = Experience.from_dict(exp.to_dict())
            bullets = exp_copy.get_responsibilities_list()

            enhanced_bullets = []
            for idx, b in enumerate(bullets):
                clean_b = b.strip()
                if not clean_b:
                    continue
                words = clean_b.split()
                if words and words[0].lower() not in ACTION_VERBS:
                    verb = list(ACTION_VERBS)[idx % len(ACTION_VERBS)].capitalize()
                    clean_b = f"{verb} {clean_b[0].lower()}{clean_b[1:]}"
                enhanced_bullets.append(clean_b)

            exp_copy.responsibilities = "\n".join(enhanced_bullets) if enhanced_bullets else exp_copy.responsibilities
            tailored.experience.append(exp_copy)

        # 4. Projects
        tailored.projects = []
        for proj in base_resume.projects:
            proj_copy = Project.from_dict(proj.to_dict())
            tailored.projects.append(proj_copy)

        # 5. Skills - Incorporate JD keywords cleanly
        tailored.skills = [Skill.from_dict(s.to_dict()) for s in base_resume.skills]
        existing_skills = {s.skill_name.lower() for s in tailored.skills}

        for kw in jd_result.missing_keywords[:6]:
            if kw.lower() not in existing_skills and len(kw) >= 3:
                tailored.skills.append(Skill(
                    skill_name=kw.capitalize(),
                    category="Technical Skills",
                    proficiency="",
                ))
                existing_skills.add(kw.lower())

        # 6. Copy Certifications
        tailored.certifications = [Certification.from_dict(c.to_dict()) for c in base_resume.certifications]

        # Re-evaluate final ATS result on tailored resume
        final_jd_result = self.analyze_job_description(tailored, job_description)
        return tailored, final_jd_result

