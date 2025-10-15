import os
import asyncio
from dotenv import load_dotenv

load_dotenv()

from MedicalAgent.med_agents.agent_runner import run_medical_interview


def check_environmental_variables():
    open_ai_key = os.environ.get("OPENAI_API_KEY")

    if not open_ai_key:
        raise ValueError("OPENAI_API_KEY is not in the .env file")


if __name__ == "__main__":
    try:
        check_environmental_variables()
        asyncio.run(run_medical_interview())
    except ValueError as e:
        print(f"Configuration Error: {e}")
    except Exception as e:
        print(f"A fatal error occurred: {e}")
