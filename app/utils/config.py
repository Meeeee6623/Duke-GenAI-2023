import os

WEAVIATE_CLIENT_URL = ""
WEAVIATE_API_KEY = os.environ["WEAVIATE_API_KEY"]

MONGODB_URL = 'mongodb+srv://awesome:uZZnSgXroGrSpMR@cluster0.pwoojny.mongodb.net/?retryWrites=true&w=majority'
MONGODB_DB = 'ai-server'
MONGODB_COLLECTION = 'prompts'

OPENAI_API_KEY = os.environ['OPENAI_API_KEY']