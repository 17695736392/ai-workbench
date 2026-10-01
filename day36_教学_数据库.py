# ============================================
# Day 36 教学：数据库（AI的记忆）
# 你的工具箱其实已经在用数据库了（云端 records.db）！
# 今天搞懂最常用的 4 个操作：增 删 改 查
# ============================================
import sqlite3

# 1. 连接数据库（没有就自动创建）——像打开一个"记账本"
conn = sqlite3.connect("教学库.db")
cur = conn.cursor()

# 2. 建表（像Excel的表头：哪几列）
cur.execute("""
CREATE TABLE IF NOT EXISTS 客户 (
    key TEXT UNIQUE,      -- 密钥（客户唯一身份）
    客户名 TEXT,           -- 客户叫啥
    次数 INTEGER           -- 用了多少次
)
""")
print("✅ 建好'客户'表（列：key / 客户名 / 次数）")
print()

# 3. 增 INSERT —— 新开一个客户（工具箱的 /开通 就是这个）
cur.execute("INSERT INTO 客户 VALUES ('test001', '测试客户', 0)")
conn.commit()
print("【增】INSERT 新开客户 → 测试客户")

# 4. 查 SELECT —— 看看有几个客户、各自用了多少次
cur.execute("SELECT * FROM 客户")
print("【查】SELECT 全部客户：", cur.fetchall())

# 5. 改 UPDATE —— 客户用了一次，次数+1（工具箱每次调用都干这个）
cur.execute("UPDATE 客户 SET 次数 = 次数 + 1 WHERE key = 'test001'")
conn.commit()
cur.execute("SELECT 客户名, 次数 FROM 客户 WHERE key = 'test001'")
print("【改】UPDATE 次数+1 后：", cur.fetchall())

# 6. 删 DELETE —— 删掉测试数据（别把真客户删了！）
cur.execute("DELETE FROM 客户 WHERE key = 'test001'")
conn.commit()
cur.execute("SELECT * FROM 客户")
print("【删】DELETE 后还剩：", cur.fetchall())
print()
print("=" * 40)
print("核心就 4 个词：增 INSERT / 删 DELETE / 改 UPDATE / 查 SELECT")
print("合称：增删改查（SQL入门的一半就是它）")
print()
print("你工具箱 day31.py 里的：")
print("  - 验证密钥 = SELECT（查）")
print("  - 开通客户 = INSERT（增）")
print("  - 次数+1   = UPDATE（改）")
print("  - 看记录   = SELECT（查）")
print("你其实已经在用数据库了，今天只是把名字对上号！")
conn.close()
