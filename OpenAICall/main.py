# main.py

import os
import asyncio
from dotenv import load_dotenv
from physician_assistant_agent import conversational_history_taking
from medical_research_agent import obtain_medical_news

load_dotenv()

def check_environmental_variables():
    open_ai_key = os.environ.get("OPENAI_API_KEY")

    if not open_ai_key:
        raise ValueError("OPENAI_API_KEY is not in the .env file")

# Standard Python entry point to run the asynchronous main function
if __name__ == "__main__":
    try:
        check_environmental_variables()
        asyncio.run(conversational_history_taking())
    except ValueError as e:
        print(f"Configuration Error: {e}")
    except Exception as e:
        print(f"A fatal error occurred: {e}")