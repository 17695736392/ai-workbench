import gradio as gr
import sqlite3
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
"""

conn = sqlite3.connect("对话记录.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS 对话 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    问题 TEXT,
    回答 TEXT
)
""")
conn.commit()

def 客服回答(问题, history):
    messages = [
        {"role": "system", "content": f"你是一个榴莲店客服。根据知识库回答。\n\n知识库：\n{知识库}"}
    ]
    messages.extend(history)
    messages.append({"role": "user", "content": 问题})
    
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages
    )
    回答 = response.choices[0].message.content
    
    cursor.execute("INSERT INTO 对话 (问题, 回答) VALUES (?, ?)", (问题, 回答))
    conn.commit()
    
    return 回答

demo = gr.ChatInterface(
    fn=客服回答,
    title="榴莲店AI客服（带记录）"
)

demo.launch()
