# ============================================
# Day 41 教学：Agent框架（你自己造一个）
# 你写过的"循环+工具"，封装成框架：
#   1. 工具注册表（谁都能用）
#   2. Agent类：名字 + 系统提示词 + 干活循环
#   3. 一行代码创建N个AI（你的军团）
# 这就是 LangGraph / CrewAI / MCP 的最小核心！
# ============================================
import json
from openai import OpenAI

client = OpenAI(
    api_key="sk-6a8868ea41a140fead84ebda91965ac9",
    base_url="https://api.deepseek.com"
)

# ===== 框架三件套 =====

# 1. 工具注册表（所有Agent共用的"技能库"）
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
    },
    "search_policy": {
        "def": lambda 问题: "坏果包赔：收货24小时内拍照联系客服，坏多少赔多少。发货：48小时内发出，全国包邮。规格：1斤~3斤装。客服时间：早9点到晚10点。",
        "schema": {
            "type": "function",
            "function": {
                "name": "search_policy",
                "description": "查店铺售后/发货/规格/工作时间政策",
                "parameters": {
                    "type": "object",
                    "properties": {"问题": {"type": "string", "description": "客户的问题"}},
                    "required": ["问题"]
                }
            }
        }
    }
}

# 2. Agent类：一个AI = 名字 + 系统提示词 + 可选工具（自己会循环干活）
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
            r = client.chat.completions.create(
                model="deepseek-chat",
                messages=messages,
                tools=self.工具 or None
            )
            msg = r.choices[0].message
            if msg.tool_calls:    # 这个AI决定：调用工具！
                messages.append({"role": "assistant", "content": msg.content, "tool_calls": [
                    {"id": 调用.id, "type": "function", "function": {"name": 调用.function.name, "arguments": 调用.function.arguments}}
                    for 调用 in msg.tool_calls
                ]})
                for 调用 in msg.tool_calls:
                    结果 = 工具注册表[调用.function.name]["def"](**json.loads(调用.function.arguments))
                    messages.append({"role": "tool", "tool_call_id": 调用.id, "content": 结果})
            else:
                return msg.content    # 这个AI判断：干完了，回答
        return "轮数太多，搞不定"

# 3. 一行代码创建你的AI军团（每个AI都有自己的岗位和技能）
店长 = Agent("店长", "你是夏天榴莲店的AI店长，客户消息来了你负责搞定，回复100字内像真实店员。", ["calc_price", "search_policy"])
文案 = Agent("文案", "你是资深小红书榴莲文案专家，口语化有网感80字内，直接输出不解释。")
分析师 = Agent("分析师", "你是店铺数据分析师，用数字说话，输出要点式分析。")

# ===== 使用 =====
print("【店长】客户：金枕一箱8斤780元出肉率45%，3斤装卖多少钱？")
print("店长说：" + 店长.干活("金枕一箱8斤780元出肉率45%，3斤装卖多少钱？"))
print()
print("【文案】任务：夸夸猫山王")
print("文案说：" + 文案.干活("夸夸猫山王，突出浓郁和高级感"))
print()
print("【分析师】任务：金枕120单8.4万，猫山王40单6万，坏果退5单，分析一下")
print("分析师说：" + 分析师.干活("金枕120单收入8.4万，猫山王40单收入6万，坏果退5单，分析一下"))
print()
print("=" * 45)
print("✅ 框架本质：注册工具 + Agent类 + 一行一个AI")
print("LangGraph=把流程画成图；CrewAI=团队分工；")
print("MCP=统一工具插头标准。核心全是上面这套！")
