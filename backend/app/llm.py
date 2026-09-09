import os

from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_cloudflare import ChatCloudflareWorkersAI
from  langchain_nvidia_ai_endpoints import ChatNVIDIA

from app.models import (
    SupervisorDecision,
    RequirementsArchitectureOutput,
    TechnologyRecommendations,
    Critique,
)

load_dotenv()


# ---------------------------------------------------------
# Groq
# ---------------------------------------------------------

groq_model = None

if os.getenv("GROQ_API_KEY"):
    groq_model = ChatGroq(
        model="openai/gpt-oss-120b",
        temperature=0,
    )

groq_tool_model = None

if os.getenv("GROQ_API_KEY"):
    groq_tool_model = ChatGroq(
        model="qwen/qwen3.6-27b",
        temperature=0, max_tokens=900
    )

groq_structured_model = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0,
)

groq_diagram_model = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0,
   

)
# ---------------------------------------------------------
# Gemini
# ---------------------------------------------------------

google_model = None

if os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"):
    google_model = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0,
    )




# ---------------------------------------------------------
# Cloudflare
# ---------------------------------------------------------

cloudfare_model = None

if os.getenv("CF_AI_API_TOKEN"):
    cloudfare_model = ChatCloudflareWorkersAI(
        model="@cf/google/gemma-4-26b-a4b-it",
        temperature=0,
        max_tokens=4096,
    )


# ---------------------------------------------------------
# Structured models
# ---------------------------------------------------------

supervisor_model = (
    groq_model.with_structured_output(
        SupervisorDecision,
        method="json_mode",
    )
    if groq_model
    else None
)


requirements_architecture_model = (
    cloudfare_model.with_structured_output(
        RequirementsArchitectureOutput,
    )
    if cloudfare_model
    else None
)


technologyrecommendations_model = (
    groq_structured_model.with_structured_output(
        TechnologyRecommendations,
        method="json_schema",
        strict=True
    )
    if cloudfare_model
    else None
)


critic_model = (
    groq_model.with_structured_output(
        Critique,
        method="json_schema",
    )
    if groq_model
    else None
)