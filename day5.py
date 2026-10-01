# 第一步：写文件
with open("test.txt", "w", encoding="utf-8") as f:
    f.write("你好，这是第一行\n")
    f.write("这是第二行\n")
    f.write("我是夏天，转行 AI 第 5 天\n")

print("文件已写入")

# 第二步：读文件
with open("test.txt", "r", encoding="utf-8") as f:
    content = f.read()

print("文件内容是：")
print(content)
