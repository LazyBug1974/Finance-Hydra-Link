import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import pytz

def get_taipei_time():
    return datetime.now(pytz.timezone('Asia/Taipei'))

def scrape_pchome_news():
    url = "https://news.pchome.com.tw/cat/finance/"
    response = requests.get(url)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'html.parser')

    news_list = []
    for item in soup.select('dl.list-news01 a'):
        title = item.text.strip()
        link = item['href']
        news_list.append({'title': title, 'link': link})

    return news_list

def main():
    print("Starting scraping process...")
    
    # 確保 data 資料夾存在
    output_dir = 'data'
    os.makedirs(output_dir, exist_ok=True)
    print(f"Directory '{output_dir}' created or already exists.")

    # 爬取新聞
    news_data = scrape_pchome_news()
    
    if not news_data:
        print("No news found. Exiting.")
        return

    # 轉換為 DataFrame
    df = pd.DataFrame(news_data)

    # 產生帶有台北時間的檔名
    taipei_time = get_taipei_time()
    filename = taipei_time.strftime("%Y-%m-%d_%H-%M-%S_pchome_news.csv")
    file_path = os.path.join(output_dir, filename)

    # 儲存為 CSV
    df.to_csv(file_path, index=False, encoding='utf-8-sig')
    print(f"Data saved to {file_path}")

if __name__ == "__main__":
    main()
