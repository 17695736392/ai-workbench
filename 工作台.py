import gradio as gr
import pandas as pd
import requests
import os
from datetime import datetime
from openai import OpenAI

API_KEY = ""
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

对话记录文件 = "对话记录.txt"
正确密码 = "981101"

def 初始化客户端():
    return OpenAI(api_key=API_KEY, base_url="https://api.deepseek.com")

def 调AI(system_prompt, 用户输入):
    client = 初始化客户端()
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": 用户输入}
        ]
    )
    return response.choices[0].message.content

def 保存对话(用户问题, AI回答):
    时间 = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(对话记录文件, "a", encoding="utf-8") as f:
        f.write(f"【{时间}】\n客户：{用户问题}\nAI：{AI回答}\n\n")

def 客服回答(问题, history):
    client = 初始化客户端()
    messages = [{"role": "system", "content": f"你是榴莲店客服。根据知识库回答，礼貌专业。\n\n知识库：{知识库}"}]
    messages.extend(history)
    messages.append({"role": "user", "content": 问题})
    response = client.chat.completions.create(model="deepseek-chat", messages=messages)
    回答 = response.choices[0].message.content
    保存对话(问题, 回答)
    return 回答

def 查看对话记录():
    if not os.path.exists(对话记录文件):
        return "还没有对话记录"
    with open(对话记录文件, "r", encoding="utf-8") as f:
        return f.read()

def 分析文件(文件):
    if 文件 is None:
        return "请先上传Excel文件"
    df = pd.read_excel(文件.name)
    数据摘要 = f"{len(df)}行{len(df.columns)}列，列名：{list(df.columns)}\n前5行：\n{df.head().to_string()}"
    return 调AI("你是数据分析专家，分析概况、问题、建议。", 数据摘要)

def 算价(品种, 斤数):
    prices = {"金枕": 75, "猫山王": 150, "干尧": 80}
    if 品种 not in prices:
        return "没有这个品种"
    return f"{品种} {斤数}斤，单价{prices[品种]}元/斤，总价{prices[品种]*斤数}元"

def 查天气(城市):
    if not 城市:
        return "请输入城市名"
    url = f"https://wttr.in/{城市}?format=3&lang=zh"
    response = requests.get(url)
    return response.text

def 查汇率(货币):
    if not 货币:
        return "请输入货币代码，如USD、EUR、JPY"
    url = f"https://api.exchangerate-api.com/v4/latest/{货币}"
    response = requests.get(url)
    data = response.json()
    人民币 = data["rates"]["CNY"]
    return f"1 {货币} = {人民币} 人民币"

def 总结长文(长文本):
    if not 长文本:
        return "请输入要总结的内容"
    return 调AI("你是文章总结专家，把下面的内容总结成200字以内的摘要，保留关键信息。", 长文本)

def 写代码(需求):
    if not 需求:
        return "请描述你要写什么代码"
    return 调AI("你是Python编程专家，根据需求写出完整可运行的代码，带注释说明。", 需求)

def 写标书(需求):
    if not 需求:
        return "请描述标书要求（项目名称、公司信息、资质等）"
    return 调AI("""你是专业标书撰写专家。根据客户提供的信息，写出一份完整的投标文件，包括：
1. 投标函
2. 公司简介
3. 技术方案
4. 报价表
5. 资质证明
6. 售后服务承诺
要求：格式正式、语言专业、符合招投标规范。""", 需求)

def 检查密码(密码):
    if 密码 == 正确密码:
        return gr.update(visible=True), ""
    return gr.update(visible=False), "❌ 密码错误"

def 保存设置(key):
    global API_KEY
    API_KEY = key
    return "✅ API Key 设置成功"

def 保存新知识库(新内容):
    global 知识库
    知识库 = 新内容
    return "✅ 知识库已更新"

自定义CSS = """
.gradio-container {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%) !important;
    color: white !important;
}
#title {
    text-align: center;
    font-size: 32px;
    font-weight: bold;
    color: #00d4ff !important;
    text-shadow: 0 0 20px rgba(0, 212, 255, 0.5);
    margin-bottom: 20px;
}
button.primary {
    background: linear-gradient(90deg, #00d4ff, #0099ff) !important;
    border: none !important;
    color: white !important;
    font-weight: bold !important;
    border-radius: 10px !important;
}
"""

with gr.Blocks(title="AI工作台", css=自定义CSS) as demo:
    gr.Markdown("# 🧰 AI工作台", elem_id="title")
    
    密码框 = gr.Textbox(label="请输入密码", type="password")
    错误提示 = gr.Markdown("")
    解锁按钮 = gr.Button("🔓 解锁", variant="primary", size="lg")
    
    内容区 = gr.Group(visible=False)
    解锁按钮.click(检查密码, inputs=密码框, outputs=[内容区, 错误提示])
    
    with 内容区:
        with gr.Tab("⚙️ 设置"):
            gr.Markdown("**第一步：填你的 DeepSeek API Key**（[获取地址](https://platform.deepseek.com)）")
            key输入 = gr.Textbox(label="API Key", type="password")
            key按钮 = gr.Button("保存API Key", variant="primary")
            状态 = gr.Textbox(label="状态", interactive=False)
            key按钮.click(保存设置, inputs=key输入, outputs=状态)
            
            gr.Markdown("---")
            gr.Markdown("**第二步：编辑知识库（改价格、产品信息）**")
            知识库输入 = gr.Textbox(label="知识库内容", value=知识库, lines=10)
            保存知识库按钮 = gr.Button("保存知识库", variant="primary")
            保存知识库按钮.click(保存新知识库, inputs=知识库输入, outputs=状态)
        
        with gr.Tab("AI工具箱"):
            with gr.Tab("小红书文案"):
                输入1 = gr.Textbox(label="输入产品信息")
                输出1 = gr.Textbox(label="AI生成", lines=10)
                gr.Button("生成").click(lambda x: 调AI("你是小红书文案助手，直接输出文案，带emoji。", x), inputs=输入1, outputs=输出1)
            with gr.Tab("客服话术"):
                输入2 = gr.Textbox(label="客户说什么")
                输出2 = gr.Textbox(label="回复", lines=5)
                gr.Button("生成").click(lambda x: 调AI("你是专业客服，礼貌回复。", x), inputs=输入2, outputs=输出2)
            with gr.Tab("AI起名"):
                输入4 = gr.Textbox(label="描述业务")
                输出4 = gr.Textbox(label="5个名字", lines=5)
                gr.Button("生成").click(lambda x: 调AI("你是起名专家，给5个名字加解释。", x), inputs=输入4, outputs=输出4)
            with gr.Tab("长文总结"):
                长文输入 = gr.Textbox(label="粘贴要总结的长文章", lines=10)
                总结输出 = gr.Textbox(label="AI总结", lines=8)
                gr.Button("总结").click(总结长文, inputs=长文输入, outputs=总结输出)
            with gr.Tab("写代码"):
                代码输入 = gr.Textbox(label="描述你要什么功能的代码（如：写一个计算BMI的程序）", lines=3)
                代码输出 = gr.Textbox(label="AI写的代码", lines=15)
                gr.Button("生成代码").click(写代码, inputs=代码输入, outputs=代码输出)
            with gr.Tab("写标书"):
                标书输入 = gr.Textbox(label="描述标书要求（项目名称、公司信息、资质等）", lines=5)
                标书输出 = gr.Textbox(label="AI写的标书", lines=20)
                gr.Button("生成标书").click(写标书, inputs=标书输入, outputs=标书输出)
            with gr.Tab("天气查询"):
                城市 = gr.Textbox(label="输入城市名（如：天津）")
                天气结果 = gr.Textbox(label="天气", lines=2)
                gr.Button("查询").click(查天气, inputs=城市, outputs=天气结果)
            with gr.Tab("汇率查询"):
                货币 = gr.Textbox(label="输入货币代码（如：USD、EUR、JPY）")
                汇率结果 = gr.Textbox(label="汇率", lines=2)
                gr.Button("查询").click(查汇率, inputs=货币, outputs=汇率结果)
        
        with gr.Tab("AI客服"):
            gr.ChatInterface(fn=客服回答, title="榴莲店AI客服")
        
        with gr.Tab("📋 对话记录"):
            gr.Markdown("查看客户和AI客服的所有对话")
            刷新按钮 = gr.Button("刷新记录", variant="primary")
            记录显示 = gr.Textbox(label="对话记录", lines=20)
            刷新按钮.click(查看对话记录, outputs=记录显示)
        
        with gr.Tab("数据分析"):
            上传 = gr.File(label="上传Excel")
            分析结果 = gr.Textbox(label="AI分析", lines=15)
            gr.Button("分析").click(分析文件, inputs=上传, outputs=分析结果)
        
        with gr.Tab("算价工具"):
            品种 = gr.Dropdown(["金枕", "猫山王", "干尧"], label="选品种")
            斤数 = gr.Number(label="几斤", value=1)
            价格结果 = gr.Textbox(label="结果")
            gr.Button("算价").click(算价, inputs=[品种, 斤数], outputs=价格结果)

demo.launch()
