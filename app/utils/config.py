import os
from dotenv import load_dotenv

load_dotenv()

WEAVIATE_CLIENT_URL = "http://54.81.235.123:8080/v1"

MONGODB_URL = os.environ["MONGODB_URL"]
MONGODB_DB = 'ai-server'
MONGODB_COLLECTION = 'prompts'

OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
