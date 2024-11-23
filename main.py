from utils import *

CONFIG_PATH = ""
CONFIG_FILE = "config.json"
MAX_RETRY = 1

async def main():
    with open(CONFIG_PATH + CONFIG_FILE, 'r', encoding='utf-8') as f:
        config = json.load(f)
    task_queue = asyncio.Queue(maxsize=MAX_RETRY)
    tasks = []
    for item in config["streams"]:
        platform_name = item['platform'].capitalize()
        platform_class = globals().get(platform_name)
        if platform_class is None:
            raise ValueError(f"Unknown platform: {platform_name}")
        relay = platform_class(config, item, task_queue)
        tasks.append(asyncio.create_task(relay.start()))
        await asyncio.sleep(5)
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())