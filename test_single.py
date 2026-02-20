# ===== 第一个测试：调用 ChatGPT =====

# 导入需要的工具
import os
from dotenv import load_dotenv
from openai import OpenAI

# 读取 .env 文件里的密钥
load_dotenv()

# 创建 ChatGPT 客户端
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

# 向 ChatGPT 发送一个问题
response = client.chat.completions.create(
    model="gpt-4o-mini",          # 使用的模型（便宜又好用）
    messages=[
        {"role": "user", "content": "用一句话介绍你自己"}
    ]
)

# 打印 ChatGPT 的回答
print("ChatGPT 说：")
print(response.choices[0].message.content)