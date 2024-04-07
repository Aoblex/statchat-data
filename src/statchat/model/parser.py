from langchain_core.output_parsers import (
    JsonOutputParser,
    StrOutputParser,
    PydanticOutputParser,
)
from typing import List
from langchain_core.pydantic_v1 import BaseModel, Field

class Question(BaseModel):
    questions: List[str] = Field(description="一个有关上下文的问题列表")

class Triplet(BaseModel):
    subject: str = Field(description="主语")
    predicate: str = Field(description="谓语")
    object: str = Field(description="宾语")

class Triplets(BaseModel):
    triplets: List[Triplet] = Field(description="知识三元组列表")

class CustomParser:

    question_parser = StrOutputParser()
    answer_parser = StrOutputParser()
    triplets_parser = PydanticOutputParser(pydantic_object=Triplets)