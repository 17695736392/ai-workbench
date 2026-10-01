import pandas as pd

# 模拟客户给你两个表
df1 = pd.DataFrame({"姓名": ["张三", "李四"], "电话": ["13800000001", "13800000002"]})
df2 = pd.DataFrame({"姓名": ["王五", "赵六"], "电话": ["13800000003", "13800000004"]})

# 存成两个文件
df1.to_excel("表1.xlsx", index=False)
df2.to_excel("表2.xlsx", index=False)

# 读回来
a = pd.read_excel("表1.xlsx")
b = pd.read_excel("表2.xlsx")

# 合并
合并 = pd.concat([a, b], ignore_index=True)
合并.to_excel("合并结果.xlsx", index=False)

print("=== 合并完成 ===")
print(合并)
