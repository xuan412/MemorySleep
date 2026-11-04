# vector_store.py —— 长期记忆库
# 用本地向量库 Chroma 存长期记忆，数据落盘在项目目录的 chroma_db 文件夹里。
# 这里只做四件事：回忆（查相似）、判重、存入、重复次数加一。

import os
import uuid

import chromadb

from embeddings import embed
from config import SIMILARITY_THRESHOLD

# 数据库文件夹固定放在本代码文件旁边，从哪个目录启动都能找到
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 打开本地库（没有就自动建），用余弦方式算相似度
client = chromadb.PersistentClient(path=os.path.join(BASE_DIR, "chroma_db"))
collection = client.get_or_create_collection(
    name="long_term_memory",
    metadata={"hnsw:space": "cosine"},
)


def search_similar(text: str, k: int) -> list:
    """【回忆】拿一段话去长期库里找最像的 k 条，返回列表，每条带相似度"""
    if collection.count() == 0:
        return []

    result = collection.query(query_embeddings=[embed(text)], n_results=k)

    hits = []
    for i in range(len(result["ids"][0])):
        hits.append({
            "id": result["ids"][0][i],
            "summary": result["documents"][0][i],        # 存的是记忆的一句话概括
            "metadata": result["metadatas"][0][i],       # 打分、时间这些附加信息
            "similarity": 1 - result["distances"][0][i], # 距离越小 = 越像，换成相似度好理解
        })
    return hits


def find_repeat(text: str):
    """【判重】最像的那条超过阈值就当同一件事，返回那条；不是重复就返回 None"""
    hits = search_similar(text, k=1)
    if hits and hits[0]["similarity"] >= SIMILARITY_THRESHOLD:
        return hits[0]
    return None


def save_memory(summary: str, metadata: dict) -> str:
    """【存入长期库】把一条新记忆写进向量库，返回它的编号"""
    memory_id = uuid.uuid4().hex
    collection.add(
        ids=[memory_id],
        embeddings=[embed(summary)],
        documents=[summary],
        metadatas=[metadata],
    )
    return memory_id


def add_repeat(hit: dict):
    """【记重复】同一件事又发生了，只把长期库里的 repeat_count 加一，不重复存"""
    metadata = hit["metadata"]
    metadata["repeat_count"] = int(metadata.get("repeat_count", 1)) + 1
    collection.update(ids=[hit["id"]], metadatas=[metadata])
