# ===== 第二个测试：调用 Gemini =====

import os
from dotenv import load_dotenv
from google import genai

# 读取 .env 文件里的密钥
load_dotenv()

# 创建 Gemini 客户端
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# 向 Gemini 发送一个问题
response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents="用一句话介绍你自己"
)

# 打印 Gemini 的回答
print("Gemini 说：")
print(response.text)