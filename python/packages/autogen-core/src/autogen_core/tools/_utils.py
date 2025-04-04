from datetime import datetime
import chromadb
import json

class Utils:
    @staticmethod
    def get_current_time_str() -> str:
        """
        获取当前时间的字符串表示，精确到毫秒
        格式：YYYY-MM-DD HH:MM:SS.sss
        """
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

    @staticmethod
    async def display_preferences_data(path: str, name: str = "preferences") -> None:
        # 初始化Chroma客户端
        client = chromadb.PersistentClient(path=path)
        # 获取或创建一个集合
        collection = client.get_or_create_collection(name=name)
        all_data = collection.get()
        # 写入JSON文件
        json_path = path + ".json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(all_data, f, indent=4, ensure_ascii=False)
        print(f"数据已写入: {json_path}") 