import weaviate
from .config import WEAVIATE_CLIENT_URL, OPENAI_API_KEY
from ..utils.weaviate_classes import default_class

db = weaviate.Client(
    url=WEAVIATE_CLIENT_URL,
    additional_headers={"X-OpenAI-Api-Key": OPENAI_API_KEY},
)


def create_default_class(class_name: str):
    """
    Create a class in Weaviate
    """
    new_class = default_class
    new_class["class"] = class_name
    try:
        db.schema.create_class(new_class)
    except Exception as e:
        print(e)
        return {"error": "Class already exists"}
    return {"response": "Class created successfully"}