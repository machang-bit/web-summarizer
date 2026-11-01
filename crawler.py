import trafilatura
from langchain_core.documents import Document

def load_webpage(url):
    downloaded = trafilatura.fetch_url(url)
    if not downloaded:
        raise Exception("网页抓取失败，链接失效/网站反爬")
    text = trafilatura.extract(downloaded)
    if not text:
        raise Exception("无法提取正文，该网站有反爬限制")
    return [Document(page_content=text, metadata={"source": url})]
