# AI-Powered Resume Screening & Ranking System (ATS)
### College Mini Project

A complete, modern, ATS-style recruitment and candidate screening web application built with **Python Flask**, **SQLite**, **HTML5/CSS3/JavaScript**, and **scikit-learn** (TF-IDF vectorization & Cosine Similarity).

---

## 📌 Important Disclaimer

> **“This system is a college-project decision-support tool and should not be used as the sole basis for hiring decisions.”**
> 
> The application is designed to aid recruiters and HR personnel in prioritizing candidate applications through transparent NLP matching and heuristic skill extraction. Final employment decisions should always involve comprehensive human evaluation and personal interviews.

---

## 🌟 Key Features

1. **Recruiter Dashboard**
   - Live metrics: Total Resumes, Shortlisted, Under Review, Rejected, and Average Match Score.
   - Quick Active Job Switcher.
   - Candidate Ranking Leaderboard sorted by algorithm match percentage.
   - Match tier breakdown (Strong, Moderate, Low).

2. **Job Description Management**
   - Create, customize, and store job openings.
   - Configure Job Title, Company, Required Skills (Weight: 35%), Preferred Skills (Weight: 15%), Minimum Experience (Weight: 20%), and Full Description (TF-IDF Weight: 30%).
   - Switch active screening target with 1-click.

3. **Multi-Format Resume Upload & Parsing**
   - Drag-and-drop or file browser upload.
   - Supports **PDF** (via `pypdf`), **DOCX** (via `python-docx`), and **TXT** files.
   - Multi-file batch upload support.
   - Client-side validation: format check and file size (max 10MB per file).
   - Instant extraction of Candidate Name, Email, Phone, Skills, Education, Experience years, Certifications, and Projects.

4. **Transparent 0–100% Match Engine**
   - **Required Skills Match (35%)**: Calculates matched vs. missing core requirements.
   - **Preferred Skills Match (15%)**: Evaluates nice-to-have bonus skills.
   - **TF-IDF + Cosine Similarity (30%)**: Uses `scikit-learn` N-gram vectorizer to evaluate contextual semantic similarity between job description and resume content.
   - **Experience Duration Match (20%)**: Compares detected candidate experience against minimum required years.
   - **Evaluation Tiers**:
     - 🟢 **80–100%**: Strong Match
     - 🟡 **60–79%**: Moderate Match
     - 🔴 **Below 60%**: Low Match

5. **Filterable Candidates Directory**
   - Search across candidate names, emails, and extracted skills.
   - Filter by Match Score Tier (Strong, Moderate, Low, All).
   - Filter by Status (Shortlisted, Under Review, Rejected, All).
   - Sort by highest match score, lowest score, name, or experience.
   - Quick one-click status actions.

6. **Candidate Details & Score Breakdown**
   - Candidate contact information & overview.
   - Transparent visual breakdown meters for all 4 score components.
   - Visual pill badges for Matched Required Skills vs Missing Required Skills.
   - Full raw extracted resume text preview drawer.
   - Status actions: Shortlist, Reject, Mark Under Review, Delete.
   - Re-screen candidate against any other configured job opening.

7. **Project Settings & Reset Utilities**
   - System metadata and algorithm weight explanations.
   - One-click **"Restore Sample Data"** button to reset or re-seed the SQLite database with rich demo data at any time.

---

## 🛠️ Project Structure

```
resume-screening-system/
│
├── app.py                     # Main Flask server with page & API routes
├── database.py                # SQLite database management & sample data seeder
├── requirements.txt           # Python package dependencies
├── README.md                  # Project documentation & instructions
├── resume_screening.db        # SQLite database (auto-generated)
│
├── services/
│   ├── __init__.py
│   ├── resume_parser.py       # PDF/DOCX/TXT text & entity extractor
│   └── screening_engine.py    # TF-IDF, Cosine Similarity & match scoring
│
├── static/
│   ├── css/
│   │   └── style.css          # Modern ATS design styling
│   └── js/
│       ├── main.js            # Global utilities & toast notifications
│       ├── upload.js          # Drag-and-drop & AJAX upload handler
│       └── candidates.js      # Status toggles, deletion & re-screening
│
├── templates/
│   ├── base.html              # Layout skeleton, sidebar & disclaimer
│   ├── dashboard.html         # Main ATS recruiter dashboard
│   ├── jobs.html              # Job description manager
│   ├── upload.html            # Resume upload dropzone
│   ├── candidates.html        # Candidates table with filters & search
│   ├── candidate_detail.html  # Candidate profile & score breakdown
│   └── settings.html          # Settings, algorithm breakdown & disclaimer
│
├── uploads/                   # Uploaded resume files storage
└── sample_resumes/            # Sample PDF, DOCX, and TXT resumes ready for testing
```

---

## 🚀 How to Run Locally in VS Code

### 1. Open the Project Folder in VS Code
Open VS Code, press `Ctrl + O` (or `File` -> `Open Folder...`), and select:
```
C:\Users\ANKUSH\.gemini\antigravity\scratch\resume-screening-system
```

### 2. Install Dependencies (If not already installed)
Open the integrated terminal in VS Code (`Ctrl + ~`) and run:
```bash
pip install -r requirements.txt
```

### 3. Run the Flask Web Application
In the terminal, run:
```bash
python app.py
```

### 4. Open in Your Browser
Open your browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 🧪 How to Test Resume Uploading & Screening

1. Launch the application and visit `http://127.0.0.1:5000`.
2. Notice that the dashboard is already pre-populated with realistic jobs and candidate rankings!
3. Click on **"Upload Resumes"** in the sidebar.
4. Drag and drop any of the pre-generated sample resumes located in `sample_resumes/`:
   - `sample_resumes/rahul_mehra_resume.pdf` (PDF format - Full Stack Developer)
   - `sample_resumes/sarah_chen_fullstack.docx` (DOCX format - Senior Full Stack)
   - `sample_resumes/alex_morgan_frontend.docx` (DOCX format - Frontend Developer)
   - `sample_resumes/david_kim_devops.txt` (TXT format - DevOps Engineer)
5. Click **"Screen & Process Resumes"**.
6. The system will parse the resume text, extract candidate information and skills, compute the TF-IDF cosine similarity, calculate the composite match score, and present the results immediately.
7. Click **"View Profile"** to examine the transparent score breakdown, matched vs. missing skills, and test the **Shortlist** / **Reject** buttons!
