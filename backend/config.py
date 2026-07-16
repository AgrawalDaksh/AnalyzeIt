# Centralized configuration variables for ResumeRAG backend modules

# Ollama Models
OLLAMA_CHAT_MODEL = "llama3:8b"
OLLAMA_EMBED_MODEL = "bge-m3"

# Query Matching thresholds
TOP_K_DEFAULT = 3
TOP_K_SKILLS = 5
TOP_K_COMPARISON = 2
TOP_K_ACADEMIC = 1

# Candidate Matching Weights (must sum to 1.0)
SKILL_WEIGHT = 0.40
EXPERIENCE_WEIGHT = 0.25
EDUCATION_WEIGHT = 0.15
CGPA_WEIGHT = 0.10
PROJECT_WEIGHT = 0.10
