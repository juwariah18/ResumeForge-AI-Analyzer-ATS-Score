# 🚀 ResumeForge AI

### AI-Powered Resume Builder, Analyzer & Job Matcher

ResumeForge AI is a modern web application that helps users **create professional resumes, upload existing resumes, analyze them, and match their skills with job opportunities** — all through a simple and user-friendly interface.

Built with **Flask, Python, HTML, CSS, JavaScript, and AI-powered analysis**, ResumeForge AI combines resume creation and career assistance into one platform.

---

## 🌐 Live Demo

- 🚀 Live Demo: 
- 💻 GitHub Repository: https://github.com/juwariah18/ResumeForge-AI-Analyzer-ATS-Score

> Deployed using **Render** for easy online access without requiring local setup.

---

## ✨ What ResumeForge AI Can Do

| Feature                       | Description                                                       |
| ----------------------------- | ----------------------------------------------------------------- |
| 📝 **Resume Builder**         | Create a professional resume through a guided multi-step form     |
| 📄 **Resume Upload**          | Upload existing resumes in PDF or DOCX format                     |
| 🤖 **AI Resume Analysis**     | Analyze resume content and identify areas for improvement         |
| 🎯 **Job Matching**           | Compare resume skills with job requirements                       |
| 💾 **Saved Resumes**          | Store and access previously created resumes                       |
| 📥 **PDF Download**           | Generate and download resumes as PDF                              |
| 🎨 **Professional Templates** | Choose from resume layouts designed for professional presentation |
| 📱 **Responsive UI**          | Designed to work across desktop and mobile screen sizes           |

---

## 🧠 How It Works

```text
              ┌──────────────────┐
              │   User Visits    │
              │   ResumeForge    │
              └────────┬─────────┘
                       │
                       ▼
             ┌────────────────────┐
             │ Create or Upload   │
             │      Resume        │
             └─────────┬──────────┘
                       │
                       ▼
             ┌────────────────────┐
             │ Resume Processing  │
             │ & Content Parsing  │
             └─────────┬──────────┘
                       │
              ┌────────┴────────┐
              ▼                 ▼
      ┌───────────────┐  ┌────────────────┐
      │ AI Analysis   │  │   Job Matching │
      └───────┬───────┘  └───────┬────────┘
              │                  │
              └────────┬─────────┘
                       ▼
              ┌──────────────────┐
              │ Insights & Resume│
              │     Results      │
              └────────┬─────────┘
                       │
                       ▼
              ┌──────────────────┐
              │ Download / Save  │
              │      Resume      │
              └──────────────────┘
```

---

## 🎯 Key Features

### 📝 Smart Resume Builder

Create your resume using a structured, guided process.

Users can add:

* Personal information
* Professional summary
* Education
* Work experience
* Projects
* Certifications
* Technical skills
* Achievements
* Languages
* Core strengths
* Profile photo
* Social and professional links

The generated resume is formatted according to the selected template.

---

### 📄 Resume Upload & Parsing

Already have a resume?

Upload an existing:

* **PDF**
* **DOCX**

ResumeForge AI processes the uploaded document and extracts relevant information for analysis.

---

### 🤖 AI Resume Analysis

ResumeForge AI analyzes resume content and provides useful insights such as:

* Resume strengths
* Areas that can be improved
* Skill-related observations
* Content suggestions
* ATS-oriented feedback

The goal is to help users understand how effectively their resume presents their qualifications.

---

### 🎯 Job Matching

Users can compare their resume against a job description.

The system evaluates the relationship between:

**Resume Skills → Job Requirements → Matching Skills → Missing/Relevant Skills**

This helps users identify which skills and qualifications are relevant to a particular job opportunity.

---

### 💾 Saved Resumes

Users can save generated resumes and access them later instead of recreating them from scratch.

---

### 📥 Resume PDF Generation

Generated resumes can be converted into a professional **PDF format** for downloading and sharing.

---

## 🛠️ Technology Stack

### Frontend

* HTML5
* CSS3
* JavaScript
* Jinja2 Templates
* Responsive UI

### Backend

* Python
* Flask
* Flask Routing
* Session & Authentication Handling

### Resume Processing

* PDF parsing
* DOCX processing
* Resume text extraction
* Resume analysis
* Job description matching

### AI / Data Processing

* AI-assisted resume analysis
* Natural language processing concepts
* Keyword and skill matching
* Text processing algorithms

### Database

* SQLite for development/demo usage

### PDF / Document Generation

* ReportLab
* Python document-processing libraries

### Deployment

* Render
* Gunicorn

---

## 📂 Project Structure

```text
ResumeForge-AI/
│
├── app.py
├── requirements.txt
├── Procfile
│
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── auth.html
│   ├── choose.html
│   ├── upload.html
│   ├── builder.html
│   ├── result.html
│   ├── match.html
│   └── my_resumes.html
│
├── static/
│   └── style.css
│
├── utils/
│   └── ...
│
└── README.md
```

---

## 👥 Team Contribution

ResumeForge AI was developed using a **Frontend + Backend team structure**.

### 🎨 Frontend

Responsible for:

* User interface
* Page layouts
* Resume builder interface
* Forms and interactions
* Responsive styling
* Template presentation

**Main files:**

```text
templates/base.html
templates/index.html
templates/auth.html
templates/choose.html
templates/upload.html
templates/builder.html
static/style.css
```

### ⚙️ Backend

Responsible for:

* Flask application
* Authentication
* Resume processing
* File handling
* Resume analysis
* Job matching
* Database operations
* PDF generation
* Deployment configuration

**Main files:**

```text
app.py
utils/*
templates/result.html
templates/match.html
templates/my_resumes.html
requirements.txt
Procfile
```

---

## ⚙️ Run Locally

### 1. Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd ResumeForge-AI
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Activate it

**Windows:**

```bash
.venv\Scripts\activate
```

**macOS/Linux:**

```bash
source .venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Start the application

```bash
python app.py
```

### 6. Open in your browser

```text
http://127.0.0.1:5000
```

---

## ☁️ Deployment

ResumeForge AI is deployed on **Render**.

### Render Configuration

**Build Command**

```bash
pip install -r requirements.txt
```

**Start Command**

```bash
gunicorn app:app
```

### Deployment Flow

```text
GitHub Repository
       │
       ▼
     Render
       │
       ▼
Build Dependencies
       │
       ▼
 Start Gunicorn
       │
       ▼
ResumeForge AI
       │
       ▼
   Live Website
```

---

## 🔐 Security & Data

The application includes authentication and user-specific resume handling.

For a production-scale deployment, additional improvements can include:

* PostgreSQL instead of SQLite
* Secure secret/environment variables
* Persistent file storage
* Stronger authentication controls
* Production-grade logging
* Input validation and security hardening

---

## 🚧 Future Improvements

ResumeForge AI can be extended with additional career-focused features:

* 🔍 Advanced ATS scoring
* 🧠 More detailed AI resume recommendations
* 📊 Resume analytics dashboard
* 🎯 Multiple job-description comparisons
* 💼 Job recommendation system
* ✍️ AI-powered resume rewriting
* 🔗 LinkedIn profile integration
* 📈 Resume improvement tracking
* ☁️ Cloud-based resume storage
* 🎨 Additional professional templates

---

## 🎓 Project Purpose

ResumeForge AI was developed as a **college software project** to explore the integration of:

**Web Development + Python + Flask + AI + Resume Processing + Document Generation**

The project demonstrates how these technologies can be combined to build a practical career-oriented application.

---

## 💡 Why ResumeForge AI?

Creating a resume often involves switching between different tools for:

**Writing → Formatting → Checking → Improving → Matching → Downloading**

ResumeForge AI brings these activities together into a single platform.

> **Build your resume. Understand your strengths. Match your skills. Move closer to your next opportunity.**

---

## 📌 Project Highlights

```text
✓ AI-powered resume analysis
✓ Guided resume creation
✓ PDF & DOCX resume upload
✓ Resume parsing
✓ Job description matching
✓ Professional resume templates
✓ PDF resume generation
✓ Saved resumes
✓ Responsive web interface
✓ Flask-based backend
✓ Render deployment
```

---

## 📜 License

This project was created for educational and academic purposes.

---

## ⭐ Support

If you find **ResumeForge AI** interesting, consider giving the repository a ⭐ on GitHub.

**Built with Python, Flask, AI, and a lot of learning. 🚀**
