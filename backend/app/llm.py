from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from app.models import (SupervisorDecision,RequirementsArchitectureOutput,TechnologyRecommendations)

load_dotenv()

groq_model = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0,
)

supervisor_model = groq_model.with_structured_output(SupervisorDecision,method="json_mode")


gemini_model = ChatGoogleGenerativeAI(model = "gemini-2.5-flash"
                                      ,temperature = 0)

requirements_architecture_model = gemini_model.with_structured_output(RequirementsArchitectureOutput)

technologyrecommendations_model = gemini_model.with_structured_output(TechnologyRecommendations)