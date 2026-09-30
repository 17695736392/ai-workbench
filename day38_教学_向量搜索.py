# ============================================
# Day 38 教学：向量搜索（升级版RAG）
# 关键词版："资料里必须出现一样的词才搜得到"
# 向量版：  "意思像就算，换个说法也能搜到"
# 原理：把每句话变成"向量"（数的列表），
#       越像的两句话，向量夹角越小
# ============================================
from openai import OpenAI
from collections import Counter

client = OpenAI(
    api_key="sk-6a8868ea41a140fead84ebda91965ac9",
    base_url="https://api.deepseek.com"
)

资料 = """夏天榴莲店售后政策：
1. 坏果包赔：收货后24小时内拍照联系客服，坏多少赔多少
2. 开果不满意：包退，运费我们承担
3. 金枕榴莲75元/斤，猫山王150元/斤
4. 发货：下单后48小时内发出，全国包邮
5. 榴莲纯肉分装规格：1斤装/1.5斤装/2斤装/2.5斤装/3斤装
6. 客服工作时间：早9点到晚10点"""

知识库 = [s.strip() for s in 资料.split("\n") if s.strip() and not s.startswith("夏天榴莲店")]

# ===== 向量核心：三步 =====
# 第1步：特征（把一句话变成"每个字出现几次"的计数表）
def 特征(句子):
    return Counter(c for c in 句子 if c not in "，。？！：、 ")

# 第2步：余弦相似度（两个向量夹角的"像不像"，0~1，越接近1越像）
def 相似度(句子A, 句子B):
    a, b = 特征(句子A), 特征(句子B)
    共同 = sum(a[c] * b[c] for c in a if c in b)
    长度 = (sum(a.values()) ** 0.5) * (sum(b.values()) ** 0.5)
    return 共同 / 长度 if 长度 else 0

# 第3步：搜索（给知识库每一条打分，取最像的前2条）
def 搜索(问题):
    打分 = [(相似度(问题, 条), 条) for 条 in 知识库]
    打分.sort(reverse=True)
    return [条 for _, 条 in 打分[:2]]

def 问答(问题):
    资料片段 = "\n".join(搜索(问题))
    r = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "你是客服助手。只能根据下面【资料】回答，资料里没有的就说'这个我得问老板'：\n【资料】\n" + 资料片段},
            {"role": "user", "content": 问题}
        ]
    )
    return r.choices[0].message.content

# ===== 演示 =====
print("关键词版搜不到的例子，向量版能搜到：")
print()
print("问题：你们几点下班？")
print("搜到的资料：")
for 条 in 搜索("你们几点下班？"):
    print("  -", 条)
print("回答：" + 问答("你们几点下班？"))
print()
print("问题：榴莲怎么卖？")
print("搜到的资料：")
for 条 in 搜索("榴莲怎么卖？"):
    print("  -", 条)
print("回答：" + 问答("榴莲怎么卖？"))
print()
print("问题：榴莲有什么规格？")
print("搜到的资料：")
for 条 in 搜索("榴莲有什么规格？"):
    print("  -", 条)
print("回答：" + 问答("榴莲有什么规格？"))
print()
print("=" * 40)
print("✅ 向量搜索原理：")
print("  1. 每句话 → 数每个字出现几次 → 一串数字（向量）")
print("  2. 两句话的向量夹角越小 → 越像（余弦相似度）")
print("  3. 客户怎么问都行，找'意思最像'的资料给AI")
