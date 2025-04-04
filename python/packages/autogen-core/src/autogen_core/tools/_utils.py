from datetime import datetime

class Utils:
    @staticmethod
    def get_current_time_str() -> str:
        """
        获取当前时间的字符串表示，精确到毫秒
        格式：YYYY-MM-DD HH:MM:SS.sss
        """
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]