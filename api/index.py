from flask import Flask, request, Response
import cloudscraper
from bs4 import BeautifulSoup
from datetime import datetime
import time

app = Flask(__name__)

# 嚴格對齊標的映射表
TARGET_MAP = {
    "SPXF": "indices/us-spx-500-futures-historical-data",
    "SOX": "indices/phlx-semiconductor-historical-data",
    "XAU": "currencies/xau-usd-historical-data",
    "XAG": "currencies/xag-usd-historical-data",
    "HGH6": "commodities/copper-historical-data",
    "WTI": "commodities/crude-oil-historical-data",
    "US30Y": "rates-bonds/u.s.-30-year-bond-yield-historical-data",
    "US20Y": "rates-bonds/us-20-year-bond-yield-historical-data",
    "US10Y": "rates-bonds/u.s.-10-year-bond-yield-historical-data",
    "US2Y": "rates-bonds/u.s.-2-year-bond-yield-historical-data"
}

def get_investing_data(symbol):
    if symbol not in TARGET_MAP:
        return f"Error: Symbol {symbol} not found"
    
    url = f"https://www.investing.com/{TARGET_MAP[symbol]}"
    
    # 強制使用更強大的模擬瀏覽器設定
    scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'windows',
            'desktop': True
        }
    )
    
    try:
        # 增加自定義 Headers 模擬真實存取
        headers = {
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.google.com/'
        }
        
        response = scraper.get(url, headers=headers, timeout=20)
        
        if response.status_code != 200:
            return f"Error: Investing.com blocked (HTTP {response.status_code})"
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 嘗試多種可能的點數元素位置 (防止網頁改版)
        price = None
        selectors = [
            '[data-test="instrument-price-last"]',
            '#last_last',
            '.main-current-data [data-test="instrument-price-last"]'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                price = element.get_text().replace(',', '').strip()
                break
        
        if not price:
            return "Error: Could not find price on page"
            
        date_str = datetime.now().strftime('%Y-%m-%d')
        return f"{date_str},{price}"
        
    except Exception as e:
        return f"Error: {str(e)}"

@app.route('/api')
def proxy():
    code = request.args.get('code', '').upper()
    if not code:
        return "Error: Missing code parameter", 400
        
    # 加入隨機微幅延遲，降低被封鎖機率
    result = get_investing_data(code)
    
    # 嚴格回傳純文字格式
    return Response(result, mimetype='text/plain')

if __name__ == '__main__':
    app.run(debug=True)
