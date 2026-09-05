import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from deepeval.models.base_model import DeepEvalBaseLLM


load_dotenv()


# ============================================================
# GROQ JUDGE MODEL
# ============================================================

groq_api_key = os.getenv("GROQ_API_KEY")

if not groq_api_key:
    raise ValueError(
        "GROQ_API_KEY not found in .env"
    )


groq_model = ChatGroq(
    model="openai/gpt-oss-120b",
    api_key=groq_api_key,
    temperature=0,
)


# ============================================================
# DEEPEVAL MODEL ADAPTER
# ============================================================

class GroqJudge(DeepEvalBaseLLM):

    def __init__(self, model):
        self.model = model

    def load_model(self):
        return self.model

    def generate(self, prompt: str) -> str:

        response = self.model.invoke(prompt)

        return response.content

    async def a_generate(self, prompt: str) -> str:

        response = await self.model.ainvoke(prompt)

        return response.content

    def get_model_name(self):

        return "Groq GPT-OSS-120B"


# ============================================================
# JUDGE INSTANCE
# ============================================================

judge = GroqJudge(groq_model)