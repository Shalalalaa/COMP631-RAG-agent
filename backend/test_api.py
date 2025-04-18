# test_api.py
import requests
import json

# 后端服务器地址（如果是本机就是 localhost）
url = "http://localhost:8000/analyze"

# 要测试的梦境文本
user_text = "我昨晚梦见飞翔的鱼和奇怪的建筑"

# 构造 POST 请求数据
payload = {
    "text": user_text
}

# 发送请求
print("🔄 发送请求中...")
response = requests.post(url, json=payload)

# 解析返回
if response.status_code == 200:
    data = response.json()
    print("✅ 收到回应！\n")

    print("【梦境分析回答】\n")
    print(data["answer"])
    print("\n【引用来源标题】")
    for title in data["sources"]:
        print("-", title)
else:
    print("❌ 出错了！状态码:", response.status_code)
    print(response.text)
