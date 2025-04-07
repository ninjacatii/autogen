import asyncio
import json
import random

from autogen_core import CancellationToken
from autogen_core.tools import FunctionTool
from typing_extensions import Annotated


async def get_stock_price(ticker: str, date: Annotated[str, "Date in YYYY/MM/DD"]) -> float:
    # Returns a random stock price for demonstration purposes.
    return random.uniform(10, 200)

async def my_test():
    # Create a function tool.
    stock_price_tool = FunctionTool(get_stock_price, description="Get the stock price.")

    # Run the tool.
    cancellation_token = CancellationToken()
    result = await stock_price_tool.run_json({"ticker": "AAPL", "date": "2021/01/01"}, cancellation_token)

    # Print the result.
    print("\nresult:" + stock_price_tool.return_value_as_string(result))

    data = stock_price_tool.schema
    # 格式化输出
    formatted_json = json.dumps(data, indent=4, ensure_ascii=False)
    print("\n" + formatted_json)

asyncio.run(my_test())