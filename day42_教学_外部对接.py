# ============================================
# Day 42 教学：外部对接（AI军团接真实客户消息）
# 核心概念："接线员"
#   平台（微信/飞书/抖店）→ 消息格式各不同
#   → 接线员统一转成"客户说的话"
#   → 交给同一个AI军团处理
#   → 回复客户
# 你的工具箱里那个 /客服 接口，就是接线员！
# ============================================
import json
from openai import OpenAI

client = OpenAI(
    api_key="sk-6a8868ea41a140fead84ebda91965ac9",
    base_url="https://api.deepseek.com"
)

# ===== 复用Day41的迷你框架（Agent类）=====
工具注册表 = {
    "calc_price": {
        "def": lambda 价格, 重量, 出肉率: f"纯肉{重量*出肉率/100:.1f}斤，每斤成本{价格/(重量*出肉率/100):.1f}元，加5%提点卖{价格/(重量*出肉率/100)*1.05:.1f}元/斤",
        "schema": {
            "type": "function",
            "function": {
                "name": "calc_price",
                "description": "算榴莲纯肉价格：输入整箱价格、重量、出肉率",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "价格": {"type": "number", "description": "整箱价格（元）"},
                        "重量": {"type": "number", "description": "整箱重量（斤）"},
                        "出肉率": {"type": "number", "description": "出肉率百分比，A果40，B果30"}
                    },
                    "required": ["价格", "重量", "出肉率"]
                }
            }
        }
    }
}

class Agent:
    def __init__(self, 名字, 系统提示词, 会用哪些工具=None):
        self.名字 = 名字
        self.系统提示词 = 系统提示词
        self.工具 = [工具注册表[t]["schema"] for t in (会用哪些工具 or [])]
    def 干活(self, 任务, 最多轮=5):
        messages = [
            {"role": "system", "content": self.系统提示词},
            {"role": "user", "content": 任务}
        ]
        for 轮 in range(最多轮):
            r = client.chat.completions.create(model="deepseek-chat", messages=messages, tools=self.工具 or None)
            msg = r.choices[0].message
            if msg.tool_calls:
                messages.append({"role": "assistant", "content": msg.content, "tool_calls": [
                    {"id": 调用.id, "type": "function", "function": {"name": 调用.function.name, "arguments": 调用.function.arguments}}
                    for 调用 in msg.tool_calls
                ]})
                for 调用 in msg.tool_calls:
                    结果 = 工具注册表[调用.function.name]["def"](**json.loads(调用.function.arguments))
                    messages.append({"role": "tool", "tool_call_id": 调用.id, "content": 结果})
            else:
                return msg.content
        return "轮数太多，搞不定"

店长 = Agent("店长", "你是夏天榴莲店的AI客服，客户消息来了你负责搞定，回复100字内像真实店员，会算价就自己算。", ["calc_price"])

# ===== 核心：接线员 =====
def 提取消息(平台, 消息体):
    """每家平台消息格式不一样，统一提取出'客户说的话'"""
    if 平台 == "微信":
        return 消息体["内容"]["文本"]        # 微信：{"内容": {"文本": "..."}}
    if 平台 == "飞书":
        return 消息体["text"]               # 飞书：{"text": "..."}
    if 平台 == "抖店":
        return 消息体["msg"]["content"]     # 抖店：{"msg": {"content": "..."}}
    return "看不懂的消息"

def 接线员(平台, 消息体):
    说的话 = 提取消息(平台, 消息体)      # 1. 转格式
    回复 = 店长.干活(说的话)             # 2. 同一个AI处理（无论哪个平台）
    return 回复

# ===== 模拟三个平台发来消息 =====
测试 = [
    ("微信", {"内容": {"文本": "金枕一箱8斤780元出肉率45%，3斤装卖多少钱？"}}),
    ("飞书", {"text": "买回来是坏的怎么办？"}),
    ("抖店", {"msg": {"content": "你们几点下班？"}}),
]

print("===== 三个平台同时来消息，接线员统一处理 =====")
for 平台, 消息 in 测试:
    print(f"\n【{平台}】客户说：{提取消息(平台, 消息)}")
    print(f"   AI回复：{接线员(平台, 消息)}")
print()
print("=" * 45)
print("✅ 外部对接原理：")
print("  平台格式不同 → 接线员统一 → 同一个AI军团处理")
print("  你工具箱的 /客服 接口就是接线员，对接=把平台webhook指向它")
