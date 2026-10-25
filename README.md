# MemorySleep

模仿人类记忆的情感化记忆系统。外界文字进来后，系统按内置的人格和动机打分，写成带情绪倾向的短期记忆，存进 JSON。

现在做的是第一阶段，短期记忆缓冲区。后面还有睡眠巩固和长期记忆库。

## 怎么用

### 配好 .env

文件里至少要有密钥

```env
API_KEY=sk-你的密钥
MODEL_NAME=deepseek-chat
BASE_URL=https://api.deepseek.com/v1
```

### 准备输入

写好 `information.txt`，用 `###` 把内容切成若干片段。一片段就是一条记忆。

### 跑起来

在项目目录里执行：

```powershell
python main.py
```

跑完打开 `short_term_memory.json`，能看到新写入的记忆。每次运行都是追加，不会覆盖旧数据。想清空就把这个文件内容改成 `[]`。

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

- `main.py` 入口，读输入、调模型、写记忆
- `models.py` 创建模型，配置都在 `.env`
- `persona.py` 人格、动机和打分口径
- `schemas.py` 记忆的字段定义
- `short_memory_store.py` 读写短期记忆 JSON
- `tools.py` 时间工具

## 依赖

```powershell
pip install langchain-openai langchain-core python-dotenv pydantic
```
