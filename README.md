# MemorySleep

模仿人类记忆的情感化记忆系统。外界文字进来后，系统按内置的人格和动机打分，写成带情绪倾向的短期记忆，存进 JSON。睡觉时模型逐条判断，合格的转成长期记忆（本地向量库），不合格的忘掉。新输入进来之前，还会先去长期记忆里翻一翻，把想起的旧事塞进提示词。

## 怎么用

### 配好 .env

文件里要有两组密钥，一组聊天模型，一组 embedding 模型（用来判重和回忆）

```env
API_KEY=sk-你的密钥
MODEL_NAME=deepseek-chat
BASE_URL=https://api.deepseek.com/v1

EMBEDDING_API_KEY=sk-你的密钥
EMBEDDING_BASE_URL=https://api.siliconflow.cn/v1
EMBEDDING_MODEL=BAAI/bge-m3
```

### 准备输入

写好 `information.txt`，用 `###` 把内容切成若干片段。一片段就是一条记忆。

### 跑起来

在项目目录里执行：

```powershell
python main.py
```

跑完打开 `short_term_memory.json`，能看到新写入的记忆。每次运行都是追加，不会覆盖旧数据。

### 睡觉（巩固成长期记忆）

白天记完，晚上跑一次：

```powershell
python consolidate.py
```

每条短期记忆按四个分数加权算一个巩固分，过线的存进长期记忆库（`chroma_db` 文件夹），连着的打分、时间、原文一起存；不过线的忘掉。存入线在 `config.py` 的 `SAVE_SCORE` 里调。全部处理完，短期库清空。每条记忆的去向都记录在 `sleep_log.jsonl` 里。



## 换模型

改 `.env` 三行就行，代码不用动。走 OpenAI 兼容接口，DeepSeek 和通义、Kimi 这类服务都能接。

```env
API_KEY=sk-你的密钥
MODEL_NAME=你的模型名
BASE_URL=对应服务的接口地址
```


## 一条记忆有什么

- `raw_content` 原文片段
- `summary` 第一人称的一句话概括
- `timestamp` 时间
- 四个分数。名字是情感冲击、动机吻合、反常程度和兴趣指数，口径写在 `persona.py`
- `repeat_count` 重复次数，目前固定写 1，重复判断还没做

## 文件

- `main.py` 入口，读输入、调模型、判重、写短期记忆，还会把想起的旧记忆塞进提示词
- `models.py` 创建聊天模型，配置都在 `.env`
- `embeddings.py` 把文本变成向量，给判重和回忆用
- `vector_store.py` 长期记忆库（本地 Chroma），存入、判重、回忆都在这
- `consolidate.py` 睡觉命令：预筛、模型判决、入库、清空短期库
- `config.py` 巩固分权重、遗忘线、判重阈值这些参数，调优只改这里
- `persona.py` 人格、动机和打分口径
- `schemas.py` 记忆和判决的字段定义
- `short_memory_store.py` 读写短期记忆 JSON
- `tools.py` 时间工具

## 依赖

```powershell
pip install langchain-openai langchain-core python-dotenv pydantic chromadb
```
