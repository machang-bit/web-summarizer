"""界面层：Streamlit 网页总结助手入口。

运行：streamlit run app.py
"""

import os

import streamlit as st

from config import get_llm
from crawler import load_webpage
from splitter import split_docs
from summarizer import CHAIN_TYPES, summarize

st.set_page_config(page_title="网页总结助手", page_icon="📄", layout="centered")

st.title("📄 网页 / 文章总结助手")
st.caption("输入一个网页 URL，自动抓取正文并生成 300 字以内的中文摘要")

# ---- 侧边栏：当前配置展示 ----
with st.sidebar:
    st.header("⚙️ 当前配置")
    provider = os.getenv("LLM_PROVIDER", "zhipu")
    st.write(f"模型提供方：`{provider}`")
    st.write("切换模型或密钥请修改项目根目录的 `.env` 文件。")
    st.markdown("---")
    st.write("摘要模式说明：")
    st.write("- **map_reduce**：各块并行摘要再合并，适合长文")
    st.write("- **refine**：逐块滚动精炼，衔接更自然")

# ---- 主界面 ----
url = st.text_input(
    "网页 URL",
    placeholder="https://example.com/some-article",
    help="支持 http/https 网页",
)

col1, col2 = st.columns([2, 1])
with col1:
    chain_type = st.radio(
        "摘要链路模式",
        options=list(CHAIN_TYPES),
        horizontal=True,
        help="map_reduce 速度快；refine 上下文衔接好但较慢",
    )
with col2:
    chunk_size = st.number_input("chunk_size", value=1000, min_value=200, max_value=4000, step=100)
    chunk_overlap = st.number_input("chunk_overlap", value=100, min_value=0, max_value=500, step=10)

submit = st.button("🚀 生成摘要", type="primary", use_container_width=True)

if submit:
    if not url.strip():
        st.warning("请先输入一个网页 URL 再提交哦。")
    else:
        try:
            with st.spinner("正在抓取网页并生成摘要，请稍候…"):
                docs = load_webpage(url)
                chunks = split_docs(docs, int(chunk_size), int(chunk_overlap))
                llm = get_llm()
                summary = summarize(chunks, llm, chain_type)

            char_count = sum(len(d.page_content) for d in docs)
            st.success(
                f"摘要生成完成！正文 {char_count} 字，切分为 {len(chunks)} 块，"
                f"使用 {chain_type} 模式。"
            )
            st.markdown("### ✨ 核心摘要")
            st.markdown(summary)
            with st.expander("查看抓取到的正文（前 800 字）"):
                st.text(docs[0].page_content[:800])
        except (ValueError, RuntimeError) as exc:
            # 抓取/切割阶段的友好中文提示
            st.error(f"😥 处理失败：{exc}")
        except Exception as exc:  # 大模型调用等未知异常兜底
            st.error(
                "😥 摘要生成失败，请检查 .env 中的模型配置与 API Key 是否正确，"
                "或确认本地 Ollama 服务已启动。\n"
                f"原始错误：{exc}"
            )
