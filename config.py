"""配置层：从 .env 读取环境变量，按 LLM_PROVIDER 构建大模型实例。

支持的提供方：
- openai : 在线 OpenAI 兼容接口（也可指向任何 OpenAI 兼容网关）
- zhipu  : 在线智谱 GLM
- ollama : 本地离线 Ollama
"""

import os

from dotenv import load_dotenv

load_dotenv()  # 从项目根目录的 .env 读取环境变量

SUPPORTED_PROVIDERS = ("openai", "zhipu", "ollama")


def get_llm():
    """根据环境变量 LLM_PROVIDER 返回对应的 Chat 模型实例。"""
    provider = os.getenv("LLM_PROVIDER", "zhipu").strip().lower()

    if provider == "openai":
        from langchain_openai import ChatOpenAI

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("未检测到 OPENAI_API_KEY，请在 .env 中配置。")
        return ChatOpenAI(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            api_key=api_key,
            base_url=os.getenv("OPENAI_BASE_URL") or None,
            temperature=0.3,
        )

    if provider == "zhipu":
        from langchain_community.chat_models import ChatZhipuAI

        api_key = os.getenv("ZHIPU_API_KEY")
        if not api_key:
            raise RuntimeError("未检测到 ZHIPU_API_KEY，请在 .env 中配置。")
        return ChatZhipuAI(
            model=os.getenv("ZHIPU_MODEL", "glm-4-flash"),
            api_key=api_key,
            temperature=0.3,
        )

    if provider == "ollama":
        # 本地离线模型，无需 API Key
        from langchain_ollama import ChatOllama

        return ChatOllama(
            model=os.getenv("OLLAMA_MODEL", "qwen2.5:7b"),
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            temperature=0.3,
        )

    raise RuntimeError(
        f"不支持的 LLM_PROVIDER：{provider}，可选值为 {SUPPORTED_PROVIDERS}"
    )
