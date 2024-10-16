import os
from typing import Any, Awaitable, Callable, Dict

import django
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from asgiref.sync import sync_to_async

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'work_exchange.settings')
django.setup()

from core.models import Worker, Text


class IsActiveProfileMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
        *args,
        **kwargs
    ):
        user_id = data["event_from_user"].id

        worker = await sync_to_async(Worker.objects.filter(tg_id=user_id).first)()
        if worker:
            if worker.is_approved is None:
                reply_text = await sync_to_async(Text.objects.get)(slug='worker_wait_check')
                try:
                    await event.bot.answer_callback_query(
                        callback_query_id=event.id,
                        text=reply_text.rus,
                        show_alert=True,
                        )
                except:
                    pass
                return True

            elif worker.is_approved is False:
                reply_text = await sync_to_async(Text.objects.get)(slug='worker_check_failed')
                try:
                    await event.bot.answer_callback_query(
                        callback_query_id=event.id,
                        text=reply_text.rus,
                        show_alert=True,
                        )
                except:
                    pass
                return True

        else:
            reply_text = await sync_to_async(Text.objects.get)(slug='worker_profile_error')
            try:
                await event.bot.answer_callback_query(
                    callback_query_id=event.id,
                    text=reply_text.rus,
                    show_alert=True,
                    )
            except:
                pass
            return True

        return await handler(event, data)


class IsReviewedByAdminsMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
        *args,
        **kwargs
    ):
        user_id = data["event_from_user"].id

        worker = await sync_to_async(Worker.objects.filter(tg_id=user_id).first)()
        if worker:
            if worker.is_approved is None:
                reply_text = await sync_to_async(Text.objects.get)(slug='worker_wait_check')
                try:
                    await event.bot.answer_callback_query(
                        callback_query_id=event.id,
                        text=reply_text.rus,
                        show_alert=True,
                        )
                except:
                    pass
                return True

        else:
            reply_text = await sync_to_async(Text.objects.get)(slug='worker_profile_error')
            await event.bot.answer_callback_query(
                callback_query_id=event.id,
                text=reply_text.rus,
                show_alert=True,
                )
            return True

        return await handler(event, data)
        