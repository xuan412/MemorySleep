# embeddings.py —— 把一段话变成向量
# 向量就是一串数字。意思相近的两段话，转出来的向量也挨得近，
# 靠这个就能算"两段话像不像"，这是判重和回忆的基础。
# 用的模型在 .env 里配：EMBEDDING_API_KEY / EMBEDDING_BASE_URL / EMBEDDING_MODEL。

import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# 密钥没填就直接提示，别等报一堆英文错误
if not os.getenv("EMBEDDING_API_KEY"):
    raise SystemExit(
        "还没配 embedding 模型：请在 .env 里填 EMBEDDING_API_KEY、"
    )

client = OpenAI(
    api_key=os.getenv("EMBEDDING_API_KEY"),
    base_url=os.getenv("EMBEDDING_BASE_URL"),
)


def embed(text: str) -> list:
    """【文本转向量】把一段话变成一串数字（向量）"""
    response = client.embeddings.create(
        model=os.getenv("EMBEDDING_MODEL"),
        input=text,
    )
    return response.data[0].embedding
