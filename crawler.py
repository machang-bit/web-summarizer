"""抓取层：使用 LangChain 的 WebBaseLoader 抓取网页并提取正文。

WebBaseLoader 内部基于 BeautifulSoup 解析 HTML，自动剥离 script/style 等标签；
本层额外对文本做清洗（压缩空行等），并把各类异常转成友好的中文提示。
"""

import re

from langchain_community.document_loaders import WebBaseLoader

# 模拟常见浏览器 UA，避免被简单反爬拦截
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}


def _clean_text(text: str) -> str:
    """压缩多余空白，去掉连续空行，减少无效 token 占用。"""
    lines = [re.sub(r"\s+", " ", line).strip() for line in text.splitlines()]
    lines = [line for line in lines if line]
    return "\n".join(lines)


def load_webpage(url: str):
    """抓取网页，返回 LangChain Document 列表。

    失败时抛出带中文说明的异常，由界面层统一捕获展示。
    """
    url = (url or "").strip()
    if not url.startswith(("http://", "https://")):
        raise ValueError("URL 格式不正确，请以 http:// 或 https:// 开头。")

    try:
        loader = WebBaseLoader(
            web_paths=[url],
            header_template=HEADERS,
            requests_kwargs={"timeout": 15},
        )
        docs = loader.load()
    except Exception as exc:  # 网络错误、4xx/5xx、解析失败等统一兜底
        raise RuntimeError(
            "网页抓取失败，请检查：① URL 是否有效；② 网络是否正常；"
            f"③ 目标网站是否有反爬限制。\n原始错误：{exc}"
        ) from exc

    if not docs:
        raise RuntimeError("网页可以访问，但没有抓取到任何内容，可能是动态渲染页面。")

    # 清洗正文，剔除空白噪声
    cleaned = []
    for doc in docs:
        text = _clean_text(doc.page_content)
        if text:
            doc.page_content = text
            cleaned.append(doc)

    if not cleaned:
        raise RuntimeError(
            "未能从该页面提取到有效正文内容。若页面依赖 JavaScript 动态渲染，"
            "可改用 UnstructuredURLLoader 或 Selenium 方案。"
        )
    return cleaned
