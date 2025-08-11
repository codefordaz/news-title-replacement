// 偏見檢測模式
const biasPatterns = [
    {
        id: 'occupation_label',
        pattern: /女公關|酒店小姐|酒店妹|坐檯小姐/g,
        replacement: '女性',
        explanation: '使用職業標籤暗示受害者品行，轉移焦點',
        severity: 'high'
    },
    {
        id: 'lifestyle_judgment',
        pattern: /風塵女子|夜生活|複雜交友|私生活混亂/g,
        replacement: '受害者',
        explanation: '以生活型態進行道德評判',
        severity: 'high'
    },
    {
        id: 'crime_minimization',
        pattern: /情殺|恐怖情人|為情所困/g,
        replacement: '謀殺案',
        explanation: '淡化暴力犯罪的嚴重性',
        severity: 'high'
    },
    {
        id: 'relationship_focus',
        pattern: /感情糾紛|分分合合|藕斷絲連/g,
        replacement: '案件',
        explanation: '將焦點從犯罪行為轉移到關係問題',
        severity: 'medium',
        contextRequired: true
    },
    {
        id: 'appearance_judgment',
        pattern: /衣著暴露|穿著清涼|打扮性感|濃妝豔抹/g,
        replacement: '',
        explanation: '以外表評判暗示受害者「引誘」加害',
        severity: 'high'
    },
    {
        id: 'victim_behavior',
        pattern: /深夜外出|獨自一人|單獨會面|夜歸/g,
        replacement: '',
        explanation: '檢討受害者行為而非加害者暴力',
        severity: 'medium',
        contextRequired: true
    },
    {
        id: 'implied_responsibility',
        pattern: /曾有過節|積怨已久|早有嫌隙/g,
        replacement: '',
        explanation: '暗示受害者部分責任',
        severity: 'medium'
    }
];

// 儲存分析結果和評分
let analysisResults = {};
let userFeedback = [];

function switchTab(tabName) {
    document.querySelectorAll('.tab').forEach(tab => {
        tab.classList.remove('active');
    });
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });

    if (tabName === 'url') {
        document.querySelector('.tab:first-child').classList.add('active');
        document.getElementById('urlTab').classList.add('active');
    } else {
        document.querySelector('.tab:last-child').classList.add('active');
        document.getElementById('textTab').classList.add('active');
    }
}

async function fetchAndAnalyze() {
    const url = document.getElementById('newsUrl').value.trim();
    if (!url) {
        showError('請輸入新聞網址');
        return;
    }

    showLoading();
    hideError();

    try {
        const mockData = getMockDataFromUrl(url);
        
        if (mockData) {
            processNews(mockData);
            document.getElementById('loading').style.display = 'none';
            document.getElementById('resultSection').style.display = 'block';
        } else {
            throw new Error('無法從此網址抓取內容，請使用「貼上文字」功能');
        }
    } catch (error) {
        showError(error.message);
        document.getElementById('loading').style.display = 'none';
    }
}

function getMockDataFromUrl(url) {
    const mockDatabase = {
        'example.com': `【標題】女公關遭前男友砍殺身亡 生前曾多次分合
【內容】一名在酒店工作的女子昨日深夜獨自外出時，遭前男友持刀攻擊，送醫不治。據了解，兩人感情糾紛已久，死者生前曾多次與嫌犯分分合合。鄰居表示，死者平時穿著暴露，經常深夜外出，交友複雜。警方初步研判為情殺案件。`,
        'news.tw': `【標題】酒店妹慘遭恐怖情人殺害 疑因感情糾紛
【內容】一名酒店小姐今日凌晨在住處遭到前男友持刀攻擊身亡。據悉，兩人因感情問題早有嫌隙，死者友人透露她生前曾提到害怕前男友，但仍多次單獨與對方見面。`
    };

    for (let domain in mockDatabase) {
        if (url.includes(domain)) {
            return mockDatabase[domain];
        }
    }
    return null;
}

function analyzeNews() {
    const input = document.getElementById('newsInput').value.trim();
    if (!input) {
        showError('請輸入新聞內容');
        return;
    }

    showLoading();
    hideError();

    setTimeout(() => {
        processNews(input);
        document.getElementById('loading').style.display = 'none';
        document.getElementById('resultSection').style.display = 'block';
    }, 1000);
}

function processNews(input) {
    const titleMatch = input.match(/【標題】(.+?)(?=【內容】|$)/s);
    const contentMatch = input.match(/【內容】(.+)/s);
    
    let title = titleMatch ? titleMatch[1].trim() : input.split('\n')[0];
    let content = contentMatch ? contentMatch[1].trim() : input;

    // 重置分析結果
    analysisResults = {
        title: title,
        content: content,
        biases: []
    };

    let markedTitle = title;
    let markedContent = content;
    const foundBiases = [];

    biasPatterns.forEach(bias => {
        const titleHasBias = bias.pattern.test(title);
        const contentHasBias = bias.pattern.test(content);
        
        if (titleHasBias || contentHasBias) {
            if (!bias.contextRequired || checkContext(title + ' ' + content, bias)) {
                const biasRecord = {
                    ...bias,
                    id: bias.id + '_' + Date.now(),
                    rating: null
                };
                foundBiases.push(biasRecord);
                analysisResults.biases.push(biasRecord);
                
                markedTitle = markedTitle.replace(bias.pattern, match => 
                    `<span class="bias-highlight">${match}<span class="bias-explanation">${bias.explanation}</span></span>`
                );
                markedContent = markedContent.replace(bias.pattern, match => 
                    `<span class="bias-highlight">${match}<span class="bias-explanation">${bias.explanation}</span></span>`
                );
            }
        }
    });

    document.getElementById('originalTitle').innerHTML = markedTitle;
    document.getElementById('originalContent').innerHTML = markedContent;

    // 生成修正版本
    let revisedTitle = title;
    let revisedContent = content;

    foundBiases.forEach(bias => {
        if (bias.replacement !== '') {
            revisedTitle = revisedTitle.replace(bias.pattern, bias.replacement);
            revisedContent = revisedContent.replace(bias.pattern, bias.replacement);
        } else {
            revisedContent = revisedContent.split('。')
                .filter(sentence => !bias.pattern.test(sentence))
                .join('。');
        }
    });

    revisedTitle = rewriteTitle(revisedTitle, foundBiases);

    document.getElementById('revisedTitle').textContent = revisedTitle;
    document.getElementById('revisedContent').textContent = revisedContent;

    // 顯示偏見分析（含評分系統）
    displayBiasAnalysis(foundBiases);
    
    // 啟用文字選取功能
    setTimeout(() => {
        setupTextSelection();
    }, 100);
}

function displayBiasAnalysis(biases) {
    const biasList = document.getElementById('biasList');
    biasList.innerHTML = '';

    if (biases.length === 0) {
        const li = document.createElement('li');
        li.className = 'bias-item';
        li.innerHTML = '<p style="text-align: center; color: #999;">未發現明顯的性別偏見或受害者譴責內容</p>';
        biasList.appendChild(li);
        return;
    }

    biases.forEach((bias, index) => {
        const li = document.createElement('li');
        li.className = 'bias-item';
        
        const biasText = bias.pattern.source.replace(/\\/g, '').replace(/\|/g, '、');
        
        li.innerHTML = `
            <div class="bias-item-header">
                <div class="bias-item-content">
                    <strong>「${biasText}」</strong>
                    <p>${bias.explanation}</p>
                </div>
            </div>
            <div class="rating-section">
                <span class="rating-label">評分：</span>
                <div class="rating-buttons">
                    <button class="rating-btn extreme" onclick="rateBias('${bias.id}', 'extreme', this)">
                        過度極端
                    </button>
                    <button class="rating-btn neutral" onclick="rateBias('${bias.id}', 'neutral', this)">
                        中性
                    </button>
                    <button class="rating-btn correct" onclick="rateBias('${bias.id}', 'correct', this)">
                        正確評斷
                    </button>
                </div>
            </div>
        `;
        
        biasList.appendChild(li);
    });
}

function rateBias(biasId, rating, button) {
    // 更新評分狀態
    const buttons = button.parentElement.querySelectorAll('.rating-btn');
    buttons.forEach(btn => btn.classList.remove('selected'));
    button.classList.add('selected');

    // 記錄評分
    const bias = analysisResults.biases.find(b => b.id === biasId);
    if (bias) {
        bias.rating = rating;
        logFeedback(`評分「${bias.pattern.source}」為${getRatingText(rating)}`);
    }

    // 這裡可以將評分資料傳送到後端
    console.log('Bias rated:', biasId, rating);
}

function getRatingText(rating) {
    const ratingTexts = {
        'extreme': '過度極端',
        'neutral': '中性',
        'correct': '正確評斷'
    };
    return ratingTexts[rating] || rating;
}

function setupTextSelection() {
    console.log('Setting up text selection...');
    
    // 監聽document的mouseup事件
    document.addEventListener('mouseup', function(e) {
        // 確保點擊在結果區域內
        if (!e.target.closest('.result-box')) {
            hideSelectionTooltip();
            return;
        }
        
        // 延遲檢查選取的文字
        setTimeout(() => {
            const selection = window.getSelection();
            const selectedText = selection.toString().trim();
            
            console.log('Mouse up - Selected text:', selectedText);
            
            // 確保選取的文字長度大於2
            if (selectedText && selectedText.length > 2) {
                try {
                    const range = selection.getRangeAt(0);
                    const rect = range.getBoundingClientRect();
                    
                    if (rect.width > 0 && rect.height > 0) {
                        const tooltip = document.getElementById('selectionTooltip');
                        
                        // 計算提示框位置
                        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
                        const scrollLeft = window.pageXOffset || document.documentElement.scrollLeft;
                        
                        tooltip.style.display = 'block';
                        tooltip.style.left = (rect.left + scrollLeft + rect.width / 2 - 40) + 'px';
                        tooltip.style.top = (rect.top + scrollTop - 35) + 'px';
                        
                        console.log('Tooltip shown at:', tooltip.style.left, tooltip.style.top);
                        
                        // 綁定點擊事件
                        tooltip.onclick = function(event) {
                            event.stopPropagation();
                            console.log('Tooltip clicked');
                            markUserSelection(selectedText, e.target);
                            selection.removeAllRanges();
                            hideSelectionTooltip();
                        };
                    }
                } catch (err) {
                    console.error('Error showing tooltip:', err);
                }
            }
        }, 50);
    });
}

function markUserSelection(text, container) {
    // 判斷是原始版本還是修正版本
    const isOriginal = container.closest('.original') !== null;
    const context = isOriginal ? '原始版本' : '修正版本';
    
    // 記錄使用者標記
    const feedback = {
        type: 'user_highlight',
        text: text,
        context: context,
        timestamp: new Date().toISOString(),
        container: container.className
    };
    
    userFeedback.push(feedback);
    
    // 視覺標記
    const selection = window.getSelection();
    if (selection.rangeCount > 0) {
        const range = selection.getRangeAt(0);
        const span = document.createElement('span');
        span.className = 'user-highlight';
        span.title = '使用者標記的內容';
        
        try {
            range.surroundContents(span);
        } catch (e) {
            // 如果選取跨越多個元素，使用替代方法
            const content = range.extractContents();
            span.appendChild(content);
            range.insertNode(span);
        }
    }
    
    logFeedback(`標記了${context}中的文字：「${text}」`);
}

function logFeedback(message) {
    const log = document.getElementById('feedbackLog');
    const entry = document.createElement('div');
    entry.className = 'feedback-entry';
    
    const timestamp = new Date().toLocaleTimeString('zh-TW');
    entry.innerHTML = `
        <span class="timestamp">${timestamp}</span><br>
        ${message}
    `;
    
    // 清除預設訊息
    if (log.querySelector('p')) {
        log.innerHTML = '';
    }
    
    log.insertBefore(entry, log.firstChild);
    
    // 限制顯示數量
    if (log.children.length > 10) {
        log.removeChild(log.lastChild);
    }
}

function checkContext(text, bias) {
    const negativeContext = /應該|不應該|導致|引發|造成|所以/;
    return negativeContext.test(text);
}

function rewriteTitle(title, foundBiases) {
    if (foundBiases.some(b => b.severity === 'high')) {
        if (title.includes('殺') || title.includes('亡')) {
            return '女性遭暴力攻擊身亡 警方積極偵辦中';
        } else if (title.includes('傷')) {
            return '女性遭暴力攻擊受傷 嫌犯已遭逮捕';
        }
    }
    return title;
}

function showLoading() {
    document.getElementById('loading').style.display = 'block';
    document.getElementById('resultSection').style.display = 'none';
}

function showError(message) {
    const errorEl = document.getElementById('errorMessage');
    errorEl.textContent = message;
    errorEl.style.display = 'block';
}

function hideError() {
    document.getElementById('errorMessage').style.display = 'none';
}

function hideSelectionTooltip() {
    document.getElementById('selectionTooltip').style.display = 'none';
}

function loadExample() {
    const exampleNews = `【標題】女公關遭前男友砍殺身亡 生前曾多次分合
【內容】一名在酒店工作的女子昨日深夜獨自外出時，遭前男友持刀攻擊，送醫不治。據了解，兩人感情糾紛已久，死者生前曾多次與嫌犯分分合合。鄰居表示，死者平時穿著暴露，經常深夜外出，交友複雜。警方初步研判為情殺案件。`;
    
    document.getElementById('newsInput').value = exampleNews;
}

// 匯出分析資料（供開發使用）
function exportAnalysisData() {
    const data = {
        analysisResults: analysisResults,
        userFeedback: userFeedback,
        timestamp: new Date().toISOString()
    };
    
    console.log('Analysis Data:', data);
    return data;
}

// 鍵盤快捷鍵
document.addEventListener('keydown', (e) => {
    // Ctrl/Cmd + E: 匯出資料
    if ((e.ctrlKey || e.metaKey) && e.key === 'e') {
        e.preventDefault();
        const data = exportAnalysisData();
        console.log('Exported data:', data);
        alert('分析資料已匯出至控制台');
    }
});

// 頁面載入完成後的初始化
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM loaded');
    
    // 點擊其他地方時隱藏選取提示
    document.addEventListener('click', (e) => {
        if (!e.target.closest('#selectionTooltip')) {
            hideSelectionTooltip();
        }
    });
});