from langchain_core.output_parsers import (
    JsonOutputParser,
    StrOutputParser,
)
from langchain_core.pydantic_v1 import BaseModel, Field

class Question(BaseModel):
    questions: str = Field(description="一个有关上下文的问题列表")


class CustomParser:

    question_parser = JsonOutputParser(pydantic_object=Question)
    answer_parser = StrOutputParser()