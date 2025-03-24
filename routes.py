import os
import json
import tempfile
import logging
from werkzeug.utils import secure_filename
from flask import render_template, request, redirect, url_for, flash, jsonify, session

from app import app, db
from models import Resume, JobDescription, JobApplication
from resume_analyzer import analyze_resume

# Allowed file extensions
ALLOWED_EXTENSIONS = {'pdf', 'docx'}

def allowed_file(filename):
    """Check if the file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET'])
def index():
    """Render the main page"""
    return render_template('index.html')

@app.route('/upload_resume', methods=['POST'])
def upload_resume():
    """Handle resume upload and analysis"""
    # Check if a file was uploaded
    if 'resume' not in request.files:
        flash('No file part', 'danger')
        return redirect(request.url)
    
    file = request.files['resume']
    
    # Check if file was selected
    if file.filename == '':
        flash('No selected file', 'danger')
        return redirect(request.url)
    
    # Check if job description was provided
    job_description = request.form.get('job_description', '').strip()
    job_title = request.form.get('job_title', 'Untitled Job').strip()
    
    if not job_description:
        flash('Job description is required', 'danger')
        return redirect(request.url)
    
    # Check if the file is allowed
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        
        # Create a temporary file
        temp_dir = tempfile.gettempdir()
        file_path = os.path.join(temp_dir, filename)
        file.save(file_path)
        
        try:
            # Extract file extension
            file_extension = os.path.splitext(filename)[1]
            
            # Analyze the resume
            analysis_result = analyze_resume(file_path, file_extension, job_description)
            
            if 'error' in analysis_result:
                flash(analysis_result['error'], 'danger')
                return redirect(request.url)
            
            # Store resume in database
            resume = Resume(
                filename=filename,
                content=analysis_result['resume_text'],
                extracted_skills=json.dumps(analysis_result['skills']),
                extracted_education=json.dumps(analysis_result['education']),
                extracted_experience=json.dumps(analysis_result['experience'])
            )
            db.session.add(resume)
            
            # Store job description in database
            job_desc = JobDescription(
                title=job_title,
                content=job_description,
                required_skills=json.dumps(analysis_result['skills_match'].get('matched', []) + 
                                          analysis_result['skills_match'].get('missing', []))
            )
            db.session.add(job_desc)
            db.session.flush()  # Flush to get IDs
            
            # Store application/match in database
            application = JobApplication(
                resume_id=resume.id,
                job_description_id=job_desc.id,
                score=analysis_result['match_score'],
                skills_match=json.dumps(analysis_result['skills_match'])
            )
            db.session.add(application)
            db.session.commit()
            
            # Store application ID in session for results page
            session['application_id'] = application.id
            
            return redirect(url_for('results'))
            
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error processing resume: {str(e)}")
            flash(f"Error processing resume: {str(e)}", 'danger')
            return redirect(request.url)
        finally:
            # Clean up temporary file
            if os.path.exists(file_path):
                os.remove(file_path)
    else:
        flash('File type not allowed. Please upload a PDF or DOCX file.', 'danger')
        return redirect(request.url)

@app.route('/results')
def results():
    """Show results of resume analysis"""
    application_id = session.get('application_id')
    if not application_id:
        flash('No analysis results found', 'warning')
        return redirect(url_for('index'))
    
    # Get application with related resume and job description
    application = JobApplication.query.get(application_id)
    if not application:
        flash('Analysis results not found', 'warning')
        return redirect(url_for('index'))
    
    # Get resume and job description data
    resume = Resume.query.get(application.resume_id)
    job = JobDescription.query.get(application.job_description_id)
    
    # Prepare data for template
    resume_skills = json.loads(resume.extracted_skills) if resume.extracted_skills else []
    resume_education = json.loads(resume.extracted_education) if resume.extracted_education else []
    resume_experience = json.loads(resume.extracted_experience) if resume.extracted_experience else []
    skills_match = json.loads(application.skills_match) if application.skills_match else {}
    
    return render_template('results.html', 
                           application=application,
                           resume=resume,
                           job=job,
                           resume_skills=resume_skills,
                           resume_education=resume_education,
                           resume_experience=resume_experience,
                           skills_match=skills_match)

@app.route('/history')
def history():
    """Show history of analyzed resumes"""
    # Get recent applications with resume and job information
    applications = JobApplication.query.order_by(JobApplication.created_at.desc()).limit(10).all()
    
    return render_template('results.html', applications=applications)

@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle file too large error"""
    flash('File too large. Maximum file size is 16MB.', 'danger')
    return redirect(url_for('index')), 413

@app.errorhandler(404)
def page_not_found(error):
    """Handle 404 error"""
    return render_template('index.html', error="Page not found"), 404

@app.errorhandler(500)
def internal_server_error(error):
    """Handle 500 error"""
    return render_template('index.html', error="Internal server error. Please try again later."), 500
