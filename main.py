from email.mime import text
import os

from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_deepseek import ChatDeepSeek

import short_memory_store
from persona import MOTIVATION, PERSONA, SCORING_RULES
from schemas import MemoryRecord
from tools import ask_model_for_time

load_dotenv()                       # 从 .env 读 DEEPSEEK_API_KEY

DEFAULT_INPUT = "information.txt"

# ========== 模型 ==========

llm = ChatDeepSeek(model="deepseek-chat", temperature=0.2)

# ========== 提示词==========
SYSTEM_PROMPT = """你是「林一鸣」本人的记忆编码系统。
你不是旁观的分析师，你就是他本人：用他的眼睛看信息，用他的标准判断信息值不值得记住。

【人格设定】
{persona}

【当前动机】
{motivation}

【打分口径】
{scoring_rules}

要求：
1. summary 用第一人称、口语化的一句话概括，像他脑子里冒出来的念头；
2. raw_content 必须原样复制我给你的片段，一个字都不要改；
3. timestamp 直接填我给你的当前时间，不要自己编；
4. 四个分数都要根据上面的口径认真区分高低，不要都给 50 这种中间值。

"""
#==========================
HUMAN_PROMPT = """

【当前时间】{current_time}

【外界输入片段】
{information}

请输出这条记忆的元数据。
"""
#===============

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM_PROMPT),
        ("human", HUMAN_PROMPT),
    ]
)

# ========== 3. 核心 Chain：提示词 -> 模型 -> 结构化元数据 ==========
# with_structured_output 会让模型按 MemoryRecord 的字段返回，
# 拿到的直接就是 Pydantic 对象，不需要手动 json.loads
memory_chain = prompt | llm.with_structured_output(MemoryRecord)

#切割文本函数
def read_and_split(path: str) -> list:
    """读取输入文本，用关键字 ### 切割成若干独立片段"""
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    informations = []
    for i in text.split("###"):
        if i.strip()!="":
            informations.append(i.strip()) 
    return informations                 # 丢掉空片段

#处理文本函数
def process_file(path: str) -> list:
    
    # 时间由工具获取：让模型调用 get_current_time，本地执行拿到真实时间
    current_time = ask_model_for_time(llm)
    print(f"[时间工具] 本次记忆时间：{current_time}\n")

    results = []
    # ---------- 对话 / 处理循环：一个片段 = 一条短期记忆 ----------
    for i, information in enumerate(read_and_split(path), start=1):
        print(f"--- 片段 {i} ---")
        print(f"原文：{information[:40]}...")

        # 调用 Chain：模板填参 -> 模型推理 -> 结构化输出
        record: MemoryRecord = memory_chain.invoke(
            {
                "persona": PERSONA,
                "motivation": MOTIVATION,
                "scoring_rules": SCORING_RULES,
                "current_time": current_time,
                "information": information,
            }
        )

        
        record.timestamp = current_time
        
        record.raw_content = information

        # 【写入短期记忆】落盘到 JSON 记忆库
        short_memory_store.append_record(record)

        print(f"概括：{record.summary}")
        print(
            f"打分：情感冲击 {record.emotional_impact} | 动机吻合 {record.motivation_match} "
            f"| 反常程度 {record.anomaly} | 兴趣指数 {record.interest_score}\n"
        )
        results.append(record)

    return results





if __name__ == "__main__":
    input_file =  DEFAULT_INPUT



    print(f"开始读取输入：{input_file}\n" + "=" * 60)
    process_file(input_file)
    
