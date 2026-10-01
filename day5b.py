# 升级版通讯录：永久保存
contacts = {}

# 启动时读文件
try:
    with open("contacts.txt", "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                name, phone = line.split(",")
                contacts[name] = phone
    print("已加载", len(contacts), "个联系人")
except FileNotFoundError:
    print("第一次使用，通讯录为空")

# 主循环
while True:
    name = input("\n请输入名字（输入 q 退出）：")
    if name == "q":
        # 退出前保存
        with open("contacts.txt", "w", encoding="utf-8") as f:
            for name, phone in contacts.items():
                f.write(name + "," + phone + "\n")
        print("已保存，再见！")
        break
    if name in contacts:
        print(name, "的电话是：", contacts[name])
    else:
        choice = input("没有找到，要添加吗？(y/n)：")
        if choice == "y":
            phone = input("请输入电话：")
            contacts[name] = phone
            print("已添加")
