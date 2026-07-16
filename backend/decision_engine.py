import ollama
import json
import re
from .config import OLLAMA_CHAT_MODEL

class HiringDecisionEngine:
    def __init__(self, model=OLLAMA_CHAT_MODEL):
        self.model = model

    def generate_decision(self, candidate_profile, job_profile, ranking_breakdown):
        """
        Generates a structured hiring decision report using LLM based ONLY on structured JSON profiles.
        Does not use raw semantic resume retrieval.
        """
        prompt = f"""
        You are an elite executive talent acquisition recruiter.
        
        Analyze the candidate's structured profile, the job profile requirements, and the candidate's match score breakdown to produce an objective, structured hiring report.
        
        CRITICAL RULES:
        1. Base your recommendation ONLY on the provided structured JSON inputs.
        2. Do NOT assume or make up details not present in the structured profiles.
        3. Return ONLY valid JSON matching the format below.
        4. Do NOT include any markdown block characters (like ```json or ```) or explanatory text outside the JSON.
        
        Candidate Structured Profile:
        {json.dumps(candidate_profile, indent=2)}
        
        Job Description Structured Profile:
        {json.dumps(job_profile, indent=2)}
        
        Match Score & Category Breakdown:
        {json.dumps(ranking_breakdown, indent=2)}
        
        Return EXACTLY this JSON structure:
        {{
          "recommendation": "Strong Hire | Hire | Borderline | No Hire",
          "confidence": "0-100",
          "strengths": ["strength 1", "strength 2", ...],
          "weaknesses": ["weakness 1", "weakness 2", ...],
          "missing_skills": ["missing skill 1", ...],
          "risk_factors": ["risk factor 1", ...],
          "training_recommendations": ["training recommendation 1", ...],
          "estimated_ramp_up_time": "e.g., 2 weeks, 1 month",
          "summary": "Recruiter summary explaining decision rationale."
        }}
        """
        
        response = ollama.chat(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        
        content = response["message"]["content"]
        return self._parse_json_safely(content)

    def _parse_json_safely(self, text):
        text = re.sub(r"```json", "", text)
        text = re.sub(r"```", "", text)
        text = text.strip()
        try:
            return json.loads(text)
        except Exception:
            return {
                "recommendation": "Borderline",
                "confidence": "50",
                "strengths": ["Data validation completed"],
                "weaknesses": ["LLM returned unparsable formatting"],
                "missing_skills": [],
                "risk_factors": ["Formatting risk"],
                "training_recommendations": [],
                "estimated_ramp_up_time": "Unknown",
                "summary": "Successfully received LLM decision but could not parse. Raw output: " + text[:150]
            }
