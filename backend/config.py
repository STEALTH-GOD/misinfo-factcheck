import os
import torch
from dotenv import load_dotenv

load_dotenv()

class Config:
    # API Keys
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY', '')
    GOOGLE_CX = os.getenv('GOOGLE_CX', '')
    
    # Flask settings
    DEBUG = True
    HOST = '0.0.0.0'
    PORT = 5000
    
    # AI Model settings (simplified)
    SIMILARITY_MODEL_NAME = 'sentence-transformers/all-mpnet-base-v2'
    MAX_ARTICLE_CHARS = 3000
    SIMILARITY_THRESHOLD = 0.2
    
    # Search settings
    DEFAULT_SEARCH_RESULTS = 15
    FACT_CHECK_RESULTS = 5
    TIMEOUT = 10