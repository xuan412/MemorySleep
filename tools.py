# tools.py —— LangChain 工具：获取当前时间
#时间不交给大模型猜（它会编），而是做成工具让它调用，再由代码真正执行。

from datetime import datetime

from langchain_core.tools import tool


@tool
def get_current_time() -> str:
    """获取当前的日期和时间，返回格式 2025-01-01 12:00:00"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def ask_model_for_time(llm ) -> str:
    """
    让模型自己决定调用 get_current_time 工具，返回真实时间字符串。
    这是标准的 LangChain 工具调用流程：bind_tools -> 模型给出 tool_calls -> 本地执行。
    """
    ai_msg = llm.bind_tools([get_current_time]).invoke("请调用工具获取当前时间。")

    # 模型给出了工具调用请求，就本地把它执行掉
    if ai_msg.tool_calls:
        return get_current_time.invoke(ai_msg.tool_calls[0]["args"])

    # 少数情况下模型直接回答，就手动兜底调用一次工具
    return get_current_time.invoke({})


"""
@tool 会把普通函数变成agent可识别的工具
例如我们现在有工具 a，b，c，
我们可以写一个列表tools = [a,b,c]
msg = llm.bind_tool(tools).invoke("文本") 会根据文本内容返回一个AIMessage 类型的变量，
形式：
AIMessage(
    content="",                        # 文本内容
    tool_calls=[                       # 工具调用请求（可能有，也可能为空）
        {
            "name": "get_current_time",
            "args": {},
            "id": "call_abc123",
            "type": "tool_call",
        }
    ],
    response_metadata={...},           # 模型返回的元信息
    usage_metadata={...},              # token 用量
    id="run-xxx",
)
我们可以用msg.tool_calls来获取ai调用的工具
注意tool_calls中可以有多个工具，即tool_calls = [{...},{...},{...},...]
可以使用.tool_calls[i]来知道ai调用的第i个工具是什么
如果我们要用多个工具，可以定义
tools_by_name = {t.name: t for t in tools} 
            #通过这个字典将工具的name和工具联系起来
            #.name 是tool类型的属性，它将函数名变为字符串并可通过.name调用

for call in msg.tool_calls:         #遍历ai使用的工具
    tools_by_name[call["name"]].invoke(call["args"])   #逐一调用
"""
