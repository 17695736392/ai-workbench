#购物清单
shopping_list=["西瓜","牛奶","面包"]
print("初始清单:",shopping_list)

#添加商品
shopping_list.append("鸡蛋")
shopping_list.append("大米")
print("添加后:",shopping_list)

#删除商品
shopping_list.remove("牛奶")
print("删除后:",shopping_list)

#排序
shopping_list.sort()
print("排序后：",shopping_list)

#数数量
print("一共",len(shopping_list),"件商品")

#添加商品
shopping_list.append("薯条")

#删除商品
shopping_list.remove("薯条")
print("删除后:",shopping_list)