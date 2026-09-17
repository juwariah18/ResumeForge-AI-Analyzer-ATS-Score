import re

SKILLS = [
    "python", "java", "c", "c++", "c#", "javascript", "typescript", "sql",
    "html", "css", "react", "node.js", "flask", "django", "pandas", "numpy",
    "power bi", "tableau", "excel", "machine learning", "deep learning", "nlp",
    "git", "github", "docker", "aws", "azure", "mongodb", "mysql",
    "postgresql", "tensorflow", "pytorch", "communication", "leadership",
    "teamwork", "problem solving"
]

SECTION_NAMES = {
    "summary": ["summary", "objective", "profile"],
    "education": ["education", "academic"],
    "experience": ["experience", "employment", "work history"],
    "projects": ["projects", "project"],
    "skills": ["skills", "technical skills"],
    "certifications": ["certifications", "certificates"],
    "achievements": ["achievements", "awards"],
}

SECTION_ALIASES = {
    "summary": {"summary", "objective", "profile", "professional summary", "about me"},
    "education": {"education", "academic", "academic background"},
    "experience": {"experience", "employment", "work history", "professional experience"},
    "projects": {"projects", "project", "personal projects", "academic projects"},
    "skills": {"skills", "technical skills", "technologies", "core skills"},
    "certifications": {"certifications", "certificates", "courses"},
    "achievements": {"achievements", "awards", "honors"},
    "languages": {"languages", "language"},
    "links": {"websites portfolios profiles", "links", "professional links"},
    "soft_skills": {"core strengths", "strengths"},
}


def find_skills(text):
    low = text.lower()
    found = []
    for skill in SKILLS:
        if re.search(r"(?<![a-z0-9])" + re.escape(skill) + r"(?![a-z0-9])", low):
            found.append(skill.title() if skill not in {"c++", "c#", "node.js", "power bi", "nlp"} else skill.upper())
    return sorted(set(found))


def _clean_line(line):
    return re.sub(r"^[\u2022*\-\u2013\u2014\s]+", "", line).strip()


def _section_blocks(lines):
    blocks = {}
    current = None
    for line in lines:
        normalized = re.sub(r"[^a-z ]", "", line.lower()).strip()
        matched = next((key for key, aliases in SECTION_ALIASES.items() if normalized in aliases), None)
        if matched:
            current = matched
            blocks.setdefault(current, [])
        elif current:
            blocks[current].append(_clean_line(line))
    return {key: [line for line in value if line] for key, value in blocks.items()}


def _lines_as_items(lines):
    return [_clean_line(line) for line in lines if _clean_line(line)]


def _label_value(text, label):
    match = re.search(r"(?im)^\s*" + re.escape(label) + r"\s*[:|-]\s*(.+?)\s*$", text)
    return match.group(1).strip() if match else ""


def _full_url(value, kind=None):
    value = value.strip().rstrip(".,;)")
    if not value:
        return ""
    if re.match(r"^https?://", value, re.I):
        return value
    if kind == "linkedin" and re.match(r"(?:www\.)?linkedin\.com/", value, re.I):
        return "https://" + value
    if kind == "github" and re.match(r"(?:www\.)?github\.com/", value, re.I):
        return "https://" + value
    return value


def _parse_education(lines):
    items = []
    clean_lines = _lines_as_items(lines)
    degree_pattern = re.compile(r"^(?:b\.?tech|b\.?e|bachelor|m\.?tech|m\.?e|master|intermediate|schooling|high school|diploma)\b", re.I)
    index = 0
    while index < len(clean_lines):
        if not degree_pattern.search(clean_lines[index]):
            index += 1
            continue
        degree = clean_lines[index]
        college = clean_lines[index + 1] if index + 1 < len(clean_lines) else ""
        detail = clean_lines[index + 2] if index + 2 < len(clean_lines) and not degree_pattern.search(clean_lines[index + 2]) else ""
        years = re.findall(r"(?:19|20)\d{2}", detail)
        score_match = re.search(r"(?:GPA|CGPA|CPA|percentage)\s*[:.]?\s*([\d.]+)", detail, re.I)
        items.append({"degree": degree, "college": college, "start": "", "end": years[-1] if years else "", "score": score_match.group(1) if score_match else ""})
        index += 3 if detail else 2
    return items


def _parse_experience(lines):
    items = []
    for line in _lines_as_items(lines):
        years = re.findall(r"(?:19|20)\d{2}", line)
        parts = [part.strip() for part in re.split(r"\s+[|,-]\s+", line) if part.strip()]
        role = parts[0] if parts else line
        company = parts[1] if len(parts) > 1 else ""
        items.append({"role": role, "company": company, "start": years[0] if years else "", "end": years[1] if len(years) > 1 else "", "description": ""})
    return items


def _parse_projects(lines):
    clean_lines = _lines_as_items(lines)
    if not clean_lines:
        return []
    first = re.split(r"\s*(?:\||:)\s*", clean_lines[0], maxsplit=1)
    name = first[0].strip()
    remainder = first[1].strip() if len(first) > 1 else ""
    continuation = " ".join(clean_lines[1:]).strip()
    full_description = " ".join(part for part in [remainder, continuation] if part)
    tech_match = re.match(r"(.+?),\s*(Developed|Built|Created|Designed|Implemented)\b(.*)", full_description, re.I)
    technologies = tech_match.group(1).strip() if tech_match else ""
    description = (tech_match.group(2) + tech_match.group(3)).strip() if tech_match else full_description
    return [{"name": name, "description": description, "technologies": technologies, "link": ""}]


def _split_labeled_items(lines):
    items = []
    for line in _lines_as_items(lines):
        value = line.split(":", 1)[1] if ":" in line else line
        items.extend(part.strip() for part in re.split(r"[,|]", value) if part.strip())
    return items


def _clean_terminal_items(items):
    return [item for item in items if item.strip().upper() not in {"DONE", "END", "THE END"}]


def extract_resume_data(text):
    text = text or ""
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    blocks = _section_blocks(lines)
    email_match = re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)
    phone_match = re.search(r"(?:\+?\d[\d\s().-]{7,}\d)", text)
    phone_digits = re.sub(r"\D", "", phone_match.group(0)) if phone_match else ""
    phone = phone_digits[-10:] if len(phone_digits) >= 10 else phone_digits
    links = re.findall(r"https?://[^\s,|]+|(?:www\.)?(?:linkedin\.com|github\.com)/[^\s,|]+", text, re.I)
    full_links = [_full_url(link, "linkedin" if "linkedin.com" in link.lower() else "github" if "github.com" in link.lower() else None) for link in links]
    linkedin = next((link for link in full_links if "linkedin.com" in link.lower()), "")
    github = next((link for link in full_links if "github.com" in link.lower()), "")
    portfolio = next((link for link in full_links if link not in {linkedin, github}), "")
    first_line = lines[0] if lines and "@" not in lines[0] and not re.search(r"\d", lines[0]) else ""
    summary_lines = blocks.get("summary", [])
    labeled_location = _label_value(text, "location")
    city = _label_value(text, "city")
    state = _label_value(text, "state")
    country = _label_value(text, "country")
    title = _label_value(text, "title") or _label_value(text, "professional title")
    summary = " ".join(summary_lines)
    if not title:
        title_match = re.search(r"grow as a ([A-Za-z &/]+?) professional", summary, re.I)
        title = title_match.group(1).strip() if title_match else ""
    contact_location = next((line for line in lines[1:5] if re.search(r"\b\d{5,6}\b", line) and not re.search(r"@|\+?\d[\d\s().-]{7,}\d", line)), "")
    if not labeled_location and contact_location:
        labeled_location = contact_location
    if not city and contact_location:
        city = re.sub(r"\s+\d{5,6}\b", "", contact_location).strip()
    parsed_skills = _split_labeled_items(blocks.get("skills", []))
    soft_skills = _split_labeled_items(blocks.get("soft_skills", []))
    data = {
        "full_name": first_line,
        "email": email_match.group(0) if email_match else "",
        "phone": phone,
        "professional_title": title,
        "custom_title": "",
        "country": country,
        "state": state,
        "city": city,
        "location": labeled_location,
        "linkedin": linkedin,
        "github": github,
        "portfolio": portfolio,
        "summary": summary,
        "skills": parsed_skills or find_skills(text),
        "education": _parse_education(blocks.get("education", [])),
        "experience": _parse_experience(blocks.get("experience", [])),
        "projects": _parse_projects(blocks.get("projects", [])),
        "certifications": _clean_terminal_items(_lines_as_items(blocks.get("certifications", []))),
        "achievements": _clean_terminal_items(_lines_as_items(blocks.get("achievements", []))),
        "languages": _clean_terminal_items(_lines_as_items(blocks.get("languages", []))),
        "soft_skills": soft_skills or [skill for skill in find_skills(text) if skill.lower() in {"communication", "leadership", "teamwork", "problem solving"}],
        "links": list(dict.fromkeys(full_links)),
        "raw_text": text,
    }
    return data


def analyze_resume(text):
    text = text or ""
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    email = re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)
    phone = re.search(r"(?:\+?\d[\d\s().-]{7,}\d)", text)
    skills = find_skills(text)
    low = text.lower()
    sections = [name for name, words in SECTION_NAMES.items() if any(word in low for word in words)]
    name = lines[0] if lines and "@" not in lines[0] else ""
    section_score = min(len(sections) / 6, 1.0) * 35
    skill_score = min(len(skills) / 10, 1.0) * 35
    contact_score = (15 if email else 0) + (15 if phone else 0)
    score = round(min(100, section_score + skill_score + contact_score))
    return {
        "name": name,
        "email": email.group(0) if email else "",
        "phone": re.sub(r"\D", "", phone.group(0))[-10:] if phone else "",
        "skills": skills,
        "sections_found": sections,
        "resume_score": score,
        "ats_score": max(0, min(100, score - (5 if len(text) < 300 else 0))),
    }
