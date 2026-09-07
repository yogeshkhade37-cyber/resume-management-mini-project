import sqlite3
import os
import json
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resume_screening.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db(seed=True):
    conn = get_db()
    cursor = conn.cursor()
    
    # Jobs Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        company TEXT NOT NULL,
        description TEXT NOT NULL,
        required_skills TEXT NOT NULL,
        preferred_skills TEXT DEFAULT '',
        min_experience REAL DEFAULT 0,
        is_active INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Candidates Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS candidates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT,
        phone TEXT,
        extracted_skills TEXT,
        education TEXT,
        experience_years REAL DEFAULT 0,
        experience_details TEXT,
        certifications TEXT,
        projects TEXT,
        raw_resume_text TEXT,
        resume_filename TEXT,
        resume_filepath TEXT,
        status TEXT DEFAULT 'Under Review',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Screening Results Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS screening_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        candidate_id INTEGER NOT NULL,
        job_id INTEGER NOT NULL,
        total_score REAL NOT NULL,
        required_skills_score REAL NOT NULL,
        preferred_skills_score REAL NOT NULL,
        tfidf_score REAL NOT NULL,
        experience_score REAL NOT NULL,
        matched_skills TEXT,
        missing_skills TEXT,
        matched_preferred TEXT,
        missing_preferred TEXT,
        recommendation TEXT NOT NULL,
        screened_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (candidate_id) REFERENCES candidates (id) ON DELETE CASCADE,
        FOREIGN KEY (job_id) REFERENCES jobs (id) ON DELETE CASCADE,
        UNIQUE(candidate_id, job_id)
    )
    ''')
    conn.commit()

    # Check if empty, then seed sample data
    cursor.execute("SELECT COUNT(*) as count FROM jobs")
    job_count = cursor.fetchone()['count']
    if job_count == 0 and seed:
        seed_sample_data(conn)

    conn.close()

def seed_sample_data(conn=None):
    close_at_end = False
    if conn is None:
        conn = get_db()
        close_at_end = True

    cursor = conn.cursor()
    cursor.execute("DELETE FROM screening_results")
    cursor.execute("DELETE FROM candidates")
    cursor.execute("DELETE FROM jobs")

    sample_jobs = [
        (
            "Full Stack Python Developer",
            "TechSphere Solutions",
            "We are seeking a talented Full Stack Python Developer with expertise in Flask/Django, modern JavaScript, REST APIs, and database architecture to build scalable web applications.",
            "Python, Flask, JavaScript, SQL, HTML, CSS, REST APIs, Git",
            "Docker, React, PostgreSQL, TailwindCSS, Redis, AWS",
            2.0,
            1
        ),
        (
            "Machine Learning Engineer",
            "DataMind AI Labs",
            "Looking for an ML Engineer to design, train, and deploy predictive models, NLP pipelines, and computer vision systems. Strong Python and scikit-learn experience required.",
            "Python, Machine Learning, scikit-learn, Pandas, NumPy, SQL, Git",
            "TensorFlow, PyTorch, Docker, NLP, MLOps, AWS, Deep Learning",
            2.5,
            0
        ),
        (
            "Frontend Web Developer",
            "PixelCraft Studio",
            "Join our creative team crafting high-performance, accessible, and responsive user interfaces using modern JavaScript frameworks, CSS3, and web optimization techniques.",
            "JavaScript, HTML5, CSS3, React, Responsive Design, Git",
            "TypeScript, Next.js, Redux, Figma, Webpack, TailwindCSS",
            1.5,
            0
        )
    ]

    cursor.executemany('''
    INSERT INTO jobs (title, company, description, required_skills, preferred_skills, min_experience, is_active)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', sample_jobs)

    job1_id = 1
    job2_id = 2

    sample_candidates = [
        (
            "Aarav Sharma",
            "aarav.sharma@example.com",
            "+91 98765 43210",
            json.dumps(["Python", "Flask", "JavaScript", "SQL", "HTML", "CSS", "REST APIs", "Git", "Docker", "PostgreSQL"]),
            "B.Tech in Computer Science, National Institute of Technology (2020-2024)",
            3.0,
            "Full Stack Developer at NexaGen (2 yrs) - Developed scalable REST APIs using Flask and PostgreSQL. Frontend interfaces built with responsive HTML5/CSS and modern JavaScript.",
            json.dumps(["AWS Certified Developer - Associate", "Python Institute PCAP"]),
            json.dumps(["E-Commerce Microservices Platform (Flask, Docker, Redis)", "ATS Resume Screening Tool"]),
            "Experienced Python Full Stack Developer with 3 years building web apps using Flask, JavaScript, PostgreSQL, REST APIs, and Docker.",
            "aarav_sharma_resume.pdf",
            "",
            "Shortlisted"
        ),
        (
            "Priya Patel",
            "priya.patel@example.com",
            "+91 98234 56789",
            json.dumps(["Python", "Flask", "SQL", "HTML", "Git", "Pandas", "JavaScript"]),
            "B.E. in Information Technology, Mumbai University (2021-2025)",
            1.5,
            "Junior Web Developer at SoftPulse Technologies (1.5 yrs) - Created internal dashboards with Python Flask and vanilla JavaScript, integrated SQL queries.",
            json.dumps(["Meta Front-End Developer Certificate"]),
            json.dumps(["Hospital Patient Record Management System (Python, SQLite, Bootstrap)"]),
            "Junior developer proficient in Python, Flask, SQL, HTML, and basic JavaScript. Passionate about clean code and modern web design.",
            "priya_patel_resume.pdf",
            "",
            "Under Review"
        ),
        (
            "Rohan Verma",
            "rohan.verma@example.com",
            "+91 97112 34567",
            json.dumps(["Python", "Machine Learning", "scikit-learn", "Pandas", "NumPy", "SQL", "Git", "NLP", "TensorFlow"]),
            "M.Tech in Artificial Intelligence & Data Science, IIT Bombay (2022-2024)",
            3.5,
            "ML Research Assistant & Engineer at DataLabs (3.5 yrs) - Developed NLP classification algorithms and scikit-learn predictive models.",
            json.dumps(["DeepLearning.AI TensorFlow Specialization", "AWS Machine Learning Specialty"]),
            json.dumps(["Automated Medical Text Summarizer (NLP, Python, PyTorch)", "Customer Churn Prediction Engine"]),
            "Machine Learning Engineer with 3.5 years experience in scikit-learn, NLP, predictive analytics, NumPy, Pandas, and Python pipelines.",
            "rohan_verma_resume.pdf",
            "",
            "Under Review"
        ),
        (
            "Sneha Kulkarni",
            "sneha.kulkarni@example.com",
            "+91 99345 67890",
            json.dumps(["HTML", "CSS", "Photoshop", "Canva", "WordPress", "UI/UX Design"]),
            "Bachelor of Fine Arts & Multimedia (2020-2023)",
            0.5,
            "Graphic & UI Design Intern at StudioBlue (6 months) - Created web banners, WordPress landing pages, and UI mockups.",
            json.dumps(["Google UX Design Professional Certificate"]),
            json.dumps(["Portfolio Website Redesign (HTML/CSS)", "Brand Identity Kit"]),
            "Creative UI Designer with knowledge of HTML, CSS, Figma, and WordPress. Looking to transition into development.",
            "sneha_kulkarni_resume.docx",
            "",
            "Rejected"
        ),
        (
            "Vikram Sengupta",
            "vikram.sengupta@example.com",
            "+91 98450 12345",
            json.dumps(["Python", "Flask", "REST APIs", "SQL", "JavaScript", "HTML", "CSS", "React", "Git"]),
            "B.Sc in Computer Science, Delhi University (2019-2022)",
            2.5,
            "Software Engineer at CloudNine Info (2.5 yrs) - Built responsive client dashboards using React and Flask REST APIs. Handled relational database schemas.",
            json.dumps(["Certified Scrum Master (CSM)", "GitHub Foundations"]),
            json.dumps(["Real-Time Chat Application (React, Flask-SocketIO)", "Inventory Tracker"]),
            "Full stack engineer with 2.5 years experience in Python, Flask, React, and REST API development. Strong collaborator and agile enthusiast.",
            "vikram_sengupta_resume.pdf",
            "",
            "Shortlisted"
        ),
        (
            "Ananya Deshmukh",
            "ananya.d@example.com",
            "+91 91234 87654",
            json.dumps(["JavaScript", "HTML5", "CSS3", "React", "Git", "Figma", "Bootstrap"]),
            "B.Tech in Computer Engineering, Pune University (2021-2025)",
            1.0,
            "Frontend Intern at WebWorks (1 yr) - Developed clean UI components in React and optimized CSS stylesheets.",
            json.dumps(["FreeCodeCamp Responsive Web Design"]),
            json.dumps(["Task Management Kanban Board (React, LocalStorage)"]),
            "Frontend developer enthusiastic about crafting clean responsive web applications with React, HTML5, CSS3, and JavaScript.",
            "ananya_resume.pdf",
            "",
            "Under Review"
        )
    ]

    for cand in sample_candidates:
        cursor.execute('''
        INSERT INTO candidates (
            name, email, phone, extracted_skills, education, experience_years,
            experience_details, certifications, projects, raw_resume_text,
            resume_filename, resume_filepath, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', cand)

    sample_screenings = [
        # Aarav Sharma vs Job 1 (Full Stack)
        (1, 1, 92.5, 100.0, 66.7, 95.0, 100.0,
         json.dumps(["Python", "Flask", "JavaScript", "SQL", "HTML", "CSS", "REST APIs", "Git"]),
         json.dumps([]),
         json.dumps(["Docker", "PostgreSQL"]),
         json.dumps(["React", "TailwindCSS", "Redis", "AWS"]),
         "Strong Match"),
        # Priya Patel vs Job 1 (Full Stack)
        (2, 1, 69.8, 75.0, 0.0, 78.0, 75.0,
         json.dumps(["Python", "Flask", "SQL", "HTML", "Git", "JavaScript"]),
         json.dumps(["CSS", "REST APIs"]),
         json.dumps([]),
         json.dumps(["Docker", "React", "PostgreSQL", "TailwindCSS", "Redis", "AWS"]),
         "Moderate Match"),
        # Rohan Verma vs Job 1 (Full Stack)
        (3, 1, 51.2, 37.5, 0.0, 62.0, 100.0,
         json.dumps(["Python", "SQL", "Git"]),
         json.dumps(["Flask", "JavaScript", "HTML", "CSS", "REST APIs"]),
         json.dumps([]),
         json.dumps(["Docker", "React", "PostgreSQL", "TailwindCSS", "Redis", "AWS"]),
         "Low Match"),
        # Sneha Kulkarni vs Job 1 (Full Stack)
        (4, 1, 28.5, 25.0, 0.0, 32.0, 25.0,
         json.dumps(["HTML", "CSS"]),
         json.dumps(["Python", "Flask", "JavaScript", "SQL", "REST APIs", "Git"]),
         json.dumps([]),
         json.dumps(["Docker", "React", "PostgreSQL", "TailwindCSS", "Redis", "AWS"]),
         "Low Match"),
        # Vikram Sengupta vs Job 1 (Full Stack)
        (5, 1, 88.0, 100.0, 33.3, 87.0, 100.0,
         json.dumps(["Python", "Flask", "JavaScript", "SQL", "HTML", "CSS", "REST APIs", "Git"]),
         json.dumps([]),
         json.dumps(["React"]),
         json.dumps(["Docker", "PostgreSQL", "TailwindCSS", "Redis", "AWS"]),
         "Strong Match"),
        # Ananya Deshmukh vs Job 1 (Full Stack)
        (6, 1, 46.5, 50.0, 0.0, 52.0, 50.0,
         json.dumps(["JavaScript", "HTML", "CSS", "Git"]),
         json.dumps(["Python", "Flask", "SQL", "REST APIs"]),
         json.dumps([]),
         json.dumps(["Docker", "React", "PostgreSQL", "TailwindCSS", "Redis", "AWS"]),
         "Low Match")
    ]

    cursor.executemany('''
    INSERT INTO screening_results (
        candidate_id, job_id, total_score, required_skills_score,
        preferred_skills_score, tfidf_score, experience_score,
        matched_skills, missing_skills, matched_preferred, missing_preferred,
        recommendation
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', sample_screenings)

    conn.commit()
    if close_at_end:
        conn.close()

def get_active_job():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM jobs WHERE is_active = 1 LIMIT 1")
    job = cursor.fetchone()
    if not job:
        cursor.execute("SELECT * FROM jobs ORDER BY id ASC LIMIT 1")
        job = cursor.fetchone()
    conn.close()
    return job

def set_active_job(job_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE jobs SET is_active = 0")
    cursor.execute("UPDATE jobs SET is_active = 1 WHERE id = ?", (job_id,))
    conn.commit()
    conn.close()

def get_all_jobs():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM jobs ORDER BY created_at DESC")
    jobs = cursor.fetchall()
    conn.close()
    return jobs

def get_job_by_id(job_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM jobs WHERE id = ?", (job_id,))
    job = cursor.fetchone()
    conn.close()
    return job

def insert_job(title, company, description, required_skills, preferred_skills, min_experience, make_active=False):
    conn = get_db()
    cursor = conn.cursor()
    if make_active:
        cursor.execute("UPDATE jobs SET is_active = 0")
    is_active = 1 if make_active else 0
    cursor.execute('''
    INSERT INTO jobs (title, company, description, required_skills, preferred_skills, min_experience, is_active)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (title, company, description, required_skills, preferred_skills, min_experience, is_active))
    job_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return job_id

def insert_candidate(name, email, phone, extracted_skills, education, experience_years,
                     experience_details, certifications, projects, raw_resume_text,
                     resume_filename, resume_filepath):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO candidates (
        name, email, phone, extracted_skills, education, experience_years,
        experience_details, certifications, projects, raw_resume_text,
        resume_filename, resume_filepath, status
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Under Review')
    ''', (
        name, email, phone,
        json.dumps(extracted_skills) if isinstance(extracted_skills, list) else extracted_skills,
        json.dumps(education) if isinstance(education, list) else education,
        experience_years,
        experience_details,
        json.dumps(certifications) if isinstance(certifications, list) else certifications,
        json.dumps(projects) if isinstance(projects, list) else projects,
        raw_resume_text,
        resume_filename,
        resume_filepath
    ))
    candidate_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return candidate_id

def save_screening_result(candidate_id, job_id, total_score, req_score, pref_score,
                          tfidf_score, exp_score, matched_req, missing_req,
                          matched_pref, missing_pref, recommendation):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO screening_results (
        candidate_id, job_id, total_score, required_skills_score,
        preferred_skills_score, tfidf_score, experience_score,
        matched_skills, missing_skills, matched_preferred, missing_preferred,
        recommendation
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ON CONFLICT(candidate_id, job_id) DO UPDATE SET
        total_score=excluded.total_score,
        required_skills_score=excluded.required_skills_score,
        preferred_skills_score=excluded.preferred_skills_score,
        tfidf_score=excluded.tfidf_score,
        experience_score=excluded.experience_score,
        matched_skills=excluded.matched_skills,
        missing_skills=excluded.missing_skills,
        matched_preferred=excluded.matched_preferred,
        missing_preferred=excluded.missing_preferred,
        recommendation=excluded.recommendation,
        screened_at=CURRENT_TIMESTAMP
    ''', (
        candidate_id, job_id, total_score, req_score, pref_score,
        tfidf_score, exp_score,
        json.dumps(matched_req), json.dumps(missing_req),
        json.dumps(matched_pref), json.dumps(missing_pref),
        recommendation
    ))
    conn.commit()
    conn.close()

def get_candidate_detail(candidate_id, job_id=None):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM candidates WHERE id = ?", (candidate_id,))
    candidate = cursor.fetchone()
    if not candidate:
        conn.close()
        return None, None

    screening = None
    if job_id:
        cursor.execute("SELECT * FROM screening_results WHERE candidate_id = ? AND job_id = ?", (candidate_id, job_id))
        screening = cursor.fetchone()
    else:
        cursor.execute("SELECT * FROM screening_results WHERE candidate_id = ? ORDER BY total_score DESC LIMIT 1", (candidate_id,))
        screening = cursor.fetchone()

    conn.close()
    return candidate, screening

def update_candidate_status(candidate_id, new_status):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE candidates SET status = ? WHERE id = ?", (new_status, candidate_id))
    conn.commit()
    conn.close()

def delete_candidate(candidate_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM candidates WHERE id = ?", (candidate_id,))
    conn.commit()
    conn.close()

def get_dashboard_stats(job_id=None):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) as count FROM candidates")
    total_resumes = cursor.fetchone()['count']

    cursor.execute("SELECT COUNT(*) as count FROM candidates WHERE status = 'Shortlisted'")
    shortlisted = cursor.fetchone()['count']

    cursor.execute("SELECT COUNT(*) as count FROM candidates WHERE status = 'Under Review'")
    under_review = cursor.fetchone()['count']

    cursor.execute("SELECT COUNT(*) as count FROM candidates WHERE status = 'Rejected'")
    rejected = cursor.fetchone()['count']

    if job_id:
        cursor.execute("SELECT AVG(total_score) as avg_score FROM screening_results WHERE job_id = ?", (job_id,))
    else:
        cursor.execute("SELECT AVG(total_score) as avg_score FROM screening_results")
    avg_row = cursor.fetchone()
    avg_score = round(avg_row['avg_score'], 1) if avg_row and avg_row['avg_score'] is not None else 0.0

    conn.close()
    return {
        "total_resumes": total_resumes,
        "shortlisted": shortlisted,
        "under_review": under_review,
        "rejected": rejected,
        "avg_score": avg_score
    }

def get_candidates_list(job_id=None, status=None, tier=None, search=None, sort=None):
    conn = get_db()
    cursor = conn.cursor()

    query = '''
    SELECT c.*, 
           sr.total_score, sr.required_skills_score, sr.preferred_skills_score,
           sr.tfidf_score, sr.experience_score, sr.recommendation,
           sr.matched_skills, sr.missing_skills,
           j.title as job_title
    FROM candidates c
    LEFT JOIN screening_results sr ON c.id = sr.candidate_id AND sr.job_id = ?
    LEFT JOIN jobs j ON j.id = ?
    WHERE 1=1
    '''
    params = [job_id, job_id]

    if status and status != 'All':
        query += " AND c.status = ?"
        params.append(status)

    if tier and tier != 'All':
        if tier == 'Strong':
            query += " AND sr.total_score >= 80"
        elif tier == 'Moderate':
            query += " AND sr.total_score >= 60 AND sr.total_score < 80"
        elif tier == 'Low':
            query += " AND (sr.total_score < 60 OR sr.total_score IS NULL)"

    if search:
        query += " AND (c.name LIKE ? OR c.email LIKE ? OR c.extracted_skills LIKE ?)"
        search_pattern = f"%{search}%"
        params.extend([search_pattern, search_pattern, search_pattern])

    if sort == 'score_desc':
        query += " ORDER BY COALESCE(sr.total_score, -1) DESC, c.id DESC"
    elif sort == 'score_asc':
        query += " ORDER BY COALESCE(sr.total_score, -1) ASC, c.id DESC"
    elif sort == 'name_asc':
        query += " ORDER BY c.name ASC"
    elif sort == 'name_desc':
        query += " ORDER BY c.name DESC"
    elif sort == 'exp_desc':
        query += " ORDER BY c.experience_years DESC"
    else:
        # default: highest match first
        query += " ORDER BY COALESCE(sr.total_score, -1) DESC, c.id DESC"

    cursor.execute(query, tuple(params))
    candidates = cursor.fetchall()
    conn.close()
    return candidates
