import weaviate
from .config import WEAVIATE_CLIENT_URL, OPENAI_API_KEY
from ..utils.weaviate_classes import default_class

db = weaviate.Client(
    url=WEAVIATE_CLIENT_URL,
    additional_headers={"X-OpenAI-Api-Key": OPENAI_API_KEY},
)