import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "src", ".env"))

gemini_api_key = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=gemini_api_key)

output_file = "available_models.txt"
with open(output_file, "w") as f:
    f.write("Available models:\n")
    for m in genai.list_models():
        f.write(f"{m.name}\n")

print(f"Available models written to {output_file}")
