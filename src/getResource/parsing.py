import os
import json
import requests
from bs4 import BeautifulSoup
import time

BASE_URL = "https://www.zgjmorg.com"

# create data directoyr
os.makedirs("data/ZhouGong", exist_ok=True)

def get_all_pages(category_url):
    response = requests.get(category_url, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(response.text, "html.parser")

    page_urls = [category_url]
    for link in soup.select("div.list-pages a"):
        href = link["href"]
        if "list" in href and href not in page_urls:
            full_url = BASE_URL + href if href.startswith("/") else href
            page_urls.append(full_url)

    return page_urls

# get dreams under one category
def get_dream_links(category_url):
    response = requests.get(category_url, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(response.text, "html.parser")

    dream_links = []
    for link in soup.select("div#list ul li a"):
        title = link.text.strip()
        href = link["href"]
        full_url = BASE_URL + href if href.startswith("/") else href
        dream_links.append({"title": title, "url": full_url})

    return dream_links

# get dream content
def scrape_dream_content(dream_url):
    response = requests.get(dream_url, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(response.text, "html.parser")

    # get title
    title = soup.select_one("div#entrytitle h1").text.strip() if soup.select_one("div#entrytitle h1") else "无标题"

    # get content
    content = []
    content_blocks = soup.select("div.read-content p")
    for block in content_blocks:
        text = block.text.strip()
        if text:
            content.append(text)

    return {"title": title, "content": "\n".join(content)}

# store it to json file
def scrape_category(category_name, category_url):
    all_pages = get_all_pages(category_url)
    all_dreams = []

    for page_url in all_pages:
        print(f"⏳ 正在爬取分类: {category_name} | 页面: {page_url}")
        dream_links = get_dream_links(page_url)

        for i, dream in enumerate(dream_links):
            # test 10 first
            if i >= 10:  
                break

            print(f"🔍 爬取梦境: {dream['title']} - {dream['url']}")
            dream_data = scrape_dream_content(dream["url"])
            all_dreams.append(dream_data)

            time.sleep(2)

    json_filename = f"data/ZhouGong/{category_name}.json"
    with open(json_filename, "w", encoding="utf-8") as f:
        json.dump(all_dreams, f, ensure_ascii=False, indent=4)

    print(f"Complete: {json_filename}")

# test
test_category = "人物类"
test_url = "https://www.zgjmorg.com/renwu/"
scrape_category(test_category, test_url)












# import os
# import json
# import requests
# from bs4 import BeautifulSoup
# import time

# # 目标网站
# BASE_URL = "https://www.zgjmorg.com/"  # 替换成真实的周公解梦网站

# # 创建存储目录
# os.makedirs("data/ZhouGong", exist_ok=True)

# def get_category_links():
#     """爬取周公解梦分类页面，获取所有梦境分类的链接"""
#     response = requests.get(BASE_URL, headers={"User-Agent": "Mozilla/5.0"})
#     soup = BeautifulSoup(response.text, "html.parser")

#     category_links = {}
#     for link in soup.select("a.right"):  # ✅ 修改为正确的 class
#         category_name = link.text.strip()
#         category_url = link["href"]
#         category_links[category_name] = category_url

#     return category_links

# def scrape_category(category_name, category_url):
#     """爬取某个梦境分类的所有文章，并存为单独的 JSON 文件"""
#     response = requests.get(category_url, headers={"User-Agent": "Mozilla/5.0"})
#     soup = BeautifulSoup(response.text, "html.parser")

#     dreams_data = []
#     articles = soup.select("div.dream-item")  # ✅ 修改为正确的 class
#     for article in articles:
#         title = article.select_one("h2.dream-title").text.strip()  # ✅ 标题
#         content = article.select_one("p.dream-content").text.strip()  # ✅ 解析内容

#         # 存入当前分类的列表
#         dreams_data.append({"title": title, "content": content})

#         time.sleep(1)  # 避免请求过快被封

#     # 存 JSON
#     json_filename = f"data/ZhouGong/{category_name}.json"
#     with open(json_filename, "w", encoding="utf-8") as f:
#         json.dump(dreams_data, f, ensure_ascii=False, indent=4)

#     print(f"✅ 已保存：{json_filename}")

# # 获取所有分类链接
# category_links = get_category_links()

# # 遍历每个分类，爬取数据并存 JSON
# for category_name, category_url in category_links.items():
#     scrape_category(category_name, category_url)

# print("🎉 所有分类爬取完成，数据已保存！")
