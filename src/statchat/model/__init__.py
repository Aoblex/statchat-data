from langchain_openai import ChatOpenAI

class QAModel:

    def __init__(self,
                 openai_api_key_path: str,
                 temperature: float = 0.01,
                 model: str = "gpt-3.5-turbo-1106"):

        # Read api key
        with open(openai_api_key_path, "r") as f:
            self.model_api_key = f.read().strip()

        self.model = ChatOpenAI(
            openai_api_key=self.model_api_key,
            temperature=temperature,
            base_url="https://api.132999.xyz/v1",
            model=model,
            model_kwargs={
                "response_format": {
                    "type": "json_object",
                },
            }
        )



