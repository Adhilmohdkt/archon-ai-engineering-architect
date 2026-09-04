import os

from dotenv import load_dotenv
from langchain_mistralai import ChatMistralAI

from deepeval.models.base_model import DeepEvalBaseLLM


# ============================================================
# LOAD ENVIRONMENT
# ============================================================

load_dotenv()


# ============================================================
# MISTRAL API KEY
# ============================================================

mistral_api_key = os.getenv("MISTRAL_API_KEY")

if not mistral_api_key:
    raise ValueError(
        "MISTRAL_API_KEY not found in .env"
    )


# ============================================================
# MISTRAL MODEL
# ============================================================

mistral_model = ChatMistralAI(
    model="mistral-small-latest",
    api_key=mistral_api_key,
    temperature=0,
)


# ============================================================
# DEEPEVAL JUDGE ADAPTER
# ============================================================

class MistralJudge(DeepEvalBaseLLM):

    def __init__(self, model):
        self.model = model


    def load_model(self):
        return self.model


    def generate(
        self,
        prompt: str,
    ) -> str:

        response = self.model.invoke(
            prompt
        )

        return response.content


    async def a_generate(
        self,
        prompt: str,
    ) -> str:

        response = await self.model.ainvoke(
            prompt
        )

        return response.content


    def get_model_name(self):

        return "Mistral Small"


# ============================================================
# JUDGE INSTANCE
# ============================================================

judge = MistralJudge(
    mistral_model
)