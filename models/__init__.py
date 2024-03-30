from langchain_openai import ChatOpenAI

class QAModel:

    def __init__(self):

        # Read api key
        with open("model_api_key.txt", "r") as f:
            self.model_api_key = f.read().strip()

        self.model = ChatOpenAI(
            openai_api_key=self.model_api_key,
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


