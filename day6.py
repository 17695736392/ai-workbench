# 函数版通讯录

def show_menu():
    print("\n=== 通讯录 ===")
    print("1. 查联系人")
    print("2. 添加联系人")
    print("3. 退出")

def add_contact(contacts):
    name = input("输入名字：")
    phone = input("输入电话：")
    contacts[name] = phone
    print("已添加")

def find_contact(contacts):
    name = input("输入要查的名字：")
    if name in contacts:
        print(name, "的电话是：", contacts[name])
    else:
        print("没有这个人")

# 主程序
contacts = {}

while True:
    show_menu()
    choice = input("请选择：")
    if choice == "1":
        find_contact(contacts)
    elif choice == "2":
        add_contact(contacts)
    elif choice == "3":
        print("再见")
        break
