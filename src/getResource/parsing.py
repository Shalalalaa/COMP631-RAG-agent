import os
import json
import requests
from bs4 import BeautifulSoup
import time

BASE_URL = "https://www.zgjmorg.com"
DATA_DIR = "data/ZhouGong"
LOG_FILE = "data/crawled_urls.json"

os.makedirs(DATA_DIR, exist_ok=True)

# avoid repeat parsing
if os.path.exists(LOG_FILE):
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        crawled_urls = set(json.load(f))
else:
    crawled_urls = set()

# save the already stored documents website
def save_crawled_urls():
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(list(crawled_urls), f, ensure_ascii=False, indent=4)

def get_all_categories():
    response = requests.get(BASE_URL, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(response.text, "html.parser")

    categories = {}
    category_div = soup.select_one("div.left")
    for link in category_div.select("a"):
        category_name = link.text.strip()
        category_url = link["href"]

        # avoid repeat
        if not category_url.startswith("http"):
            category_url = BASE_URL.rstrip("/") + "/" + category_url.lstrip("/")

        categories[category_name] = category_url

    return categories

def get_all_pages(category_url):
    response = requests.get(category_url, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(response.text, "html.parser")

    page_urls = set([category_url])
    for link in soup.select("div.list-pages a"):
        href = link["href"].strip()
        if "list_" in href:
            full_url = BASE_URL + href if href.startswith("/") else href
            page_urls.add(full_url)

    return sorted(page_urls)

def get_dream_links(category_url):
    response = requests.get(category_url, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(response.text, "html.parser")

    dream_links = []
    for link in soup.select("div#list ul li a"):
        title = link.text.strip().replace("/", "_")
        href = link["href"]
        full_url = BASE_URL + href if href.startswith("/") else href
        dream_links.append({"title": title, "url": full_url})

    return dream_links

def scrape_dream_content(dream_url):
    response = requests.get(dream_url, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(response.text, "html.parser")

    title = soup.select_one("div#entrytitle h1").text.strip() if soup.select_one("div#entrytitle h1") else "无标题"

    content = []
    content_blocks = soup.select("div.read-content p")
    for block in content_blocks:
        text = block.text.strip()
        if text:
            content.append(text)

    return {"title": title, "content": "\n".join(content)}

def scrape_category(category_name, category_url):
    category_dir = os.path.join(DATA_DIR, category_name)
    os.makedirs(category_dir, exist_ok=True)

    all_pages = get_all_pages(category_url)

    for page_url in all_pages:
        print(f"⏳ Parsing category: {category_name} | pages: {page_url}")
        dream_links = get_dream_links(page_url)

        for dream in dream_links:
            if dream["url"] in crawled_urls:
                print(f"✅ Exist, skip: {dream['title']} - {dream['url']}")
                continue  

            print(f"🔍 Parsing dreams: {dream['title']} - {dream['url']}")
            dream_data = scrape_dream_content(dream["url"])

            json_filename = os.path.join(category_dir, f"{dream_data['title']}.json")
            with open(json_filename, "w", encoding="utf-8") as f:
                json.dump(dream_data, f, ensure_ascii=False, indent=4)

            crawled_urls.add(dream["url"])
            save_crawled_urls()

            print(f"✅ Complete json record: {json_filename}")
            time.sleep(1)

# parsing whole web
categories = get_all_categories()
for category_name, category_url in categories.items():
    scrape_category(category_name, category_url)
