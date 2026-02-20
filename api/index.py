from flask import Flask, request, Response
import cloudscraper
from bs4 import BeautifulSoup
from datetime import datetime
import traceback

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
    if symbol not in TARGET_MAP:
        return f"Error: Symbol {symbol} not found"
    
    url = f"https://www.investing.com/{TARGET_MAP[symbol]}"
    
    # 使用 cloudscraper 繞過 Cloudflare 檢測
    scraper = cloudscraper.create_scraper(
        browser={'browser': 'chrome', 'platform': 'windows', 'desktop': True}
    )
    
    try:
        response = scraper.get(url, timeout=15)
        if response.status_code != 200:
            return f"Error: Investing.com blocked (HTTP {response.status_code})"
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 抓取最新價格
        price_element = soup.select_one('[data-test="instrument-price-last"]')
        if not price_element:
            return "Error: Price element not found"
            
        price = price_element.get_text().replace(',', '').strip()
        date_str = datetime.now().strftime('%Y-%m-%d')
        return f"{date_str},{price}"
        
    except Exception:
        return f"Error Trace: {traceback.format_exc()}"

@app.route('/api')
def proxy():
    code = request.args.get('code', '').upper()
    if not code:
        return "Error: Missing code parameter", 400
        
    result = get_investing_data(code)
    return Response(result, mimetype='text/plain')

if __name__ == '__main__':
    app.run(debug=True)
