import asyncio
import uuid
from autogen_core import SingleThreadedAgentRuntime, TopicId, TypeSubscription
from autogen_core.models import UserMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_core.my_group_chat import GroupChatMessage, EditorAgent, WriterAgent, UserAgent, GroupChatManager, IllustratorAgent

async def test() -> None:
    runtime = SingleThreadedAgentRuntime()

    editor_topic_type = "Editor"
    writer_topic_type = "Writer"
    illustrator_topic_type = "Illustrator"
    user_topic_type = "User"
    group_chat_topic_type = "group_chat"

    editor_description = "Editor for planning and reviewing the content."
    writer_description = "Writer for creating any text content."
    user_description = "User for providing final approval."
    illustrator_description = "An illustrator for creating images."

    model_client = OpenAIChatCompletionClient(
        #model="deepseek-reasoner",#不支持
        model="deepseek-chat",#支持差
        # model="qwen-coder-plus",
        #  model="qwen-plus",
        # model="gemini-2.0-flash",
        temperature=0,
        # api_key="YOUR_API_KEY",
    )

    editor_agent_type = await EditorAgent.register(
        runtime,
        editor_topic_type,  # Using topic type as the agent type.
        lambda: EditorAgent(
            description=editor_description,
            group_chat_topic_type=group_chat_topic_type,
            model_client=model_client,
        ),
    )
    await runtime.add_subscription(TypeSubscription(topic_type=editor_topic_type, agent_type=editor_agent_type.type))
    await runtime.add_subscription(TypeSubscription(topic_type=group_chat_topic_type, agent_type=editor_agent_type.type))

    writer_agent_type = await WriterAgent.register(
        runtime,
        writer_topic_type,  # Using topic type as the agent type.
        lambda: WriterAgent(
            description=writer_description,
            group_chat_topic_type=group_chat_topic_type,
            model_client=model_client,
        ),
    )
    await runtime.add_subscription(TypeSubscription(topic_type=writer_topic_type, agent_type=writer_agent_type.type))
    await runtime.add_subscription(TypeSubscription(topic_type=group_chat_topic_type, agent_type=writer_agent_type.type))

    illustrator_agent_type = await IllustratorAgent.register(
        runtime,
        illustrator_topic_type,
        lambda: IllustratorAgent(
            description=illustrator_description,
            group_chat_topic_type=group_chat_topic_type,
            model_client=model_client,
        ),
    )
    await runtime.add_subscription(
        TypeSubscription(topic_type=illustrator_topic_type, agent_type=illustrator_agent_type.type)
    )
    await runtime.add_subscription(
        TypeSubscription(topic_type=group_chat_topic_type, agent_type=illustrator_agent_type.type)
    )

    user_agent_type = await UserAgent.register(
        runtime,
        user_topic_type,
        lambda: UserAgent(description=user_description, group_chat_topic_type=group_chat_topic_type),
    )
    await runtime.add_subscription(TypeSubscription(topic_type=user_topic_type, agent_type=user_agent_type.type))
    await runtime.add_subscription(TypeSubscription(topic_type=group_chat_topic_type, agent_type=user_agent_type.type))

    group_chat_manager_type = await GroupChatManager.register(
        runtime,
        "group_chat_manager",
        lambda: GroupChatManager(
            participant_topic_types=[writer_topic_type, illustrator_topic_type, editor_topic_type, user_topic_type],
            model_client=model_client,
            participant_descriptions=[writer_description, illustrator_description, editor_description, user_description],
        ),
    )
    await runtime.add_subscription(
        TypeSubscription(topic_type=group_chat_topic_type, agent_type=group_chat_manager_type.type)
    )

    runtime.start()
    session_id = str(uuid.uuid4())
    await runtime.publish_message(
        GroupChatMessage(
            body=UserMessage(
                content="请写一个关于大熊猫宝宝的短篇故事，字数限制在200字以内，并配上三幅卡通风格的插图。",
                # content="Please write a short story about the gingerbread man with up to 3 photo-realistic illustrations.",
                source="User",
            )
        ),
        TopicId(type=group_chat_topic_type, source=session_id),
    )
    await runtime.stop_when_idle()
    await model_client.close()

asyncio.run(test()) 