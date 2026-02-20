from flask import Flask, request, Response
import cloudscraper
from bs4 import BeautifulSoup
from datetime import datetime

app = Flask(__name__)

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
        # 增加 timeout 防止 Vercel 等太久自動斷線報 500
        response = scraper.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 優先抓取最重要的價格標籤
        price_el = soup.find(attrs={"data-test": "instrument-price-last"})
        if not price_el:
            return "Fetching_Error"
            
        return price_el.get_text().replace(',', '').strip()
    except Exception as e:
        return f"Error_{str(e)[:20]}"

@app.route('/api')
def proxy():
    code = request.args.get('code', '').upper()
    # 處理 date 參數：沒傳、傳 now、或任何值，目前都預設為今天
    date_param = request.args.get('date', 'now')
    
    if not code or code not in TARGET_MAP:
        return "Invalid_Code", 400

    price = get_investing_data(code)
    current_date = datetime.now().strftime('%Y-%m-%d')
    
    # 輸出格式嚴格對齊：日期,價格
    return Response(f"{current_date},{price}", mimetype='text/plain')
