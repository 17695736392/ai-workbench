import gradio as gr
from openai import OpenAI
from config import API_KEY

client = OpenAI(
    api_key=API_KEY,
    base_url="https://api.deepseek.com"
)

def 起名(业务描述):
    history = [
        {"role": "system", "content": "你是一个起名专家。用户告诉你他的业务，你直接给5个好听、好记、有寓意的名字，每个名字配一句解释，不要废话。"},
        {"role": "user", "content": 业务描述}
    ]
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=history
    )
    return response.choices[0].message.content

demo = gr.Interface(
    fn=起名,
    inputs=gr.Textbox(label="你要起什么名？描述一下你的业务"),
    outputs=gr.Textbox(label="AI起的名字"),
    title="AI起名助手"
)

demo.launch()
