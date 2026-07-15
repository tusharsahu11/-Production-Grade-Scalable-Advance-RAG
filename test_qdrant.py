from qdrant_client import QdrantClient
from app.config import settings

print("URL:", settings.QURANT_URL)
print("Collection:", settings.QDRANT_COLLECTION)

client = QdrantClient(
    url=settings.QURANT_URL,
    api_key=settings.QURANT_API_KEY,
)

print("Client Created")

print(client.get_collections())