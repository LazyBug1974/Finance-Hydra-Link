from flask import Flask, request, Response
import cloudscraper
from bs4 import BeautifulSoup
from datetime import datetime

app = Flask(__name__)

# 標的映射表
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
    url = f"https://www.investing.com/{TARGET_MAP[symbol]}"
    scraper = cloudscraper.create_scraper(browser={'browser': 'chrome', 'platform': 'windows', 'desktop': True})
    
    try:
        response = scraper.get(url, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        price_el = soup.find(attrs={"data-test": "instrument-price-last"})
        if not price_el: return "Error: Price not found"
        
        price = price_el.get_text().replace(',', '').strip()
        return price
    except Exception as e:
        return f"Error: {str(e)}"

@app.route('/api')
def proxy():
    code = request.args.get('code', '').upper()
    # 處理 date 參數：如果沒傳或傳 now，就預設為今天日期
    date_param = request.args.get('date', 'now').lower()
    
    if not code or code not in TARGET_MAP:
        return "Error: Invalid or missing code", 400
        
    price = get_investing_data(code)
    
    # 無論 date 傳什麼，目前我們都回傳當前日期 + 抓到的價格
    # 這符合你預設 now 的邏輯
    current_date = datetime.now().strftime('%Y-%m-%d')
    return Response(f"{current_date},{price}", mimetype='text/plain')

if __name__ == '__main__':
    app.run()
