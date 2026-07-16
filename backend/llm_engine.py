import ollama
from .config import OLLAMA_CHAT_MODEL

class LLMEngine:
    def __init__(self, model=OLLAMA_CHAT_MODEL):
        self.model = model

    def generate_answer(self, question, top_matches, resumes):
        """
        Generates final AI response utilizing retrieved resume context.
        """
        context = ""
        for filename, score in top_matches:
            context += f"\nFILE: {filename}\n"
            context += resumes.get(filename, "")
            context += "\n\n"

        response = ollama.chat(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": f"""
You are a resume assistant.

STRICT RULES:

1. Detect the language of the user's question.
2. Answer ONLY in that language.
3. Use ONLY the resume information below.

Resume Information:

{context}

Question:
{question}

Answer:
"""
                }
            ]
        )

        return response["message"]["content"]
