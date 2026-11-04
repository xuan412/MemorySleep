# consolidate.py —— 睡觉命令
# 人睡着后，大脑会把白天的短期记忆整理一遍：重要的转成长期记忆，没用的忘掉。
# 这个脚本就是"睡觉"：
#   读短期库 -> 算巩固分 -> 过线的存进向量库 -> 清空短期库。
# 过线标准是一条数值线，在 config.py 的 SAVE_SCORE 里调。
# 用法：python consolidate.py

import json
import os
from datetime import datetime

import vector_store
from config import SAVE_SCORE, SCORE_WEIGHTS
from short_memory_store import load_memory, save_memory


def promote_score(record: dict) -> float:
    """【算巩固分】四个分数加权求和，权重在 config.py 里调"""
    score = 0.0
    for name in ("emotional_impact", "motivation_match", "interest_score", "anomaly"):
        score += SCORE_WEIGHTS[name] * record[name]
    # 重复出现的记忆加分，最多按 5 次算
    score += SCORE_WEIGHTS["repeat"] * min(record["repeat_count"], 5) * 20
    return score


def sleep() -> None:
    loaded = load_memory()

    # 手动改 short_term_memory.json 时可能弄出不完整的记录（缺 summary），
    # 这样的直接跳过，不让一条坏数据卡住整晚的整理
    memories = [r for r in loaded if isinstance(r, dict) and r.get("summary")]
    skipped = len(loaded) - len(memories)
    if skipped:
        print(f"有 {skipped} 条不完整的记录，跳过不整理。")

    if not memories:
        print("短期记忆是空的，不用睡觉。")
        return

    print(f"今晚要整理 {len(memories)} 条短期记忆\n" + "=" * 60)

    log = []  # 每条记忆的去向，最后写进日志文件

    for i, record in enumerate(memories, start=1):
        summary = record["summary"]
        score = promote_score(record)
        print(f"--- 记忆 {i}：{summary[:30]}...（巩固分 {score:.0f}，存入线 {SAVE_SCORE}）")

        # 分数不够线的直接忘掉
        if score < SAVE_SCORE:
            print("判决：分数不过线，直接遗忘\n")
            log.append({
                "summary": summary,
                "score": score,
                "decision": "forget",
                "reason": f"巩固分低于存入线 {SAVE_SCORE}",
            })
            continue

        # 过线的先判重：长期库里已经有同一件事，就只把重复次数加一
        hit = vector_store.find_repeat(summary)
        if hit:
            vector_store.add_repeat(hit)
            print(f"入库：和已存的「{hit['summary'][:30]}...」是同一件事，重复次数 +1\n")
            log.append({"summary": summary, "score": score, "decision": "repeat", "reason": "与长期记忆重复"})
            continue

        # 真正的新记忆：短期记录里的全部数据（原文、时间、四个分数、重复次数）都带进长期库
        vector_store.save_memory(
            summary,
            {k: v for k, v in record.items() if k != "summary"},  # summary 本身就是检索正文，不重复存
        )
        print(f"入库：{summary}\n")
        log.append({"summary": summary, "score": score, "decision": "save", "reason": "巩固分过线"})

    # 走到这里说明全部处理成功：写日志（日志也固定放项目目录里），然后才敢清空短期库
    log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sleep_log.jsonl")
    with open(log_path, "a", encoding="utf-8") as f:
        for entry in log:
            entry["time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    save_memory([])

    saved = sum(1 for e in log if e["decision"] in ("save", "repeat"))
    forgot = sum(1 for e in log if e["decision"] == "forget")
    print("=" * 60)
    print(f"睡醒了：存入长期记忆 {saved} 条，遗忘 {forgot} 条，短期库已清空。")


if __name__ == "__main__":
    sleep()
