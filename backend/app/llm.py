from dotenv import load_dotenv
from langchain_groq import ChatGroq
from app.models import SupervisorDecision

load_dotenv()

model = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0,
)

supervisor_model = model.with_structured_output(SupervisorDecision)
