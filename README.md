# AI-Powered Resume Screening System

An AI-powered resume screening system that matches candidate resumes to job descriptions using NLP techniques.

## Features

- Upload resumes in PDF or DOCX format
- Enter job descriptions and requirements
- Advanced Natural Language Processing for resume analysis
- Skills extraction and matching
- Education and experience analysis
- Visual match score calculation
- Detailed skill gap analysis

## Technologies Used

- **Backend**: Python, Flask, SQLAlchemy
- **Database**: PostgreSQL
- **NLP Libraries**: NLTK, spaCy, scikit-learn
- **Document Processing**: PyPDF2, python-docx
- **Frontend**: HTML, CSS, JavaScript, Bootstrap
- **Data Visualization**: Chart.js

## Installation

1. Clone the repository:
```bash
git clone https://github.com/YOUR_USERNAME/resume-screening-system.git
cd resume-screening-system
```

2. Create a virtual environment and install dependencies:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Download NLTK and spaCy data:
```bash
python -m nltk.downloader punkt stopwords wordnet
python -m spacy download en_core_web_sm
```

4. Set up the PostgreSQL database by creating a `.env` file with your database URL:
```
DATABASE_URL=postgresql://username:password@localhost/resume_screening
```

5. Run the application:
```bash
python main.py
```

## Usage

1. Access the application at `http://localhost:5000`
2. Upload your resume (PDF or DOCX)
3. Enter the job description and title
4. Click "Analyze Resume" to see your match score and detailed analysis

## License

MIT

## Acknowledgements

Inspired by and based on [AI-Powered-Resume-Screening-System](https://github.com/divishjindal19/AI-Powered-Resume-Screening-System)