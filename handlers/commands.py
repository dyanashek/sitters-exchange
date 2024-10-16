import os

import django
from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from asgiref.sync import sync_to_async
from aiogram.fsm.context import FSMContext

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'work_exchange.settings')
django.setup()

from middlewares.change_username import UpdateUsernameMiddleware
from core.models import TGUser, Worker, Employer, Text
from keyboards import keyboards
from filters import ChatTypeFilter


router = Router()
router.message.middleware(UpdateUsernameMiddleware())


@router.message(ChatTypeFilter(chat_type='private'), CommandStart())
async def process_start_command(message: Message, state: FSMContext):
    await state.clear()
    user_id = message.from_user.id
    user = await sync_to_async(TGUser.objects.filter(tg_id=user_id).first)()
    if user:
        if user.target == '1':
            worker = await sync_to_async(Worker.objects.filter(tg_id=user_id).first)()
            if worker:
                choose_menu_section = await sync_to_async(Text.objects.get)(slug='choose_menu_section')

                try:
                    await message.answer(
                        text=choose_menu_section.rus,
                        reply_markup=await keyboards.worker_main_menu(),
                    )
                except:
                    pass

                return True

        elif user.target == '2':
            employer = await sync_to_async(Employer.objects.filter(tg_id=user_id).first)()
            if employer:
                choose_menu_section = await sync_to_async(Text.objects.get)(slug='choose_menu_section')

                try:
                    await message.answer(
                        text=f'\u202B{choose_menu_section.heb}',
                        reply_markup=await keyboards.employer_main_menu(),
                    )
                except:
                    pass

                return True

    choose_option_text = await sync_to_async(Text.objects.get)(slug='choose_option')
    reply_text=f'{choose_option_text.rus}\n\u202B{choose_option_text.heb}\u202C'
    try:
        await message.answer(
            text=reply_text,
            reply_markup=await keyboards.choose_target_keyboard(),
            )
    except:
        pass


@router.message(F.text, ChatTypeFilter(chat_type='private'), Command('cancel'))
async def process_cancel_command(message: Message, state: FSMContext):
    await state.clear()

    user = await sync_to_async(TGUser.objects.filter(tg_id=message.from_user.id).first)()
    if user:
        if user.target == '2':
            reply_text = await sync_to_async(Text.objects.get)(slug='input_cancel')
            try:
                await message.reply(
                    text=f'\u202B{reply_text.heb}'
                )
            except:
                pass
            return True
    
    reply_text = await sync_to_async(Text.objects.get)(slug='input_cancel')
    try:
        await message.reply(text=reply_text.rus)
    except:
        pass
