# ============================================
# Day 39 教学：Agent编排（AI自己决定怎么干活）
# 把技能全挂上，AI当"店长"：
#   客户消息来了 → 自己判断要调哪个工具
#   → 调工具拿结果 → 再判断 → 直到能回答客户
# 这就是"让AI动手操作"的核心：AI会自己按需调用工具
# ============================================
import json
from openai import OpenAI

client = OpenAI(
    api_key="sk-6a8868ea41a140fead84ebda91965ac9",
    base_url="https://api.deepseek.com"
)

# ===== 注册工具（给AI配"手"，每只手会一门技能）=====
工具清单 = [
    {
        "type": "function",
        "function": {
            "name": "calc_price",
            "description": "客户问价格、要买榴莲时调用：输入整箱价格、整箱重量、出肉率，算出纯肉每斤成本和售价",
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
    },
    {
        "type": "function",
        "function": {
            "name": "search_policy",
            "description": "客户问售后、退换、发货、规格、工作时间时调用：输入问题，返回店里相关资料",
            "parameters": {
                "type": "object",
                "properties": {"问题": {"type": "string", "description": "客户的问题"}},
                "required": ["问题"]
            }
        }
    }
]

# ===== AI的"手"：工具真的干活 =====
def 算榴莲价(价格, 重量, 出肉率):
    纯肉 = 重量 * 出肉率 / 100
    每斤成本 = 价格 / 纯肉
    售价 = 每斤成本 * 1.05    # 抖音每单5%提点
    return f"整箱{重量}斤、出肉率{出肉率}% → 纯肉{纯肉:.1f}斤，每斤成本{每斤成本:.1f}元，加5%提点后卖{售价:.1f}元/斤"

知识库 = [
    "坏果包赔：收货后24小时内拍照联系客服，坏多少赔多少",
    "开果不满意：包退，运费我们承担",
    "发货：下单后48小时内发出，全国包邮",
    "榴莲纯肉分装规格：1斤装/1.5斤装/2斤装/2.5斤装/3斤装",
    "客服工作时间：早9点到晚10点",
]

def 查售后政策(问题):
    # 向量搜索：不管客户怎么措辞，找"意思最像"的资料（Day38学过的）
    from collections import Counter
    def 特征(句子):
        return Counter(c for c in 句子 if c not in "，。？！：、 ")
    def 相似度(A, B):
        a, b = 特征(A), 特征(B)
        共同 = sum(a[c] * b[c] for c in a if c in b)
        长度 = (sum(a.values()) ** 0.5) * (sum(b.values()) ** 0.5)
        return 共同 / 长度 if 长度 else 0
    打分 = sorted(((相似度(问题, 条), 条) for 条 in 知识库), reverse=True)
    命中 = [条 for _, 条 in 打分[:2] if _ > 0]
    return "\n".join(命中) if 命中 else "资料里没有这条，让店长问老板"

# ===== Agent循环：AI自己安排干活，最多5轮防死循环 =====
def 店长(消息):
    messages = [
        {"role": "system", "content": "你是'夏天榴莲店'的AI店长。客户消息来了你负责搞定：需要算价就调算价工具，需要售后政策就调查询工具，全部干完再给客户最终回复。回复要像真实店员，100字以内。"},
        {"role": "user", "content": 消息}
    ]
    for 轮 in range(5):
        r = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            tools=工具清单
        )
        msg = r.choices[0].message
        if msg.tool_calls:    # AI决定：我要调用工具！
            messages.append({"role": "assistant", "content": msg.content, "tool_calls": [
                {"id": 调用.id, "type": "function", "function": {"name": 调用.function.name, "arguments": 调用.function.arguments}}
                for 调用 in msg.tool_calls
            ]})
            for 调用 in msg.tool_calls:
                工具 = {"calc_price": 算榴莲价, "search_policy": 查售后政策}[调用.function.name]
                结果 = 工具(**json.loads(调用.function.arguments))
                print(f"   [第{轮+1}轮] AI决定调用「{调用.function.name}」→ {结果}")
                messages.append({"role": "tool", "tool_call_id": 调用.id, "content": 结果})
        else:
            return msg.content    # AI判断：不用调工具了，直接回答
    return "轮数太多，我搞不定了，先这样回复吧"

# ===== 演示 =====
print("客户消息：金枕一箱8斤780元，出肉率45%，3斤装卖多少钱？")
print("店长回复：" + 店长("金枕一箱8斤780元，出肉率45%，3斤装卖多少钱？"))
print()
print("客户消息：买回来是坏的怎么办？")
print("店长回复：" + 店长("买回来是坏的怎么办？"))
print()
print("客户消息：你们几点下班？")
print("店长回复：" + 店长("你们几点下班？"))
print()
print("=" * 45)
print("✅ Agent编排核心：AI自己决定调哪个工具 → 拿到结果 → 再决定")
print("这和你工具箱里客服的原理一样，只是从'1只手'升级成'多只手'")
