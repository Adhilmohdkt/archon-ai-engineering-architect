from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_cloudflare import ChatCloudflareWorkersAI
from app.models import (SupervisorDecision,RequirementsArchitectureOutput,TechnologyRecommendations)

load_dotenv()

groq_model = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0,
)

supervisor_model = groq_model.with_structured_output(SupervisorDecision,method="json_mode")


cloudfare_model = ChatCloudflareWorkersAI(model = "@cf/google/gemma-4-26b-a4b-it"
                                      ,temperature = 0)

requirements_architecture_model = cloudfare_model.with_structured_output(RequirementsArchitectureOutput)

technologyrecommendations_model = cloudfare_model.with_structured_output(TechnologyRecommendations)