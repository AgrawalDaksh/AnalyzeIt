import numpy as np
import re
import datetime
from .config import SKILL_WEIGHT, EXPERIENCE_WEIGHT, EDUCATION_WEIGHT, CGPA_WEIGHT, PROJECT_WEIGHT

class CandidateMatcher:
    def __init__(self):
        pass

    @staticmethod
    def cosine_similarity(a, b):
        a = np.array(a)
        b = np.array(b)
        denom = np.linalg.norm(a) * np.linalg.norm(b)
        if denom == 0:
            return 0.0
        return np.dot(a, b) / denom

    def _parse_candidate_experience(self, experience_list, raw_text=None):
        import datetime
        months_map = {
            "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
            "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
            "january": 1, "february": 2, "march": 3, "april": 4, "june": 6,
            "july": 7, "august": 8, "september": 9, "october": 10, "november": 11, "december": 12
        }

        def calculate_years(exp_entries):
            years_sum = 0.0
            for exp in exp_entries:
                if not exp:
                    continue
                exp_str = str(exp).lower().strip()
                
                # Check explicit duration mentions
                years_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:year|yr)', exp_str)
                months_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:month|mo)', exp_str)
                
                if years_match:
                    years_sum += float(years_match.group(1))
                    continue
                elif months_match:
                    years_sum += float(months_match.group(1)) / 12.0
                    continue
                    
                # Match: (optional month) (year) (separator) (optional month) (year or present)
                range_match = re.search(
                    r'(?:([a-z]{3,10})\s+)?(\d{4})\s*(?:-|-|–|—|to|until)\s*(?:([a-z]{3,10})\s+)?(\d{4}|present|current|now)',
                    exp_str
                )
                
                if range_match:
                    start_month_str = range_match.group(1)
                    start_year = int(range_match.group(2))
                    end_month_str = range_match.group(3)
                    end_val = range_match.group(4)
                    
                    end_year = datetime.datetime.now().year if end_val in ['present', 'current', 'now'] else int(end_val)
                    
                    start_month = 1
                    if start_month_str:
                        for mname, mnum in months_map.items():
                            if mname in start_month_str:
                                start_month = mnum
                                break
                                
                    end_month = 12
                    if end_val in ['present', 'current', 'now']:
                        end_month = datetime.datetime.now().month
                    elif end_month_str:
                        for mname, mnum in months_map.items():
                            if mname in end_month_str:
                                end_month = mnum
                                break
                                
                    total_months = (end_year - start_year) * 12 + (end_month - start_month) + 1
                    if total_months <= 0:
                        total_months = 1
                    years_sum += max(0.0, total_months / 12.0)
            return years_sum

        # Calculate using extracted experience array first
        total_years = 0.0
        if experience_list and isinstance(experience_list, list):
            total_years = calculate_years(experience_list)

        # Fallback: if calculated years is 0.0 and raw_text is provided, extract experience text section and parse ranges directly!
        if total_years == 0.0 and raw_text:
            # Clean and look for headings
            lower_text = raw_text.lower()
            headings = ["experience", "work experience", "professional experience", "employment history", "internship"]
            start_idx = -1
            for heading in headings:
                idx = lower_text.find(heading)
                if idx != -1:
                    start_idx = idx + len(heading)
                    break
                    
            exp_section_text = raw_text
            if start_idx != -1:
                # The section ends at the next major heading
                end_headings = ["projects", "education", "skills", "certifications", "achievements", "interests", "languages"]
                end_idx = len(raw_text)
                for heading in end_headings:
                    idx = lower_text.find(heading, start_idx)
                    if idx != -1 and idx < end_idx:
                        end_idx = idx
                exp_section_text = raw_text[start_idx:end_idx]

            # Find all date range entries in the extracted experience section
            lines = [l.strip() for l in exp_section_text.split("\n") if l.strip()]
            total_years = calculate_years(lines)

        return total_years

    def _parse_job_experience(self, min_exp_val):
        if min_exp_val is None:
            return 0.0
        min_exp_str = str(min_exp_val).lower()
        match = re.search(r'(\d+(?:\.\d+)?)', min_exp_str)
        if match:
            return float(match.group(1))
        return 0.0

    def _parse_cgpa(self, val):
        if val is None:
            return None
        try:
            # Extract number from string like "9.2/10" or "8.5"
            match = re.search(r'(\d+(?:\.\d+)?)', str(val))
            if match:
                return float(match.group(1))
        except (ValueError, TypeError):
            pass
        return None

    def rank(self, profiles, job, raw_resumes=None):
        """
        Ranks candidate profiles against a Job Description using a weighted candidate matcher.
        Overall Score (100%):
        - Skills: 40%
        - Experience: 25%
        - Education: 15%
        - CGPA: 10%
        - Projects: 10%
        """
        ranked_candidates = []
        
        required_skills = [s.strip().lower() for s in job.get("required_skills", []) if s]
        preferred_skills = [s.strip().lower() for s in job.get("preferred_skills", []) if s]
        min_exp_val = job.get("minimum_experience")
        target_exp = self._parse_job_experience(min_exp_val)
        required_degree = str(job.get("degree") or "").strip().lower()
        min_cgpa = self._parse_cgpa(job.get("minimum_cgpa"))

        for filename, profile in profiles.items():
            candidate_skills = [s.strip().lower() for s in profile.get("skills", []) if s]
            
            # 1. Skills Match (40% of Overall)
            skills_score = 0.0
            matched_req = []
            matched_pref = []
            
            if required_skills:
                matched_req = list(set(required_skills) & set(candidate_skills))
                req_score = (len(matched_req) / len(required_skills)) * 100.0
            else:
                req_score = 100.0
                
            if preferred_skills:
                matched_pref = list(set(preferred_skills) & set(candidate_skills))
                pref_score = (len(matched_pref) / len(preferred_skills)) * 100.0
            else:
                pref_score = 100.0
                
            # If both lists were specified, weight is 70% required / 30% preferred
            if required_skills and preferred_skills:
                skills_score = (req_score * 0.7) + (pref_score * 0.3)
            elif required_skills:
                skills_score = req_score
            elif preferred_skills:
                skills_score = pref_score
            else:
                skills_score = 100.0
                
            # 2. Experience Match (25% of Overall)
            raw_resume_text = raw_resumes.get(filename) if raw_resumes else None
            cand_exp = self._parse_candidate_experience(profile.get("experience", []), raw_text=raw_resume_text)
            if target_exp <= 0:
                experience_score = 100.0
            else:
                experience_score = min(100.0, (cand_exp / target_exp) * 100.0)
                
            # 3. Education Match (15% of Overall)
            cand_degree = str(profile.get("degree") or "").strip().lower()
            if not required_degree:
                education_score = 100.0
            elif required_degree in cand_degree:
                education_score = 100.0
            else:
                # Substring check of common degree levels: e.g. check if candidate degree mentions btech, mtech, phd, etc.
                education_score = 0.0
                # Simple level check: if job requires BTech/BE and candidate has MTech/ME or PhD, mark as 100%
                for deg in ["btech", "b.tech", "be", "b.e.", "bachelors", "bachelor"]:
                    if deg in required_degree and any(adv in cand_degree for adv in ["mtech", "m.tech", "me", "m.e.", "masters", "master", "phd"]):
                        education_score = 100.0
                        break
                # Partial match (e.g. computer science or engineering mentions)
                if education_score == 0.0 and any(keyword in cand_degree for keyword in required_degree.split()):
                    education_score = 50.0

            # 4. CGPA Match (10% of Overall)
            cand_cgpa = self._parse_cgpa(profile.get("cgpa"))
            if min_cgpa is None:
                cgpa_score = 100.0
            elif cand_cgpa is None:
                cgpa_score = 0.0
            elif cand_cgpa >= min_cgpa:
                cgpa_score = 100.0
            else:
                cgpa_score = max(0.0, (cand_cgpa / min_cgpa) * 100.0)
                
            # 5. Projects Match (10% of Overall)
            projects_list = profile.get("projects", [])
            num_projects = len(projects_list) if isinstance(projects_list, list) else 0
            if num_projects >= 3:
                projects_score = 100.0
            elif num_projects == 2:
                projects_score = 80.0
            elif num_projects == 1:
                projects_score = 50.0
            else:
                projects_score = 0.0
                
            # Calculate Weighted Overall Score
            overall_score = (
                (skills_score * SKILL_WEIGHT) +
                (experience_score * EXPERIENCE_WEIGHT) +
                (education_score * EDUCATION_WEIGHT) +
                (cgpa_score * CGPA_WEIGHT) +
                (projects_score * PROJECT_WEIGHT)
            )
            
            ranked_candidates.append({
                "filename": filename,
                "name": profile.get("name") or filename.replace(".pdf", ""),
                "score": round(overall_score, 2),
                "breakdown": {
                    "skills": round(skills_score, 2),
                    "experience": round(experience_score, 2),
                    "education": round(education_score, 2),
                    "cgpa": round(cgpa_score, 2),
                    "projects": round(projects_score, 2)
                },
                "cand_experience_years": round(cand_exp, 1),
                "cand_cgpa": cand_cgpa,
                "matched_required": matched_req,
                "matched_preferred": matched_pref,
                "missing_required": list(set(required_skills) - set(candidate_skills))
            })
            
        ranked_candidates.sort(key=lambda x: x["score"], reverse=True)
        return ranked_candidates
