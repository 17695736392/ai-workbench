from openai import OpenAI
from config import API_KEY

client = OpenAI(
    api_key=API_KEY,
    base_url="https://api.deepseek.com"
)

# 这是你的知识库（你自己的产品信息）
知识库 = """
榴莲品种：
- 金枕：肉厚核小，甜度高，适合入门，65元/斤
- 猫山王：苦味重，口感浓郁，老饕最爱，150元/斤
- 干尧：果肉细腻，味道清淡，80元/斤

售后政策：
- 坏果包赔
- 不支持无理由退货
- 下单后24小时内发货
"""

def 问AI(问题):
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": f"你是一个榴莲店客服。根据下面的知识库回答问题。如果知识库没有，就说'不知道，请联系老板'。\n\n知识库：\n{知识库}"},
            {"role": "user", "content": 问题}
        ]
    )
    return response.choices[0].message.content

# 测试
print(问AI("金枕榴莲多少钱？"))
print(问AI("坏了怎么办？"))
print(问AI("能退货吗？"))
