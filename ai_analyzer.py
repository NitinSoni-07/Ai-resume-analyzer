"""
ai_analyzer.py - Rule-based Resume Analyzer (No API Key needed)
"""

import re


COMMON_SKILLS = [
    "python", "java", "javascript", "c++", "c#", "html", "css", "sql",
    "react", "nodejs", "django", "flask", "mongodb", "mysql", "postgresql",
    "machine learning", "deep learning", "data analysis", "excel", "power bi",
    "tableau", "git", "docker", "kubernetes", "aws", "azure", "linux",
    "communication", "teamwork", "leadership", "problem solving", "ms office",
    "photoshop", "figma", "android", "ios", "flutter", "tensorflow", "keras"
]

SECTION_KEYWORDS = {
    "education": ["education", "degree", "university", "college", "school", "b.tech", "m.tech", "bsc", "msc", "mba", "10th", "12th"],
    "experience": ["experience", "internship", "work", "job", "company", "organization", "employed"],
    "skills": ["skills", "technologies", "tools", "languages", "frameworks"],
    "projects": ["project", "developed", "built", "created", "implemented"],
    "achievements": ["achievement", "award", "certificate", "honor", "rank", "winner"],
    "contact": ["email", "phone", "mobile", "linkedin", "github", "address"],
}


def extract_text_from_pdf(file_bytes: bytes) -> str:
    import PyPDF2, io
    reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text.strip()


def extract_text_from_docx(file_bytes: bytes) -> str:
    import docx, io
    doc = docx.Document(io.BytesIO(file_bytes))
    return "\n".join([p.text for p in doc.paragraphs]).strip()


def extract_resume_text(uploaded_file) -> str:
    file_bytes = uploaded_file.read()
    filename = uploaded_file.name.lower()
    if filename.endswith(".pdf"):
        return extract_text_from_pdf(file_bytes)
    elif filename.endswith(".docx"):
        return extract_text_from_docx(file_bytes)
    elif filename.endswith(".txt"):
        return file_bytes.decode("utf-8", errors="ignore")
    else:
        raise ValueError(f"Unsupported file type: {uploaded_file.name}")


def analyze_resume(resume_text: str, job_description: str = None) -> dict:
    text_lower = resume_text.lower()
    lines = resume_text.strip().splitlines()
    non_empty = [l for l in lines if l.strip()]

    # --- Candidate Name (first non-empty line) ---
    candidate_name = non_empty[0].strip() if non_empty else "Unknown"

    # --- Contact Info ---
    email = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', resume_text)
    phone = re.search(r'(\+91[\s\-]?)?[6-9]\d{9}', resume_text)
    linkedin = re.search(r'linkedin\.com/in/[\w\-]+', resume_text, re.IGNORECASE)

    contact_info = {
        "email": email.group() if email else None,
        "phone": phone.group() if phone else None,
        "linkedin": linkedin.group() if linkedin else None,
    }

    # --- Sections Found ---
    sections_found = {}
    for section, keywords in SECTION_KEYWORDS.items():
        sections_found[section] = any(kw in text_lower for kw in keywords)

    # --- Skills Found ---
    found_skills = [skill for skill in COMMON_SKILLS if skill in text_lower]

    # --- Experience Years ---
    exp_match = re.search(r'(\d+)\+?\s*years?\s*(of\s*)?(experience|exp)', text_lower)
    experience_years = int(exp_match.group(1)) if exp_match else 0

    # --- Section Scores ---
    formatting_score = min(100, len(non_empty) * 2)
    formatting_score = max(30, min(formatting_score, 90))

    skills_score = min(100, len(found_skills) * 8)
    education_score = 80 if sections_found["education"] else 20
    experience_score = min(100, 40 + experience_years * 10) if sections_found["experience"] else 20
    achievements_score = 75 if sections_found["achievements"] else 30
    content_score = sum([
        20 if sections_found["experience"] else 0,
        20 if sections_found["education"] else 0,
        20 if sections_found["skills"] else 0,
        20 if sections_found["projects"] else 0,
        20 if sections_found["achievements"] else 0,
    ])

    section_scores = {
        "formatting": formatting_score,
        "content_quality": content_score,
        "skills_relevance": skills_score,
        "experience_depth": experience_score,
        "education": education_score,
        "achievements": achievements_score,
    }

    overall_score = int(sum(section_scores.values()) / len(section_scores))

    # --- ATS Score ---
    ats_score = 50
    if contact_info["email"]: ats_score += 10
    if contact_info["phone"]: ats_score += 10
    if sections_found["skills"]: ats_score += 10
    if sections_found["experience"]: ats_score += 10
    if len(found_skills) >= 5: ats_score += 10
    ats_score = min(ats_score, 100)

    ats_issues = []
    if not contact_info["email"]: ats_issues.append("Email address not found")
    if not contact_info["phone"]: ats_issues.append("Phone number not found")
    if not sections_found["skills"]: ats_issues.append("Skills section missing")
    if len(found_skills) < 3: ats_issues.append("Very few skills detected")

    # --- Strengths ---
    strengths = []
    if len(found_skills) >= 5: strengths.append(f"{len(found_skills)} relevant skills found")
    if sections_found["projects"]: strengths.append("Projects section present — good for freshers")
    if sections_found["achievements"]: strengths.append("Achievements/Certifications mentioned")
    if contact_info["email"] and contact_info["phone"]: strengths.append("Complete contact information provided")
    if experience_years > 2: strengths.append(f"{experience_years}+ years of experience")
    if not strengths: strengths.append("Resume has basic structure")

    # --- Weaknesses ---
    weaknesses = []
    if not sections_found["achievements"]: weaknesses.append("No achievements or certifications found")
    if len(found_skills) < 4: weaknesses.append("Too few skills listed")
    if not sections_found["projects"]: weaknesses.append("No projects section found")
    if not contact_info["linkedin"]: weaknesses.append("LinkedIn profile not mentioned")
    if len(non_empty) < 20: weaknesses.append("Resume seems too short")
    if not weaknesses: weaknesses.append("Minor formatting improvements possible")

    # --- Suggestions ---
    suggestions = []
    if not sections_found["achievements"]:
        suggestions.append({"priority": "High", "area": "Achievements", "suggestion": "Add certifications, awards, or academic achievements"})
    if len(found_skills) < 5:
        suggestions.append({"priority": "High", "area": "Skills", "suggestion": "Add more relevant technical and soft skills"})
    if not contact_info["linkedin"]:
        suggestions.append({"priority": "Medium", "area": "Contact", "suggestion": "Add your LinkedIn profile URL"})
    if not sections_found["projects"]:
        suggestions.append({"priority": "Medium", "area": "Projects", "suggestion": "Add a projects section with descriptions"})
    suggestions.append({"priority": "Low", "area": "Formatting", "suggestion": "Use consistent font and bullet points throughout"})

    # --- Career Level ---
    if experience_years == 0:
        career_level = "Fresher"
    elif experience_years <= 2:
        career_level = "Junior"
    elif experience_years <= 5:
        career_level = "Mid"
    elif experience_years <= 10:
        career_level = "Senior"
    else:
        career_level = "Lead/Expert"

    # --- Job Match (if JD provided) ---
    job_match_score = None
    matching_keywords = []
    missing_keywords = []
    job_match_summary = None

    if job_description and job_description.strip():
        jd_lower = job_description.lower()
        jd_words = set(re.findall(r'\b\w{4,}\b', jd_lower))
        resume_words = set(re.findall(r'\b\w{4,}\b', text_lower))
        matching_keywords = list(jd_words & resume_words)[:15]
        missing_keywords = list(jd_words - resume_words)[:15]
        match_ratio = len(matching_keywords) / max(len(jd_words), 1)
        job_match_score = min(100, int(match_ratio * 200))
        job_match_summary = f"Resume matches {job_match_score}% of job description keywords."

    return {
        "candidate_name": candidate_name,
        "contact_info": contact_info,
        "overall_score": overall_score,
        "section_scores": section_scores,
        "experience_years": experience_years,
        "current_role": None,
        "top_skills": found_skills[:8],
        "strengths": strengths[:4],
        "weaknesses": weaknesses[:4],
        "suggestions": suggestions[:5],
        "ats_score": ats_score,
        "ats_issues": ats_issues,
        "career_level": career_level,
        "recommended_roles": [],
        "summary": f"Resume analyzed. {len(found_skills)} skills found. Career level: {career_level}.",
        "job_match_score": job_match_score,
        "matching_keywords": matching_keywords,
        "missing_keywords": missing_keywords,
        "job_match_summary": job_match_summary,
    }


def score_label(score: int) -> tuple:
    if score >= 85:
        return "Excellent", "#00C896"
    elif score >= 70:
        return "Good", "#4A9EFF"
    elif score >= 50:
        return "Average", "#FFB347"
    else:
        return "Needs Work", "#FF6B6B"
