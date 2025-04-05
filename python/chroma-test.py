from pathlib import Path

import asyncio
from datetime import datetime
from autogen_core.tools import Utils
from autogen_core.memory import MemoryContent, MemoryMimeType
from autogen_ext.memory.chromadb import ChromaDBVectorMemory, PersistentChromaDBVectorMemoryConfig

# 获取当前脚本所在目录
SCRIPT_DIR = Path(__file__).parent.absolute()

# 添加连接Chroma数据库并写入数据的函数
async def write_to_chroma(type: str, data: str):
    # Initialize ChromaDB memory with custom config
    chroma_user_memory = ChromaDBVectorMemory(
        config=PersistentChromaDBVectorMemoryConfig(
            collection_name="preferences",
            persistence_path=str(SCRIPT_DIR / ".chromadb_autogen"),  # 修改为使用当前目录
            k=2,  # Return top  k results
            score_threshold=0.4,  # Minimum similarity score
        )
    )

    await chroma_user_memory.add(
        MemoryContent(
            content=data,
            mime_type=MemoryMimeType.TEXT,
            metadata={"category": "user", "type": type, "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")},
        ), overwrite=True
    )

    await chroma_user_memory.close()

async def run_team_stream() -> None:
    # 写入Chroma数据库
    # await write_to_chroma("idcard", "333444555")

    await Utils.display_preferences_data(path=str(SCRIPT_DIR / ".chromadb_autogen"))

asyncio.run(run_team_stream())