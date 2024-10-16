import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import Redis, RedisStorage

import config
from handlers import (
    commands,
    profile,
    admin_controls,

    worker_profile,
    worker_profile_controls,
    worker_back_controls,
    worker_main_sections,
    worker_pages,
    worker_details,

    employer_profile,
    employer_profile_controls,
    employer_back_controls,
    employer_main_sections,
    employer_job,
    employer_pages,
    employer_details,

    error,
)


async def main() -> None:
    redis = Redis(
        host=config.REDIS_HOST,
        port=config.REDIS_PORT,
        db=config.REDIS_DB,
        decode_responses=True,
    )

    storage = RedisStorage(redis=redis, state_ttl=3600 * 24)

    bot = Bot(token=config.TELEGRAM_TOKEN)
    dp = Dispatcher(storage=storage)

    dp.include_router(commands.router)
    dp.include_router(profile.router)
    dp.include_router(admin_controls.router)
    dp.include_router(worker_profile.router)
    dp.include_router(worker_profile_controls.router)
    dp.include_router(worker_profile_controls.cv_router)
    dp.include_router(worker_back_controls.router)
    dp.include_router(worker_main_sections.router)
    dp.include_router(worker_main_sections.profile_router)
    dp.include_router(worker_pages.router)
    dp.include_router(worker_details.router)
    dp.include_router(employer_profile.router)
    dp.include_router(employer_profile_controls.router)
    dp.include_router(employer_back_controls.router)
    dp.include_router(employer_main_sections.router)
    dp.include_router(employer_job.router)
    dp.include_router(employer_pages.router)
    dp.include_router(employer_details.router)
    dp.include_router(error.router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
