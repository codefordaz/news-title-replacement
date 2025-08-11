from flask import jsonify, request
from app.api import api_bp
from app.services.news_scraper import NewsScraper
from app.services.bias_analyzer import BiasAnalyzer
from app.utils.validators import validate_url

@api_bp.route('/health', methods=['GET'])
def health_check():
    """健康檢查端點"""
    return jsonify({
        'status': 'healthy',
        'service': 'news-bias-remover-api'
    })

@api_bp.route('/fetch-news', methods=['POST'])
def fetch_news():
    """從 URL 抓取新聞內容"""
    try:
        data = request.get_json()
        url = data.get('url')
        
        if not url:
            return jsonify({
                'error': '請提供新聞網址'
            }), 400
        
        if not validate_url(url):
            return jsonify({
                'error': '無效的網址格式'
            }), 400
        
        # 抓取新聞
        scraper = NewsScraper()
        news_data = scraper.scrape(url)
        
        if not news_data:
            return jsonify({
                'error': '無法從此網址抓取內容'
            }), 404
        
        return jsonify({
            'success': True,
            'data': news_data
        })
        
    except Exception as e:
        return jsonify({
            'error': f'處理時發生錯誤：{str(e)}'
        }), 500

@api_bp.route('/analyze', methods=['POST'])
def analyze_bias():
    """分析新聞偏見"""
    try:
        data = request.get_json()
        title = data.get('title', '')
        content = data.get('content', '')
        
        if not title and not content:
            return jsonify({
                'error': '請提供標題或內容'
            }), 400
        
        # 分析偏見
        analyzer = BiasAnalyzer()
        analysis_result = analyzer.analyze(title, content)
        
        return jsonify({
            'success': True,
            'data': analysis_result
        })
        
    except Exception as e:
        return jsonify({
            'error': f'分析時發生錯誤：{str(e)}'
        }), 500

@api_bp.route('/feedback', methods=['POST'])
def submit_feedback():
    """提交使用者回饋"""
    try:
        data = request.get_json()
        
        # TODO: 儲存回饋到資料庫
        # 目前先回傳成功訊息
        
        return jsonify({
            'success': True,
            'message': '感謝您的回饋'
        })
        
    except Exception as e:
        return jsonify({
            'error': f'提交回饋時發生錯誤：{str(e)}'
        }), 500