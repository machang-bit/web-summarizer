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
