from autogen_core.models import ChatCompletionClient
from autogen_core.my_group_chat import BaseGroupChatAgent

class EditorAgent(BaseGroupChatAgent):
    def __init__(self, description: str, group_chat_topic_type: str, model_client: ChatCompletionClient) -> None:
        super().__init__(
            description=description,
            group_chat_topic_type=group_chat_topic_type,
            model_client=model_client,
            system_message="You are an Editor. Plan and guide the task given by the user. Provide critical feedbacks to the draft and illustration produced by Writer and Illustrator. "
            "Your task is to plan and guide the task given by the user or provide critical feedbacks."
            "Approve if the task is completed and the draft and illustration meets user's requirements and ouput all the draft and illustration completely in Markdown format.",
        )