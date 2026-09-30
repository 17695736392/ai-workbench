# ============================================
# Day 34 教学：流式输出（AI打字机效果）
# 对比：普通模式（一次性吐完）vs 流式模式（边出边看）
# ============================================
from openai import OpenAI

client = OpenAI(
    api_key="sk-6a8868ea41a140fead84ebda91965ac9",
    base_url="https://api.deepseek.com"
)

对话 = [{"role": "user", "content": "帮我写一段介绍榴莲的种草文案，要生动有画面感"}]

print("===== 普通模式（等30秒，一次性全吐出来） =====")
r = client.chat.completions.create(model="deepseek-chat", messages=对话)
print(r.choices[0].message.content)
print()

print("===== 流式模式（打字机效果，1秒就开始出字） =====")
流 = client.chat.completions.create(
    model="deepseek-chat",
    messages=对话,
    stream=True,        # 【关键】就加这一个参数，开启流式
)
文字 = ""
for 片段 in 流:
    if 片段.choices and 片段.choices[0].delta and 片段.choices[0].delta.content:
        字 = 片段.choices[0].delta.content
        print(字, end="", flush=True)   # 不换行，边出边打印
        文字 += 字
print()
print()
print("===== 总结 =====")
print("普通模式：一次请求，等全部生成完才返回")
print("流式模式：stream=True，AI每生成一点就吐一点，体验像真人打字")
