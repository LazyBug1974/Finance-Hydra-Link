from http.server import BaseHTTPRequestHandler
import cloudscraper
import json
from urllib.parse import urlparse, parse_qs
import datetime

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Parse query parameters
        query_components = parse_qs(urlparse(self.path).query)
        code = query_components.get('code', [None])[0]
        # Default to today's date in UTC+8 if not provided
        tz = datetime.timezone(datetime.timedelta(hours=8))
        default_date = datetime.datetime.now(tz).strftime("%Y-%m-%d")
        date = query_components.get('date', [default_date])[0]

        if not code:
            self.send_response(400)
            self.send_header('Content-type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write(b"Error: 'code' parameter is required.")
            return

        # --- Data Fetching Logic ---
        url = f"https://www.sinotrade.com.tw/new/stocks/stock_3_8_1?code={code}&date={date}"
        scraper = cloudscraper.create_scraper(browser={'browser': 'firefox', 'platform': 'windows', 'mobile': False})
        
        try:
            res = scraper.get(url)
            res.raise_for_status()
            data = res.json()

            # --- Data Processing Logic ---
            if data and data.get('data'):
                result_entry = None
                # The API returns data for a range, find the exact date match
                for entry in data.get('data', []):
                    if entry.get('updated_at') == date:
                        result_entry = entry
                        break
                
                if result_entry:
                    # Format the output as "日期,數值"
                    value_str = str(result_entry.get('target', '')).replace(',', '')
                    output = f"{result_entry.get('updated_at')},{value_str}"

                    self.send_response(200)
                    self.send_header('Content-type', 'text/csv; charset=utf-8')
                    self.end_headers()
                    self.wfile.write(output.encode('utf-8'))
                else:
                    self.send_response(404)
                    self.send_header('Content-type', 'text/plain; charset=utf-8')
                    self.end_headers()
                    self.wfile.write(f"Error: Data not found for code '{code}' on date '{date}'.".encode('utf-8'))

            else:
                self.send_response(404)
                self.send_header('Content-type', 'text/plain; charset=utf-8')
                self.end_headers()
                self.wfile.write(b"Error: No data received from the source API.")

        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write(f"An internal error occurred: {str(e)}".encode('utf-8'))

        return