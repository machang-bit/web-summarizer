"""抓取层：使用 trafilatura 抓取网页并提取正文。

trafilatura 是专注于正文抽取的库，能自动剔除导航栏、页脚、广告、
侧边栏推荐等噪声，提取效果优于通用 HTML 解析，尤其适合新闻/博客类页面。
（早期版本使用 LangChain 的 WebBaseLoader，后升级为 trafilatura 以提升正文准确率。）

本层同时负责把各种异常转成友好的中文提示，交由界面层展示。
"""

import re

import trafilatura
from langchain_core.documents import Document


def _clean_text(text: str) -> str:
    """压缩多余空白、去掉空行，减少无效 token 占用。"""
    lines = [re.sub(r"\s+", " ", line).strip() for line in text.splitlines()]
    return "\n".join([line for line in lines if line])


def load_webpage(url: str):
    """抓取指定 URL 的正文，返回包含一个 Document 的列表。"""
    url = (url or "").strip()
    if not url.startswith(("http://", "https://")):
        raise ValueError("URL 格式不正确，请以 http:// 或 https:// 开头。")

    try:
        downloaded = trafilatura.fetch_url(url)
    except Exception as exc:  # 网络超时、DNS 失败等
        raise RuntimeError(
            "网页抓取失败：无法连接到目标网站，请检查网络是否正常、"
            f"链接是否可访问。原始错误：{exc}"
        ) from exc

    if not downloaded:
        raise RuntimeError(
            "网页抓取失败：链接已失效，或目标网站启用了反爬限制，未能下载到页面内容。"
        )

    text = trafilatura.extract(downloaded)
    if not text or not text.strip():
        raise RuntimeError(
            "未能从该页面提取到有效正文：页面可能依赖 JavaScript 动态渲染，"
            "或存在反爬限制。可尝试换成其他公开文章页。"
        )

    return [Document(page_content=_clean_text(text), metadata={"source": url})]
