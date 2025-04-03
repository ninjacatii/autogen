from pathlib import Path
import asyncio
from typing import Any, List
import uuid
from collections.abc import Mapping

from autogen_core.memory import MemoryContent, MemoryMimeType
from autogen_ext.memory.chromadb import ChromaDBVectorMemory, PersistentChromaDBVectorMemoryConfig

SCRIPT_DIR = Path(__file__).parent.absolute()

class ChromaCRUD:
    def __init__(self):
        self.chroma_memory = ChromaDBVectorMemory(
            config=PersistentChromaDBVectorMemoryConfig(
                collection_name="preferences",
                persistence_path=str(SCRIPT_DIR / ".chromadb_autogen"),
                k=10,
                score_threshold=0.5,
                allow_reset=True
            )
        )

    async def add_item(self, content: str, metadata: dict[str, str]) -> str:
        """添加数据到preferences集合"""
        item_id = str(uuid.uuid4())
        await self.chroma_memory.add(
            MemoryContent(
                content=content,
                mime_type=MemoryMimeType.TEXT,
                metadata={
                    **metadata,
                    "id": item_id
                }
            )
        )
        return item_id

    def convert_to_mapping(self, data: dict[Any, Any] | None) -> Mapping[str, str]:
        if data is None:
            return {}
        else:
            return {str(key): str(value) for key, value in data}

    async def query_items(self, query_text: str, n_results: int = 5) -> List[dict[str, str | float | Mapping[str, str]]]:
        """查询preferences集合中的数据"""
        query_result = await self.chroma_memory.query(query_text)
        result : List[dict[str, str | float | Mapping[str, str]]] = []
        for item in query_result.results[:n_results]:
            result.append({
                # 强制将 content 转换为字符串类型以解决类型不兼容问题
                "content": str(item.content),
                # 修改形参类型注解以匹配传入的参数类型
                "metadata": self.convert_to_mapping(item.metadata if isinstance(item.metadata, dict) else None),
                # 假设 score 是查询结果的相似度分数，确保其类型为 float
                "score": float(getattr(item, 'score', 0.0))
            })
        return result

    async def update_item(self, item_id: str, new_content: str, new_metadata: dict[str, str]) -> bool:
        """更新preferences集合中的数据"""
        # ChromaDB更新需要先删除再添加
        await self.delete_item(item_id)
        await self.add_item(new_content, {**new_metadata, "id": item_id})
        return True

    async def delete_item(self, item_id: str) -> bool:
        """从preferences集合中删除数据"""
        # ChromaDB没有直接更新API，需要通过metadata过滤删除
        items : List[dict[str, str | float | Mapping[str, str]]] = await self.query_items("")  # 查询所有
        for item in items:
            # 检查 "metadata" 是否为 Mapping 类型
            if isinstance(item["metadata"], Mapping) and type(item["metadata"].get("id")) == str and item["metadata"].get("id") == item_id:
                await self.chroma_memory.delete(item_id)
                return True
        return False

    async def close(self):
        """关闭连接"""
        await self.chroma_memory.close()

    async def query_all_items(self) -> List[dict[str, str | float | Mapping[str, str]]]:
        """查询preferences集合中的所有数据"""
        return await self.query_items("")        

async def main():
    crud = ChromaCRUD()
    
    try:

        # 添加示例数据
        print("添加数据...")
        item_id = await crud.add_item(
            "用户喜欢蓝色",
            {"category": "color", "priority": "high"}
        )
        print(f"添加成功，ID: {item_id}")

        # 查询所有数据
        print("\n查询所有数据...")
        all_results = await crud.query_all_items()
        for result in all_results:
            print(f"内容: {result['content']}, 分数: {result['score']:.2f}")

        # # 查询数据
        # print("\n查询数据...")
        # results = await crud.query_items("颜色偏好")
        # for result in results:
        #     print(f"内容: {result['content']}, 分数: {result['score']:.2f}")

        # # 更新数据
        # print("\n更新数据...")
        # updated = await crud.update_item(
        #     item_id,
        #     "用户最喜欢蓝色",
        #     {"category": "color", "priority": "very high"}
        # )
        # print(f"更新{'成功' if updated else '失败'}")

        # # 删除数据
        # print("\n删除数据...")
        # deleted = await crud.delete_item(item_id)
        # print(f"删除{'成功' if deleted else '失败'}")

    finally:
        await crud.close()

if __name__ == "__main__":
    asyncio.run(main())