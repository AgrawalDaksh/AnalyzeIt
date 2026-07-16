import ollama
import json
import re
from .config import OLLAMA_CHAT_MODEL

class JobParser:
    def __init__(self, model=OLLAMA_CHAT_MODEL):
        self.model = model

    def extract(self, text):
        response = ollama.chat(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": f"""
        You are an expert HR recruiter.

        Your task is to extract structured information from a Job Description.

        IMPORTANT RULES:

        1. Return ONLY valid JSON.
        2. Do NOT include markdown.
        3. Do NOT include explanations.
        4. Do NOT include ```json.
        5. If a field is missing, use null.
        6. Skills must always be arrays.
        7. Do not invent information.

        Return EXACTLY this JSON format:

        {{
            "job_title": null,
            "company": null,
            "required_skills": [],
            "preferred_skills": [],
            "minimum_experience": null,
            "degree": null,
            "minimum_cgpa": null,
            "location": null,
            "responsibilities": []
        }}

        Job Description:

        {text}
        """
                }
            ]
        )

        output = response["message"]["content"]
        return self.parse_job_profile(output)

    def parse_job_profile(self, text):
        # Remove ```json and ```
        text = re.sub(r"```json", "", text)
        text = re.sub(r"```", "", text)
        text = text.strip()

        try:
            return json.loads(text)
        except Exception:
            return {
                "job_title": None,
                "company": None,
                "required_skills": [],
                "preferred_skills": [],
                "minimum_experience": None,
                "degree": None,
                "minimum_cgpa": None,
                "location": None,
                "responsibilities": []
            }
