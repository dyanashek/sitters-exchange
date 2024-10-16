import os

import django
from aiogram import Router, F
from aiogram.types import CallbackQuery
from asgiref.sync import sync_to_async
from aiogram.fsm.context import FSMContext

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'work_exchange.settings')
django.setup()

from middlewares.change_username import UpdateUsernameMiddleware
from core.models import Employer, Text
from keyboards import keyboards
from utils import validate_phone
from keyboards.callbacks import EmployerMainSectionsCallBackFactory


router = Router()
router.callback_query.middleware(UpdateUsernameMiddleware())


@router.callback_query(EmployerMainSectionsCallBackFactory.filter(F.destination == 'profile'))
async def handle_profile_menu(callback: CallbackQuery, callback_data: EmployerMainSectionsCallBackFactory, state: FSMContext):
    await state.clear()

    employer = await sync_to_async(Employer.objects.filter(tg_id=callback.from_user.id).first)()
    if employer:

        your_profile = await sync_to_async(Text.objects.get)(slug='your_profile')
        phone_text = await sync_to_async(Text.objects.get)(slug='phone')
        rating_text = await sync_to_async(Text.objects.get)(slug='rating')
        name_text = await sync_to_async(Text.objects.get)(slug='employer_company_name')

        rating = await sync_to_async(lambda: employer.rating_heb)()

        reply_text =f'''\u202B*{your_profile.heb}*\
                    \n\
                    \n*{rating_text.heb}* {rating}\
                    \n*{name_text.heb}* {employer.name}\
                    \n*{phone_text.heb}* {employer.phone}'''

        try:
            await callback.message.edit_text(
                text=reply_text,
                reply_markup=await keyboards.employer_profile_keyboard(),
                parse_mode='Markdown',
            )
        except:
            pass


@router.callback_query(EmployerMainSectionsCallBackFactory.filter(F.destination == 'jobs'))
async def handle_jobs_menu(callback: CallbackQuery, callback_data: EmployerMainSectionsCallBackFactory, state: FSMContext):
    await state.clear()

    choose_jobs_type = await sync_to_async(Text.objects.get)(slug='choose_jobs_type')

    try:
        await callback.message.edit_text(
            text=f'\u202B{choose_jobs_type.heb}',
            reply_markup=await keyboards.employer_jobs_menu_keyboard(),
        )
    except:
        pass


@router.callback_query(EmployerMainSectionsCallBackFactory.filter(F.destination == 'workers'))
async def handle_workers_menu(callback: CallbackQuery, callback_data: EmployerMainSectionsCallBackFactory, state: FSMContext):
    await state.clear()

    choose_workers_type = await sync_to_async(Text.objects.get)(slug='choose_workers_type')

    try:
        await callback.message.edit_text(
            text=f'\u202B{choose_workers_type.heb}',
            reply_markup=await keyboards.employer_workers_menu_keyboard(),
        )
    except:
        pass


@router.callback_query(EmployerMainSectionsCallBackFactory.filter(F.destination == 'proposals'))
async def handle_proposals_menu(callback: CallbackQuery, callback_data: EmployerMainSectionsCallBackFactory, state: FSMContext):
    await state.clear()

    choose_proposals_type = await sync_to_async(Text.objects.get)(slug='choose_proposals_type')

    try:
        await callback.message.edit_text(
            text=f'\u202B{choose_proposals_type.heb}',
            reply_markup=await keyboards.employer_proposals_menu_keyboard(),
        )
    except:
        pass


@router.callback_query(EmployerMainSectionsCallBackFactory.filter(F.destination == 'reviews'))
async def handle_notifications_controls(callback: CallbackQuery, callback_data: EmployerMainSectionsCallBackFactory, state: FSMContext):
    await state.clear()

    choose_reviews_type = await sync_to_async(Text.objects.get)(slug='choose_reviews_type')

    try:
        await callback.message.edit_text(
            text=f'\u202B{choose_reviews_type.heb}',
            reply_markup=await keyboards.employer_reviews_menu_keyboard(),
        )
    except:
        pass
