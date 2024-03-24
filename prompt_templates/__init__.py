from langchain.prompts import (
    SystemMessagePromptTemplate,
    ChatPromptTemplate,
)

from langchain.output_parsers import (
    ResponseSchema,
    StructuredOutputParser,
)

class QuestionTemplate:

    def __init__(self, prompt_topic: str):
        self.prompt_topic = prompt_topic
        self.system_prompt = SystemMessagePromptTemplate.from_template(
            """你是一个热爱{prompt_topic}的学生，你的任务是基于给定的上下文提出十个{prompt_topic}问题，你的提问应当满足以下要求：
            1. 问答主题：你的提问应当以{prompt_topic}作为主题。
            2. 结合材料：请针对上下文中的知识点、关键词和短语提出问题。
            3. 灵活表达：尝试使用不同的句式和表达方式，增加提问的多样性和丰富度。
            4. 清晰易懂：请确保提问清晰易懂，避免使用过于专业的术语或复杂的句子结构。
            5. 适当省略：如果上下文中是与{prompt_topic}无关的内容，请忽略这些内容，只生成{prompt_topic}相关问题。
            """
        )
        self.response_schemas = [
            ResponseSchema(
                name="问题列表",
                description="{prompt_topic}问题列表".format(prompt_topic=prompt_topic),
                type="list",
            ),
        ]
        self.output_parser = StructuredOutputParser.from_response_schemas(self.response_schemas)
        self.format_instructions = f"你的提问应该是一段具有以下格式的markdown代码，包括开头和结尾的 \"```json\" 和 \"```\"\n{self.output_parser.get_format_instructions(only_json=True)}"
        self.prompt_template = ChatPromptTemplate.from_messages(
            [
                self.system_prompt,
                ("human", "\n```上下文\n{input}\n```\n{format_instructions}"),
            ],
        ).partial(
            format_instructions=self.format_instructions,
            prompt_topic=self.prompt_topic,
        )

    def get_prompt(self, input: str):
        return self.prompt_template.format(input=input)
    
class AnswerTemplate:

    def __init__(self, prompt_topic: str):
        self.prompt_topic = prompt_topic
        
        self.response_schemas = [
            ResponseSchema(
                name="回答",
                description="{prompt_topic}问题的回答".format(prompt_topic=prompt_topic),
            ),
        ]

        self.output_parser = StructuredOutputParser.from_response_schemas(self.response_schemas)
        self.format_instructions = f"你可以参考给定的上下文给出回答，你的回答应该是一段具有以下格式的markdown代码，包括开头和结尾的 \"```json\" 和 \"```\"\n{self.output_parser.get_format_instructions(only_json=True)}"

        self.prompt_template = ChatPromptTemplate.from_messages(
            [
                ("system", "你是一名经验丰富的{prompt_topic}领域专家，请使用你丰富的{prompt_topic}专业知识回答我提出的问题。如果你对这个问题不确定，你可以参考给定的上下文给出回答。".format(prompt_topic=prompt_topic)),
                ("human", "\n```上下文\n{context}\n```\n```问题\n{input}\n```\n{format_instructions}"),
            ]
        ).partial(format_instructions=self.format_instructions)

    def get_prompt_with_context(self, context: str):
        return self.prompt_template.partial(context=context)

    def get_prompt(self, input: str):
        return self.prompt_template.format(input=input)