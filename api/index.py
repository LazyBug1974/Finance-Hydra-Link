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
        response = scraper.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 使用更穩定的選擇器並加入檢查
        price_el = soup.find(attrs={"data-test": "instrument-price-last"})
        if price_el:
            return price_el.get_text().replace(',', '').strip()
        return "Fetch_Failed_No_Price"
    except Exception as e:
        return f"Fetch_Error_{str(e)[:15]}"

@app.route('/api')
def proxy():
    code = request.args.get('code', '').upper()
    # 解決你的疑問：如果沒有傳 date，就預設為 'now'
    date_param = request.args.get('date', 'now').lower()
    
    if not code or code not in TARGET_MAP:
        return "Error_Invalid_Code", 400

    price = get_investing_data(code)
    
    # 統一回傳格式：日期,價格
    # 無論 date 傳什麼，目前邏輯都先回傳今天日期 (即 now)
    current_date = datetime.now().strftime('%Y-%m-%d')
    return Response(f"{current_date},{price}", mimetype='text/plain')
