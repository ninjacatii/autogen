import asyncio

from typing import Any, Dict, List

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import HandoffTermination, TextMentionTermination
from autogen_agentchat.messages import HandoffMessage
from autogen_agentchat.teams import Swarm
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient

def refund_flight(flight_id: str) -> str:
    """Refund a flight"""
    return f"Flight {flight_id} refunded"

model_client = OpenAIChatCompletionClient(
    #model="deepseek-reasoner",#不支持
    model="deepseek-chat",#支持差
    #model="qwen-plus",
    #model="gemini-2.0-flash",
    temperature=0,
    # api_key="YOUR_API_KEY",
)

travel_agent = AssistantAgent(
    "travel_agent",
    model_client=model_client,
    handoffs=["flights_refunder", "user"],
    system_message="""You are a travel agent.
    The flights_refunder is in charge of refunding flights.
    If you need information from the user, you must first send your message, then you can handoff to the user.
    Use TERMINATE when the travel planning is complete.""",
)

flights_refunder = AssistantAgent(
    "flights_refunder",
    model_client=model_client,
    handoffs=["travel_agent", "user"],
    tools=[refund_flight],
    system_message="""You are an agent specialized in refunding flights.
    You only need flight reference numbers to refund a flight.
    You have the ability to refund a flight using the refund_flight tool.
    If you need information from the user, you must first send your message, then you can handoff to the user.
    When the transaction is complete, handoff to the travel agent to finalize.""",
)

termination = HandoffTermination(target="user") | TextMentionTermination("TERMINATE")
team = Swarm([travel_agent, flights_refunder], termination_condition=termination)

task = "I need to refund my flight."

async def main() -> None:
    async def run_team_stream() -> None:
        task_result = await Console(team.run_stream(task=task))
        last_message = task_result.messages[-1]

        while isinstance(last_message, HandoffMessage) and last_message.target == "user":
            user_message = input("User: ")

            task_result = await Console(
                team.run_stream(task=HandoffMessage(source="user", target=last_message.source, content=user_message))
            )
            last_message = task_result.messages[-1]


    # Use asyncio.run(...) if you are running this in a script.
    await run_team_stream()

asyncio.run(main())