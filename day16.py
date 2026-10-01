from openai import OpenAI
from config import API_KEY
import json
import sqlite3

client = OpenAI(
    api_key=API_KEY,
    base_url="https://api.deepseek.com"
)

# ===== 这是Agent能"动手"的工具 =====

def 查价格(品种):
    prices = {"金枕": 75, "猫山王": 150, "干尧": 80}
    return f"{品种} {prices.get(品种, 0)} 元/斤"

def 算总价(品种, 斤数):
    prices = {"金枕": 75, "猫山王": 150, "干尧": 80}
    单价 = prices.get(品种, 0)
    总价 = 单价 * 斤数
    return f"{品种} {斤数}斤，总价 {总价} 元"

def 写订单(品种, 斤数):
    conn = sqlite3.connect("订单.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS 订单 (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            品种 TEXT,
            斤数 INTEGER
        )
    """)
    cursor.execute("INSERT INTO 订单 (品种, 斤数) VALUES (?, ?)", (品种, 斤数))
    conn.commit()
    conn.close()
    return f"订单已保存：{品种} {斤数}斤"

# ===== 告诉AI这些工具怎么用 =====
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_price",
            "description": "查询榴莲单价",
            "parameters": {
                "type": "object",
                "properties": {"品种": {"type": "string"}},
                "required": ["品种"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calc_total",
            "description": "计算总价",
            "parameters": {
                "type": "object",
                "properties": {
                    "品种": {"type": "string"},
                    "斤数": {"type": "number"}
                },
                "required": ["品种", "斤数"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "save_order",
            "description": "保存订单到数据库",
            "parameters": {
                "type": "object",
                "properties": {
                    "品种": {"type": "string"},
                    "斤数": {"type": "number"}
                },
                "required": ["品种", "斤数"]
            }
        }
    }
]

# ===== 客户下单 =====
messages = [{"role": "user", "content": "我要2斤金枕，帮我算下多少钱，然后记下来"}]

# 第1轮：问AI要做什么
response = client.chat.completions.create(
    model="deepseek-chat",
    messages=messages,
    tools=tools
)
AI的回复 = response.choices[0].message
messages.append(AI的回复)

# 执行AI决定的工具
for tool_call in AI的回复.tool_calls:
    函数名 = tool_call.function.name
    参数 = json.loads(tool_call.function.arguments)
    
    if 函数名 == "get_price":
        结果 = 查价格(参数["品种"])
    elif 函数名 == "calc_total":
        结果 = 算总价(参数["品种"], 参数["斤数"])
    elif 函数名 == "save_order":
        结果 = 写订单(参数["品种"], 参数["斤数"])
    
    print(f"调用 {函数名}：{结果}")
    messages.append({"role": "tool", "tool_call_id": tool_call.id, "content": 结果})

# 第2轮：AI根据结果生成最终回复
final = client.chat.completions.create(
    model="deepseek-chat",
    messages=messages,
    tools=tools
)
print("\n最终回复：")
print(final.choices[0].message.content)
工作台.py