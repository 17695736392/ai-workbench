# 通讯录雏形
contacts = {
    "妈妈": "13800001111",
    "爸爸": "13800002222",
    "小明": "13800003333",
    "小黄": "15502229062",
    "老王": "13512055056"
}

# 1. 查询联系人
print("妈妈的电话：", contacts["妈妈"])

# 2. 添加新联系人
contacts["小红"] = "13800004444"
print("添加后：", contacts)

# 3. 遍历所有联系人
print("\n=== 通讯录 ===")
for name, phone in contacts.items():
    print(name, ":", phone)
if "老王" in contacts:
    print("老王的电话：", contacts["老王"])
else:
    print("通讯录里没有老王")
