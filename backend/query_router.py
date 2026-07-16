class QueryRouter:
    def __init__(self):
        pass

    def detect_query_type(self, question):
        question = question.lower()

        # Questions about CGPA / marks
        if any(word in question for word in [
            "cgpa",
            "percentage",
            "10th",
            "12th",
            "marks"
        ]):
            return "academic"

        # Questions about skills
        if any(word in question for word in [
            "skill",
            "skills",
            "python",
            "java",
            "sql",
            "react",
            "machine learning",
            "deep learning"
        ]):
            return "skills"

        # Questions about projects
        if any(word in question for word in [
            "project",
            "projects",
            "built",
            "developed"
        ]):
            return "projects"

        # Comparison
        if any(word in question for word in [
            "compare",
            "difference",
            "better",
            "best"
        ]):
            return "comparison"

        return "semantic"
