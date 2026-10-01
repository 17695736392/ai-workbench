import sqlite3

# 连接数据库（文件不存在会自动创建）
conn = sqlite3.connect("客户.db")
cursor = conn.cursor()

# 建表
cursor.execute("""
CREATE TABLE IF NOT EXISTS 客户 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    名字 TEXT,
    电话 TEXT,
    需求 TEXT
)
""")

# 插入3条数据
cursor.execute("INSERT INTO 客户 (名字, 电话, 需求) VALUES (?, ?, ?)", 
               ("张三", "13800138000", "金枕榴莲"))
cursor.execute("INSERT INTO 客户 (名字, 电话, 需求) VALUES (?, ?, ?)", 
               ("李四", "13900139000", "猫山王"))
cursor.execute("INSERT INTO 客户 (名字, 电话, 需求) VALUES (?, ?, ?)", 
               ("王五", "13700137000", "干尧"))

conn.commit()

# 查询所有客户
cursor.execute("SELECT * FROM 客户")
print("所有客户：")
for row in cursor.fetchall():
    print(row)

# 按条件查询
cursor.execute("SELECT * FROM 客户 WHERE 需求 = ?", ("金枕榴莲",))
print("\n买金枕的客户：")
for row in cursor.fetchall():
    print(row)

conn.close()

