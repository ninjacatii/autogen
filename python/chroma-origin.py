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

async def delete_preferences_data(ids: chromadb.IDs):
    """删除指定ID的记录"""
    collection.delete(ids=ids)
    print(f"已删除ID为 {ids} 的记录")

async def display_preferences_data():
    # 获取集合中的所有数据
    all_data = collection.get()
    # 写入JSON文件
    json_path = SCRIPT_DIR / "chroma-origin.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, indent=4, ensure_ascii=False)
    print(f"数据已写入: {json_path}")  

async def delete_all_preferences_data():
    """删除集合中的所有记录"""
    all_data = collection.get()
    if all_data['ids']:
        collection.delete(ids=all_data['ids'])
        print("已删除所有记录")
    else:
        print("集合中无记录可删除")       

async def run_team_stream() -> None:
    await delete_all_preferences_data()

    # 写入Chroma数据库
    # await write_to_chroma(["111"])
    # 显示preferences集合里的所有数据
    await display_preferences_data()

asyncio.run(run_team_stream())