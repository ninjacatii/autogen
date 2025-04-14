import asyncio
import uuid
from autogen_core import SingleThreadedAgentRuntime, TopicId, TypeSubscription
from autogen_core.models import SystemMessage
from autogen_core.my_hand_offs import TriageAgent, UserAgent, UserLogin
from autogen_core.my_hand_offs.writer import IllustratorAgent, WriterAgent
from autogen_core.tools import FunctionTool
from autogen_ext.models.openai import OpenAIChatCompletionClient


editor_agent_topic_type = "EditorAgent"
writer_agent_topic_type = "WriterAgent"
illustrator_agent_topic_type = "IllustratorAgent"
triage_agent_topic_type = "TriageAgent"
user_topic_type = "User"

# def transfer_to_editor_agent() -> str:
#     return editor_agent_topic_type

def transfer_to_writer_agent() -> str:
    return writer_agent_topic_type

def transfer_to_illustrator_agent() -> str:
    return illustrator_agent_topic_type

def transfer_back_to_triage() -> str:
    return triage_agent_topic_type

# transfer_to_editor_agent_tool = FunctionTool(
#     transfer_to_editor_agent, description="Use for plan and guide the task given by the user."
# )
transfer_to_writer_agent_tool = FunctionTool(
    transfer_to_writer_agent, description="Use for write for creating any text content."
)
transfer_to_illustrator_agent_tool = FunctionTool(
    transfer_to_illustrator_agent, description="Use for create images for user's requirements."
)
transfer_back_to_triage_tool = FunctionTool(
    transfer_back_to_triage,
    description="Call this if the agent finished the task.",
)

async def test() -> None:
    runtime = SingleThreadedAgentRuntime()

    model_client = OpenAIChatCompletionClient(
        #model="deepseek-reasoner",#不支持
        # model="deepseek-chat",#支持差
        model="gemini-2.5-pro-exp-03-25",
        # model="qwen-coder-plus",
        # model="qwen-plus",
        # model="gemini-2.0-flash",
        temperature=0,
        # api_key="YOUR_API_KEY",
    )

    # Register the triage agent.
    triage_agent_type = await TriageAgent.register(
        runtime,
        type=triage_agent_topic_type,  # Using the topic type as the agent type.
        factory=lambda: TriageAgent(
            description="A organizer agent.",
            system_message=SystemMessage(
                content="You are a organizer."
                "First, you give the request to the writer for writing."
                "Second, When the writer finished writing, you give the writing result to the illustrator for creating image."
                "Last, you out the writing content and images by markdown format."
            ),
            model_client=model_client,
            delegate_tools=[
                # transfer_to_editor_agent_tool,
                transfer_to_writer_agent_tool,
                transfer_to_illustrator_agent_tool,
            ],
            agent_topic_type=triage_agent_topic_type,
            user_topic_type=user_topic_type,
        ),
    )
    # Add subscriptions for the triage agent: it will receive messages published to its own topic only.
    await runtime.add_subscription(TypeSubscription(topic_type=triage_agent_topic_type, agent_type=triage_agent_type.type))

    # editor_agent_type = await EditorAgent.register(
    #     runtime,
    #     type=editor_agent_topic_type,  # Using the topic type as the agent type.
    #     factory=lambda: EditorAgent(
    #         model_client=model_client,
    #         delegate_tools=[transfer_back_to_triage_tool],
    #         agent_topic_type=editor_agent_topic_type,
    #         user_topic_type=user_topic_type,
    #     ),
    # )
    # # Add subscriptions for the sales agent: it will receive messages published to its own topic only.
    # await runtime.add_subscription(TypeSubscription(topic_type=editor_agent_topic_type, agent_type=editor_agent_type.type))

    writer_agent_type = await WriterAgent.register(
        runtime,
        type=writer_agent_topic_type,  # Using the topic type as the agent type.
        factory=lambda: WriterAgent(
            model_client=model_client,
            delegate_tools=[transfer_back_to_triage_tool],
            agent_topic_type=writer_agent_topic_type,
            user_topic_type=user_topic_type,
        ),
    )
    # Add subscriptions for the sales agent: it will receive messages published to its own topic only.
    await runtime.add_subscription(TypeSubscription(topic_type=writer_agent_topic_type, agent_type=writer_agent_type.type))

    illustrator_agent_type = await IllustratorAgent.register(
        runtime,
        type=illustrator_agent_topic_type,  # Using the topic type as the agent type.
        factory=lambda: IllustratorAgent(
            model_client=model_client,
            delegate_tools=[transfer_back_to_triage_tool],
            agent_topic_type=illustrator_agent_topic_type,
            user_topic_type=user_topic_type,
        ),
    )
    # Add subscriptions for the sales agent: it will receive messages published to its own topic only.
    await runtime.add_subscription(TypeSubscription(topic_type=illustrator_agent_topic_type, agent_type=illustrator_agent_type.type))

    # Register the user agent.
    user_agent_type = await UserAgent.register(
        runtime,
        type=user_topic_type,
        factory=lambda: UserAgent(
            description="A user agent.",
            user_topic_type=user_topic_type,
            agent_topic_type=triage_agent_topic_type,  # Start with the triage agent.
        ),
    )
    # Add subscriptions for the user agent: it will receive messages published to its own topic only.
    await runtime.add_subscription(TypeSubscription(topic_type=user_topic_type, agent_type=user_agent_type.type))

    # Start the runtime.
    runtime.start()

    # Create a new session for the user.
    session_id = str(uuid.uuid4())
    await runtime.publish_message(UserLogin(), topic_id=TopicId(user_topic_type, source=session_id))

    # Run until completion.
    await runtime.stop_when_idle()
    await model_client.close()

asyncio.run(test()) 