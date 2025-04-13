from typing import List
from autogen_core.models import ChatCompletionClient, SystemMessage
from autogen_core.my_hand_offs import AIAgent
from autogen_core.tools import FunctionTool, Tool

def execute_order(product: str, price: int) -> str:
    print("\n\n=== Order Summary ===")
    print(f"Product: {product}")
    print(f"Price: ${price}")
    print("=================\n")
    confirm = input("Confirm order? y/n: ").strip().lower()
    if confirm == "y":
        print("Order execution successful!")
        return "Success"
    else:
        print("Order cancelled!")
        return "User cancelled order."
execute_order_tool = FunctionTool(execute_order, description="Price should be in USD.")

class SalesAgent(AIAgent):
    def __init__(self, 
        model_client: ChatCompletionClient, 
        delegate_tools: List[Tool],
        agent_topic_type: str,
        user_topic_type: str,) -> None:
        super().__init__(
            description="A sales agent.",
            system_message=SystemMessage(
                content="You are a sales agent for ACME Inc."
                "Always answer in a sentence or less."
                "Follow the following routine with the user:"
                "1. Ask them about any problems in their life related to catching roadrunners.\n"
                "2. Casually mention one of ACME's crazy made-up products can help.\n"
                " - Don't mention price.\n"
                "3. Once the user is bought in, drop a ridiculous price.\n"
                "4. Only after everything, and if the user says yes, "
                "tell them a crazy caveat and execute their order.\n"
                ""
            ),
            model_client=model_client,
            tools=[execute_order_tool],
            delegate_tools=delegate_tools,
            agent_topic_type=agent_topic_type,
            user_topic_type=user_topic_type,
        )