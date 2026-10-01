import gradio as gr
from openai import OpenAI

client = OpenAI(
    api_key="sk-6a8868ea41a140fead84ebda91965ac9",
    base_url="https://api.deepseek.com"
)

def 写客服话术(客户问题):
    history = [
        {"role": "system", "content": "你是一个专业客服。用户告诉你客户的问题，你直接给一段礼貌、专业、能解决问题的回复，不要解释。"},
        {"role": "user", "content": 客户问题}
    ]
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=history
    )
    return response.choices[0].message.content

demo = gr.Interface(
    fn=写客服话术,
    inputs=gr.Textbox(label="客户说什么"),
    outputs=gr.Textbox(label="你回复客户的话术"),
    title="AI客服话术生成器"
)

demo.launch()
