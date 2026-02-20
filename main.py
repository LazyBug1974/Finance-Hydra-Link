import os
import pandas as pd
import cloudscraper
from bs4 import BeautifulSoup
from datetime import datetime
import pytz

# Mapping of target names to their Investing.com URLs and types
TARGET_MAP = {
    # Indices
    'SPX': {'url': 'https://www.investing.com/indices/us-spx-500-historical-data', 'type': 'index'},
    'SOX': {'url': 'https://www.investing.com/indices/phlx-semiconductor-historical-data', 'type': 'index'},
    'IXIC': {'url': 'https://www.investing.com/indices/nasdaq-composite-historical-data', 'type': 'index'},
    'DJI': {'url': 'https://www.investing.com/indices/dow-jones-industrial-average-historical-data', 'type': 'index'},
    # Commodities
    'XAU': {'url': 'https://www.investing.com/commodities/gold-spot-historical-data', 'type': 'commodity'},
    'XAG': {'url': 'https://www.investing.com/commodities/silver-spot-historical-data', 'type': 'commodity'},
    'WTI': {'url': 'https://www.investing.com/commodities/crude-oil-historical-data', 'type': 'commodity'},
    # Currencies
    'USDTWD': {'url': 'https://www.investing.com/currencies/usd-twd-historical-data', 'type': 'currency'},
    'USDJPY': {'url': 'https://www.investing.com/currencies/usd-jpy-historical-data', 'type': 'currency'},
    'EURUSD': {'url': 'https://www.investing.com/currencies/eur-usd-historical-data', 'type': 'currency'},
}

def get_taipei_time():
    """Gets the current time in Taipei (UTC+8)."""
    utc_now = datetime.utcnow().replace(tzinfo=pytz.utc)
    taipei_tz = pytz.timezone('Asia/Taipei')
    return utc_now.astimezone(taipei_tz)

def get_real_time_price(soup):
    """Extracts the real-time price from the page soup."""
    price_selector = '[data-test="instrument-price-last"]'
    price_element = soup.select_one(price_selector)
    return price_element.text.strip() if price_element else 'N/A'

def get_historical_price(soup, target_date):
    """Extracts the closing price for a specific date from the historical data table."""
    try:
        table_selector = 'table.historical-data-table_table__3cPPk'
        table = soup.select_one(table_selector)
        df = pd.read_html(str(table))[0]
        df['Date'] = pd.to_datetime(df['Date'], format='%m/%d/%Y')
        target_row = df[df['Date'] == target_date]
        if not target_row.empty:
            return target_row.iloc[0]['Price']
        return 'Date Not Found'
    except Exception as e:
        print(f"Error parsing historical data: {e}")
        return 'Parse Error'

def main():
    """Main function to scrape data based on environment variables."""
    target = os.getenv('TARGET', 'SPX')
    date_str = os.getenv('DATE', 'now')

    if target not in TARGET_MAP:
        raise ValueError(f"Invalid target specified: {target}")

    scraper = cloudscraper.create_scraper()
    url = TARGET_MAP[target]['url']
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    }
    
    try:
        response = scraper.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        taipei_time = get_taipei_time()
        
        if date_str.lower() == 'now':
            price = get_real_time_price(soup)
            record_date = taipei_time.strftime('%Y-%m-%d')
        else:
            try:
                target_date = pd.to_datetime(date_str, format='%Y/%m/%d')
                price = get_historical_price(soup, target_date)
                record_date = target_date.strftime('%Y-%m-%d')
            except ValueError:
                raise ValueError("Invalid date format. Please use YYYY/MM/DD.")

        # Prepare data for saving
        data = {
            'target': [target],
            'price': [price],
            'date': [record_date],
            'updated_at': [taipei_time.strftime('%Y-%m-%d %H:%M')]
        }
        df = pd.DataFrame(data)

        # Create directory and save to CSV
        output_dir = 'data'
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f'{target}_data.csv')
        
        df.to_csv(output_path, index=False)
        print(f"Data for {target} saved to {output_path}")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
