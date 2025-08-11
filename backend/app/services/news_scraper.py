import requests
from bs4 import BeautifulSoup
# from newspaper import Article
from flask import current_app
import re

class NewsScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': current_app.config.get('USER_AGENT', 
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        }
        self.timeout = current_app.config.get('REQUEST_TIMEOUT', 30)
    
    def scrape(self, url):
        """主要的爬蟲方法"""
        try:
            # # 先嘗試使用 newspaper3k
            # article = self._scrape_with_newspaper(url)
            # if article:
            #     return article
            
            # 如果失敗，使用 BeautifulSoup
            return self._scrape_with_beautifulsoup(url)
            
        except Exception as e:
            print(f"爬取錯誤: {str(e)}")
            return None
    
    def _scrape_with_newspaper(self, url):
        """使用 newspaper3k 爬取"""
        try:
            article = Article(url, language='zh')
            article.download()
            article.parse()
            
            if article.title and article.text:
                return {
                    'title': article.title,
                    'content': article.text,
                    'authors': article.authors,
                    'publish_date': str(article.publish_date) if article.publish_date else None,
                    'source': url
                }
        except:
            pass
        return None
    
    def _scrape_with_beautifulsoup(self, url):
        """使用 BeautifulSoup 爬取"""
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 嘗試各種常見的標題選擇器
            title = None
            title_selectors = [
                'h1',
                'h1.article-title',
                'h1.news-title',
                'h1.title',
                'meta[property="og:title"]',
                'title'
            ]
            
            for selector in title_selectors:
                element = soup.select_one(selector)
                if element:
                    if selector.startswith('meta'):
                        title = element.get('content', '')
                    else:
                        title = element.get_text(strip=True)
                    if title:
                        break
            
            # 嘗試各種常見的內容選擇器
            content = None
            content_selectors = [
                'article',
                'div.article-content',
                'div.news-content',
                'div.content',
                'div.story-body',
                'div[itemprop="articleBody"]',
                'main'
            ]
            
            for selector in content_selectors:
                element = soup.select_one(selector)
                if element:
                    # 移除腳本和樣式
                    for tag in element(['script', 'style']):
                        tag.decompose()
                    
                    # 取得段落文字
                    paragraphs = element.find_all('p')
                    if paragraphs:
                        content = '\n'.join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])
                        if content:
                            break
            
            # 如果還是找不到內容，嘗試取得所有段落
            if not content:
                all_paragraphs = soup.find_all('p')
                content_parts = []
                for p in all_paragraphs:
                    text = p.get_text(strip=True)
                    if len(text) > 30:  # 過濾太短的段落
                        content_parts.append(text)
                if len(content_parts) > 3:  # 至少要有幾個段落
                    content = '\n'.join(content_parts)
            
            if title and content:
                return {
                    'title': self._clean_text(title),
                    'content': self._clean_text(content),
                    'source': url
                }
                
        except Exception as e:
            print(f"BeautifulSoup 爬取錯誤: {str(e)}")
        
        return None
    
    def _clean_text(self, text):
        """清理文字"""
        if not text:
            return ''
        
        # 移除多餘的空白和換行
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\n+', '\n', text)
        
        return text.strip()