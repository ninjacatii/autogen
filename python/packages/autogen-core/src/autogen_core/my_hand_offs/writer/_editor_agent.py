from typing import List
from autogen_core.models import ChatCompletionClient, SystemMessage
from autogen_core.my_hand_offs import AIAgent
from autogen_core.tools import Tool

class EditorAgent(AIAgent):
    def __init__(self, 
        model_client: ChatCompletionClient, 
        delegate_tools: List[Tool],
        agent_topic_type: str,
        user_topic_type: str,) -> None:
        super().__init__(
            description="Editor for planning and reviewing the content.",
            system_message=SystemMessage(
                content="You are an Editor. Plan and guide the task given by the user. Provide critical feedbacks to the draft and illustration produced by Writer and Illustrator. "
                        "Your task is to plan and guide the task given by the user or provide critical feedbacks."
                        "Approve if the task is completed and the draft and illustration meets user's requirements and ouput all the draft and illustration completely in Markdown format.",
            ),
            model_client=model_client,
            tools=[],
            delegate_tools=delegate_tools,
            agent_topic_type=agent_topic_type,
            user_topic_type=user_topic_type,
        )