import gradio as gr
from openai import OpenAI
from config import API_KEY

client = OpenAI(
    api_key=API_KEY,
    base_url="https://api.deepseek.com"
)

def 写周报(这周干了啥):
    history = [
        {"role": "system", "content": "你是一个职场周报助手。用户告诉你这周干了什么，你帮他整理成一份正式周报，分'本周完成''下周计划''需要协调'三部分，专业简洁，不要废话。"},
        {"role": "user", "content": 这周干了啥}
    ]
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=history
    )
    return response.choices[0].message.content

demo = gr.Interface(
    fn=写周报,
    inputs=gr.Textbox(label="这周干了啥（随便写几句）", lines=5),
    outputs=gr.Textbox(label="AI生成的周报", lines=10),
    title="AI周报生成器"
)

demo.launch()
