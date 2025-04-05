from datetime import datetime
from pathlib import Path
import asyncio
from typing import Sequence
import chromadb
from autogen_core.tools import Utils
from chromadb.api.types import GetResult

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
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # 获取当前时间字符串
        # 写入数据
        collection.add(
            documents=[content],
            metadatas=[{"category": "history", "type": "workflow", "timestamp": current_time}],
            ids=[str(i)]
        )

async def upsert_to_chroma(personal_info_type: str, personal_info_data: str):
    # 使用upsert方法
    collection.upsert(
        documents=[personal_info_data],
        metadatas=[{"category": "user", "type": personal_info_type, "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}],
        ids=["user:" + personal_info_type]
    )
    await Utils.display_preferences_data(path=str(SCRIPT_DIR / ".chromadb_autogen"))


async def delete_preferences_data(ids: chromadb.IDs):
    """删除指定ID的记录"""
    collection.delete(ids=ids)
    print(f"已删除ID为 {ids} 的记录")

 

async def delete_all_preferences_data():
    """删除集合中的所有记录"""
    all_data = collection.get()
    if all_data['ids']:
        collection.delete(ids=all_data['ids'])
        print("已删除所有记录")
    else:
        print("集合中无记录可删除")    

async def query_by_type(type_value: str, limit: int = 1) -> str | None:
    """根据metadata中的type字段查询记录"""
    results: GetResult = collection.get(
        where={"type": type_value},  # 查询条件
        limit=limit,  # 返回结果数量限制
        include=["documents", "metadatas"]  # 包含文档内容和元数据
    )
    if results['documents'] is not None and len(results['documents']) > 0:
        return results['documents'][0]
    return None

async def run_team_stream() -> None:
    # await delete_all_preferences_data()

    # 写入Chroma数据库
    #await upsert_to_chroma(["111"])
    # await delete_preferences_data(["user:ID Card No."])
    result: str | None = await query_by_type("ID Card No.")
    if result is not None:
        print("\n1:" + result)
    else:
        print("\n1:No result found")

    await Utils.display_preferences_data(path=str(SCRIPT_DIR / ".chromadb_autogen"))

asyncio.run(run_team_stream())