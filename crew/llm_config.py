import os
import litellm
from dotenv import load_dotenv
from crewai import LLM

load_dotenv()
litellm.drop_params = True

# Llama 3.1 8b on Groq — fast, for research/retrieval tasks
llama_instant = LLM(
    model="groq/llama-3.1-8b-instant",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.1,
    drop_params=True,
)

# Llama 3.3 70b on Groq — highly capable, for report writing
llama_versatile = LLM(
    model="groq/llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.3,
    drop_params=True,
)
