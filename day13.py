from openai import OpenAI
from config import API_KEY

client = OpenAI(
    api_key=API_KEY,
    base_url="https://api.deepseek.com"
)

def 查榴莲价格(品种):
    prices = {"金枕": 75, "猫山王": 150, "干尧": 80}
    if 品种 in prices:
        return f"{品种}榴莲 {prices[品种]} 元/斤"
    else:
        return "没有这个品种"

def 查售后政策():
    return "坏果包赔，不支持无理由退货，下单后24小时内发货"

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_price",
            "description": "查询榴莲价格",
            "parameters": {
                "type": "object",
                "properties": {
                    "品种": {"type": "string", "description": "榴莲品种名"}
                },
                "required": ["品种"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "after_sale",
            "description": "查询售后政策",
            "parameters": {"type": "object", "properties": {}}
        }
    }
]

# 1. 客户问问题
messages = [{"role": "user", "content": "金枕多少钱？坏了能赔吗？"}]

# 2. 问AI
response = client.chat.completions.create(
    model="deepseek-chat",
    messages=messages,
    tools=tools
)

AI的回复 = response.choices[0].message

# 3. 把AI的决定加到对话里
messages.append(AI的回复)

# 4. 看AI要调用哪个工具
for tool_call in AI的回复.tool_calls:
    函数名 = tool_call.function.name
    
    if 函数名 == "get_price":
        import json
        参数 = json.loads(tool_call.function.arguments)
        结果 = 查榴莲价格(参数["品种"])
    elif 函数名 == "after_sale":
        结果 = 查售后政策()
    
    # 把执行结果告诉AI
    messages.append({
        "role": "tool",
        "tool_call_id": tool_call.id,
        "content": 结果
    })
    print(f"调用了 {函数名}，结果：{结果}")

# 5. 再问AI，让它根据结果生成最终回复
final_response = client.chat.completions.create(
    model="deepseek-chat",
    messages=messages,
    tools=tools
)

print("\n最终回复：")
print(final_response.choices[0].message.content)
