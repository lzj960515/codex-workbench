import asyncio
from engine import ReportConfig, ReportEngine


async def main():
    entered = asyncio.Event()
    release = asyncio.Event()
    calls = 0

    async def renderer(template):
        nonlocal calls
        calls += 1
        if calls == 1:
            entered.set()
            await release.wait()
        else:
            release.set()
        return template

    engine = ReportEngine(ReportConfig("monthly"), renderer)
    first = asyncio.create_task(engine.render("request-a"))
    await entered.wait()
    second = asyncio.create_task(engine.render("request-b"))
    print(await first, await second)


if __name__ == "__main__":
    asyncio.run(main())
