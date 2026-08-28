from cerebras.cloud.sdk import Cerebras
from dotenv import load_dotenv
import os

load_dotenv()

client = Cerebras(
    api_key=os.getenv("CEREBRAS_API_KEY")
)

response = client.chat.completions.create(
    model="gpt-oss-120b",
    messages=[
        {
            "role": "user",
            "content": "Say hello in one sentence."
        }
    ],
)

print(response.choices[0].message.content)