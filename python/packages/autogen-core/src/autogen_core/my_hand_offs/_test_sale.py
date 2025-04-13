import asyncio
import uuid
from autogen_core import SingleThreadedAgentRuntime, TopicId, TypeSubscription
from autogen_core.models import SystemMessage
from autogen_core.my_hand_offs import HumanAgent, IssuesAndRepairsAgent, SalesAgent, TriageAgent, UserAgent, UserLogin
from autogen_core.tools import FunctionTool
from autogen_ext.models.openai import OpenAIChatCompletionClient


sales_agent_topic_type = "SalesAgent"
issues_and_repairs_agent_topic_type = "IssuesAndRepairsAgent"
triage_agent_topic_type = "TriageAgent"
human_agent_topic_type = "HumanAgent"
user_topic_type = "User"

def transfer_to_sales_agent() -> str:
    return sales_agent_topic_type


def transfer_to_issues_and_repairs() -> str:
    return issues_and_repairs_agent_topic_type


def transfer_back_to_triage() -> str:
    return triage_agent_topic_type


def escalate_to_human() -> str:
    return human_agent_topic_type


transfer_to_sales_agent_tool = FunctionTool(
    transfer_to_sales_agent, description="Use for anything sales or buying related."
)
transfer_to_issues_and_repairs_tool = FunctionTool(
    transfer_to_issues_and_repairs, description="Use for issues, repairs, or refunds."
)
transfer_back_to_triage_tool = FunctionTool(
    transfer_back_to_triage,
    description="Call this if the user brings up a topic outside of your purview,\nincluding escalating to human.",
)
escalate_to_human_tool = FunctionTool(escalate_to_human, description="Only call this if explicitly asked to.")

async def test() -> None:
    runtime = SingleThreadedAgentRuntime()

    model_client = OpenAIChatCompletionClient(
        #model="deepseek-reasoner",#不支持
        #model="deepseek-chat",#支持差
        #model="gemini-2.5-pro-preview-03-25",
        # model="qwen-coder-plus",
        model="qwen-plus",
        # model="gemini-2.0-flash",
        temperature=0,
        # api_key="YOUR_API_KEY",
    )

    # Register the triage agent.
    triage_agent_type = await TriageAgent.register(
        runtime,
        type=triage_agent_topic_type,  # Using the topic type as the agent type.
        factory=lambda: TriageAgent(
            description="A triage agent.",
            system_message=SystemMessage(
                content="You are a customer service bot for ACME Inc. "
                "Introduce yourself. Always be very brief. "
                "Gather information to direct the customer to the right department. "
                "But make your questions subtle and natural."
            ),
            model_client=model_client,
            delegate_tools=[
                transfer_to_issues_and_repairs_tool,
                transfer_to_sales_agent_tool,
                escalate_to_human_tool,
            ],
            agent_topic_type=triage_agent_topic_type,
            user_topic_type=user_topic_type,
        ),
    )
    # Add subscriptions for the triage agent: it will receive messages published to its own topic only.
    await runtime.add_subscription(TypeSubscription(topic_type=triage_agent_topic_type, agent_type=triage_agent_type.type))

    # Register the sales agent.
    sales_agent_type = await SalesAgent.register(
        runtime,
        type=sales_agent_topic_type,  # Using the topic type as the agent type.
        factory=lambda: SalesAgent(
            model_client=model_client,
            delegate_tools=[transfer_back_to_triage_tool],
            agent_topic_type=sales_agent_topic_type,
            user_topic_type=user_topic_type,
        ),
    )
    # Add subscriptions for the sales agent: it will receive messages published to its own topic only.
    await runtime.add_subscription(TypeSubscription(topic_type=sales_agent_topic_type, agent_type=sales_agent_type.type))

    # Register the issues and repairs agent.
    issues_and_repairs_agent_type = await IssuesAndRepairsAgent.register(
        runtime,
        type=issues_and_repairs_agent_topic_type,  # Using the topic type as the agent type.
        factory=lambda: IssuesAndRepairsAgent(
            model_client=model_client,
            delegate_tools=[transfer_back_to_triage_tool],
            agent_topic_type=issues_and_repairs_agent_topic_type,
            user_topic_type=user_topic_type,
        ),
    )
    # Add subscriptions for the issues and repairs agent: it will receive messages published to its own topic only.
    await runtime.add_subscription(
        TypeSubscription(topic_type=issues_and_repairs_agent_topic_type, agent_type=issues_and_repairs_agent_type.type)
    )

    # Register the human agent.
    human_agent_type = await HumanAgent.register(
        runtime,
        type=human_agent_topic_type,  # Using the topic type as the agent type.
        factory=lambda: HumanAgent(
            description="A human agent.",
            agent_topic_type=human_agent_topic_type,
            user_topic_type=user_topic_type,
        ),
    )
    # Add subscriptions for the human agent: it will receive messages published to its own topic only.
    await runtime.add_subscription(TypeSubscription(topic_type=human_agent_topic_type, agent_type=human_agent_type.type))

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