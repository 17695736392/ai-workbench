# ============================================
# Day 43 教学：AI军团（多AI并行协作）
# Day41 是"一个AI干完再干下一个"（串行）
# 今天升级成真军团：
#   1. 总指挥：把你的一句话任务，拆成多个子任务
#   2. 并行：多个AI同时开工（ThreadPoolExecutor）
#   3. 汇总：总指挥把各AI的产出，合成一份完整报告
# 这就是"一个人指挥AI军团"的真相！
# ============================================
import json
from concurrent.futures import ThreadPoolExecutor
from openai import OpenAI

client = OpenAI(
    api_key="sk-6a8868ea41a140fead84ebda91965ac9",
    base_url="https://api.deepseek.com"
)

# ===== 1. 工具注册表（所有AI共用的技能库，延续Day41） =====
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
    },
    # 总指挥的专用工具：拆任务（注意！工具名必须英文，中文会报400错）
    "split_task": {
        "def": None,   # 这个不由普通AI调，总指挥用它
        "schema": {
            "type": "function",
            "function": {
                "name": "split_task",
                "description": "把用户的一句话任务拆成多个子任务。ai只能是以下之一：分析师、文案、周报员、店长。",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "子任务们": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "ai": {"type": "string", "description": "分配给谁：分析师/文案/周报员/店长"},
                                    "任务": {"type": "string", "description": "给这个AI的具体任务"}
                                },
                                "required": ["ai", "任务"]
                            }
                        }
                    },
                    "required": ["子任务们"]
                }
            }
        }
    }
}

# ===== 2. Agent类（延续Day41：一个AI = 名字 + 岗位 + 技能） =====
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

# ===== 3. 一行一个AI，组成你的军团 =====
专职AI = {
    "店长": Agent("店长", "你是夏天榴莲店的AI店长，客户消息来了你负责搞定，回复100字内像真实店员。", ["calc_price", "search_policy"]),
    "文案": Agent("文案", "你是资深小红书榴莲文案专家，口语化有网感80字内，直接输出不解释。"),
    "分析师": Agent("分析师", "你是店铺数据分析师，用数字说话，输出要点式分析，给出结论和行动建议。"),
    "周报员": Agent("周报员", "你是店铺周报写手，把数据整理成一份周报：本周概况、数据明细、问题、下周计划。"),
}

# ===== 4. 总指挥：拆任务（用AI判断活怎么分） =====
def 拆任务(用户任务):
    messages = [
        {"role": "system", "content": "你是军团总指挥。把用户的任务拆成2-4个子任务，分配给最合适的AI：分析师（数据）、文案（小红书文案）、周报员（周报）、店长（定价/客服）。必须调用split_task工具。每个子任务要写清给那个AI的具体要求。"},
        {"role": "user", "content": 用户任务}
    ]
    r = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        tools=[工具注册表["split_task"]["schema"]]
    )
    msg = r.choices[0].message
    if not msg.tool_calls:
        return [{"ai": "店长", "任务": 用户任务}]   # AI没拆，原话丢给店长
    子任务们 = []
    for 调用 in msg.tool_calls:   # AI可能一次返回多个调用，全部收下
        try:
            args = json.loads(调用.function.arguments)
        except Exception:
            continue
        if "子任务们" in args:
            子任务们.extend(args["子任务们"])
        elif "ai" in args:
            子任务们.append(args)
    # 兜底：AI偶尔不按字段名写，用get取，取不到就原话丢给店长
    return 子任务们 or [{"ai": "店长", "任务": 用户任务}]

# ===== 5. 总指挥：并行执行 + 汇总 =====
def 总指挥(用户任务):
    print("【总指挥】收到任务，开始拆解...")
    子任务们 = 拆任务(用户任务)
    print(f"【总指挥】拆成 {len(子任务们)} 个子任务：")
    for 子 in 子任务们:
        print(f"   - {子.get('ai','店长')} ← {(子.get('任务') or '')[:40]}...")

    print("\n【军团】所有AI同时开工（并行）...")
    def 干一个(子):
        ai名 = 子.get("ai", "店长")                     # 兜底：AI字段写得不标准也能干活
        任务文本 = 子.get("任务") or 子.get("task") or 子.get("content") or str(子)
        return (ai名, 专职AI.get(ai名, 专职AI["店长"]).干活(任务文本))
    with ThreadPoolExecutor(max_workers=4) as pool:
        结果们 = list(pool.map(干一个, 子任务们))

    print("【军团】全部干完，汇总成报告...\n")
    # 把各AI的产出拼给总指挥，生成最终完整报告
    if len(结果们) == 1:
        return 结果们[0][1]
    汇总材料 = "\n\n".join([f"### {名字}的产出：\n{内容}" for 名字, 内容 in 结果们])
    messages = [
        {"role": "system", "content": "你是军团总指挥。把下面各AI的产出合并成一份给老板看的完整报告：分模块、去重复、逻辑连贯，开头一句话总结。直接输出报告，不解释。"},
        {"role": "user", "content": 汇总材料}
    ]
    r = client.chat.completions.create(model="deepseek-chat", messages=messages)
    return r.choices[0].message.content

# ===== 使用：一句话，军团出动 =====
if __name__ == "__main__":
    任务 = "本周金枕卖了120单收入8.4万，猫山王卖了40单收入6万，坏果退单5单。帮我：1分析这周经营情况 2给猫山王写条小红书文案 3写本周周报 4算金枕3斤装定价（整箱780元8斤出肉率45%）"
    print("=" * 50)
    print("老板一句话：" + 任务[:30] + "...")
    print("=" * 50 + "\n")
    报告 = 总指挥(任务)
    print("\n" + "=" * 50)
    print("【最终报告】")
    print("=" * 50)
    print(报告)
