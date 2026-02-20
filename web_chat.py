# ===== AI 群聊系统 - 网页版（流式优化） =====

import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from flask import Flask, render_template, request, jsonify, Response, stream_with_context

load_dotenv()

app = Flask(__name__)

# 硅基流动客户端
api_key = os.getenv("SILICONFLOW_API_KEY")
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


@app.route("/")
def home():
    return render_template("index.html", ai_list=AI_LIST)


@app.route("/health")
def health():
    return jsonify({"status": "ok", "api_key_set": bool(api_key)})


@app.route("/chat", methods=["POST"])
def chat():
    """流式处理：每个 AI 回答完立刻发送给前端"""
    data = request.json
    if not data or not data.get("question", "").strip():
        return jsonify({"error": "请输入问题"}), 400

    question = data["question"].strip()
    rounds = data.get("rounds", 2)

    if not api_key:
        return jsonify({"error": "API Key 未配置"}), 500

    def generate():
        chat_history = []
        chat_history.append({"speaker": "用户", "content": question})

        # 发送用户消息
        user_msg = {"speaker": "用户", "content": question, "type": "user"}
        yield f"data: {json.dumps(user_msg, ensure_ascii=False)}\n\n"

        # 格式化历史
        def format_history():
            return "\n\n".join(f"{m['speaker']}：{m['content']}" for m in chat_history)

        # 多轮讨论
        for r in range(1, rounds + 1):
            # 发送轮次标记
            yield f"data: {json.dumps({'type': 'round', 'round': r}, ensure_ascii=False)}\n\n"

            for ai in AI_LIST:
                # 告诉前端谁在思考
                yield f"data: {json.dumps({'type': 'thinking', 'speaker': ai['name'], 'emoji': ai['emoji']}, ensure_ascii=False)}\n\n"

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
                    chat_history.append({"speaker": ai["name"], "content": answer})
                except Exception as e:
                    msg = {
                        "speaker": ai["name"],
                        "content": f"[发言失败：{e}]",
                        "type": "error",
                        "emoji": ai["emoji"],
                        "color": ai["color"],
                        "round": r,
                    }
                    chat_history.append({"speaker": ai["name"], "content": msg["content"]})

                yield f"data: {json.dumps(msg, ensure_ascii=False)}\n\n"

        # 总结
        yield f"data: {json.dumps({'type': 'summary_start'}, ensure_ascii=False)}\n\n"

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
            msg = {
                "speaker": "主持人",
                "content": summary.choices[0].message.content,
                "type": "summary",
                "emoji": "🎯",
                "color": "#E74C3C",
            }
        except Exception as e:
            msg = {
                "speaker": "主持人",
                "content": f"总结生成失败：{e}",
                "type": "error",
                "emoji": "🎯",
                "color": "#E74C3C",
            }

        yield f"data: {json.dumps(msg, ensure_ascii=False)}\n\n"
        yield "data: {\"type\": \"done\"}\n\n"

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("   AI 群聊网页版已启动！")
    print("   打开浏览器访问：http://127.0.0.1:5000")
    print("=" * 50 + "\n")
    app.run(debug=True)