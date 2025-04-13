from typing import List
from autogen_core.models import ChatCompletionClient, SystemMessage
from autogen_core.my_hand_offs import AIAgent
from autogen_core.tools import Tool

class WriterAgent(AIAgent):
    def __init__(self, 
        model_client: ChatCompletionClient, 
        delegate_tools: List[Tool],
        agent_topic_type: str,
        user_topic_type: str,) -> None:
        super().__init__(
            description="Writer for creating any text content.",
            system_message=SystemMessage(
                content="You are a Writer. You produce good work. when your work is over, Give the user the options: 1. If satisfied, proceed to the next step. 2. If not satisfied, make revisions again.",
            ),
            model_client=model_client,
            tools=[],
            delegate_tools=delegate_tools,
            agent_topic_type=agent_topic_type,
            user_topic_type=user_topic_type,
        )