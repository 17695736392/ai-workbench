from fastapi import FastAPI

# 创建应用
app = FastAPI()

# 首页
@app.get("/")
def 首页():
    return {"消息": "欢迎来到夏天的AI工具站！"}

# 带参数的接口
@app.get("/hello/{name}")
def 打招呼(name: str):
    return {"消息": f"你好, {name}!欢迎使用AI工具站"}

# 查询参数
@app.get("/工具")
def 工具列表(分类: str = "全部"):
    return {"消息": f"正在查找分类：{分类}"}

# 启动
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
