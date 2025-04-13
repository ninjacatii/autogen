from typing import List
from autogen_core.models import ChatCompletionClient, SystemMessage
from autogen_core.my_hand_offs import AIAgent
from autogen_core.tools import Tool


class TriageAgent(AIAgent):
    def __init__(self, 
        description: str, 
        system_message: SystemMessage, 
        model_client: ChatCompletionClient, 
        delegate_tools: List[Tool],
        agent_topic_type: str,
        user_topic_type: str,) -> None:
        super().__init__(
            description=description,
            system_message=system_message,
            model_client=model_client,
            tools=[],
            delegate_tools=delegate_tools,
            agent_topic_type=agent_topic_type,
            user_topic_type=user_topic_type,
        )