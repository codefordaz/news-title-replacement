import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'
    
    # 爬蟲設定
    USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    REQUEST_TIMEOUT = 30
    
    # API 設定
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max request size

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///news_bias.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False