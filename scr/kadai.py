import time
import requests
import csv
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, urldefrag

url = 'https://www.musashino-u.ac.jp/'

time.sleep(1)
res = requests.get(url, timeout=30)

print(f"ステータスコード：{res.status_code}")
res.raise_for_status()

html_soup = BeautifulSoup(res.content, 'html.parser')
title = html_soup.title.get_text().strip() if html_soup.title else ''
print(f"タイトル：{title}")

pages = {}
pages[url] = title

domain = urlparse(url).netloc

links = html_soup.find_all('a', href=True)
same_domain_urls = []

for link in links:

    next_url = urljoin(res.url, link['href'])
    next_url = urldefrag(next_url)[0]
    parsed_url = urlparse(next_url)

    if parsed_url.scheme in ('http', 'https') and parsed_url.netloc == domain:
        if next_url not in same_domain_urls:
            same_domain_urls.append(next_url)

print(f"初期発見URL数：{len(same_domain_urls)}")

index = 0
while index < len(same_domain_urls):
    page_url = same_domain_urls[index]
    
    index += 1
    if page_url in pages:
        continue

    print(f"取得中 ({index}/{len(same_domain_urls)}): {page_url}")

    time.sleep(1)
    
    try:
        res = requests.get(page_url, timeout=30)
        res.raise_for_status()
    except requests.RequestException as error:
        print(f"取得失敗：{page_url}：{error}")
        continue

    if urlparse(res.url).netloc != domain:
        continue

    content_type = res.headers.get('Content-Type', '').lower()
    if 'text/html' not in content_type:
        continue

    html_soup = BeautifulSoup(res.content, 'html.parser')

    if html_soup.title is not None:
        title = html_soup.title.get_text().strip()
    else:
        title = ''

    pages[page_url] = title
    print(f"{page_url} → {title}")
    links = html_soup.find_all('a', href=True)
    for link in links:
        next_url = urljoin(res.url, link['href'])
        next_url = urldefrag(next_url)[0]
        parsed_url = urlparse(next_url)

        if parsed_url.scheme in ('http', 'https') and parsed_url.netloc == domain:
            if next_url not in same_domain_urls:
                same_domain_urls.append(next_url)

print("\n巡回処理が完了しました")
print(f"タイトルを保存したページ数：{len(pages)}")
print(f"リンク先も調べた後のURL数：{len(same_domain_urls)}")

with open('sitemap.csv', 'w', encoding='utf-8-sig', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['URL', 'タイトル'])
    writer.writerows(pages.items())

print('sitemap.csvに保存しました')