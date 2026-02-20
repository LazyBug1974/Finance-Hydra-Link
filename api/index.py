import os
from flask import Flask, request, Response
import cloudscraper
from bs4 import BeautifulSoup
from datetime import datetime

app = Flask(__name__)

# 嚴格對齊標的映射表與指定的 Historical Data 路徑
TARGET_MAP = {
    "SPXF": "indices/us-spx-500-futures-historical-data", # 美國標普500指數期貨
    "SOX": "indices/phlx-semiconductor-historical-data", # 費城半導體指數
    "XAU": "currencies/xau-usd-historical-data", # 黃金現貨美元
    "XAG": "currencies/xag-usd-historical-data", # 白銀現貨美元
    "HGH6": "commodities/copper-historical-data", # 銅期貨
    "WTI": "commodities/crude-oil-historical-data", # 西德州原油
    "US30Y": "rates-bonds/u.s.-30-year-bond-yield-historical-data", # 美國 30Y 公債殖利率
    "US20Y": "rates-bonds/us-20-year-bond-yield-historical-data", # 美國 20Y 公債殖利率
    "US10Y": "rates-bonds/u.s.-10-year-bond-yield-historical-data", # 美國 10Y 公債殖利率
    "US2Y": "rates-bonds/u.s.-2-year-bond-yield-historical-data" # 美國 2Y 公債殖利率
}

def get_investing_data(symbol):
    if symbol not in TARGET_MAP:
        return f"Error: Symbol {symbol} not found in map"
    
    url = f"https://www.investing.com/{TARGET_MAP[symbol]}"
    scraper = cloudscraper.create_scraper(
        browser={'browser': 'chrome', 'platform': 'windows', 'mobile': False}
    )
    
    try:
        response = scraper.get(url, timeout=15)
        if response.status_code != 200:
            return f"Error: HTTP {response.status_code}"
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 針對 Historical Data 頁面抓取最新價格 (instrument-price-last)
        price_element = soup.select_one('[data-test="instrument-price-last"]')
        
        if not price_element:
            return "Error: Price element not found"
            
        # 移除千分號
        raw_price = price_element.get_text().replace(',', '')
        
        # 取得當前日期 (YYYY-MM-DD)
        date_str = datetime.now().strftime('%Y-%m-%d')
        
        return f"{date_str},{raw_price}"
        
    except Exception as e:
        return f"Error: {str(e)}"

@app.route('/api')
def proxy():
    code = request.args.get('code', '').upper()
    # 接收 date 參數但目前邏輯預設回傳最新值 (符合 date=now 需求)
    target_date = request.args.get('date', 'now')
    
    if not code:
        return "Error: Missing code parameter", 400
        
    result = get_investing_data(code)
    
    # 輸出格式：日期,數值
    return Response(result, mimetype='text/plain')

if __name__ == '__main__':
    app.run(debug=True)
