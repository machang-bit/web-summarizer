<<<<<<< HEAD
import os
from dotenv import load_dotenv
from langchain_community.chat_models import ChatZhipuAI
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()
ZHIPU_API_KEY = os.getenv("ZHIPU_API_KEY")

llm = ChatZhipuAI(
    api_key=ZHIPU_API_KEY,
    model="glm-4-flash",
    temperature=0.3
)

CHAIN_TYPES = {
    "stuff": "stuff",
    "map_reduce": "map_reduce",
    "refine": "refine"
}

parser = StrOutputParser()

prompt_stuff = ChatPromptTemplate.from_messages([
    ("human", "用中文总结下面这段内容，控制在300字以内：\n{context}")
])
chain_stuff = prompt_stuff | llm | parser

# 这里改成 3 个形参，第三个参数随便命名，用来接住app传过来的chunk参数
def summarize(docs: list[Document], chain_type: str, chunk_cfg):
    content = "\n".join([d.page_content for d in docs])
    if chain_type == "map_reduce":
        mid_prompt = ChatPromptTemplate.from_messages([("human", "简要总结：\n{text}")])
        mid_chain = mid_prompt | llm | parser
        partial_summaries = [mid_chain.invoke({"text": d.page_content}) for d in docs]
        all_sum = "\n".join(partial_summaries)
        final_prompt = ChatPromptTemplate.from_messages([("human", "合并下面所有摘要，输出最终总结：\n{text}")])
        final_chain = final_prompt | llm | parser
        return final_chain.invoke({"text": all_sum})
    elif chain_type == "refine":
        res = ""
        refine_prompt = ChatPromptTemplate.from_messages([("human", "原有总结：{old_sum}\n新内容：{new_text}\n更新总结：")])
        refine_chain = refine_prompt | llm | parser
        for d in docs:
            res = refine_chain.invoke({"old_sum": res, "new_text": d.page_content})
        return res
    else:
        return chain_stuff.invoke({"context": content})
=======
"""摘要层：使用 load_summarize_chain，支持 map_reduce 与 refine 两种模式。

- map_reduce：每个块独立摘要，再合并成最终摘要，适合长文、可并行；
- refine：逐块滚动精炼摘要，前后文衔接好，但串行较慢。
所有 Prompt 都要求中文输出，最终摘要控制在 300 字以内。
"""

from langchain.chains.summarize import load_summarize_chain
from langchain_core.prompts import PromptTemplate

# ---- map_reduce 模式的两个 Prompt ----
MAP_TEMPLATE = """请用中文对下面这段网页内容做要点提炼，只保留核心信息，忽略广告、导航等噪声：

{text}

中文要点："""

COMBINE_TEMPLATE = """下面是同一篇网页文章各部分的中文要点。
请将它们去重、整合成一段连贯的摘要，要求：
1. 用简体中文输出；
2. 总字数不超过 300 字；
3. 只输出摘要本身，不要加"摘要："等前缀。

{text}

300 字以内的中文摘要："""

# ---- refine 模式的两个 Prompt ----
QUESTION_TEMPLATE = """请用中文对下面这段网页内容写一段简明摘要，忽略广告、导航等噪声：

{text}

中文摘要："""

REFINE_TEMPLATE = """目前已有部分内容的摘要：
{existing_answer}

请结合下面新增的内容，对摘要进行补充和精炼：
{text}

要求：
1. 用简体中文输出；
2. 最终摘要不超过 300 字；
3. 若新增内容没有重要信息，直接返回原摘要。

精炼后的中文摘要："""

MAP_PROMPT = PromptTemplate(template=MAP_TEMPLATE, input_variables=["text"])
COMBINE_PROMPT = PromptTemplate(template=COMBINE_TEMPLATE, input_variables=["text"])
QUESTION_PROMPT = PromptTemplate(template=QUESTION_TEMPLATE, input_variables=["text"])
REFINE_PROMPT = PromptTemplate(
    template=REFINE_TEMPLATE, input_variables=["existing_answer", "text"]
)

CHAIN_TYPES = ("map_reduce", "refine")


def summarize(chunks, llm, chain_type: str = "map_reduce") -> str:
    """对切块后的文档执行摘要，返回摘要字符串。"""
    if chain_type == "map_reduce":
        chain = load_summarize_chain(
            llm,
            chain_type="map_reduce",
            map_prompt=MAP_PROMPT,
            combine_prompt=COMBINE_PROMPT,
        )
    elif chain_type == "refine":
        chain = load_summarize_chain(
            llm,
            chain_type="refine",
            question_prompt=QUESTION_PROMPT,
            refine_prompt=REFINE_PROMPT,
        )
    else:
        raise ValueError(f"未知的摘要模式：{chain_type}，可选 {CHAIN_TYPES}")

    result = chain.invoke({"input_documents": chunks})
    return result["output_text"].strip()
>>>>>>> 07bbed75ffe45bc3b5405c12fd222972f1fecb2d
