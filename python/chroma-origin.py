from pathlib import Path
import asyncio
from typing import Sequence
import chromadb
import json

# 获取当前脚本所在目录
SCRIPT_DIR = Path(__file__).parent.absolute()

# 初始化Chroma客户端
client = chromadb.PersistentClient(path=str(SCRIPT_DIR / ".chromadb_autogen"))
# 获取或创建一个集合
collection = client.get_or_create_collection(name="preferences")

# 添加连接Chroma数据库并写入数据的函数
async def write_to_chroma(data: Sequence[str]):
    for i in range(len(data)):
        content = "content" + str(i)
        # 写入数据
        collection.add(
            documents=[content],
            metadatas=[{"category": "history", "type": "workflow"}],
            ids=[str(i)]
        )

async def display_preferences_data():
    # 获取集合中的所有数据
    all_data = collection.get()
    print(json.dumps(all_data, indent=4, ensure_ascii=False))      

async def run_team_stream() -> None:
    # 写入Chroma数据库
    # await write_to_chroma(["111"])
    # 显示preferences集合里的所有数据
    await display_preferences_data()

asyncio.run(run_team_stream())