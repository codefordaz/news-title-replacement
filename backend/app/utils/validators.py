import re
from urllib.parse import urlparse

def validate_url(url: str) -> bool:
    """驗證 URL 格式"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def is_news_url(url: str) -> bool:
    """檢查是否為新聞網站 URL"""
    # 可以加入已知的新聞網站域名白名單
    news_domains = [
        'cna.com.tw',
        'udn.com',
        'chinatimes.com',
        'ltn.com.tw',
        'ettoday.net',
        'tvbs.com.tw',
        'setn.com',
        'mirrormedia.mg',
        'storm.mg',
        'thenewslens.com',
        'cw.com.tw',
        'bnext.com.tw'
    ]
    
    try:
        domain = urlparse(url).netloc.lower()
        return any(news_domain in domain for news_domain in news_domains)
    except:
        return False