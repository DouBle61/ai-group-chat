# ===== AI 群聊系统 - 网页版 =====

import os
from dotenv import load_dotenv
from openai import OpenAI
from flask import Flask, render_template, request, jsonify

load_dotenv()

# 创建网页应用
app = Flask(__name__)

# 硅基流动客户端
api_key = os.getenv("SILICONFLOW_API_KEY")
if not api_key:
    print("⚠️ 警告：SILICONFLOW_API_KEY 未设置！")

client = OpenAI(
    api_key=api_key or "missing-key",
    base_url="https://api.siliconflow.cn/v1",
)

# 参与群聊的 AI 们
AI_LIST = [
    {"name": "DeepSeek", "model": "deepseek-ai/DeepSeek-V3", "emoji": "🔵", "color": "#4A90D9"},
    {"name": "KIMI", "model": "moonshotai/Kimi-K2-Instruct", "emoji": "🟣", "color": "#9B59B6"},
    {"name": "智谱", "model": "THUDM/GLM-4-9B-Chat", "emoji": "🟢", "color": "#2ECC71"},
    {"name": "千问", "model": "Qwen/Qwen3-8B", "emoji": "🟠", "color": "#E67E22"},
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


@app.route("/")
def home():
    """显示主页"""
    return render_template("index.html", ai_list=AI_LIST)


@app.route("/health")
def health():
    """健康检查"""
    return jsonify({"status": "ok", "api_key_set": bool(api_key)})


@app.route("/chat", methods=["POST"])
def chat():
    """处理用户发送的消息"""
    try:
        data = request.json
        if not data or "question" not in data:
            return jsonify({"error": "请输入问题"}), 400

        question = data.get("question", "").strip()
        if not question:
            return jsonify({"error": "问题不能为空"}), 400

        rounds = data.get("rounds", 2)

        # 检查 API Key
        if not api_key:
            return jsonify({"error": "API Key 未配置，请在 Render 环境变量中设置 SILICONFLOW_API_KEY"}), 500

        # 清空历史
        chat_history.clear()
        chat_history.append({"speaker": "用户", "content": question, "type": "user"})

        all_messages = [{"speaker": "用户", "content": question, "type": "user"}]

        # 多轮讨论
        for r in range(1, rounds + 1):
            for ai in AI_LIST:
                try:
                    answer = ask_ai(ai, format_history())
                    msg = {
                        "speaker": ai["name"],
                        "content": answer,
                        "type": "ai",
                        "emoji": ai["emoji"],
                        "color": ai["color"],
                        "round": r,
                    }
                    chat_history.append(msg)
                    all_messages.append(msg)
                except Exception as e:
                    msg = {
                        "speaker": ai["name"],
                        "content": f"[发言失败：{e}]",
                        "type": "error",
                        "emoji": ai["emoji"],
                        "color": ai["color"],
                        "round": r,
                    }
                    chat_history.append(msg)
                    all_messages.append(msg)

        # 生成总结
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
            all_messages.append(
                {
                    "speaker": "主持人",
                    "content": summary.choices[0].message.content,
                    "type": "summary",
                    "emoji": "🎯",
                    "color": "#E74C3C",
                }
            )
        except Exception as e:
            all_messages.append(
                {
                    "speaker": "主持人",
                    "content": f"总结生成失败：{e}",
                    "type": "error",
                    "emoji": "🎯",
                    "color": "#E74C3C",
                }
            )

        return jsonify({"messages": all_messages})

    except Exception as e:
        return jsonify({"error": f"服务器错误：{str(e)}"}), 500


if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("   AI 群聊网页版已启动！")
    print("   打开浏览器访问：http://127.0.0.1:5000")
    print("=" * 50 + "\n")
    app.run(debug=True)