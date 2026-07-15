import os
from dotenv import load_dotenv
load_dotenv()

class Settings:
    OPENAI_API_KEY=os.getenv("OPENAI_API_KEY")
    QURANT_URL=os.getenv("QDRANT_CLUSTER_ENDPOINT")
    QURANT_API_KEY=os.getenv("QDRANT_API_KEY")
    QDRANT_COLLECTION="enterprise_rag"

    GROQ_API_KEY=os.getenv("GROQ_API_KEY")
    GROQ_MODEL="llama-3.3-70b-versatile"

settings=Settings()
