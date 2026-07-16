import re

class ProfileEngine:
    def __init__(self):
        pass

    def query(self, candidate_profiles, question):
        """
        Executes structured searches on candidate profiles for specific questions
        like highest CGPA, highest percentage, skill sets, and degrees.
        """
        question = question.lower()
        profiles = list(candidate_profiles.values())
        if not profiles:
            return None

        # 1. Highest CGPA
        if "highest" in question and ("cgpa" in question or "gpa" in question):
            valid_profiles = []
            for profile in profiles:
                try:
                    if profile.get("cgpa") is not None:
                        # Clean CGPA string like "9.2/10" or "8.5"
                        match = re.search(r'(\d+(?:\.\d+)?)', str(profile["cgpa"]))
                        if match:
                            cgpa = float(match.group(1))
                            valid_profiles.append((cgpa, profile))
                except (ValueError, TypeError):
                    pass
            if valid_profiles:
                best = max(valid_profiles, key=lambda x: x[0])[1]
                return {
                    "type": "profile",
                    "answer": f'{best.get("name") or "Candidate"} has the highest CGPA ({best.get("cgpa")}).'
                }

        # 2. Highest Percentage (10th or 12th)
        if "highest" in question and ("percentage" in question or "marks" in question or "percent" in question):
            is_tenth = "10" in question or "tenth" in question
            is_twelfth = "12" in question or "twelfth" in question
            
            field = None
            field_label = ""
            if is_tenth:
                field = "tenth_percentage"
                field_label = "10th Percentage"
            elif is_twelfth:
                field = "twelfth_percentage"
                field_label = "12th Percentage"
            else:
                # Default to 12th if unspecified
                field = "twelfth_percentage"
                field_label = "12th Percentage"
                
            valid_profiles = []
            for profile in profiles:
                val = profile.get(field)
                if val is None and not is_tenth and not is_twelfth:
                    val = profile.get("tenth_percentage")
                    field_label = "10th/12th Percentage"
                if val is not None:
                    try:
                        clean_val = float(str(val).replace("%", "").strip())
                        valid_profiles.append((clean_val, profile, val))
                    except (ValueError, TypeError):
                        pass
            if valid_profiles:
                best_score, best_prof, orig_val = max(valid_profiles, key=lambda x: x[0])
                return {
                    "type": "profile",
                    "answer": f'{best_prof.get("name") or "Candidate"} has the highest {field_label} ({orig_val}).'
                }

        # 3. Dynamic Skill Search
        # Gather all skills mentioned in candidate profiles to scan for matches in query
        all_skills = set()
        for p in profiles:
            for s in p.get("skills", []):
                if s:
                    all_skills.add(s.strip().lower())
                    
        # Check if any skill keyword is present in the question
        mentioned_skills = []
        for skill in all_skills:
            # Word boundary matching to avoid partial matches (e.g. 'c' matching 'cgpa')
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, question):
                mentioned_skills.append(skill)
                
        # Ensure python is added if directly asked (e.g. "Who knows python?")
        if "python" in question and "python" not in mentioned_skills:
            mentioned_skills.append("python")
            
        if mentioned_skills:
            skill_to_people = {}
            for skill in mentioned_skills:
                people = []
                for profile in profiles:
                    cand_skills = [s.lower() for s in profile.get("skills", []) if s]
                    if skill in cand_skills:
                        people.append(profile.get("name") or "Candidate")
                if people:
                    skill_to_people[skill] = people
                    
            if skill_to_people:
                answers = []
                for skill, people in skill_to_people.items():
                    answers.append(f"{', '.join(people)} know(s) {skill.capitalize()}")
                return {
                    "type": "profile",
                    "answer": ". ".join(answers) + "."
                }

        # 4. Degree Search
        degrees_to_check = ["btech", "mtech", "b.tech", "m.tech", "be", "me", "bsc", "msc", "phd", "bachelor", "master"]
        mentioned_degrees = [d for d in degrees_to_check if d in question]
        if mentioned_degrees:
            degree_to_people = {}
            for deg in mentioned_degrees:
                people = []
                for profile in profiles:
                    cand_deg = str(profile.get("degree") or "").lower()
                    if deg in cand_deg:
                        people.append(profile.get("name") or "Candidate")
                if people:
                    degree_to_people[deg] = people
            if degree_to_people:
                answers = []
                for deg, people in degree_to_people.items():
                    answers.append(f"{', '.join(people)} has/have a {deg.upper()} degree")
                return {
                    "type": "profile",
                    "answer": ". ".join(answers) + "."
                }

        return None
