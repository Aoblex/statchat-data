from langchain_openai import ChatOpenAI

class QAModel:

    def __init__(self):
        self.model = ChatOpenAI(
            openai_api_key="sk-n4wVb574XCbb0p3SFbF7547e4a484b3d82640c8dCe553e20",
            temperature=0.1,
            base_url="https://api.132999.xyz/v1",
            model="gpt-3.5-turbo-1106",
            model_kwargs={
                "frequency_penalty": 0.1,
                "presence_penalty": 0.1,
                "response_format": {
                    "type": "json_object",
                },
            }
        )


