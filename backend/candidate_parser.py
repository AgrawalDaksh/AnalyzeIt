import ollama
import json
import re
import logging
from .config import OLLAMA_CHAT_MODEL

# Configure logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("CandidateParser")

class CandidateParser:
    def __init__(self, model=OLLAMA_CHAT_MODEL):
        self.model = model

    def extract(self, text):
        try:
            response = ollama.chat(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": f"""
            You are an expert resume parser.

            Your task is to extract structured information from the resume.

            IMPORTANT RULES:

            1. Return ONLY valid JSON.
            2. Do NOT include markdown.
            3. Do NOT include ```json.
            4. Do NOT explain anything.
            5. If a field is missing, use null.
            6. Skills, projects and experience must always be arrays.
            7. Preserve the original wording from the resume.
            8. Do not guess any missing information.
            9. FIELD DEFINITIONS:
               - "college": The name of the educational institution, university, or school attended (e.g., IIT Bombay, Delhi University, Stanford). Do NOT put degree qualifications here.
               - "degree": The qualification name or field of study obtained (e.g., B.Tech Computer Science, Master of Science, Ph.D.). Do NOT put university/college names here.
               - "experience": Array of strings representing job experience entries. Keep date ranges intact in the strings (e.g., ["Software Engineering Intern, TechNova Solutions (Jan 2026 – Jun 2026)"]).

            FEW-SHOT EXAMPLE:

            Input Resume Text:
            ---
            Rahul Sharma
            Email: rahul.sharma@gmail.com
            Phone: +91 98XXXXXX21
            Education
            B.Tech Computer Science — IIIT Hyderabad
            CGPA: 9.21 | Class X: 94% | Class XII: 92%
            Technical Skills
            Python, FastAPI, SQL
            Experience
            Software Engineering Intern, TechNova Solutions (Jan 2026 – Jun 2026)
            Projects
            • Resume Intelligence Platform
            ---

            Expected JSON output:
            {{
                "name": "Rahul Sharma",
                "email": "rahul.sharma@gmail.com",
                "phone": "+91 98XXXXXX21",
                "tenth_percentage": "94%",
                "twelfth_percentage": "92%",
                "cgpa": "9.21",
                "college": "IIIT Hyderabad",
                "degree": "B.Tech Computer Science",
                "skills": ["Python", "FastAPI", "SQL"],
                "projects": ["Resume Intelligence Platform"],
                "experience": ["Software Engineering Intern, TechNova Solutions (Jan 2026 – Jun 2026)"]
            }}

            Resume:

            {text}
            """
                    }
                ]
            )
            profile_text = response["message"]["content"]
            return self.parse_profile_json(profile_text)
        except Exception as e:
            logger.error(f"Ollama chat execution failed: {e}")
            return self.get_default_profile()

    def get_default_profile(self):
        return {
            "name": "Not Available",
            "email": "Not Available",
            "phone": "Not Available",
            "tenth_percentage": "Not Available",
            "twelfth_percentage": "Not Available",
            "cgpa": "Not Available",
            "college": "Not Available",
            "degree": "Not Available",
            "skills": [],
            "projects": [],
            "experience": []
        }

    def repair_json_string(self, text):
        text = text.strip()
        if not text:
            return "{}"
            
        # Count braces and brackets
        open_braces = text.count("{")
        close_braces = text.count("}")
        open_brackets = text.count("[")
        close_brackets = text.count("]")
        
        # Balance quotes if odd number of quotes
        if text.count('"') % 2 != 0:
            text += '"'
            
        # Balance brackets first
        if open_brackets > close_brackets:
            text += "]" * (open_brackets - close_brackets)
            
        # Balance braces
        if open_braces > close_braces:
            if not text.endswith('"') and not text.endswith(']') and not text.endswith('}') and not text.endswith('null') and not text.endswith('true') and not text.endswith('false') and not text.isdigit():
                if text.endswith(','):
                    text = text[:-1]
            text += "}" * (open_braces - close_braces)
            
        return text

    def parse_profile_json(self, text):
        text = re.sub(r"```json", "", text)
        text = re.sub(r"```", "", text)
        text = text.strip()

        # Repair possibly truncated JSON from Ollama
        text = self.repair_json_string(text)

        parsed = {}
        try:
            parsed = json.loads(text)
        except Exception as e:
            logger.error(f"Failed to parse candidate JSON text: '{text}'. Error: {e}")

        default_profile = self.get_default_profile()

        # Sanitize and merge keys
        for key, default_val in default_profile.items():
            val = parsed.get(key)
            if val is None or val == "null" or val == "" or str(val).lower() == "none":
                parsed[key] = default_val
            elif isinstance(default_val, list):
                if not isinstance(val, list):
                    parsed[key] = [str(val)]
                else:
                    parsed[key] = [str(item).strip() for item in val if item]
            else:
                parsed[key] = str(val).strip()

        # Robust Heuristic Check to auto-fix swapped college and degree fields
        college = parsed.get("college", "Not Available")
        degree = parsed.get("degree", "Not Available")

        degree_keywords = [
            "b.tech", "btech", "m.tech", "mtech", "b.s", "bs", "ms", "m.s", "b.e", "be",
            "bachelor", "master", "phd", "p.h.d", "doctorate", "diploma", "b.sc", "bsc",
            "m.sc", "msc", "b.b.a", "bba", "m.b.a", "mba", "computer science", "information technology"
        ]
        college_keywords = ["college", "university", "institute", "school", "academy", "iit", "nit", "bits", "iiit"]

        is_college_actually_degree = False
        if college != "Not Available":
            coll_lower = college.lower()
            if any(keyword in coll_lower for keyword in degree_keywords):
                is_college_actually_degree = True

        is_degree_actually_college = False
        if degree != "Not Available":
            deg_lower = degree.lower()
            if any(keyword in deg_lower for keyword in college_keywords):
                is_degree_actually_college = True

        # Perform correction if they are reversed or if degree is "Not Available" while college holds degree text
        if is_college_actually_degree and (is_degree_actually_college or degree == "Not Available"):
            parsed["college"] = degree if degree != "Not Available" else "Not Available"
            parsed["degree"] = college

        return parsed
