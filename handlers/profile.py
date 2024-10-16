import os

import django
from aiogram import Router
from aiogram.types import CallbackQuery
from asgiref.sync import sync_to_async
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'work_exchange.settings')
django.setup()

from keyboards import keyboards
from middlewares.change_username import UpdateUsernameMiddleware
from core.models import TGUser, Worker, Employer, Text
from keyboards.callbacks import TargetCallbackFactory
from states.create_worker import CreateWorker
from states.create_employer import CreateEmployer


router = Router()
router.callback_query.middleware(UpdateUsernameMiddleware())
router.message.middleware(UpdateUsernameMiddleware())


@router.callback_query(TargetCallbackFactory.filter())
async def proceed_target(callback: CallbackQuery, callback_data: TargetCallbackFactory, state: FSMContext):
    await state.clear()

    user_id = callback.from_user.id
    user = await sync_to_async(TGUser.objects.filter(tg_id=user_id).first)()
    if user:
        data_outdated_text = await sync_to_async(Text.objects.get)(slug='data_outdated')
        if user.target == '1':
            worker = await sync_to_async(Worker.objects.filter(tg_id=user_id).first)()
            if worker:
                reply_text = data_outdated_text.rus
                try:
                    await callback.message.edit_text(
                        text=reply_text,
                        reply_markup=InlineKeyboardBuilder().as_markup(),
                    )
                except:
                    pass
                return True
            else:
                user.target = str(callback_data.target)
                await sync_to_async(user.save)()
                
        else:
            employer = await sync_to_async(Employer.objects.filter(tg_id=user_id).first)()
            if employer:
                reply_text = data_outdated_text.heb
                try:
                    await callback.message.edit_text(
                        text=reply_text,
                        reply_markup=InlineKeyboardBuilder().as_markup(),
                    )
                except:
                    pass
                return True
            else:
                user.target = str(callback_data.target)
                await sync_to_async(user.save)()

    else:
        await sync_to_async(TGUser.objects.create)(
            tg_id=user_id,
            target=str(callback_data.target),
        )

    if callback_data.target == 1:
        await state.set_state(CreateWorker.input_name)

        reply_text = await sync_to_async(Text.objects.get)(slug='worker_name')

        try:
            await callback.message.edit_text(
                    text=reply_text.rus,
                    reply_markup=InlineKeyboardBuilder().as_markup(),
                )
        except:
            pass

    elif callback_data.target == 2:
        await state.set_state(CreateEmployer.input_phone)

        reply_text = await sync_to_async(Text.objects.get)(slug='input_phone')

        try:
            await callback.message.answer(
                    text=f'\u202B{reply_text.heb}',
                    reply_markup=await keyboards.request_phone_keyboard('heb'),
                )
            await callback.message.delete()
        except:
            pass
        