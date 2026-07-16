<div align="center">

# 📄 AnalyzeIt

### AI-Powered Recruitment & Resume Intelligence Platform

*Transforming recruitment with AI-powered resume analysis, semantic search, candidate ranking, and intelligent hiring assistance.*

<br>

![Python](https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-Framework-FF4B4B?style=for-the-badge&logo=streamlit)
![Ollama](https://img.shields.io/badge/Ollama-Local%20LLMs-black?style=for-the-badge)
![Llama3](https://img.shields.io/badge/Llama3-8B-blueviolet?style=for-the-badge)
![BGE-M3](https://img.shields.io/badge/BGE--M3-Embeddings-success?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Active-success?style=for-the-badge)

</div>

---

# 🚀 Overview

Hiring should be about finding the **best talent**, not manually reading hundreds of resumes.

**AnalyzeIt** is an AI-powered recruitment assistant that helps recruiters intelligently analyze resumes, match candidates against job descriptions, perform semantic search using Retrieval-Augmented Generation (RAG), and generate AI-assisted hiring insights—all while running completely **locally** using Ollama.

Instead of keyword matching, AnalyzeIt understands the **meaning** behind resumes and recruiter queries, enabling faster, smarter, and more reliable hiring decisions.

---

# ✨ Key Features

### 📄 Resume Intelligence

- AI Resume Parsing
- Structured Candidate Profiles
- Skills Extraction
- Experience Extraction
- Education Parsing
- Projects Extraction

---

### 💼 Recruitment Intelligence

- AI Job Description Parsing
- Candidate Ranking
- Candidate Comparison
- Hiring Recommendation Engine
- Recruiter Analytics Dashboard

---

### 🤖 AI Capabilities

- Retrieval-Augmented Generation (RAG)
- Semantic Resume Search
- Natural Language Resume Q&A
- AI Interview Question Generator
- Multilingual Query Support

---

### 📊 Analytics

- Candidate Match Scores
- Skills Distribution
- Average CGPA
- Candidate Insights
- Hiring Metrics

---

### 📤 Export Center

- PDF Reports
- CSV Export
- Excel Export

---

# 🖼️ Screenshots

## Recruiter Dashboard

> *(Replace with actual screenshot)*

![](screenshots/dashboard.png)

---

## Candidate Rankings

![](screenshots/rankings.png)

---

## AI Recruiter Chat

![](screenshots/chat.png)

---

## Candidate Comparison

![](screenshots/comparison.png)

---

# 🏗️ System Architecture

```text
                     Resume PDFs
                          │
                          ▼
              AI Resume Parser (LLM)
                          │
                          ▼
             Structured Candidate Profiles
                          │
             ┌────────────┴─────────────┐
             ▼                          ▼
      Embedding Engine           Candidate Matcher
        (BGE-M3)                     Engine
             │                          │
             └────────────┬─────────────┘
                          ▼
                 Recruiter Dashboard
                          │
        ┌─────────────────┼──────────────────┐
        ▼                 ▼                  ▼
   RAG Chat        Hiring Decision      Interview Guide
```

---

# 🎯 Workflow

```text
Upload Resumes
       │
       ▼
AI Resume Parsing
       │
       ▼
Generate Embeddings
       │
       ▼
Upload Job Description
       │
       ▼
AI Candidate Matching
       │
       ▼
Recruiter Dashboard
       │
       ▼
Chat • Compare • Interview • Export
```

---

# 🛠️ Tech Stack

## Frontend

- Streamlit
- HTML
- CSS
- Plotly

## Backend

- Python
- Ollama
- NumPy
- PyPDF

## AI Models

- Llama 3
- BGE-M3

## AI Techniques

- Retrieval-Augmented Generation (RAG)
- Semantic Search
- Resume Parsing
- Prompt Engineering
- Candidate Ranking

---

# 📂 Project Structure

```text
AnalyzeIt
│
├── assets/
├── backend/
├── components/
├── sample_data/
│   ├── resumes/
│   └── job_descriptions/
├── screenshots/
├── .streamlit/
├── app.py
├── requirements.txt
├── README.md
└── .gitignore
```

---

# ⚙️ Installation

Clone the repository

```bash
git clone https://github.com/AgrawalDaksh/AnalyzeIt.git
```

Move into the project

```bash
cd AnalyzeIt
```

Install dependencies

```bash
pip install -r requirements.txt
```

Start Ollama

```bash
ollama serve
```

Download required models

```bash
ollama pull llama3:8b
ollama pull bge-m3
```

Launch the application

```bash
streamlit run app.py
```

---

# 📈 Feature Matrix

| Feature | Status |
|----------|:------:|
| Resume Parsing | ✅ |
| Job Description Parsing | ✅ |
| Semantic Search | ✅ |
| RAG Chat | ✅ |
| Candidate Ranking | ✅ |
| Recruiter Dashboard | ✅ |
| Candidate Comparison | ✅ |
| Hiring Recommendation | ✅ |
| Interview Generator | ✅ |
| Export Reports | ✅ |

---

# 🚧 Roadmap

- OCR Support
- Candidate Database
- Recruiter Authentication
- REST API
- Cloud Deployment
- React Frontend
- Multi-Job Hiring
- Email Integration

---

# 🤝 Contributing

Contributions, feature suggestions, and bug reports are welcome.

Feel free to fork the repository, create a feature branch, and submit a pull request.

---

# ⭐ Support

If you found this project useful, consider giving it a **⭐ Star** on GitHub.

It helps others discover the project and motivates future development.

---

<div align="center">

### Built with ❤️ using Python, Streamlit & Local LLMs

**AnalyzeIt — Smarter Hiring with AI**

</div>