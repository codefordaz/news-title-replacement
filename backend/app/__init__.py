from flask import Flask
from flask_cors import CORS
from config.config import Config
from app.database import init_db
from flask_login import LoginManager

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
    # 初始化 Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'admin.login'

    @login_manager.user_loader
    def load_user(user_id):
        from app.models import Admin
        return Admin.query.get(int(user_id))

    # 註冊管理後台路由
    from app.admin import admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')





    
    # 註冊 API 路由
    from app.api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    return app