import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("API_KEY"))

models = genai.list_models()

for model in models:
    print(f"Model Name: {model.name}")
    print(f"Supported Generation Methods: {model.supported_generation_methods}")
    print("-" * 40)
