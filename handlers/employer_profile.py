import os

import django
from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove
from asgiref.sync import sync_to_async
from aiogram.fsm.context import FSMContext

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'work_exchange.settings')
django.setup()

from config import ADMIN_CHAT_ID
from middlewares.change_username import UpdateUsernameMiddleware
from core.models import Employer, Text
from states.create_employer import CreateEmployer
from keyboards import keyboards
from utils import validate_phone, escape_markdown


router = Router()
router.message.middleware(UpdateUsernameMiddleware())


@router.message(F.contact, CreateEmployer.input_phone)
async def employer_contact(message: Message, state: FSMContext):
    phone = await validate_phone(phone = message.contact.phone_number)

    if phone:
        await state.update_data(phone=phone)
        await state.set_state(CreateEmployer.input_name)

        name_text = await sync_to_async(Text.objects.get)(slug='input_employer_name')
        
        try:
            await message.answer(
                text=f'\u202B{name_text.heb}',
                reply_markup=ReplyKeyboardRemove(),
            )
        except:
            pass

    else:
        reply_text = await sync_to_async(Text.objects.get)(slug='wrong_phone')
        try:
            await message.reply(text=f'\u202B{reply_text.heb}')
        except:
            pass


@router.message(F.text, CreateEmployer.input_phone)
async def employer_phone(message: Message, state: FSMContext):
    phone = await validate_phone(message.text)

    if phone:
        await state.update_data(phone=phone)
        await state.set_state(CreateEmployer.input_name)

        name_text = await sync_to_async(Text.objects.get)(slug='input_employer_name')
        
        try:
            await message.answer(
                text=f'\u202B{name_text.heb}',
                reply_markup=ReplyKeyboardRemove(),
            )
        except:
            pass

    else:
        reply_text = await sync_to_async(Text.objects.get)(slug='wrong_phone')
        try:
            await message.reply(text=f'\u202B{reply_text.heb}')
        except:
            pass


@router.message(F.text, CreateEmployer.input_name)
async def employer_company_name(message: Message, state: FSMContext):
    name = await escape_markdown(message.text)

    state_data = await state.get_data()
    phone = state_data.get('phone')
    await state.clear()

    employer = await sync_to_async(Employer.objects.filter(tg_id=message.from_user.id).first)()
    if employer:
        employer.name = name
        employer.phone = phone
        await sync_to_async(employer.save)()
    else:
        employer = await sync_to_async(Employer.objects.create)(
            tg_id=message.from_user.id,
            username=message.from_user.username,
            phone=phone,
            name=name,
        )

    your_profile = await sync_to_async(Text.objects.get)(slug='your_profile')
    phone_text = await sync_to_async(Text.objects.get)(slug='phone')
    rating_text = await sync_to_async(Text.objects.get)(slug='rating')
    name_text = await sync_to_async(Text.objects.get)(slug='employer_company_name')

    rating = await sync_to_async(lambda: employer.rating_heb)()

    reply_text =f'''\u202B*{your_profile.heb}*\
                \n\
                \n*{rating_text.heb}* {rating}\
                \n*{name_text.heb}* {name}\
                \n*{phone_text.heb}* {phone}'''

    try:
        await message.answer(
            text=reply_text,
            reply_markup=await keyboards.employer_profile_keyboard(),
            parse_mode='Markdown',
        )
    except:
        pass
