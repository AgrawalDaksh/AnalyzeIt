import os
from pypdf import PdfReader
import ollama
import logging

from .candidate_parser import CandidateParser
from .job_parser import JobParser
from .matcher import CandidateMatcher
from .query_router import QueryRouter
from .rag import RAGEngine
from .profile_engine import ProfileEngine
from .llm_engine import LLMEngine
from .decision_engine import HiringDecisionEngine
from .interview_generator import InterviewGenerator
from .pdf_utils import generate_interview_pdf, generate_reportlab_pdf

# Configure logger
logger = logging.getLogger("ResumeRAG")

class ResumeRAG:
    def __init__(self):
        self.resumes = {}
        self.resume_embeddings = {}
        self.candidate_metadata = {}
        self.candidate_profiles = {}
        self.job_description = ""
        self.job_profile = {}

        # Component Initialization
        self.parser = CandidateParser()
        self.job_parser = JobParser()
        self.matcher = CandidateMatcher()
        self.rag = RAGEngine()
        self.router = QueryRouter()
        self.profile_engine = ProfileEngine()
        self.llm_engine = LLMEngine()
        self.decision_engine = HiringDecisionEngine()
        self.interview_generator = InterviewGenerator()

    def load_resumes(self, uploaded_files):
        """
        Loads resumes from PDF uploaded files.
        Performs robust validation on PDF files.
        Returns: (loaded_count, list_of_error_strings)
        """
        self.resumes = {}
        self.candidate_metadata = {}
        self.candidate_profiles = {}
        
        errors = []
        seen_filenames = set()

        for uploaded_file in uploaded_files:
            filename = uploaded_file.name
            
            # 1. Unsupported File Type Check
            if not filename.lower().endswith(".pdf"):
                errors.append(f"❌ {filename}: Unsupported file type. Only PDF files are supported.")
                continue
                
            # 2. Duplicate Upload Check
            if filename in seen_filenames:
                errors.append(f"⚠️ {filename}: Duplicate file detected and skipped.")
                continue
            seen_filenames.add(filename)

            try:
                # 3. Parse PDF page by page
                reader = PdfReader(uploaded_file)
                
                # Check for encryption
                if reader.is_encrypted:
                    errors.append(f"❌ {filename}: PDF is encrypted. Please decrypt it first.")
                    continue
                    
                text = ""
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                
                # 4. Check for extractable text
                if not text.strip():
                    errors.append(f"❌ {filename}: PDF contains no extractable text (it may be scanned or empty).")
                    continue

                # Store resume text
                self.resumes[filename] = text
                
                # Extract candidate profile using parser instance
                profile = self.parser.extract(text)
                self.candidate_profiles[filename] = profile

                # Extract candidate name safely
                lines = [line.strip() for line in text.split("\n") if line.strip()]
                candidate_name = lines[0] if lines else filename.replace(".pdf", "")

                # Store metadata
                self.candidate_metadata[filename] = {
                    "filename": filename,
                    "full_name": candidate_name,
                    "first_name": candidate_name.split()[0].lower() if candidate_name.split() else candidate_name.lower(),
                    "full_name_lower": candidate_name.lower()
                }

            except Exception as e:
                logger.error(f"Failed to read PDF '{filename}': {e}")
                errors.append(f"❌ {filename}: Corrupted PDF or read failure. Details: {str(e)}")
                continue

        return len(self.resumes), errors

    def generate_embeddings(self):
        """
        Generates semantic embeddings for parsed resumes.
        Handles Ollama connection exceptions gracefully.
        """
        self.resume_embeddings = {}
        for filename, content in self.resumes.items():
            try:
                response = ollama.embed(
                    model=self.rag.embedding_model,
                    input=content
                )
                self.resume_embeddings[filename] = response["embeddings"][0]
            except Exception as e:
                logger.error(f"Failed to generate embedding for '{filename}': {e}")

    def load_job_description(self, jd_file_or_text):
        """
        Loads job description from text or a PDF file-like object.
        Returns: (success_bool, error_message)
        """
        if isinstance(jd_file_or_text, str):
            text = jd_file_or_text.strip()
            if not text:
                return False, "Job description text is empty."
            self.job_description = text
            self.job_profile = self.job_parser.extract(text)
            return True, None

        # Else it is an uploaded file
        filename = jd_file_or_text.name
        if not filename.lower().endswith(".pdf"):
            return False, f"Unsupported file type for {filename}. Only PDF is supported."

        try:
            reader = PdfReader(jd_file_or_text)
            if reader.is_encrypted:
                return False, f"Job description PDF '{filename}' is encrypted."
                
            text = ""
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"

            text = text.strip()
            if not text:
                return False, f"Job description PDF '{filename}' is empty or contains no extractable text."

            self.job_description = text
            self.job_profile = self.job_parser.extract(text)
            return True, None

        except Exception as e:
            logger.error(f"Failed to load job description PDF '{filename}': {e}")
            return False, f"Failed to parse Job Description PDF '{filename}': {str(e)}"

    def rank_candidates(self):
        if not self.job_profile or not self.candidate_profiles:
            return []
        return self.matcher.rank(self.candidate_profiles, self.job_profile, raw_resumes=self.resumes)

    def ask_question(self, question):
        if not self.resume_embeddings:
            return {
                "answer": "⚠️ Please upload resumes first to generate embeddings before asking questions.",
                "matches": []
            }
        
        query_type = self.router.detect_query_type(question)
        
        # 1. Check structured profile query engine
        profile_result = self.profile_engine.query(self.candidate_profiles, question)
        if profile_result is not None:
            return {
                "answer": profile_result["answer"],
                "matches": []
            }

        # 2. Check semantic RAG engine
        top_matches = self.rag.search(
            question=question,
            resume_embeddings=self.resume_embeddings,
            candidate_metadata=self.candidate_metadata,
            query_type=query_type
        )
        
        # 3. Generate answer using LLM engine
        try:
            answer = self.llm_engine.generate_answer(
                question=question,
                top_matches=top_matches,
                resumes=self.resumes
            )
        except Exception as e:
            logger.error(f"Failed to generate answer for query '{question}': {e}")
            answer = f"⚠️ Sorry, I encountered an issue querying the model. Details: {str(e)}"

        return {
            "answer": answer,
            "matches": top_matches
        }

    def generate_hiring_decision(self, filename):
        candidate_profile = self.candidate_profiles.get(filename)
        if not candidate_profile or not self.job_profile:
            return {
                "recommendation": "Borderline",
                "confidence": "0",
                "strengths": ["Data incomplete"],
                "weaknesses": ["Data incomplete"],
                "missing_skills": [],
                "risk_factors": ["Missing candidate profile"],
                "training_recommendations": [],
                "estimated_ramp_up_time": "Unknown",
                "summary": "Cannot generate hiring report because candidate profile or job profile is missing."
            }
        
        # Get breakdown details
        rankings = self.rank_candidates()
        cand_ranking = {}
        for r in rankings:
            if r["filename"] == filename:
                cand_ranking = r
                break
                
        try:
            return self.decision_engine.generate_decision(
                candidate_profile=candidate_profile,
                job_profile=self.job_profile,
                ranking_breakdown=cand_ranking
            )
        except Exception as e:
            logger.error(f"Failed to generate hiring decision report for '{filename}': {e}")
            return {
                "recommendation": "Borderline",
                "confidence": "0",
                "strengths": ["Error processing report"],
                "weaknesses": ["Error processing report"],
                "missing_skills": [],
                "risk_factors": [f"Exception: {str(e)}"],
                "training_recommendations": [],
                "estimated_ramp_up_time": "Unknown",
                "summary": "Error generating AI Hiring Decision. Check server logs."
            }

    def generate_interview_questions(self, filename, difficulty):
        candidate_profile = self.candidate_profiles.get(filename)
        if not candidate_profile or not self.job_profile:
            return {
                "technical": [],
                "behavioral": [],
                "project": [],
                "missing_skill": []
            }
        try:
            return self.interview_generator.generate_questions(
                candidate_profile=candidate_profile,
                job_profile=self.job_profile,
                difficulty=difficulty
            )
        except Exception as e:
            logger.error(f"Failed to generate interview questions for '{filename}': {e}")
            return {
                "technical": [{"question": "Failed to generate question. Please try again.", "ideal_answer": "N/A", "criteria": "N/A"}],
                "behavioral": [],
                "project": [],
                "missing_skill": []
            }

    def export_interview_pdf(self, filename, difficulty, questions_data):
        candidate_profile = self.candidate_profiles.get(filename, {})
        candidate_name = candidate_profile.get("name") or filename.replace(".pdf", "")
        try:
            return generate_interview_pdf(
                candidate_name=candidate_name,
                difficulty=difficulty,
                questions_data=questions_data
            )
        except Exception as e:
            logger.error(f"Failed to generate Interview questions PDF: {e}")
            return b""

    def export_recruitment_report(self):
        rankings = self.rank_candidates()
        if not rankings or not self.job_profile:
            return b""
        try:
            return generate_reportlab_pdf(self.job_profile, rankings)
        except Exception as e:
            logger.error(f"Failed to generate Recruitment PDF report: {e}")
            return b""
