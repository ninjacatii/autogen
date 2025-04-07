import json
from pathlib import Path

import asyncio
from datetime import datetime
from typing_extensions import Annotated

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import HandoffTermination, TextMentionTermination
from autogen_agentchat.messages import HandoffMessage
from autogen_agentchat.teams import Swarm
from autogen_agentchat.ui import Console
from autogen_core.tools import FunctionTool, Utils
from autogen_ext.models.openai import OpenAIChatCompletionClient
import chromadb
from chromadb.api.types import GetResult


# 获取当前脚本所在目录
SCRIPT_DIR = Path(__file__).parent.absolute()
DB_PATH = str(SCRIPT_DIR / ".chromadb_autogen")
# 初始化Chroma客户端
client = chromadb.PersistentClient(path=DB_PATH)
# 获取或创建一个集合
collection = client.get_or_create_collection(name="preferences")

async def query_by_type(type_value: str, limit: int = 1) -> str | None:
    """根据metadata中的type字段查询记录"""
    results: GetResult = collection.get(
        where={"type": type_value},  # 查询条件
        limit=limit,  # 返回结果数量限制
        include=["documents", "metadatas"]  # 包含文档内容和元数据
    )
    if results['documents'] is not None and len(results['documents']) > 0:
        return results['documents'][0]
    return None

async def query_id_card_no() -> str | None:
    return await query_by_type("ID Card No.")

async def write_to_chroma(personal_info_type: str, personal_info_data: str):
    # 使用upsert方法
    collection.upsert(
        documents=[personal_info_data],
        metadatas=[{"category": "user", "type": personal_info_type, "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}],
        ids=["user:" + personal_info_type]
    )
    await Utils.display_preferences_data(path=DB_PATH)

def query_price(airplane: str) -> str:
    return "The price is $1234"

def query_flight(date: str) -> str: 
    return f"{date}: Boeing 737 airplane"

def refund_flight(id_card_no: Annotated[str, "User's ID card No."]) -> str:
    """Refund a flight"""
    return f"Flight refunded by user's ID Card No. :{id_card_no}"

refund_flight_tool = FunctionTool(refund_flight, description="Flight refunded by user's ID Card No.")
data = refund_flight_tool.schema
# 格式化输出
formatted_json = json.dumps(data, indent=4, ensure_ascii=False)
print("\n" + formatted_json)

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
    handoffs=["flights_refunder", "flights_queryer", "flights_pricer", "user_preferences_recorder", "user"],
    system_message="""You are a travel agent.
    The flights_refunder is in charge of refunding flights.
    The flights_queryer is in charge of querying flights.
    The flights_pricer is in charge of querying price of airplane.
    The user_preferences_recorder is used to record user personal information when task is complete.
    If you need information from the user, you must first send your message, then you can handoff to the user.
    Use user_preferences_recorder when the task is complete.""",
)

user_preferences_recorder = AssistantAgent(
    "user_preferences_recorder",
    model_client=model_client,
    handoffs=["travel_agent", "user"], 
    tools=[write_to_chroma],
    system_message="""You are an agent specialized in recording user personal information.
    If the user discloses his personal information during the process of performing a task, please record it by using the write_to_chroma tool.
    Use TERMINATE when recording is complete.""",
)

flights_pricer = AssistantAgent(
    "flights_pricer",
    model_client=model_client,
    handoffs=["travel_agent", "user"],
    tools=[query_price],
    system_message="""You are an agent specialized in querying the price of airplane.
    You only need the airplane type to query price.
    You have the ability to query price of airplane type using the query_price tool.
    If you need information from the user, you must first send your message, then you can handoff to the user.
    When the query is complete, handoff to the travel agent to finalize.""",
)

flights_queryer = AssistantAgent(
    "flights_queryer",
    model_client=model_client,
    handoffs=["travel_agent", "user"],
    tools=[query_flight],
    system_message="""You are an agent specialized in querying flights.
    You only need the date of flight to query a flight.
    You have the ability to query a flight using the query_flight tool.
    If you need information from the user, you must first send your message, then you can handoff to the user.
    When the query is complete, handoff to the travel agent to finalize.""",
)

flights_refunder = AssistantAgent(
    "flights_refunder",
    model_client=model_client,
    handoffs=["travel_agent", "user"],
    tools=[refund_flight_tool, query_id_card_no],
    system_message="""You are an agent specialized in refunding flights.
    You only need the ID Card No. of the user to refund a flight.
    You can first query the ID Card No. of the user using the query_id_card_no tool.
    If the ID Card No. of the user is not found, you can ask the user to provide it.
    If the ID Card No. of the user is founded, you need send the ID Card No. to the user to confirm.
    If the user consider the ID Card No. is not correct, you can ask the user to provide by handoff to the user.
    You have the ability to refund a flight using the refund_flight_tool tool.
    If you need information from the user, you must first send your message, then you can handoff to the user.
    When the transaction is complete, handoff to the travel agent to finalize.""",
)

termination = HandoffTermination(target="user") | TextMentionTermination("TERMINATE")
team = Swarm([travel_agent, user_preferences_recorder, flights_refunder, flights_queryer, flights_pricer], termination_condition=termination)

#task = "I need to query flight."
task = "I need to refund my flight."

async def run_team_stream() -> None:
    task_result = await Console(team.run_stream(task=task))
    last_message = task_result.messages[-1]

    while isinstance(last_message, HandoffMessage) and last_message.target == "user":
        user_message = input("User: ")

        task_result = await Console(
            team.run_stream(task=HandoffMessage(source="user", target=last_message.source, content=user_message))
        )
        last_message = task_result.messages[-1]

asyncio.run(run_team_stream())