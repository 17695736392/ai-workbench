from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI

# 创建应用
app = FastAPI()

# 允许网页调用接口（CORS：放开跨域限制，网页才能访问）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 配置AI
client = OpenAI(
    api_key="sk-6a8868ea41a140fead84ebda91965ac9",
    base_url="https://api.deepseek.com"
)

# 请求格式（所有接口都用这个）
class 请求(BaseModel):
    内容: str

# ---------- 1. AI客服 ----------
@app.post("/客服")
def 客服(请求: 请求):
    知识库 = """
你是"夏天榴莲店"的AI客服。
价格：金枕榴莲 75元/斤，猫山王 150元/斤
服务：坏果包赔，拍照片发微信就行
发货：下单后48小时内发货，全国包邮
"""
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": 知识库},
            {"role": "user", "content": 请求.内容}
        ]
    )
    return {"回答": response.choices[0].message.content}

# ---------- 2. 小红书文案 ----------
@app.post("/文案")
def 文案(请求: 请求):
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "你是小红书文案专家，输出50字以内的种草文案，要吸引人，用emoji。"},
            {"role": "user", "content": 请求.内容}
        ]
    )
    return {"回答": response.choices[0].message.content}

# ---------- 3. 写周报 ----------
@app.post("/周报")
def 周报(请求: 请求):
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "你是周报助手，把工作内容整理成正式的周报格式，分条列出。"},
            {"role": "user", "content": 请求.内容}
        ]
    )
    return {"回答": response.choices[0].message.content}

# ---------- 4. 起名 ----------
@app.post("/起名")
def 起名(请求: 请求):
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "你是起名专家，给出5个名字，每个附一句解释。"},
            {"role": "user", "content": 请求.内容}
        ]
    )
    return {"回答": response.choices[0].message.content}

# ---------- 5. 写标书 ----------
@app.post("/标书")
def 标书(请求: 请求):
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "你是标书撰写专家，输出规范的标书框架和内容。"},
            {"role": "user", "content": 请求.内容}
        ]
    )
    return {"回答": response.choices[0].message.content}

# 首页
@app.get("/")
def 首页():
    return {"消息": "AI接口超市，有5个接口：/客服 /文案 /周报 /起名 /标书"}

# 启动
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
