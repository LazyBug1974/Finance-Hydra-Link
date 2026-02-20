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
    
    # 強力模擬真實瀏覽器環境
    scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'windows',
            'desktop': True
        }
    )
    
    try:
        # 額外的真實請求標頭
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.google.com/'
        }
        
        response = scraper.get(url, headers=headers, timeout=20)
        
        if response.status_code != 200:
            return f"Error: HTTP {response.status_code} (Blocked)"
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 嘗試多個可能的 CSS 選擇器，應對網頁變動
        price = None
        selectors = [
            '[data-test="instrument-price-last"]', 
            '#last_last',
            '.main-current-data [data-test="instrument-price-last"]',
            'span[data-test="instrument-price-last"]'
        ]
        
        for s in selectors:
            element = soup.select_one(s)
            if element:
                price = element.get_text().replace(',', '').strip()
                break
        
        if not price:
            return "Error: Price element not found"
            
        date_str = datetime.now().strftime('%Y-%m-%d')
        return f"{date_str},{price}"
        
    except Exception as e:
        return f"Error: {str(e)}"

@app.route('/api')
def proxy():
    code = request.args.get('code', '').upper()
    if not code:
        return "Error: Missing code parameter", 400
        
    # 執行抓取
    result = get_investing_data(code)
    
    # 確保回傳純文字，方便 Google Sheets 讀取
    return Response(result, mimetype='text/plain')

if __name__ == '__main__':
    app.run(debug=True)
