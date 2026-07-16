import ollama
import json
import re
from .config import OLLAMA_CHAT_MODEL

class InterviewGenerator:
    def __init__(self, model=OLLAMA_CHAT_MODEL):
        self.model = model

    def generate_questions(self, candidate_profile, job_profile, difficulty="Medium"):
        """
        Generates tailored interview questions based on candidate profile, job description,
        and target difficulty level (Easy, Medium, Hard).
        Returns a structured dictionary of question groups, ideal answers, and evaluation criteria.
        """
        prompt = f"""
        You are a principal technical interviewer and HR analyst.
        
        Generate a set of tailored interview questions for a candidate based ONLY on the provided structured profile and the job description requirements.
        
        Difficulty Level: {difficulty}
        
        CRITICAL RULES:
        1. Generate exactly 2 questions per category (Technical, Behavioral, Project-based, and Missing Skills).
        2. If candidate has no missing skills, base 'missing_skill' questions on the most critical required skills for the job.
        3. For every question, generate a detailed 'ideal_answer' and specific 'criteria' for evaluation.
        4. Return ONLY valid JSON matching the format below.
        5. Do NOT include markdown blocks like ```json or ```.
        
        Candidate Profile:
        {json.dumps(candidate_profile, indent=2)}
        
        Job description requirements:
        {json.dumps(job_profile, indent=2)}
        
        Return EXACTLY this JSON structure:
        {{
          "technical": [
            {{
              "question": "technical question 1",
              "ideal_answer": "ideal answer explanation",
              "criteria": "evaluation criteria detail"
            }},
            ...
          ],
          "behavioral": [
            {{
              "question": "behavioral question 1",
              "ideal_answer": "ideal answer explanation",
              "criteria": "evaluation criteria detail"
            }},
            ...
          ],
          "project": [
            {{
              "question": "project-based question 1 related to candidate's listed projects",
              "ideal_answer": "ideal answer explanation",
              "criteria": "evaluation criteria detail"
            }},
            ...
          ],
          "missing_skill": [
            {{
              "question": "question assessing candidate's familiarity or learning capacity for job skills not explicitly listed in their profile",
              "ideal_answer": "ideal answer explanation",
              "criteria": "evaluation criteria detail"
            }},
            ...
          ]
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
                "technical": [
                    {
                        "question": "Could you explain your technical background and experience with the core requirements of this role?",
                        "ideal_answer": "Candidate should articulate experience mapping to the core tech stack requirements.",
                        "criteria": "Clarity of expression, direct stack alignment, depth of technical terminology."
                    }
                ],
                "behavioral": [
                    {
                        "question": "Describe a scenario where you had to adapt quickly to a major stack or timeline change.",
                        "ideal_answer": "Explanation using the STAR method highlighting problem, action, and positive resolution.",
                        "criteria": "Problem-solving adaptability, teamwork style, stress management."
                    }
                ],
                "project": [
                    {
                        "question": "Walk through one of your listed projects. What were the technical hurdles and design patterns chosen?",
                        "ideal_answer": "System design walkthrough explaining choices, architectural patterns, and final output metric.",
                        "criteria": "Architectural depth, engineering standards, results validation."
                    }
                ],
                "missing_skill": [
                    {
                        "question": "If you needed to learn a new framework or tool for a deadline, what is your acceleration methodology?",
                        "ideal_answer": "Structured self-education methodology including documentation study, sandbox builds, and peer guidance.",
                        "criteria": "Learning speed, autonomy, utilization of resources."
                    }
                ]
            }
