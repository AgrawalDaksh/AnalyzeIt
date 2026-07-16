import ollama
from .matcher import CandidateMatcher
from .config import OLLAMA_EMBED_MODEL, TOP_K_DEFAULT, TOP_K_SKILLS, TOP_K_COMPARISON, TOP_K_ACADEMIC

class RAGEngine:
    def __init__(self, embedding_model=OLLAMA_EMBED_MODEL):
        self.embedding_model = embedding_model

    def search(self, question, resume_embeddings, candidate_metadata, query_type):
        """
        Performs semantic search across candidate resumes.
        Determines target matching count top_k based on query intent.
        """
        if query_type == "academic":
            top_k = TOP_K_ACADEMIC
        elif query_type == "comparison":
            top_k = TOP_K_COMPARISON
        elif query_type == "skills":
            top_k = TOP_K_SKILLS
        else:
            top_k = TOP_K_DEFAULT

        question_lower = question.lower()
        matched_resumes = []

        # 1. Exact Name Matching Check
        for filename, metadata in candidate_metadata.items():
            first_name = metadata.get("first_name", "")
            full_name = metadata.get("full_name_lower", "")

            if first_name and first_name in question_lower:
                matched_resumes.append(filename)
                continue

            if full_name and full_name in question_lower:
                matched_resumes.append(filename)

        # If name matches are found, prioritize them
        if matched_resumes:
            return [
                (filename, 1.0)
                for filename in matched_resumes
            ]

        # 2. Semantic Embedding Search
        query_embedding_response = ollama.embed(
            model=self.embedding_model,
            input=question
        )
        query_embedding = query_embedding_response["embeddings"][0]

        scores = []
        for filename, embedding in resume_embeddings.items():
            score = CandidateMatcher.cosine_similarity(
                query_embedding,
                embedding
            )
            scores.append((filename, score))

        scores.sort(
            key=lambda x: x[1],
            reverse=True
        )

        return scores[:top_k]
