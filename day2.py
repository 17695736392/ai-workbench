# 升级版购物清单
shopping_list = ["西瓜", "牛奶", "面包", "鸡蛋", "大米"]

# for 循环：把清单里的东西一个一个拿出来
print("=== 购物清单 ===")
for item in shopping_list:
    print("- " + item)

# if 判断：看看清单里有没有牛奶
if "可乐" in shopping_list:
    print("好，可乐要买")
else:
    print("忘了买可乐，记得加上")

# 数一下有几件
    print("一共", len(shopping_list), "件商品")
if "西瓜"in shopping_list:
    print("西瓜是我最爱吃的")