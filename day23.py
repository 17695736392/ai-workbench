import requests
from bs4 import BeautifulSoup

# 许嵩热门歌曲列表（先手动整理，确保准确）
许嵩的歌 = [
    "雅俗共赏",
    "素颜",
    "想象之中",
    "千百度",
    "庐州月",
    "半城烟沙",
    "断桥残雪",
    "城府",
    "玫瑰花的葬礼",
    "认错",
    "灰色头像",
    "多余的解释",
    "有何不可",
    "如果当时",
    "宿敌",
    "天龙八部之宿敌",
    "幻听",
    "弹指一挥间",
    "山水之间",
    "千古",
    "最佳歌手",
    "素颜",
    "雅俗共赏",
    "九月清晨",
    "温泉",
    "呼吸之野",
]

# 保存成文件
with open("许嵩演唱会歌单.txt", "w", encoding="utf-8") as f:
    f.write("许嵩演唱会歌单\n")
    f.write("=" * 30 + "\n\n")
    for i, song in enumerate(许嵩的歌, 1):
        f.write(f"{i}. {song}\n")

print("✅ 歌单已保存：许嵩演唱会歌单.txt")
print("\n=== 许嵩演唱会歌单 ===")
for i, song in enumerate(许嵩的歌, 1):
    print(f"{i}. {song}")
