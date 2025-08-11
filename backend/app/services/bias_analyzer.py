import re
from typing import List, Dict, Tuple

class BiasAnalyzer:
    def __init__(self):
        self.bias_patterns = [
            {
                'id': 'occupation_label',
                'pattern': r'女公關|酒店小姐|酒店妹|坐檯小姐',
                'replacement': '女性',
                'explanation': '使用職業標籤暗示受害者品行，轉移焦點',
                'severity': 'high'
            },
            {
                'id': 'lifestyle_judgment',
                'pattern': r'風塵女子|夜生活|複雜交友|私生活混亂',
                'replacement': '受害者',
                'explanation': '以生活型態進行道德評判',
                'severity': 'high'
            },
            {
                'id': 'crime_minimization',
                'pattern': r'情殺|恐怖情人|為情所困',
                'replacement': '謀殺案',
                'explanation': '淡化暴力犯罪的嚴重性',
                'severity': 'high'
            },
            {
                'id': 'relationship_focus',
                'pattern': r'感情糾紛|分分合合|藕斷絲連',
                'replacement': '案件',
                'explanation': '將焦點從犯罪行為轉移到關係問題',
                'severity': 'medium',
                'context_required': True
            },
            {
                'id': 'appearance_judgment',
                'pattern': r'衣著暴露|穿著清涼|打扮性感|濃妝豔抹',
                'replacement': '',
                'explanation': '以外表評判暗示受害者「引誘」加害',
                'severity': 'high'
            },
            {
                'id': 'victim_behavior',
                'pattern': r'深夜外出|獨自一人|單獨會面|夜歸',
                'replacement': '',
                'explanation': '檢討受害者行為而非加害者暴力',
                'severity': 'medium',
                'context_required': True
            },
            {
                'id': 'implied_responsibility',
                'pattern': r'曾有過節|積怨已久|早有嫌隙',
                'replacement': '',
                'explanation': '暗示受害者部分責任',
                'severity': 'medium'
            }
        ]
    
    def analyze(self, title: str, content: str) -> Dict:
        """分析文章中的偏見"""
        full_text = f"{title} {content}"
        found_biases = []
        
        # 檢測偏見
        for bias in self.bias_patterns:
            matches = self._find_matches(full_text, bias)
            if matches:
                if not bias.get('context_required') or self._check_context(full_text, bias):
                    found_biases.append({
                        'id': bias['id'],
                        'pattern': bias['pattern'],
                        'explanation': bias['explanation'],
                        'severity': bias['severity'],
                        'matches': matches
                    })
        
        # 生成修正版本
        revised_title, revised_content = self._generate_revised_version(
            title, content, found_biases
        )
        
        # 標記原始文本中的偏見
        marked_title = self._mark_biases(title, found_biases)
        marked_content = self._mark_biases(content, found_biases)
        
        return {
            'original': {
                'title': title,
                'content': content,
                'marked_title': marked_title,
                'marked_content': marked_content
            },
            'revised': {
                'title': revised_title,
                'content': revised_content
            },
            'biases': found_biases,
            'bias_count': len(found_biases)
        }
    
    def _find_matches(self, text: str, bias: Dict) -> List[str]:
        """找出文本中符合偏見模式的詞彙"""
        pattern = re.compile(bias['pattern'])
        matches = pattern.findall(text)
        return list(set(matches))  # 去重
    
    def _check_context(self, text: str, bias: Dict) -> bool:
        """檢查上下文是否確實存在偏見"""
        negative_context_pattern = r'應該|不應該|導致|引發|造成|所以'
        return bool(re.search(negative_context_pattern, text))
    
    def _generate_revised_version(self, title: str, content: str, 
                                  found_biases: List[Dict]) -> Tuple[str, str]:
        """生成修正版本"""
        revised_title = title
        revised_content = content
        
        for bias_info in found_biases:
            bias = next((b for b in self.bias_patterns 
                        if b['id'] == bias_info['id']), None)
            if not bias:
                continue
            
            pattern = re.compile(bias['pattern'])
            
            if bias['replacement']:
                revised_title = pattern.sub(bias['replacement'], revised_title)
                revised_content = pattern.sub(bias['replacement'], revised_content)
            else:
                # 如果沒有替代詞，移除包含偏見的句子
                sentences = revised_content.split('。')
                filtered_sentences = []
                for sentence in sentences:
                    if not pattern.search(sentence):
                        filtered_sentences.append(sentence)
                revised_content = '。'.join(filtered_sentences)
        
        # 如果標題包含嚴重偏見，重寫標題
        if any(b['severity'] == 'high' for b in found_biases):
            revised_title = self._rewrite_title(revised_title)
        
        return revised_title, revised_content
    
    def _rewrite_title(self, title: str) -> str:
        """重寫標題"""
        if '殺' in title or '亡' in title:
            return '女性遭暴力攻擊身亡 警方積極偵辦中'
        elif '傷' in title:
            return '女性遭暴力攻擊受傷 嫌犯已遭逮捕'
        return title
    
    def _mark_biases(self, text: str, found_biases: List[Dict]) -> str:
        """在文本中標記偏見"""
        marked_text = text
        
        for bias_info in found_biases:
            for match in bias_info['matches']:
                # 使用 HTML 標記偏見
                replacement = f'<span class="bias-highlight" data-explanation="{bias_info["explanation"]}">{match}</span>'
                marked_text = marked_text.replace(match, replacement)
        
        return marked_text