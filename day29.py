import requests

# 调用自己的AI客服接口
url = "http://127.0.0.1:8000/客服"

# 发问题
数据 = {"问题": "你们店有活动吗？"}
response = requests.post(url, json=数据)

# 打印AI回答
print("AI客服回答：")
print(response.json()["回答"])
