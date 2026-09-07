import os
import json
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from werkzeug.utils import secure_filename
import database as db
from services.resume_parser import parse_resume
from services.screening_engine import screen_resume

app = Flask(__name__)
app.secret_key = "resume-screening-mini-project-secret-key"

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'doc', 'txt'}
MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10 MB per file limit

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Initialize DB and seed if empty
db.init_db()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Context processor for global template variables
@app.context_processor
def inject_global_data():
    active_job = db.get_active_job()
    all_jobs = db.get_all_jobs()
    return {
        "active_job": active_job,
        "all_jobs": all_jobs,
        "disclaimer": "This system is a college-project decision-support tool and should not be used as the sole basis for hiring decisions."
    }

# --- PAGE ROUTES ---

@app.route('/')
def index():
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    active_job = db.get_active_job()
    job_id = active_job['id'] if active_job else None
    
    stats = db.get_dashboard_stats(job_id=job_id)
    recent_candidates = db.get_candidates_list(job_id=job_id, sort='score_desc')[:7]
    
    # Calculate score tier counts for distribution chart/cards
    strong_count = sum(1 for c in recent_candidates if c['total_score'] and c['total_score'] >= 80)
    moderate_count = sum(1 for c in recent_candidates if c['total_score'] and 60 <= c['total_score'] < 80)
    low_count = sum(1 for c in recent_candidates if not c['total_score'] or c['total_score'] < 60)

    # Process JSON fields in candidates for template
    processed_candidates = []
    for c in recent_candidates:
        c_dict = dict(c)
        try:
            c_dict['skills_list'] = json.loads(c_dict['extracted_skills']) if c_dict.get('extracted_skills') else []
        except Exception:
            c_dict['skills_list'] = []
        processed_candidates.append(c_dict)

    return render_template(
        'dashboard.html',
        stats=stats,
        candidates=processed_candidates,
        active_job=active_job,
        strong_count=strong_count,
        moderate_count=moderate_count,
        low_count=low_count
    )

@app.route('/jobs', methods=['GET', 'POST'])
def jobs():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        company = request.form.get('company', '').strip()
        description = request.form.get('description', '').strip()
        required_skills = request.form.get('required_skills', '').strip()
        preferred_skills = request.form.get('preferred_skills', '').strip()
        try:
            min_experience = float(request.form.get('min_experience', 0) or 0)
        except ValueError:
            min_experience = 0.0
        make_active = request.form.get('make_active') == 'on'

        if not title or not description or not required_skills:
            flash("Please provide Job Title, Description, and Required Skills.", "danger")
        else:
            new_id = db.insert_job(title, company, description, required_skills, preferred_skills, min_experience, make_active)
            flash(f"Job '{title}' created successfully!", "success")
            return redirect(url_for('jobs'))

    jobs_list = db.get_all_jobs()
    return render_template('jobs.html', jobs=jobs_list)

@app.route('/upload')
def upload_page():
    active_job = db.get_active_job()
    return render_template('upload.html', active_job=active_job)

@app.route('/candidates')
def candidates_page():
    active_job = db.get_active_job()
    job_id = active_job['id'] if active_job else None

    status_filter = request.args.get('status', 'All')
    tier_filter = request.args.get('tier', 'All')
    search_query = request.args.get('search', '').strip()
    sort_by = request.args.get('sort', 'score_desc')

    raw_candidates = db.get_candidates_list(
        job_id=job_id,
        status=status_filter,
        tier=tier_filter,
        search=search_query,
        sort=sort_by
    )

    processed_candidates = []
    for c in raw_candidates:
        c_dict = dict(c)
        try:
            c_dict['skills_list'] = json.loads(c_dict['extracted_skills']) if c_dict.get('extracted_skills') else []
        except Exception:
            c_dict['skills_list'] = []
            
        try:
            c_dict['matched_skills_list'] = json.loads(c_dict['matched_skills']) if c_dict.get('matched_skills') else []
        except Exception:
            c_dict['matched_skills_list'] = []

        try:
            c_dict['missing_skills_list'] = json.loads(c_dict['missing_skills']) if c_dict.get('missing_skills') else []
        except Exception:
            c_dict['missing_skills_list'] = []

        processed_candidates.append(c_dict)

    return render_template(
        'candidates.html',
        candidates=processed_candidates,
        active_job=active_job,
        current_status=status_filter,
        current_tier=tier_filter,
        current_search=search_query,
        current_sort=sort_by
    )

@app.route('/candidates/<int:candidate_id>')
def candidate_detail(candidate_id):
    active_job = db.get_active_job()
    job_id = active_job['id'] if active_job else None

    # Allow query parameter to inspect score for a specific job
    requested_job_id = request.args.get('job_id')
    if requested_job_id:
        try:
            job_id = int(requested_job_id)
        except ValueError:
            pass

    job = db.get_job_by_id(job_id) if job_id else active_job
    candidate_row, screening_row = db.get_candidate_detail(candidate_id, job_id=job_id)

    if not candidate_row:
        flash("Candidate not found.", "danger")
        return redirect(url_for('candidates_page'))

    candidate = dict(candidate_row)
    screening = dict(screening_row) if screening_row else None

    # Parse JSON fields safely
    for key in ['extracted_skills', 'certifications', 'projects']:
        if candidate.get(key):
            try:
                candidate[key] = json.loads(candidate[key])
            except Exception:
                pass
        else:
            candidate[key] = []

    if screening:
        for key in ['matched_skills', 'missing_skills', 'matched_preferred', 'missing_preferred']:
            if screening.get(key):
                try:
                    screening[key] = json.loads(screening[key])
                except Exception:
                    pass
            else:
                screening[key] = []

    return render_template(
        'candidate_detail.html',
        candidate=candidate,
        screening=screening,
        job=job,
        all_jobs=db.get_all_jobs()
    )

@app.route('/settings')
def settings():
    return render_template('settings.html')

# --- API ENDPOINTS ---

@app.route('/api/jobs/<int:job_id>/activate', methods=['POST'])
def api_activate_job(job_id):
    db.set_active_job(job_id)
    return jsonify({"success": True, "message": "Active job updated successfully!"})

@app.route('/api/candidates/<int:candidate_id>/status', methods=['POST'])
def api_update_status(candidate_id):
    data = request.get_json() or {}
    new_status = data.get('status')
    if new_status in ['Under Review', 'Shortlisted', 'Rejected']:
        db.update_candidate_status(candidate_id, new_status)
        return jsonify({"success": True, "status": new_status})
    return jsonify({"success": False, "error": "Invalid status"}), 400

@app.route('/api/candidates/<int:candidate_id>/delete', methods=['POST', 'DELETE'])
def api_delete_candidate(candidate_id):
    db.delete_candidate(candidate_id)
    return jsonify({"success": True, "message": "Candidate deleted successfully."})

@app.route('/api/candidates/<int:candidate_id>/rescreen', methods=['POST'])
def api_rescreen(candidate_id):
    data = request.get_json() or {}
    job_id = data.get('job_id')
    if not job_id:
        active_job = db.get_active_job()
        job_id = active_job['id'] if active_job else None
    
    if not job_id:
        return jsonify({"success": False, "error": "No job available for screening"}), 400

    candidate_row, _ = db.get_candidate_detail(candidate_id)
    job_row = db.get_job_by_id(job_id)

    if not candidate_row or not job_row:
        return jsonify({"success": False, "error": "Candidate or Job not found"}), 404

    candidate_data = dict(candidate_row)
    job_data = dict(job_row)

    screening = screen_resume(candidate_data, job_data)
    db.save_screening_result(
        candidate_id, job_id,
        screening['total_score'],
        screening['required_skills_score'],
        screening['preferred_skills_score'],
        screening['tfidf_score'],
        screening['experience_score'],
        screening['matched_skills'],
        screening['missing_skills'],
        screening['matched_preferred'],
        screening['missing_preferred'],
        screening['recommendation']
    )
    return jsonify({"success": True, "screening": screening})

@app.route('/api/upload', methods=['POST'])
def api_upload():
    if 'resumes' not in request.files:
        return jsonify({"success": False, "error": "No resume files uploaded."}), 400

    files = request.files.getlist('resumes')
    if not files or files[0].filename == '':
        return jsonify({"success": False, "error": "No files selected."}), 400

    active_job = db.get_active_job()
    if not active_job:
        return jsonify({"success": False, "error": "No active job configured. Please create or activate a job first."}), 400

    results = []

    for file in files:
        if file and allowed_file(file.filename):
            orig_filename = secure_filename(file.filename) or file.filename
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], orig_filename)
            
            # Avoid overwriting identical filenames
            counter = 1
            base, ext = os.path.splitext(orig_filename)
            while os.path.exists(save_path):
                save_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{base}_{counter}{ext}")
                counter += 1

            file.save(save_path)

            # 1. Parse Resume
            parsed = parse_resume(save_path, original_filename=orig_filename)

            # 2. Insert Candidate into DB
            candidate_id = db.insert_candidate(
                name=parsed['name'],
                email=parsed['email'],
                phone=parsed['phone'],
                extracted_skills=parsed['extracted_skills'],
                education=parsed['education'],
                experience_years=parsed['experience_years'],
                experience_details=parsed['experience_details'],
                certifications=parsed['certifications'],
                projects=parsed['projects'],
                raw_resume_text=parsed['raw_resume_text'],
                resume_filename=orig_filename,
                resume_filepath=save_path
            )

            # 3. Screen against Active Job
            job_dict = dict(active_job)
            screening = screen_resume(parsed, job_dict)

            # 4. Save Screening Results
            db.save_screening_result(
                candidate_id, job_dict['id'],
                screening['total_score'],
                screening['required_skills_score'],
                screening['preferred_skills_score'],
                screening['tfidf_score'],
                screening['experience_score'],
                screening['matched_skills'],
                screening['missing_skills'],
                screening['matched_preferred'],
                screening['missing_preferred'],
                screening['recommendation']
            )

            results.append({
                "candidate_id": candidate_id,
                "name": parsed['name'],
                "filename": orig_filename,
                "score": screening['total_score'],
                "recommendation": screening['recommendation'],
                "skills_count": len(parsed['extracted_skills']),
                "matched_count": len(screening['matched_skills']),
                "missing_count": len(screening['missing_skills'])
            })
        else:
            results.append({
                "filename": file.filename,
                "error": "Invalid format. Only PDF, DOCX, and TXT are supported."
            })

    return jsonify({"success": True, "screened_count": len(results), "results": results})

@app.route('/api/settings/reset-db', methods=['POST'])
def api_reset_db():
    db.seed_sample_data()
    return jsonify({"success": True, "message": "Database successfully reset and re-seeded with demo data!"})

if __name__ == '__main__':
    print("Starting Resume Screening System on http://127.0.0.1:5000 ...")
    app.run(host='127.0.0.1', port=5000, debug=True)
