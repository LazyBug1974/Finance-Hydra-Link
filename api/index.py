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
    if symbol not in TARGET_MAP:
        return f"Error: {symbol} not supported"
    
    url = f"https://www.investing.com/{TARGET_MAP[symbol]}"
    
    # 建立強力爬蟲實例
    scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'windows',
            'desktop': True
        }
    )
    
    try:
        # 模擬真實存取的 Headers
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        response = scraper.get(url, headers=headers, timeout=15)
        
        if response.status_code != 200:
            return f"Error: Investing.com (Status {response.status_code})"
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 使用最穩定的數據標籤抓取即時價格
        price_el = soup.find(attrs={"data-test": "instrument-price-last"})
        
        if not price_el:
            # 備用方案：抓取舊版 id
            price_el = soup.find(id="last_last")
            
        if not price_el:
            return "Error: Element not found"
            
        price = price_el.get_text().replace(',', '').strip()
        date_str = datetime.now().strftime('%Y-%m-%d')
        
        return f"{date_str},{price}"
        
    except Exception as e:
        return f"System Error: {str(e)}"

@app.route('/api')
def proxy():
    code = request.args.get('code', '').upper()
    if not code:
        return "Error: Code required", 400
        
    result = get_investing_data(code)
    return Response(result, mimetype='text/plain')

if __name__ == '__main__':
    app.run(debug=True)
