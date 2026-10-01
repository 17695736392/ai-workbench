# 终极版通讯录：函数 + 文件读写

def load_contacts():
    contacts = {}
    try:
        with open("contacts.txt", "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    name, phone = line.split(",")
                    contacts[name] = phone
    except FileNotFoundError:
        pass
    return contacts

def save_contacts(contacts):
    with open("contacts.txt", "w", encoding="utf-8") as f:
        for name, phone in contacts.items():
            f.write(name + "," + phone + "\n")

def show_menu():
    print("\n=== 通讯录 ===")
    print("1. 查联系人")
    print("2. 添加联系人")
    print("3. 退出")

def find_contact(contacts):
    name = input("输入要查的名字：")
    if name in contacts:
        print(name, "的电话是：", contacts[name])
    else:
        print("没有这个人")

def add_contact(contacts):
    name = input("输入名字：")
    phone = input("输入电话：")
    contacts[name] = phone
    print("已添加")

# 主程序
contacts = load_contacts()
print("已加载", len(contacts), "个联系人")

while True:
    show_menu()
    choice = input("请选择：")
    if choice == "1":
        find_contact(contacts)
    elif choice == "2":
        add_contact(contacts)
    elif choice == "3":
        save_contacts(contacts)
        print("已保存，再见")
        break
