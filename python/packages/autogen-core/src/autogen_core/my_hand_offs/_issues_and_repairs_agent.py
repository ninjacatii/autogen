from typing import List
from autogen_core.models import ChatCompletionClient, SystemMessage
from autogen_core.my_hand_offs import AIAgent
from autogen_core.tools import FunctionTool, Tool

def look_up_item(search_query: str) -> str:
    item_id = "item_132612938"
    print("Found item:", item_id)
    return item_id

def execute_refund(item_id: str, reason: str = "not provided") -> str:
    print("\n\n=== Refund Summary ===")
    print(f"Item ID: {item_id}")
    print(f"Reason: {reason}")
    print("=================\n")
    print("Refund execution successful!")
    return "success"

look_up_item_tool = FunctionTool(
    look_up_item, description="Use to find item ID.\nSearch query can be a description or keywords."
)
execute_refund_tool = FunctionTool(execute_refund, description="")

class IssuesAndRepairsAgent(AIAgent):
    def __init__(self, 
        model_client: ChatCompletionClient, 
        delegate_tools: List[Tool],
        agent_topic_type: str,
        user_topic_type: str,) -> None:
        super().__init__(
            description="An issues and repairs agent.",
            system_message=SystemMessage(
                content="You are a customer support agent for ACME Inc."
                "Always answer in a sentence or less."
                "Follow the following routine with the user:"
                "1. First, ask probing questions and understand the user's problem deeper.\n"
                " - unless the user has already provided a reason.\n"
                "2. Propose a fix (make one up).\n"
                "3. ONLY if not satisfied, offer a refund.\n"
                "4. If accepted, search for the ID and then execute refund."
            ),
            model_client=model_client,
            tools=[
                execute_refund_tool,
                look_up_item_tool,
            ],
            delegate_tools=delegate_tools,
            agent_topic_type=agent_topic_type,
            user_topic_type=user_topic_type,
        )