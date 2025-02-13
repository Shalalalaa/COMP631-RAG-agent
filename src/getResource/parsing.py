import requests
from bs4 import BeautifulSoup

# 目标网站
BASE_URL = "https://www.zgjmorg.com/"

def get_category_links():
    """爬取周公解梦分类页面，获取所有梦境分类的链接"""
    response = requests.get(BASE_URL, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(response.text, "html.parser")

    category_links = {}

    # 选取分类部分
    category_div = soup.select_one("div.left")  # ✅ 选择正确的 div
    for link in category_div.select("a"):  # ✅ 选择所有 <a> 标签
        category_name = link.text.strip()
        category_url = BASE_URL + link["href"]  # 拼接完整 URL

        category_links[category_name] = category_url

    return category_links

# 测试是否能正确获取分类
category_links = get_category_links()
print(category_links)  # ✅ 运行后应输出 {'交通运输': 'https://www.example.com/wupin/jiaotong/', ...}


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
