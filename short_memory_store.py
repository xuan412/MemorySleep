
import json
import os

from schemas import MemoryRecord

# 短期记忆库文件（就在当前目录下）
MEMORY_FILE = "short_term_memory.json"


def load_memory() -> list:
    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_memory(memories: list) -> None:
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memories, f, ensure_ascii=False, indent=2)


def append_record(record: MemoryRecord) -> dict:
    """【写入短期记忆】把一条新记忆追加进 JSON 记忆库，并返回这条记忆"""
    memories = load_memory()
    item = record.model_dump()          # 把这个类里面的数据变为字典
    memories.append(item)
    save_memory(memories)
    return item
