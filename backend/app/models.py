from datetime import datetime
from app.database import db

class NewsAnalysis(db.Model):
    """新聞分析記錄"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500), nullable=False)
    content = db.Column(db.Text, nullable=False)
    source_url = db.Column(db.String(500))
    bias_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 關聯到回饋
    feedbacks = db.relationship('Feedback', backref='analysis', lazy=True)

class BiasPattern(db.Model):
    """偏見模式"""
    id = db.Column(db.Integer, primary_key=True)
    pattern_id = db.Column(db.String(100), unique=True, nullable=False)
    pattern_text = db.Column(db.String(200), nullable=False)
    explanation = db.Column(db.String(500))
    severity = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Feedback(db.Model):
    """使用者回饋"""
    id = db.Column(db.Integer, primary_key=True)
    analysis_id = db.Column(db.Integer, db.ForeignKey('news_analysis.id'))
    feedback_type = db.Column(db.String(50))  # 'bias_rating' or 'user_highlight'
    content = db.Column(db.Text)
    rating = db.Column(db.String(20))  # 'extreme', 'neutral', 'correct'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)