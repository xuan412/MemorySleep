# 情感化记忆系统 · 第一阶段：短期记忆缓冲区

> 给第一次打开这个文件夹的你。
> 读完这篇，你应该能：**跑起来、看懂它在干嘛、知道改哪里、遇到报错知道怎么办。**

---

## 目录

1. [这个项目在做什么](#1-这个项目在做什么)
2. [先跑起来（3 步）](#2-先跑起来3-步)
3. [文件都是干什么的](#3-文件都是干什么的)
4. [数据是怎么流动的](#4-数据是怎么流动的)
5. [一条记忆长什么样](#5-一条记忆长什么样)
6. [新人必懂的 5 个概念](#6-新人必懂的-5-个概念)
7. [我想改点东西，改哪里？](#7-我想改点东西改哪里)
8. [建议的代码阅读顺序](#8-建议的代码阅读顺序)
9. [常见报错与解法](#9-常见报错与解法)
10. [接下来是什么（第二阶段）](#10-接下来是什么第二阶段)

---

## 1. 这个项目在做什么

一句话：**把外界输入的文字，变成"带着情绪和倾向的记忆"，存进一个 JSON 文件。**

为什么需要它？因为普通程序存的是"信息"，而这个系统存的是"这个人对信息的反应"。

同样是"明星官宣恋情"这条新闻：

| | 普通人存下来 | 这个系统存下来 |
|---|---|---|
| 内容 | 明星 A 和 B 官宣恋情 | 明星 A 和 B 官宣恋情 |
| 这个人什么反应 | 无 | 情感冲击 8 分、兴趣 2 分、跟我毫无关系 |

因为系统里内置了一个**人格**（大二学生林一鸣，数码控）和一个**动机**（做数码账号赚钱换设备）。同一段文字，不同的人格会打出完全不同的分数——这就是"情感模仿人脑"的起点。

整个系统规划分三阶段，**你现在拿到的是第一阶段**：

```
✅ 第一阶段：短期记忆缓冲区（纯文本 + 打分，存 JSON）   ← 就是这个文件夹
⬜ 第二阶段：睡眠巩固引擎（把短期记忆整理压缩成长期记忆）
⬜ 第三阶段：长期记忆库（向量库 + 图数据库，带元数据检索）
```

---

## 2. 先跑起来（3 步）

### 第 1 步：确认 `.env` 里有 key

打开文件夹里的 `.env`，内容应该长这样：

```
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx
```

没有的话去 https://platform.deepseek.com 申请一个填进去。

### 第 2 步：确认你在正确的目录里

**必须在 `dd` 这个文件夹里运行**（原因见 [第 9 节](#9-常见报错与解法)）：

```powershell
cd C:\Users\xuan\Desktop\dd
```

### 第 3 步：运行

```powershell
python main.py
```

### 你应该看到什么

```
开始读取输入：information.txt
============================================================
[时间工具] 本次记忆时间：2026-10-10 16:47:12

--- 片段 1 ---
原文：今天刷闲鱼蹲到一把二手的客制化机械键盘，Gasket 结构加铝坨坨，卖家标价 3...
概括：闲鱼蹲到一把 380 的 Gasket 铝坨坨客制化键盘，新价 1200 多，我手抖拍了，现在怕被砍单。
打分：情感冲击 92 | 动机吻合 62 | 反常程度 78 | 兴趣指数 95

--- 片段 2 ---
...
```

跑完后，打开 `short_term_memory.json`，你会看到 6 条新记忆。

> **注意**：每跑一次就会**追加** 6 条，不会覆盖。想清空就把 `short_term_memory.json` 的内容改成 `[]`。
> ⚠️ 但注意：**完全删掉这个文件会导致下一次运行报错**（见 [9.1](#91-filenotfounderror-short_term_memoryjson)）。

### 花了多少时间和钱

每处理一个片段 = 1 次 API 调用，加上开头获取时间 1 次。`information.txt` 有 6 段，所以一次运行约 **7 次调用**，几十秒、几分钱。片段越多越慢，这是正常的。

---

## 3. 文件都是干什么的

| 文件 | 作用 | 你大概多久会动它一次 |
|---|---|---|
| `main.py` | **主流程**：读文件 → 切割 → 建 Chain → 循环处理 → 存记忆 | 偶尔 |
| `persona.py` | **人格 + 动机 + 打分口径**（三块提示词文本） | ⭐ 最常改，换人就改这里 |
| `schemas.py` | 定义"一条记忆有哪些字段"（Pydantic 模型） | 想加新字段时 |
| `tools.py` | 时间工具 + 让模型调用工具的封装 | 基本不动 |
| `short_memory_store.py` | 短期记忆库的读写（存 JSON / 读 JSON） | 基本不动 |
| `information.txt` | **输入文本**，用 `###` 分隔成多条 | ⭐ 天天改 |
| `short_term_memory.json` | **短期记忆库**，程序生成的结果文件 | 只看，不手改 |
| `.env` | 存放 API Key，不要提交到 git | 一次 |

---

## 4. 数据是怎么流动的

```
                     information.txt
                           │
                           │  read_and_split()：按 ### 切开、去掉空白
                           ▼
        ┌──────────── 6 个独立片段 ────────────┐
        │  片段1   片段2   片段3   ...   片段6  │
        └──────────────────┬───────────────────┘
                           │
                           │  一次处理一个片段（for 循环）
                           ▼
   ┌───────────────── memory_chain ─────────────────┐
   │                                                │
   │   prompt（提示词模板）                          │
   │     ├─ {persona}         ← persona.py  人格     │
   │     ├─ {motivation}      ← persona.py  动机     │
   │     ├─ {scoring_rules}   ← persona.py  打分口径  │
   │     ├─ {current_time}    ← tools.py    时间工具  │
   │     └─ {information}     ← 当前片段原文          │
   │                    │                           │
   │                    ▼                           │
   │            ChatDeepSeek 大模型                  │
   │                    │                           │
   │                    ▼                           │
   │     with_structured_output(MemoryRecord)       │
   │        强制模型按字段返回，直接得到对象           │
   └────────────────────┬───────────────────────────┘
                        │
                        │  short_memory_store.append_record()
                        ▼
              short_term_memory.json  ← 短期记忆库
```

**时间那一支单独说**（这是唯一用到"工具"的地方）：

```
   ┌── 启动时先问一句："请调用工具获取当前时间" ──┐
   │  llm.bind_tools([get_current_time])        │
   │            ↓                               │
   │  模型回复：我要调用 get_current_time        │  ← tool_calls
   │            ↓                               │
   │  本地真正执行函数，拿到 2026-10-10 16:47:12  │
   └────────────────────────────────────────────┘
```

为什么要这么绕？因为**大模型不知道今天几号，直接问它它会编一个**。做成工具，时间就是真实可靠的。

---

## 5. 一条记忆长什么样

`short_term_memory.json` 里存的就是这样一个数组，每个元素是一条记忆：

```json
[
  {
    "raw_content": "今天刷闲鱼蹲到一把二手的客制化机械键盘，Gasket 结构加铝坨坨……",
    "summary": "闲鱼蹲到一把 380 的 Gasket 铝坨坨客制化键盘，新价 1200 多，我手抖拍了，现在怕被砍单。",
    "timestamp": "2026-10-10 16:47:12",
    "emotional_impact": 92,
    "motivation_match": 62,
    "anomaly": 78,
    "interest_score": 95
  }
]
```

七个字段的含义：

| 字段 | 含义 | 谁来填 |
|---|---|---|
| `raw_content` | 原始内容，切割后的原文，一个字不改 | **代码强制覆盖**（防止模型乱改） |
| `summary` | 浓缩概括，第一人称口语化的一句话 | 模型 |
| `timestamp` | 时间（工具获取的真实时间） | **代码强制覆盖**（防止模型编造） |
| `emotional_impact` | 情感冲击 0-100：让我情绪波动的强度 | 模型 |
| `motivation_match` | 动机吻合 0-100：跟我的目标有多相关 | 模型 |
| `anomaly` | 反常程度 0-100：跟我的认知偏离多大 | 模型 |
| `interest_score` | 兴趣点 0-100：落在我的数码兴趣上有多深 | 模型 |

> 💡 **前三个字段为什么要"代码强制覆盖"？**
> 大模型有"自作主张"的毛病：让它填时间，它可能编一个；让它复制原文，它可能顺手润色一下。
> 所以 `main.py` 的 101-103 行做了兜底——模型只负责**打分的判断**，客观事实由代码保证。

### 分数是怎么拉开差距的（实测结果）

| 输入片段 | 情感 | 动机 | 反常 | 兴趣 |
|---|---|---|---|---|
| 闲鱼 380 捡到 1200 的客制化键盘 | **92** | 62 | 78 | **95** |
| 舍友嘲讽"折腾这些有什么用" | **85** | 70 | 25 | 60 |
| 酷安 NAS 固件刷崩四块硬盘 | 82 | 62 | 58 | **90** |
| 隔壁班 200 块捡到二手微单 | 72 | 55 | **78** | 85 |
| 图书馆闭馆检修通知 | 15 | 10 | 10 | 10 |
| 明星官宣恋情 | **8** | **3** | 10 | **2** |

能看出来：人格设定真的在起作用——数码相关的高分，明星八卦接近 0 分。

---

## 6. 新人必懂的 5 个概念

不需要精通 LangChain，先懂这 5 个词就够了。

### ① Prompt 模板里的 `{花括号}` = 占位符

```python
HUMAN_PROMPT = """
【当前时间】{current_time}
【外界输入片段】{information}
"""
```

这不是 Python 的格式化，是 **LangChain 的占位符**。调用时用字典填进去：

```python
memory_chain.invoke({"current_time": "2026-10-10 16:47:12", "information": "今天刷闲鱼……"})
```

> ⚠️ 所以如果你在提示词文本里想写真正的花括号，要写成 `{{` 和 `}}`，否则会报 KeyError。

### ② `|` 竖线 = 管道，把组件串成 Chain

```python
memory_chain = prompt | llm.with_structured_output(MemoryRecord)
```

读作："数据先经过 prompt 填好模板，再交给 llm 处理，最后按 MemoryRecord 的结构输出"。
就像 Linux 的 `cat a.txt | grep xxx`，**左边的东西流进右边**。这就是 LangChain 的核心思想。

### ③ 结构化输出 = 让模型必须按表格填

普通调用模型，你得到一段自由发挥的文字，还得自己写解析。用 `with_structured_output`：

```python
llm.with_structured_output(MemoryRecord)
```

你得到的是一个 **Python 对象**，可以直接 `record.summary`、`record.emotional_impact` 取字段，**不用 `json.loads`**。

### ④ Pydantic 模型 = 用类描述数据长什么样

```python
class MemoryRecord(BaseModel):
    summary: str = Field(description="浓缩概括：一句话说清这条内容")
    emotional_impact: int = Field(ge=0, le=100, description="情感冲击打分 0-100")
```

- `str` / `int` → 规定类型
- `Field(description=...)` → **这段描述会一并告诉大模型**，写清楚了它才填得准
- `ge=0, le=100` → 限制范围（大于等于 0，小于等于 100）
- `model_dump()` → 把这个对象转成普通字典，好存 JSON

**这是"提示词工程"的一部分**：你觉得模型哪个字段填得不好，先改这里的 `description`。

### ⑤ 工具调用 = 给模型一个"能伸手去拿数据"的能力

```python
@tool
def get_current_time() -> str:
    """获取当前的日期和时间"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
```

模型不会自己去执行这个函数。流程是：**模型说"我要调用它" → 你的代码去执行 → 把结果给模型**。

---

## 7. 我想改点东西，改哪里？

### 换个输入文本（最常用）

直接编辑 `information.txt`，用 `###` 分隔每一条：

```
第一条内容……
###
第二条内容……
###
第三条内容……
```

⚠️ **正文里不能出现 `###`**，否则会被切开。写"井号"就用中文的 `＃` 或者加空格 `# # #`。

### 换一个人格（改性格 = 改分数）

编辑 `persona.py` 里的 `PERSONA`。这是纯文本，随便写，越具体分数越有个性：

```python
PERSONA = """姓名：张小满
年龄：19 岁
身份：某师范大学 汉语言文学专业 大一学生
性格：爱看小说，怕生，对便宜的书和文具没有抵抗力……
【核心兴趣】
- 二手书市、旧书摊、绝版小说
- 手账文具、钢笔、墨水
【情感敏感点】
- 绝版书被别人抢先买走
【不太关心的事】
- 显卡、跑分、硬件参数
"""
```

### 换动机（改"什么对我重要"）

编辑 `persona.py` 里的 `MOTIVATION`。**它直接决定 `motivation_match` 这一列的分数**：

```python
MOTIVATION = """我今年的动机是：把宿舍改造成一个能安心看书的角落，
在二手书市淘到 50 本绝版小说，并写一篇能发表的书评。"""
```

### 改打分尺度（觉得分数太松/太紧）

编辑 `persona.py` 里的 `SCORING_RULES`。比如你觉得"80 分"给得太容易：

```python
4. interest_score（兴趣点）：
   0-30 = 完全不感兴趣；50-70 = 有兴趣会点开看；
   90-100 = 只有我真正会熬夜研究的东西才能给 90 分以上。
```

### 加一个新字段（比如"是否值得记录"）

**改三处**：

1. `schemas.py` 加字段：
   ```python
   worth_keeping: bool = Field(description="这条信息值不值得长期留存")
   ```
2. `main.py` 的 `SYSTEM_PROMPT` 的"要求"里加一句说明，告诉模型怎么判断
3. 完事。`main.py` 的打印和 `short_memory_store.py` 的存储**不用改**，它们用的是整对象

### 换模型 / 调节稳定性

`main.py` 第 19 行：

```python
llm = ChatDeepSeek(model="deepseek-chat", temperature=0.2)
```

- `model="deepseek-reasoner"` → 换成推理模型（更聪明，但更慢更贵）
- `temperature=0.2` → 越低打分越稳定。想每次跑分一模一样就设 `0`
  （注意：受模型本身影响，**即使设 0 分数也可能有轻微浮动，这很正常**）

### 读取记忆库（给第二阶段用）

现在的 `main.py` 只负责**写入**。想**读取**记忆，用 `short_memory_store.load_memory()`：

```python
import short_memory_store

memories = short_memory_store.load_memory()      # 读全部记忆
for m in memories[-3:]:                          # 看最近 3 条
    print(m["timestamp"], m["summary"], m["emotional_impact"])
```

再比如，只挑"情感冲击 > 80"的记忆（这些就是最该被记住的事）：

```python
high_impact = [m for m in memories if m["emotional_impact"] > 80]
```

---

## 8. 建议的代码阅读顺序

别一上来啃 `main.py`，按这个顺序读，由易到难：

| 顺序 | 文件 | 看什么 | 预计耗时 |
|---|---|---|---|
| 1 | `information.txt` | 输入长什么样 | 30 秒 |
| 2 | `short_term_memory.json` | 输出长什么样 ← **先看结果，再看过程** | 1 分钟 |
| 3 | `persona.py` | 评判标准（全是中文文本，零门槛） | 3 分钟 |
| 4 | `schemas.py` | 记忆的"字段清单" | 2 分钟 |
| 5 | `tools.py` | 时间工具怎么做的 | 3 分钟 |
| 6 | `short_memory_store.py` | 读写 JSON，一共 27 行 | 2 分钟 |
| 7 | `main.py` | **最后读**，它把上面全部串起来 | 10 分钟 |

读 `main.py` 时，只看这 4 个关键位置就够了：

| 行号 | 内容 | 重要性 |
|---|---|---|
| 22-58 | 提示词模板 | 系统的"灵魂" |
| **63** | `memory_chain = prompt \| llm.with_structured_output(...)` | ⭐ **核心就这一行** |
| 66-74 | 按 `###` 切割文本 | 输入处理 |
| 85-113 | 处理循环：调 Chain → 覆盖字段 → **写入短期记忆** | 主流程 |

---

## 9. 常见报错与解法

### 9.1 `FileNotFoundError: short_term_memory.json`

**什么时候出现**：第一次运行、或者你手动删掉了记忆库文件之后。

**原因**：`short_memory_store.py` 第 12 行的 `load_memory()` 直接打开文件读，
文件不存在就抛异常。它一开始设计时假设文件总是存在。

**解法 A（改代码，推荐，一劳永逸）**：给 `short_memory_store.py` 的 `load_memory()` 加两行判断：

```python
def load_memory() -> list:
    # 记忆库还不存在（第一次运行）就当作空库，不要报错
    if not os.path.exists(MEMORY_FILE):
        return []
    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)
```

> 文件顶部已经 `import os` 了，直接用就行。

**解法 B（最快，只救这一次）**：手动建一个空记忆库。在 `dd` 目录下运行：

```powershell
python -c "open('short_term_memory.json','w',encoding='utf-8').write('[]')"
```

> ⚠️ **不要用 PowerShell 的 `'[]' | Out-File -Encoding utf8`**！
> 在 PowerShell 5.1 下它会写入一个看不见的 BOM 头（`EF BB BF`），
> 然后 `json.load` 会报 `JSONDecodeError: Unexpected UTF-8 BOM`。
> 这是个非常容易被坑的地方，实测过，所以这里用 Python 来建文件。

---

### 9.2 输出里中文变成 `��������`

**长这样**：

```
��֣���г�� 72 | �����Ǻ� 55 | �����̶� 78
```

**先放心**：⚠️ **这只是显示问题，`short_term_memory.json` 里的中文永远是好的**，数据本身没坏。

**什么时候会出现**：当你**把输出重定向到文件，或者通过管道、IDE 输出窗口、其他程序捕获输出**的时候，比如：

```powershell
python main.py > log.txt
```

原因：此时 Python 不再走 Windows 控制台的 Unicode 接口，而是按**系统区域编码（GBK）**输出，
于是接收方按 UTF-8 去读就成了一堆乱码。
（实测：被捕获时 `sys.stdout.encoding` 是 `gbk`。直接在终端里运行时一般不会乱码。）

**解法（三选一，实测有效）**：

**A. 当前窗口生效**（推荐先试这个）：

```powershell
$env:PYTHONUTF8 = "1"
python main.py
```

**B. 永久生效**（执行一次，以后所有新窗口都有效）：

```powershell
[Environment]::SetEnvironmentVariable("PYTHONUTF8", "1", "User")
```

**C. 改代码（最稳，跟运行环境无关）** — 在 `main.py` 最上面加两行：

```python
import sys
sys.stdout.reconfigure(encoding="utf-8")   # 保证打印中文不乱码
```

> 如果这些你都不想做，那就**别管它**——控制台看着难受，但 `short_term_memory.json` 打开一看中文是正常的，不影响后面两个阶段。

---

### 9.3 `ModuleNotFoundError: No module named 'xxx'`

说明依赖没装好。这个项目需要：

```powershell
pip install langchain-deepseek langchain-core python-dotenv pydantic
```

检查装好了没：

```powershell
pip list | Select-String "langchain|dotenv|pydantic"
```

---

### 9.4 `AuthenticationError` / `401` / `Insufficient Balance`

- `401` → `.env` 里的 key 不对，或者文件里多了引号/空格。正确格式：`DEEPSEEK_API_KEY=sk-xxxx`，**等号两边不要有空格，值不要加引号**
- `Insufficient Balance` → DeepSeek 账户余额用完了，去官网充值

---

### 9.5 在其他目录运行就报错

因为 `main.py` 第 15 行的 `DEFAULT_INPUT = "information.txt"` 和
`short_memory_store.py` 第 8 行的 `MEMORY_FILE = "short_term_memory.json"`
都是**相对路径**，会按"当前工作目录"去找文件。

**解法**：运行前先 `cd` 到 `dd` 目录。或者想在哪都能跑，改成绝对路径：

```python
# main.py
DEFAULT_INPUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "information.txt")

# short_memory_store.py
MEMORY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "short_term_memory.json")
```

---

### 9.6 分数每次跑都不一样

**正常现象**，大模型本身带随机性。想更稳定：把 `main.py` 第 19 行的 `temperature` 调到 `0`。

### 9.7 模型没按人格打分（比如明星八卦给了 80 分）

按顺序排查：

1. `persona.py` 里"不太关心的事"写清楚了没？**负面清单往往比正面清单更管用**
2. `SCORING_RULES` 里的分数区间是不是太模糊？把"80-100"具体描述成"只有……才能给 80 以上"
3. `schemas.py` 里对应字段的 `description` 是不是太简单？那里也会告诉模型怎么填

---

### 9.8 小提示：`main.py` 第 1 行可以删掉

```python
from email.mime import text    # ← 这行没用，是编辑器自动补全误加的，且 text 这个名字没人用
```

删掉不影响任何功能。

---

## 10. 接下来是什么（第二阶段）

第一阶段交付的是"**存**"。第二阶段"睡眠巩固引擎"要做的是"**整理**"：

```
short_term_memory.json  ──► 睡眠巩固引擎 ──► 长期记忆库
   （短期，什么都在）          │              （向量库+图数据库）
                              │
                        像人睡觉时大脑做的事：
                        · 把同主题的记忆聚成一类（键盘/耳机/NAS…）
                        · 合并重复的（6 条键盘记忆 → 1 条"我是个键盘发烧友"）
                        · 遗忘低分记忆（interest<20 且 emotional<20 的直接丢）
                        · 提升高分记忆的权重（情感冲击 90+ 的长期保留）
```

**现在写第一阶段时，已经为第二阶段留好的接口**：

| 接口 | 位置 | 第二阶段怎么用 |
|---|---|---|
| `load_memory()` | `short_memory_store.py` | 读全部短期记忆做聚类 |
| 四个分数字段 | `schemas.py` | 当"遗忘/保留"的权重依据 |
| `summary` 字段 | `schemas.py` | 直接喂给向量库做 embedding |
| `MemoryRecord` | `schemas.py` | 加 `embedding`、`related_ids` 字段即可复用 |

所以你现在不用着急，**只要保证记忆库里数据质量干净、分数有意义**，第二阶段的原料就备好了。

---

## 一句话总结

```
information.txt --(按 ### 切)--> 片段 --(人格+动机+时间工具)×大模型--> 七个字段 --(append)--> short_term_memory.json
```

**读文本 → 结合提示词处理 → 产出元数据 → 存入 JSON。** 就这么简单，剩下的都是细节。
