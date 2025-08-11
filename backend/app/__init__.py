from flask import Flask
from flask_cors import CORS
from config.config import Config
from app.database import init_db

def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # 啟用 CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:*", "http://127.0.0.1:*",  "https://spiffy-kataifi-bc6cd2.netlify.app" ],
            "methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": ["Content-Type"]
        }
    })
    init_db(app)
    
    # 註冊 API 路由
    from app.api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    return app