import requests
from bs4 import BeautifulSoup
from openai import OpenAI

# 配置AI
client = OpenAI(
    api_key="sk-6a8868ea41a140fead84ebda91965ac9",
    base_url="https://api.deepseek.com"
)

# 爬取豆瓣电影Top250
url = "https://movie.douban.com/top250"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, "html.parser")

# 提取电影信息
movies = []
for movie in soup.find_all("div", class_="item"):
    title = movie.find("span", class_="title").text
    rating = movie.find("span", class_="rating_num").text
    movies.append(f"{title}（{rating}分）")

电影列表 = "\n".join(movies)

# 让AI分析
print("🤖 AI正在分析豆瓣Top250...")
response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "system", "content": "你是电影分析专家，根据电影列表分析规律。"},
        {"role": "user", "content": f"以下是豆瓣Top250前25部电影：\n{电影列表}\n\n请分析：1.评分最高的电影有哪些？2.有什么共同特点？3.给我一个总结报告。"}
    ]
)

print("\n=== AI分析报告 ===")
print(response.choices[0].message.content)
