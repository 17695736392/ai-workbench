import gradio as gr
from openai import OpenAI
from config import API_KEY

client = OpenAI(
    api_key=API_KEY,
    base_url="https://api.deepseek.com"
)

def 调AI(system_prompt, 用户输入):
    history = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": 用户输入}
    ]
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=history
    )
    return response.choices[0].message.content

with gr.Blocks(title="AI工具箱") as demo:
    gr.Markdown("# 🧰 我的AI工具箱")
    
    with gr.Tab("小红书文案"):
        输入1 = gr.Textbox(label="输入产品信息")
        输出1 = gr.Textbox(label="AI生成的文案", lines=10)
        gr.Button("生成").click(
            lambda x: 调AI("你是一个小红书文案助手，直接输出小红书风格文案，带emoji，不要解释。", x),
            inputs=输入1, outputs=输出1
        )
    
    with gr.Tab("客服话术"):
        输入2 = gr.Textbox(label="客户说什么")
        输出2 = gr.Textbox(label="你回复客户的话术", lines=10)
        gr.Button("生成").click(
            lambda x: 调AI("你是一个专业客服，直接给礼貌专业的回复，不要解释。", x),
            inputs=输入2, outputs=输出2
        )
    
    with gr.Tab("AI周报"):
        输入3 = gr.Textbox(label="这周干了啥", lines=5)
        输出3 = gr.Textbox(label="AI生成的周报", lines=10)
        gr.Button("生成").click(
            lambda x: 调AI("你是一个职场周报助手，分本周完成/下周计划/需要协调三部分，不要废话。", x),
            inputs=输入3, outputs=输出3
        )
    
    with gr.Tab("AI起名"):
        输入4 = gr.Textbox(label="你要起什么名？描述业务")
        输出4 = gr.Textbox(label="AI起的名字", lines=10)
        gr.Button("生成").click(
            lambda x: 调AI("你是起名专家，直接给5个名字配解释，不要废话。", x),
            inputs=输入4, outputs=输出4
        )

    with gr.Tab("AI翻译"):
        输入5 = gr.Textbox(label="要翻译的中文")
        输出5 = gr.Textbox(label="英文翻译", lines=5)
        gr.Button("翻译").click(
            lambda x: 调AI("你是专业翻译，把中文翻译成英文，只给译文，不要解释。", x),
            inputs=输入5, outputs=输出5
        )
    
    with gr.Tab("AI总结"):
        输入6 = gr.Textbox(label="要总结的长文", lines=8)
        输出6 = gr.Textbox(label="总结结果", lines=5)
        gr.Button("总结").click(
            lambda x: 调AI("你是总结专家，把长文用3句话总结核心，不要废话。", x),
            inputs=输入6, outputs=输出6
        )
    
    with gr.Tab("AI写邮件"):
        输入7 = gr.Textbox(label="邮件主题和要点")
        输出7 = gr.Textbox(label="AI写的邮件", lines=10)
        gr.Button("生成").click(
            lambda x: 调AI("你是商务邮件助手，帮用户写正式礼貌的商务邮件，不要废话。", x),
            inputs=输入7, outputs=输出7
        )

    with gr.Tab("AI起标题"):
        输入8 = gr.Textbox(label="写的是什么内容")
        输出8 = gr.Textbox(label="AI起的标题", lines=5)
        gr.Button("生成").click(
            lambda x: 调AI("你是一个爆款标题专家，给用户5个吸引人的文章/视频标题，每个标题不超过20字，带emoji，不要废话。", x),
            inputs=输入8, outputs=输出8
        )
    
    with gr.Tab("AI润色"):
        输入9 = gr.Textbox(label="要润色的文字", lines=5)
        输出9 = gr.Textbox(label="润色后的文字", lines=5)
        gr.Button("润色").click(
            lambda x: 调AI("你是文字润色专家，把用户给的文字改得更通顺、更专业、更有吸引力，保持原意，不要解释。", x),
            inputs=输入9, outputs=输出9
        )
    
    with gr.Tab("AI写抖音脚本"):
        输入10 = gr.Textbox(label="视频主题是什么")
        输出10 = gr.Textbox(label="AI写的抖音脚本", lines=10)
        gr.Button("生成").click(
            lambda x: 调AI("你是一个抖音脚本专家。用户告诉你视频主题，你写一个30秒的抖音短视频脚本，分开头钩子、中间内容、结尾引导关注三部分，口语化，不要废话。", x),
            inputs=输入10, outputs=输出10
        )

demo.launch(share=True)