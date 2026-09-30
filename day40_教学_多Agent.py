# ============================================
# Day 40 教学：多Agent协作（你的AI军团）
# 你（老板）→ 总指挥AI → 拆任务 → 派给专职AI们 → 汇总汇报
# 这就是"一个人指挥好几个AI工具人"的原理
# ============================================
import json
from openai import OpenAI

client = OpenAI(
    api_key="sk-6a8868ea41a140fead84ebda91965ac9",
    base_url="https://api.deepseek.com"
)

# ===== 专职AI军团（每个AI一门绝活）=====
def 文案AI(任务):
    """专职1：小红书文案专家"""
    r = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "你是资深小红书榴莲文案专家。写文案要求：口语化、有网感、突出榴莲的香甜浓郁、80字以内、直接输出文案不解释。"},
            {"role": "user", "content": 任务}
        ]
    )
    return r.choices[0].message.content

def 数据分析AI(任务):
    """专职2：数据分析师"""
    r = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "你是店铺数据分析师。给你数据你用数字说话：算占比、找亮点、说问题、给建议。输出简洁要点式分析。"},
            {"role": "user", "content": 任务}
        ]
    )
    return r.choices[0].message.content

# ===== 总指挥的工具：派活（名字只能英文）=====
派活工具 = [{
    "type": "function",
    "function": {
        "name": "assign_task",
        "description": "把子任务派给专职AI",
        "parameters": {
            "type": "object",
            "properties": {
                "谁": {"type": "string", "enum": ["文案AI", "数据分析AI"], "description": "派给哪个专职AI"},
                "任务": {"type": "string", "description": "给该AI的具体任务"}
            },
            "required": ["谁", "任务"]
        }
    }
}]

# ===== 总指挥：老板的AI大管家 =====
def 总指挥(老板任务):
    messages = [
        {"role": "system", "content": "你是老板的AI总指挥。老板把整个任务交给你，你要：1.拆解成子任务 2.派给对应专职AI（assign_task）3.全部拿到结果后，整理成一份给老板的完整汇报。汇报要清晰、有条理、像职业助理。"},
        {"role": "user", "content": 老板任务}
    ]
    for 轮 in range(8):    # 最多8轮，防止死循环
        r = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            tools=派活工具
        )
        msg = r.choices[0].message
        if msg.tool_calls:    # 总指挥决定：派活！
            messages.append({"role": "assistant", "content": msg.content, "tool_calls": [
                {"id": 调用.id, "type": "function", "function": {"name": 调用.function.name, "arguments": 调用.function.arguments}}
                for 调用 in msg.tool_calls
            ]})
            for 调用 in msg.tool_calls:
                args = json.loads(调用.function.arguments)
                print(f"   [总指挥] 派活：{args['谁']} ← {args['任务']}")
                if args["谁"] == "文案AI":
                    结果 = 文案AI(args["任务"])
                else:
                    结果 = 数据分析AI(args["任务"])
                print(f"      → {args['谁']}交回：{结果[:120]}……")
                messages.append({"role": "tool", "tool_call_id": 调用.id, "content": 结果})
        else:
            return msg.content    # 活都派完了，汇总汇报
    return "轮次太多，汇报不完"

# ===== 演示 =====
print("【老板】看看这个月销售数据（金枕卖120单收入8.4万，猫山王40单收入6万，坏果退5单），分析一下，再写条小红书文案夸夸猫山王，最后一起汇报给我。")
print()
print("【总指挥干活】")
结果 = 总指挥("看看这个月销售数据（金枕卖120单收入8.4万，猫山王40单收入6万，坏果退5单），分析一下，再写条小红书文案夸夸猫山王，最后一起汇报给我。")
print()
print("【给老板的汇报】")
print(结果)
print()
print("=" * 45)
print("✅ 多Agent协作原理：")
print("  老板 → 总指挥（拆任务+派活+汇总）→ 专职AI们（各自干活）")
print("  这就是'一个人指挥多个AI工具人'，代码和你工具箱一模一样")
