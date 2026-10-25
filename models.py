# models.py —— 模型统一从这里创建
# 换模型就改 .env 里的 MODEL_NAME、API_KEY、BASE_URL，代码不用动。
# 走 OpenAI 兼容接口就行，DeepSeek、通义、Kimi 这些都能接。

import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()


def get_llm() -> ChatOpenAI:
    """按 .env 的配置建一个聊天模型"""
    api_key = os.getenv("API_KEY") 

   
    base_url = os.getenv("BASE_URL") 

    return ChatOpenAI(
        model=os.getenv("MODEL_NAME"),
        api_key=api_key,
        base_url=base_url,
        temperature=0.2,
    )
