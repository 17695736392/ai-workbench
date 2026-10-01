import gradio as gr
import pandas as pd
from openai import OpenAI
from config import API_KEY

client = OpenAI(
    api_key=API_KEY,
    base_url="https://api.deepseek.com"
)

def 分析文件(文件):
    if 文件 is None:
        return "请先上传Excel文件"
    
    df = pd.read_excel(文件.name)
    
    数据摘要 = f"这是一个{len(df)}行{len(df.columns)}列的表格。\n"
    数据摘要 += f"列名：{list(df.columns)}\n"
    数据摘要 += f"前5行数据：\n{df.head().to_string()}"
    
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "你是一个数据分析专家。用户给你一个表格数据，你帮他分析：1.数据概况 2.发现了什么问题 3.建议。简洁专业。"},
            {"role": "user", "content": f"数据：\n{数据摘要}"}
        ]
    )
    return response.choices[0].message.content

demo = gr.Interface(
    fn=分析文件,
    inputs=gr.File(label="上传Excel文件"),
    outputs=gr.Textbox(label="AI分析结果", lines=15),
    title="AI数据分析助手"
)

demo.launch()
