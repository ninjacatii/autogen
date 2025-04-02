import os
from pathlib import Path

import asyncio
from typing import Sequence

from autogen_core.memory import MemoryContent, MemoryMimeType
from autogen_ext.memory.chromadb import ChromaDBVectorMemory, PersistentChromaDBVectorMemoryConfig

# 添加连接Chroma数据库并写入数据的函数
async def write_to_chroma(data: Sequence[str]):
    # Initialize ChromaDB memory with custom config
    chroma_user_memory = ChromaDBVectorMemory(
        config=PersistentChromaDBVectorMemoryConfig(
            collection_name="preferences",
            persistence_path=os.path.join(str(Path.home()), ".chromadb_autogen"),
            k=2,  # Return top  k results
            score_threshold=0.4,  # Minimum similarity score
        )
    )

    for i in range(len(data)):
        await chroma_user_memory.add(
            MemoryContent(
                # Bug修复：将整数类型转换为字符串类型，以支持字符串拼接操作
                content="content" + str(i),
                mime_type=MemoryMimeType.TEXT,
                metadata={"category": "history", "type": "workflow"},
            )
        )
    await chroma_user_memory.close()

async def run_team_stream() -> None:
    # 写入Chroma数据库
    await write_to_chroma(["111"])

asyncio.run(run_team_stream())