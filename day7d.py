import pandas as pd
import os

# 桌面建一个"excel批量"文件夹，把所有Excel放进去
文件夹 = "excel批量"
所有表 = []

for 文件 in os.listdir(文件夹):
    if 文件.endswith(".xlsx"):
        print("正在读：", 文件)
        df = pd.read_excel(os.path.join(文件夹, 文件))
        所有表.append(df)

结果 = pd.concat(所有表, ignore_index=True)
结果.to_excel("全部合并.xlsx", index=False)
print("完成！共合并", len(结果), "行")
