# ===== AI 群聊系统（硅基流动版） =====

import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# 硅基流动客户端
client = OpenAI(
    api_key=os.getenv("SILICONFLOW_API_KEY"),
    base_url="https://api.siliconflow.cn/v1",
)

# 参与群聊的 AI 们
AI_LIST = [
    {"name": "🔵 DeepSeek", "model": "deepseek-ai/DeepSeek-R1"},
    {"name": "🟣 KIMI", "model": "Pro/moonshotai/Kimi-K2.5"},
    {"name": "🟢 智谱", "model": "Pro/zai-org/GLM-5"},
    {"name": "🟠 千问", "model": "Qwen/Qwen3-VL-32B-Thinking"},
    {"name": "🟠 腾讯", "model": "tencent/Hunyuan-A13B-Instruct"},
]

# 对话历史
chat_history = []


def ask_ai(ai, conversation_text):
    """让某个 AI 基于对话历史发言"""
    other_names = ", ".join(a["name"] for a in AI_LIST if a["name"] != ai["name"])

    response = client.chat.completions.create(
        model=ai["model"],
        messages=[
            {
                "role": "system",
                "content": (
                    f"你是{ai['name']}，正在一个多AI讨论群里。\n"
                    f"其他参与者有：{other_names}\n"
                    f"请阅读对话历史，给出你的独特观点。\n"
                    f"可以补充、反驳或赞同其他AI的观点。\n"
                    f"请保持简洁，用中文回答，不超过150字。\n"
                    f"不要重复别人已经说过的内容。"
                ),
            },
            {"role": "user", "content": conversation_text},
        ],
        max_tokens=300,
    )
    return response.choices[0].message.content


def format_history():
    """把对话历史格式化成文字"""
    text = ""
    for msg in chat_history:
        text += f"{msg['speaker']}：{msg['content']}\n\n"
    return text


def group_chat(question, rounds=2):
    """群聊主流程"""
    print("\n" + "🟢" * 25)
    print("         AI 群聊开始！")
    print("🟢" * 25)
    print(f"\n参与者：{' | '.join(a['name'] for a in AI_LIST)}")

    # 记录用户的问题
    chat_history.append({"speaker": "👤 用户", "content": question})
    print(f"\n👤 用户：{question}")

    # 多轮讨论
    for r in range(1, rounds + 1):
        print("\n" + "=" * 50)
        print(f"📢 第 {r} 轮讨论")
        print("=" * 50)

        for ai in AI_LIST:
            print(f"\n{ai['name']} 正在思考...")
            try:
                answer = ask_ai(ai, format_history())
                chat_history.append({"speaker": ai["name"], "content": answer})
                print(f"{ai['name']}：{answer}")
            except Exception as e:
                error_msg = f"[发言失败：{e}]"
                chat_history.append({"speaker": ai["name"], "content": error_msg})
                print(f"{ai['name']}：{error_msg}")

    # 最终总结（用 DeepSeek 做总结）
    print("\n" + "=" * 50)
    print("📋 讨论总结")
    print("=" * 50)

    try:
        summary = client.chat.completions.create(
            model="deepseek-ai/DeepSeek-V3",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "你是讨论主持人，请总结以下讨论：\n"
                        "1. 各方的主要观点\n"
                        "2. 大家的共识\n"
                        "3. 主要分歧\n"
                        "用中文回答，不超过200字。"
                    ),
                },
                {"role": "user", "content": format_history()},
            ],
            max_tokens=400,
        )
        print(f"\n🎯 总结：{summary.choices[0].message.content}")
    except Exception as e:
        print(f"\n🎯 总结生成失败：{e}")

    print("\n" + "🔴" * 25)
    print("         AI 群聊结束！")
    print("🔴" * 25)


# ===== 启动群聊 =====
if __name__ == "__main__":
    print("=" * 50)
    print("     欢迎使用 AI 群聊系统！")
    print("  DeepSeek | KIMI | 智谱 | 千问")
    print("=" * 50)

    question = input("\n请输入你想让 AI 们讨论的问题：")
    rounds_input = input("讨论��轮？（直接回车默认2轮）：")
    rounds = int(rounds_input) if rounds_input else 2

    group_chat(question, rounds)