# ===== 测试硅基流动调用 4 个 AI =====

import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# 硅基流动客户端（一个客户端调用所有模型）
client = OpenAI(
    api_key=os.getenv("SILICONFLOW_API_KEY"),
    base_url="https://api.siliconflow.cn/v1"
)

# 要测试的模型
models = {
    "DeepSeek": "deepseek-ai/DeepSeek-R1",
    "KIMI": "Pro/moonshotai/Kimi-K2.5",
    "智谱": "Pro/zai-org/GLM-5",
    "千问": "Qwen/Qwen3-VL-32B-Thinking",
    "腾讯": "tencent/Hunyuan-A13B-Instruct",
}

for name, model_id in models.items():
    print(f"测试 {name}（{model_id}）...")
    try:
        response = client.chat.completions.create(
            model=model_id,
            messages=[{"role": "user", "content": "用一句话介绍你自己"}],
            max_tokens=200,
        )
        print(f"   ✅ {name}：{response.choices[0].message.content}\n")
    except Exception as e:
        print(f"   ❌ {name} 失败：{e}\n")

print("🎉 测试完成！")