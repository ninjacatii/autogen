from pathlib import Path
import asyncio
from typing import Sequence
import uuid
from collections.abc import Mapping

from autogen_core.memory import MemoryContent, MemoryMimeType
from autogen_ext.memory.chromadb import ChromaDBVectorMemory, PersistentChromaDBVectorMemoryConfig

# 获取当前脚本所在目录
SCRIPT_DIR = Path(__file__).parent.absolute()

async def write_to_chroma(data: Sequence[str]):
    """向ChromaDB插入数据的完整示例"""
    # 初始化ChromaDB配置
    chroma_memory = ChromaDBVectorMemory(
        config=PersistentChromaDBVectorMemoryConfig(
            collection_name="user_data",  # 集合名称
            persistence_path=str(SCRIPT_DIR / ".chromadb_autogen"),  # 修改为使用当前目录
            k=20,  # 查询时返回的结果数量
            score_threshold=0.5,  # 相似度阈值
            allow_reset=True  # 允许重置数据库
        )
    )

    try:
        # 示例数据插入
        sample_data = [
            {"content": "用户喜欢蓝色", "metadata": {"category": "preference", "source": "survey"}},
            {"content": "用户常用电子邮件沟通", "metadata": {"category": "behavior", "priority": "high"}},
            {"content": "用户位于北京", "metadata": {"category": "location", "timezone": "UTC+8"}}
        ]

        # 批量插入数据
        for item in sample_data:
            if isinstance(item["metadata"], Mapping):
                await chroma_memory.add(
                    MemoryContent(
                        content=item["content"],
                        mime_type=MemoryMimeType.TEXT,
                        metadata={
                            **item["metadata"],
                            "uuid": str(uuid.uuid4())  # 添加唯一标识
                        }
                    )
                )
        print("数据插入成功")

        # 示例查询
        query_result = await chroma_memory.query("用户偏好")
        print(f"查询到 {len(query_result.results)} 条相关记录")

    finally:
        # 确保关闭连接
        await chroma_memory.close()

async def main():
    await write_to_chroma([])

if __name__ == "__main__":
    asyncio.run(main())