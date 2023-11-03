import weaviate
from config import WEAVIATE_CLIENT_URL, WEAVIATE_API_KEY, OPENAI_API_KEY

db = weaviate.Client(
    url=WEAVIATE_CLIENT_URL,
    auth_client_secret=weaviate.AuthApiKey(WEAVIATE_API_KEY),
    additional_headers={"X-OpenAI-Api-Key": OPENAI_API_KEY},
)



