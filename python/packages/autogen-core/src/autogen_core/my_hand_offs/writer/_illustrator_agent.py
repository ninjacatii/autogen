import base64
from datetime import datetime
import os
from pathlib import Path
import random
from typing import Annotated, List
import aiohttp
from autogen_core import Image
from autogen_core.models import ChatCompletionClient, SystemMessage
from autogen_core.my_hand_offs import AIAgent
from autogen_core.tools import FunctionTool, Tool

async def image_gen(
    character_appearence: Annotated[str, "The physical appearance characteristics of the protagonist in the story"], 
    style_attributes: Annotated[str, "The style of the image"], 
    worn_and_carried: Annotated[str, "The protagonist's attire and the items carried with them in the story"], 
    scenario: Annotated[str, "The scenario of the image"]
) -> Image:
    if os.environ["IMAGE_GEN_FLAG"] == "DEV":
        random_num = random.randint(0, 7)  # 包含0和7

        return Image.from_file(Path(f"D:\\git\\autogen\\python\\work\\generated_images\\{random_num}.png"))
    else:
        prompt = f"Digital painting of a {character_appearence} character with {style_attributes}. Wearing {worn_and_carried}, {scenario}."
        url = f"https://image.pollinations.ai/prompt/{prompt}?width=256&height=256&enhance=true&private=true"
        data: bytes = await download_image_async(url)
        base64_encoded = base64.b64encode(data).decode("utf-8")
        response: Image = Image.from_base64(base64_encoded)

        # 保存图片到本地文件
        now: str = datetime.now().strftime("%Y%m%d%H%M%S")
        output_path = Path(f"D:\\git\\autogen\\python\\work\\generated_images\\{now}.png")
        output_path.parent.mkdir(exist_ok=True)
        response.to_file(output_path)
        Image.from_pil(response.image.resize((256, 256)))

        return response  

async def download_image_async(url: str) -> bytes:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            response.raise_for_status()
            return await response.read() 

image_gen_tool = FunctionTool(image_gen, description="Call this to generate an image. ")            

class IllustratorAgent(AIAgent):
    def __init__(self, 
        model_client: ChatCompletionClient, 
        delegate_tools: List[Tool],
        agent_topic_type: str,
        user_topic_type: str,) -> None:
        super().__init__(
            description="An illustrator for creating images.",
            system_message=SystemMessage(
                content="You are an Illustrator. You use the generate_image tool to create images given user's requirement. "
                        "Make sure the images have consistent characters and style."
                        "When your work is over, Give the user the options: 1. If satisfied, proceed to the next step. 2. If not satisfied, make revisions again."
            ),
            model_client=model_client,
            tools=[image_gen_tool],
            delegate_tools=delegate_tools,
            agent_topic_type=agent_topic_type,
            user_topic_type=user_topic_type,
        )

                 