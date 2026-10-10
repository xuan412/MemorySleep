# tools.py —— LangChain 工具：获取当前时间
#时间不交给大模型猜（它会编），而是做成工具让它调用，再由代码真正执行。

from datetime import datetime

from langchain_core.tools import tool


@tool
def get_current_time() -> str:
    """获取当前的日期和时间，返回格式 2025-01-01 12:00:00"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def ask_model_for_time(llm) -> str:
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
