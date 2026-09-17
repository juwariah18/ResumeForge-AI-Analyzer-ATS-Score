from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .analyzer import find_skills


def match_resume_to_job(resume_text, job_text):
    resume_text = resume_text or ""
    job_text = job_text or ""
    if not job_text.strip():
        return {"score": 0, "matched": [], "missing": [], "similarity": 0}

    resume_skills = set(find_skills(resume_text))
    job_skills = set(find_skills(job_text))
    matched = sorted(resume_skills & job_skills)
    missing = sorted(job_skills - resume_skills)

    try:
        vectors = TfidfVectorizer(stop_words="english").fit_transform([resume_text, job_text])
        similarity = float(cosine_similarity(vectors[0:1], vectors[1:2])[0][0])
    except ValueError:
        similarity = 0.0

    skill_score = len(matched) / len(job_skills) if job_skills else similarity
    score = round((skill_score * 0.7 + similarity * 0.3) * 100)
    return {"score": min(100, score), "matched": matched, "missing": missing, "similarity": round(similarity * 100)}
