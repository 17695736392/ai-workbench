import pandas as pd

# 1. 自己造一张客户表
data = {
    "姓名": ["张三", "李四", "王五"],
    "电话": ["13800000001", "13800000002", "13800000003"],
    "城市": ["北京", "上海", "广州"]
}
df = pd.DataFrame(data)
print("=== 造好的表 ===")
print(df)

# 2. 存成 Excel 文件
df.to_excel("客户表.xlsx", index=False)
print("\n客户表.xlsx 已存到桌面")

# 3. 读回来
df2 = pd.read_excel("客户表.xlsx")
print("\n=== 读回来的表 ===")
print(df2)
