import sqlite3

conn = sqlite3.connect("对话记录.db")
cursor = conn.cursor()
cursor.execute("SELECT * FROM 对话")

print("所有对话记录：")
for row in cursor.fetchall():
    print(f"\n问题：{row[1]}")
    print(f"回答：{row[2]}")

conn.close()
