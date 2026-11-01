"""切割层：用 RecursiveCharacterTextSplitter 把长文切成适合上下文窗口的块。

chunk_size=1000, chunk_overlap=100：
- 1000 字符的块在多数模型的上下文内都很安全；
- 100 字符重叠保证跨块句子不会被生硬截断，摘要更连贯。
"""

from langchain_text_splitters import RecursiveCharacterTextSplitter


def split_docs(docs, chunk_size: int = 1000, chunk_overlap: int = 100):
    """把 Document 列表切分成小块，返回新的 Document 列表。"""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        # 中文友好的分隔符优先级：段落 > 换行 > 句号/问号/感叹号 > 空格
        separators=["\n\n", "\n", "。", "！", "？", "；", " ", ""],
    )
    chunks = splitter.split_documents(docs)
    if not chunks:
        raise RuntimeError("文本切割结果为空，页面内容可能过短。")
    return chunks
