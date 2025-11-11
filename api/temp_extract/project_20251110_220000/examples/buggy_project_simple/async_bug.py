import asyncio


async def do_work():
    # 缺少 await 的异步调用
    asyncio.sleep(0.1)  # async_missing_await: medium


