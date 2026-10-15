from pydantic import BaseModel, Field


class MemoryRecord(BaseModel):
    """一条短期记忆的元数据"""

    raw_content: str = Field(description="原始内容：切割后未经改写的原文片段")

    summary: str = Field(description="浓缩概括：一句话说清这条内容，用第一人称")

    timestamp: str = Field(description="时间：直接填入系统提供的当前时间，不要自己编造")

    emotional_impact: int = Field(
        ge=0, le=100, description="情感冲击打分 0-100"
    )
    motivation_match: int = Field(
        ge=0, le=100, description="动机吻合打分 0-100"
    )
    anomaly: int = Field(
        ge=0, le=100, description="反常程度打分 0-100"
    )
    interest_score: int = Field(
        ge=0, le=100, description="兴趣点打分 0-100"
    )
    worth_evaluation:int = Field(
        ge=0, le=1, description="是否值得留存"
     )