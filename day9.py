import gradio as gr
from openai import OpenAI

client = OpenAI(
    api_key="sk-6a8868ea41a140fead84ebda91965ac9",
    base_url="https://api.deepseek.com"
)

def 写文案(产品信息):
    history = [
        {"role": "system", "content": "你是一个小红书文案助手，用户告诉你想发什么内容，你直接输出一篇小红书风格文案，带emoji，不要解释。"},
        {"role": "user", "content": 产品信息}
    ]
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=history
    )
    return response.choices[0].message.content

demo = gr.Interface(
    fn=写文案,
    inputs=gr.Textbox(label="输入产品信息"),
    outputs=gr.Textbox(label="AI生成的文案"),
    title="小红书文案生成器"
)

demo.launch(share=True)

