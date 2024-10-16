import os

import django
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from asgiref.sync import sync_to_async
from aiogram.utils.keyboard import InlineKeyboardBuilder

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'work_exchange.settings')
django.setup()

from core.models import TGUser, Text
from filters import ChatTypeFilter


router = Router()


@router.message(F.text, ChatTypeFilter(chat_type='private'))
async def worker_contact(message: Message):
    user_id = message.from_user.id

    user = await sync_to_async(TGUser.objects.filter(tg_id=user_id).first)()
    error_text = await sync_to_async(Text.objects.get)(slug='error_input')

    if user:
        if user.target == '1':
            try:
                await message.reply(text=error_text.rus,)
            except:
                pass
        elif user.target == '2':
            try:
                await message.reply(text=f'\u202B{error_text.heb}',)
            except:
                pass
    else:
        try:
            await message.reply(text=f'{error_text.rus}\n\u202B{error_text.heb}')
        except:
            pass


@router.callback_query()
async def employer_job_detail_active(callback: CallbackQuery):
    if callback.data != 'nothing':
        user_id = callback.from_user.id

        user = await sync_to_async(TGUser.objects.filter(tg_id=user_id).first)()
        keyboard_outdated = await sync_to_async(Text.objects.get)(slug='keyboard_outdated')

        if user:
            if user.target == '1':
                reply_text = keyboard_outdated.rus
            elif user.target == '2':
                reply_text = f'\u202B{keyboard_outdated.heb}'
        else:
            reply_text = f'{keyboard_outdated.rus}\n\u202B{keyboard_outdated.heb}'
        
        try:
            await callback.message.edit_text(
                text=reply_text,
                reply_markup=InlineKeyboardBuilder().as_markup(),
            )
        except:
            pass
        