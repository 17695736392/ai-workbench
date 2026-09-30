# ============================================
# Day 33 教学：让AI学会"动手干活"（Function Calling）
# 场景：客户问价 → AI决定调用"算价工具" → 真正算出 → 组织语言回复
# ============================================
import json
from openai import OpenAI

# ===== 第0步：连上AI =====
client = OpenAI(
    api_key="sk-6a8868ea41a140fead84ebda91965ac9",
    base_url="https://api.deepseek.com"
)

# ===== 第1步：告诉AI，你有一个"手"叫 算榴莲肉价 =====
# tools = 给AI看的"工具说明书"：有什么工具、怎么用、要什么参数
工具清单 = [
    {
        "type": "function",
        "function": {
            "name": "calc_durian_price",   # 注意：工具名只能英文/数字/下划线！
            "description": "根据整果卖价、斤数、出肉率，算出各规格榴莲纯肉的价格",
            "parameters": {
                "type": "object",
                "properties": {
                    "price": {"type": "number", "description": "整箱榴莲卖价，单位元"},
                    "weight": {"type": "number", "description": "整箱多少斤"},
                    "yield_rate": {"type": "number", "description": "出肉率百分比，A果填40，B果填30"}
                },
                "required": ["price", "weight", "yield_rate"]
            }
        }
    }
]

# ===== 第2步：这个"手"真正干活的样子（真实函数，就是算账逻辑） =====
def 算榴莲肉价(整果卖价, 斤数, 出肉率):
    每箱肉 = 斤数 * 出肉率 / 100          # 每箱能出多少斤肉
    肉单价 = 整果卖价 / 每箱肉            # 每斤肉的成本
    结果 = f"每箱肉{每箱肉:.2f}斤，纯肉单价{肉单价:.2f}元/斤\n"
    for 规格 in [1, 1.5, 2, 2.5, 3, 3.5, 4]:   # 各规格装
        成本 = 肉单价 * 规格
        提点 = 成本 * 0.05                      # 提点5%
        卖价 = 成本 + 提点
        结果 += f"{规格}斤装：成本{成本:.2f}元，加5%提点卖{卖价:.2f}元\n"
    return 结果

# ===== 第3步：客户来问价 =====
对话 = [
    {"role": "user", "content": "我家金枕780一箱，一箱8斤，出肉率45%，你帮我算算3斤装卖多少钱"}
]

# 第一次问AI：它不会直接答，而是"决定"要用哪个手，并告诉我们要什么参数
第1次 = client.chat.completions.create(
    model="deepseek-chat",
    messages=对话,
    tools=工具清单,        # 把"手"的说明书给AI
    tool_choice="auto",    # 让AI自己决定用不用
)

# 看AI的决定
调用 = 第1次.choices[0].message.tool_calls[0]
print("① AI决定要用：", 调用.function.name)
print("② AI要的参数：", 调用.function.arguments)
print()

# ===== 第4步：我们替AI执行这个"手"（真正干活！） =====
参数 = json.loads(调用.function.arguments)   # 把AI要的参数变成字典
执行结果 = 算榴莲肉价(整果卖价=参数["price"], 斤数=参数["weight"], 出肉率=参数["yield_rate"])
print("===== ③ 工具执行结果（真的算出来了） =====")
print(执行结果)

# ===== 第5步：把执行结果喂回给AI，让AI用大白话回复客户 =====
对话.append(第1次.choices[0].message)                 # 记下AI刚才的决定
对话.append({"role": "tool", "tool_call_id": 调用.id, "content": 执行结果})

第2次 = client.chat.completions.create(model="deepseek-chat", messages=对话)
print("===== ④ AI最终回复客户 =====")
print(第2次.choices[0].message.content)
