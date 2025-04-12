import base64
from datetime import datetime
import json
from pathlib import Path
from typing import List
from autogen_core import DefaultTopicId, FunctionCall, Image, message_handler
from autogen_core.models import ChatCompletionClient, UserMessage
from autogen_core.my_group_chat import BaseGroupChatAgent, GroupChatMessage, RequestToSpeak
from autogen_core.tools import FunctionTool
import aiohttp
from rich.console import Console
from rich.markdown import Markdown
from autogen_core import MessageContext

class IllustratorAgent(BaseGroupChatAgent):
    def __init__(
        self,
        description: str,
        group_chat_topic_type: str,
        model_client: ChatCompletionClient,
    ) -> None:
        super().__init__(
            description=description,
            group_chat_topic_type=group_chat_topic_type,
            model_client=model_client,
            system_message="You are an Illustrator. You use the generate_image tool to create images given user's requirement. "
            "Make sure the images have consistent characters and style.",
        )
        self._image_gen_tool = FunctionTool(
            self._image_gen, name="generate_image", description="Call this to generate an image. "
        )

    async def _download_image_async(self, url: str) -> bytes:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                response.raise_for_status()
                return await response.read()

    async def _image_gen(
        self, character_appearence: str, style_attributes: str, worn_and_carried: str, scenario: str
    ) -> Image:
        prompt = f"Digital painting of a {character_appearence} character with {style_attributes}. Wearing {worn_and_carried}, {scenario}."
        url = f"https://image.pollinations.ai/prompt/{prompt}?width=256&height=256&enhance=true&private=true"
        data: bytes = await self._download_image_async(url)
        base64_encoded = base64.b64encode(data).decode("utf-8")
        response: Image = Image.from_base64(base64_encoded)

        # 保存图片到本地文件
        now: str = datetime.now().strftime("%Y%m%d%H%M%S")
        output_path = Path(__file__).parent / "generated_images" / f"{now}.png"
        output_path.parent.mkdir(exist_ok=True)
        response.to_file(output_path)

        return response

    @message_handler
    async def handle_request_to_speak(self, message: RequestToSpeak, ctx: MessageContext) -> None:  # type: ignore
        Console().print(Markdown(f"### {self.id.type}: "))
        self._chat_history.append(
            UserMessage(content=f"Transferred to {self.id.type}, adopt the persona immediately.", source="system")
        )
        # Ensure that the image generation tool is used.
        completion = await self._model_client.create(
            [self._system_message] + self._chat_history,
            tools=[self._image_gen_tool],
            extra_create_args={"tool_choice": "required"},
            cancellation_token=ctx.cancellation_token,
        )
        assert isinstance(completion.content, list) and all(
            isinstance(item, FunctionCall) for item in completion.content
        )
        images: List[str | Image] = []
        for tool_call in completion.content:
            arguments = json.loads(tool_call.arguments)
            Console().print(arguments)
            result = await self._image_gen_tool.run_json(arguments, ctx.cancellation_token)
            assert isinstance(result, Image)
            image = result
            # image = Image.from_base64(self._image_gen_tool.return_value_as_string(result))
            image = Image.from_pil(image.image.resize((256, 256)))
            images.append(image)
        await self.publish_message(
            GroupChatMessage(body=UserMessage(content=images, source=self.id.type)),
            DefaultTopicId(type=self._group_chat_topic_type),
        )