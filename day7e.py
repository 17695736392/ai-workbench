import pandas as pd

df = pd.read_excel("全部合并.xlsx")
print("=== 原始（有重复） ===")
print(df)

# 去重
去重后 = df.drop_duplicates(subset="电话")

print("\n=== 去重后 ===")
print(去重后)

# 按电话排序
排序后 = 去重后.sort_values("电话")
print("\n=== 按电话排序 ===")
print(排序后)

排序后.to_excel("清洗结果.xlsx", index=False)
print("\n已存成 清洗结果.xlsx")
