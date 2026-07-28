import os
from dotenv import load_dotenv
from groq import AsyncGroq

# Ensure environment variables are loaded
load_dotenv()

_groq_client_instance = None

def get_groq_client() -> AsyncGroq:
    """
    Returns a singleton instance of the official AsyncGroq client with generous timeout & retries.
    Direct API communication without any agent frameworks.
    """
    global _groq_client_instance
    if _groq_client_instance is None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError(
                "GROQ_API_KEY environment variable is missing. "
                "Please set GROQ_API_KEY in backend/.env"
            )
        # Increased timeout to 120s and set max_retries to 3 for robust network stability
        _groq_client_instance = AsyncGroq(
            api_key=api_key,
            timeout=120.0,
            max_retries=3
        )
    return _groq_client_instance
