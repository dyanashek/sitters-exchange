import os
from typing import Any, Awaitable, Callable, Dict

import django
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from asgiref.sync import sync_to_async

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'work_exchange.settings')
django.setup()

from core.models import TGUser, Worker, Employer


class UpdateUsernameMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
        *args,
        **kwargs
    ):
        user_id = data["event_from_user"].id
        username = data["event_from_user"].username

        if username:
            user = await sync_to_async(TGUser.objects.filter(tg_id=user_id).first)()
            if user:
                if user.target == '1':
                    worker = await sync_to_async(Worker.objects.filter(tg_id=user_id).first)()
                    if worker and (worker.username is None or worker.username != username):
                        worker.username = username
                        await sync_to_async(worker.save)()
                
                elif user.target == '2':
                    employer = await sync_to_async(Employer.objects.filter(tg_id=user_id).first)()
                    if employer and (employer.username is None or employer.username != username):
                        employer.username = username
                        await sync_to_async(employer.save)()

        return await handler(event, data)
