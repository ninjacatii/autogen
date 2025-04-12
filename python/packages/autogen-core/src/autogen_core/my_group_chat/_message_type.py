from autogen_core.models import UserMessage
from pydantic import BaseModel


class GroupChatMessage(BaseModel):
    body: UserMessage

class RequestToSpeak(BaseModel):
    pass