import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    SERPAPI_API_KEY = os.getenv('SERPAPI_API_KEY')  
    PORT = int(os.getenv('PORT', 5000))
    UPLOAD_FOLDER = '/tmp'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size