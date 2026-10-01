# 交互式通讯录
contacts = {
    "妈妈": "13800001111",
    "爸爸": "13800002222",
    "小明": "13800003333"
}

print("=== 我的通讯录 ===")

while True:
    name = input("\n请输入名字（输入 q 退出）：")
    
    if name == "q":
        print("再见！")
        break
    
    if name in contacts:
        print(name, "的电话是：", contacts[name])
    else:
        choice = input("没有找到，要添加吗？(y/n)：")
        if choice == "y":
            phone = input("请输入电话：")
            contacts[name] = phone
            print("已添加：", name, phone)
