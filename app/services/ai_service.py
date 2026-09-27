from app.RAG.pipeline import ask_rag


class AIService:
    """
    Handles AI responses using the RAG system.
    """

    def __init__(self):
        pass

    def generate_response(
        self,
        user_message: str,
        session_id: str = "default"
    ) -> str:
        """
        Sends the customer's message through the RAG system
        and returns the assistant's response.
        """

        if not user_message:
            raise ValueError("User message cannot be empty.")

        response = ask_rag(
            user_message,
            session_id=session_id
        )

        return response.strip()