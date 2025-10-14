import os
import asyncio

from dotenv import load_dotenv

from agents import Agent, Runner, WebSearchTool

load_dotenv()


def check_environmental_variables():
    open_ai_key = os.environ.get("OPENAI_API_KEY")

    if not open_ai_key:
        raise ValueError("OPEN_API_KEY is not in the .env file")


async def obtain_medical_news():

    medical_research_agent = Agent(
        name="Medical Research Agent",
        instructions="You are are medical research assistant. You need to find all the recent medical research news articles",
        tools=[WebSearchTool()],
    )
    results = await Runner.run(
        medical_research_agent, "What is the most recent medical innovations?"
    )
    print(results)


# Standard Python entry point to run the asynchronous main function
if __name__ == "__main__":
    asyncio.run(obtain_medical_news())
