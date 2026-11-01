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
