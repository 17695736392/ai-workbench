from fastapi import FastAPI
from pydantic import BaseModel
from openai import OpenAI

# 创建应用
app = FastAPI()

# 配置AI
client = OpenAI(
    api_key="sk-6a8868ea41a140fead84ebda91965ac9",
    base_url="https://api.deepseek.com"
)

# 榴莲店知识库
知识库 = """
你是"夏天榴莲店"的AI客服。
价格：金枕榴莲 75元/斤，猫山王 150元/斤
服务：坏果包赔，拍照片发微信就行
发货：下单后48小时内发货，全国包邮
退货：收到货7天内，有问题随时联系
"""

# 定义请求格式
class 提问(BaseModel):
    问题: str

# AI客服接口
@app.post("/客服")
def ai客服(请求: 提问):
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": 知识库},
            {"role": "user", "content": 请求.问题}
        ]
    )
    return {"回答": response.choices[0].message.content}

# 首页
@app.get("/")
def 首页():
    return {"消息": "夏天榴莲店AI客服，请调用 /客服 接口"}

# 启动
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
