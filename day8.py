from openai import OpenAI

client = OpenAI(
    api_key="sk-6a8868ea41a140fead84ebda91965ac9",
    base_url="https://api.deepseek.com"
)

# 对话历史
history =[{"role": "system", "content": "你是一个客服话术助手。用户告诉你客户投诉了什么问题，你直接给一段专业、礼貌、能安抚客户的回复，不要解释。"}]
while True:
    用户输入 = input("\n你说：")
    if 用户输入 == "q":
        print("再见！")
        break

    history.append({"role": "user", "content": 用户输入})

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=history
    )

    回复 = response.choices[0].message.content
    print("AI：", 回复)

    history.append({"role": "assistant", "content": 回复})
