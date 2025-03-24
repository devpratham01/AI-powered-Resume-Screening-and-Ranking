from datetime import datetime
from app import db

class Resume(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Resume analysis data
    extracted_skills = db.Column(db.Text, nullable=True)
    extracted_education = db.Column(db.Text, nullable=True)
    extracted_experience = db.Column(db.Text, nullable=True)
    
    # Relationship with job applications
    applications = db.relationship('JobApplication', backref='resume', lazy=True)
    
    def __repr__(self):
        return f'<Resume {self.filename}>'

class JobDescription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    required_skills = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with job applications
    applications = db.relationship('JobApplication', backref='job_description', lazy=True)
    
    def __repr__(self):
        return f'<JobDescription {self.title}>'

class JobApplication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    resume_id = db.Column(db.Integer, db.ForeignKey('resume.id'), nullable=False)
    job_description_id = db.Column(db.Integer, db.ForeignKey('job_description.id'), nullable=False)
    score = db.Column(db.Float, nullable=False)
    skills_match = db.Column(db.Text, nullable=True)  # JSON string of skills matched
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<JobApplication {self.id}: Resume {self.resume_id} - Job {self.job_description_id}>'
