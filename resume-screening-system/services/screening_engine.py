import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def clean_skill_list(skills_input):
    if not skills_input:
        return []
    if isinstance(skills_input, list):
        items = skills_input
    else:
        items = re.split(r'[,;\n]+', str(skills_input))
    
    cleaned = []
    for item in items:
        s = item.strip()
        if s and s not in cleaned:
            cleaned.append(s)
    return cleaned

def match_skills(target_skills, candidate_skills, raw_text=""):
    matched = []
    missing = []
    
    cand_skills_lower = {s.lower(): s for s in candidate_skills}
    text_lower = raw_text.lower() if raw_text else ""
    
    for skill in target_skills:
        s_clean = skill.strip()
        if not s_clean:
            continue
        s_lower = s_clean.lower()
        
        # Check in extracted candidate skills
        if s_lower in cand_skills_lower:
            matched.append(s_clean)
            continue
            
        # Check in raw text with boundary check
        if s_clean in ["C", "R"]:
            pattern = rf'(?<![a-zA-Z0-9]){re.escape(s_clean)}(?![a-zA-Z0-9+#])'
            found = bool(re.search(pattern, raw_text))
        elif s_clean in ["C++", "C#", ".NET"]:
            pattern = rf'(?<![a-zA-Z0-9]){re.escape(s_clean)}(?![a-zA-Z0-9])'
            found = bool(re.search(pattern, raw_text, re.IGNORECASE))
        else:
            pattern = rf'\b{re.escape(s_lower)}\b'
            found = bool(re.search(pattern, text_lower))
            
        if found:
            matched.append(s_clean)
        else:
            missing.append(s_clean)
            
    return matched, missing

def calculate_tfidf_similarity(job_text, resume_text):
    if not job_text.strip() or not resume_text.strip():
        return 50.0
    try:
        vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2), max_features=1000)
        tfidf_matrix = vectorizer.fit_transform([job_text, resume_text])
        sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        # Normalize and scale to percentage: cosine sim typically ranges 0.1 - 0.7 for text
        # We apply a slight sigmoid/linear boost for ATS realism
        score = float(sim) * 100.0
        # Boost low values smoothly so standard matching works reasonably
        scaled_score = min(100.0, score * 1.5)
        return round(scaled_score, 1)
    except Exception as e:
        print(f"TF-IDF calculation error: {e}")
        return 50.0

def calculate_experience_score(candidate_exp, min_required_exp):
    try:
        cand_exp = float(candidate_exp or 0)
        req_exp = float(min_required_exp or 0)
    except (ValueError, TypeError):
        return 100.0
        
    if req_exp <= 0:
        return 100.0
        
    if cand_exp >= req_exp:
        return 100.0
    
    score = (cand_exp / req_exp) * 100.0
    return round(max(0.0, min(100.0, score)), 1)

def screen_resume(candidate_data, job_data):
    """
    Computes a transparent 0-100% match score using:
    - Required skill matching (35%)
    - Preferred skill matching (15%)
    - TF-IDF + Cosine similarity (30%)
    - Experience matching (20%)
    """
    req_skills = clean_skill_list(job_data.get('required_skills', ''))
    pref_skills = clean_skill_list(job_data.get('preferred_skills', ''))
    min_exp = float(job_data.get('min_experience', 0) or 0)
    
    cand_skills = candidate_data.get('extracted_skills', [])
    if isinstance(cand_skills, str):
        try:
            import json
            cand_skills = json.loads(cand_skills)
        except Exception:
            cand_skills = clean_skill_list(cand_skills)

    raw_text = candidate_data.get('raw_resume_text', '')
    cand_exp = float(candidate_data.get('experience_years', 0) or 0)
    
    # 1. Required Skills Matching (35%)
    matched_req, missing_req = match_skills(req_skills, cand_skills, raw_text)
    if req_skills:
        req_score = round((len(matched_req) / len(req_skills)) * 100.0, 1)
    else:
        req_score = 100.0
        
    # 2. Preferred Skills Matching (15%)
    matched_pref, missing_pref = match_skills(pref_skills, cand_skills, raw_text)
    if pref_skills:
        pref_score = round((len(matched_pref) / len(pref_skills)) * 100.0, 1)
    else:
        pref_score = 100.0
        
    # 3. TF-IDF + Cosine Similarity (30%)
    job_full_text = f"{job_data.get('title', '')} {job_data.get('description', '')} {' '.join(req_skills)} {' '.join(pref_skills)}"
    resume_full_text = f"{raw_text} {' '.join(cand_skills)}"
    tfidf_score = calculate_tfidf_similarity(job_full_text, resume_full_text)
    
    # 4. Experience Matching (20%)
    exp_score = calculate_experience_score(cand_exp, min_exp)
    
    # Weighted Composite Score (0 - 100%)
    total_score = round(
        (0.35 * req_score) +
        (0.15 * pref_score) +
        (0.30 * tfidf_score) +
        (0.20 * exp_score),
        1
    )
    total_score = max(0.0, min(100.0, total_score))
    
    # Recommendation
    if total_score >= 80.0:
        recommendation = "Strong Match"
    elif total_score >= 60.0:
        recommendation = "Moderate Match"
    else:
        recommendation = "Low Match"
        
    return {
        "total_score": total_score,
        "required_skills_score": req_score,
        "preferred_skills_score": pref_score,
        "tfidf_score": tfidf_score,
        "experience_score": exp_score,
        "matched_skills": matched_req,
        "missing_skills": missing_req,
        "matched_preferred": matched_pref,
        "missing_preferred": missing_pref,
        "recommendation": recommendation,
        "weights": {
            "required_skills": 35,
            "preferred_skills": 15,
            "tfidf_cosine": 30,
            "experience": 20
        }
    }
