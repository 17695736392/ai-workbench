import pandas as pd

# 读之前造的客户表
df = pd.read_excel("客户表.xlsx")
print("=== 全部客户 ===")
print(df)

# 只要北京的
北京客户 = df[df["城市"] == "北京"]
print("\n=== 只要北京 ===")
print(北京客户)

# 加一列：备注
df["备注"] = "新客户"
df.to_excel("客户表_加备注.xlsx", index=False)
print("\n已加备注列，存成 客户表_加备注.xlsx")
