import os
from langchain_groq import ChatGroq
from dotenv import load_dotenv

from deepeval import evaluate
from deepeval.models.base_model import DeepEvalBaseLLM
from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCase,SingleTurnParams

load_dotenv

API_KEY = os.getenv('GROQ_API_KEY')


model = ChatGroq(model="openai/gpt-oss-120b",
                api_key=API_KEY,
                temperature=0)
class Groqjudge(DeepEvalBaseLLM):

    def __init__(self,model):
        self.model = model

    def load_model(self):
        return self.model

    def generate(self, prompt ):
        response = self.model.invoke(prompt)
        return response.content
    async def a_generate(self, prompt ):
            response = await self.model.ainvoke(prompt)
            return response.content
    def get_model_name(self):
        return "Groq GPT-OSS-120B"



judge = Groqjudge(model)
        

test_case = LLMTestCase( input = 'What is the capital of france ',
                        actual_output= 'The capital of france is paris')


correctness_metics = GEval(name="Correctness",
                           criteria="""
    Evaluate whether the actual output correctly answers
    the user's question.

    The answer should:

    1. Be factually correct.
    2. Directly answer the question.
    3. Not contain incorrect information.
    """,
       evaluation_params=[
    SingleTurnParams.INPUT,
    SingleTurnParams.ACTUAL_OUTPUT,
],
    threshold=0.5,
    model=judge,)


results = evaluate(test_cases=[test_case],
                   metrics=[correctness_metics])

print("\nEvaluation completed.")
print(results)