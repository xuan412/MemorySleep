#导入文件,使劲导就完了
import os
import json
from dotenv import load_dotenv
from langchain_deepseek import ChatDeepSeek
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel,Field

# 读取项目根目录下的 .env 文件
load_dotenv()

#读取环境变量里的apiKey
key=os.environ.get("DEEPSEEK_API_KEY")
if not key:
    raise ValueError("看看你的apikey是否合适")

#配置大模型,记住这不是ai，是大脑
#温度就是大模型的随机程度，后期可能要微调
brain=ChatDeepSeek(
    model="deepseek-chat",
    temperature=0.4,
    api_key=key
)
#检测代码，如果调用正常，就会回复OK
print(brain.invoke("小小的deepseek,你准备好了吗？如果好了，只回答“DEEPSEEK已就绪").content)

#导入你的人格文件
with open("personality.txt","r",encoding="utf-8") as p:
    personalityDiscription=p.read()
if personalityDiscription is not None:
    print("人格加载完毕")

#导入你的提示词文件
with open("memoryPrompt.txt","r",encoding="utf-8") as pro:
    MemoryDealPrompt=pro.read()
if MemoryDealPrompt is not None:
    print("记忆提示词加载完毕") 

#创建提示词模板
MemoryDealPromptOk=ChatPromptTemplate.from_messages([("system","{人物背景}{记忆处理提示词}"),("human","你看到的：{文本}")])

#给AI的回答制定一个标准
class ResponseStandard(BaseModel):
    memoryContent:str=Field(description="你是一个正真的人，这是你大脑中看完东西留下的记忆片段,他是模糊的，不清晰的，简短的，例如这个男主好傻，竟然自杀了")
    interest:float=Field(ge=0,le=1,description="你作为一个人，你觉得有意思程度打分，0无兴趣，1有兴趣")

#我们来构建一个链条
thinking_chain=MemoryDealPromptOk | brain.with_structured_output(ResponseStandard)
    
#导入我们的文本
with open("text.json","r",encoding="utf-8") as t:
    date=json.load(t)
texts =date["news"]

#为方便循环我们创建一个函数
def AIDeal(text):
    response=thinking_chain.invoke({"人物背景":personalityDiscription,"记忆处理提示词":MemoryDealPrompt,"文本":text})
    print(response.memoryContent)
    print(response.interest)
    #把这些记忆存储到memory.json文件中
    with open("memory.json","r",encoding="utf-8") as f:
        date =json.load(f)
    date.append(response.model_dump())
    with open("memory.json","w",encoding="utf-8") as f:
        json.dump(date,f,ensure_ascii=False,indent=2)
    
#开始执行
for i,text in enumerate(texts,start=1):
    print(f"读取到第{i}块文本")
    AIDeal(text)

#睡眠功能
with open("sleepPrompt.txt","r",encoding="utf-8") as t:
    sleepPrompt=t.read()
sleepPromptOk =ChatPromptTemplate.from_messages([("system","你是{人格信息}，你要{睡眠处理}"),("human","{记忆内容}")])
sleep_chain=sleepPromptOk|brain

with open("memory.json","r",encoding="utf-8") as t:
    date=json.load(t)

for i,text in enumerate(date,start=1):
    print(f"读取到第{i}块文本")
    re=sleep_chain.invoke({"人格信息":personalityDiscription,"睡眠处理":sleepPrompt,"记忆内容":text})
    print(re.content)




