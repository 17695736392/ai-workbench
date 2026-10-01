import gradio as gr
from openai import OpenAI
from config import API_KEY

client = OpenAI(
    api_key=API_KEY,
    base_url="https://api.deepseek.com"
)

知识库 = """
榴莲品种：
- 金枕：肉厚核小，甜度高，适合入门，75元/斤
- 猫山王：苦味重，口感浓郁，老饕最爱，150元/斤
- 干尧：果肉细腻，味道清淡，80元/斤

售后政策：
- 坏果包赔
- 不支持无理由退货
- 下单后24小时内发货
"""

def 客服回答(问题, history):
    messages = [
        {"role": "system", "content": f"你是一个榴莲店客服。根据知识库回答问题。如果知识库没有，就说'请联系老板'。\n\n知识库：\n{知识库}"}
    ]
    messages.extend(history)
    messages.append({"role": "user", "content": 问题})
    
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages
    )
    return response.choices[0].message.content

demo = gr.ChatInterface(
    fn=客服回答,
    title="榴莲店AI客服"
)

demo.launch()
