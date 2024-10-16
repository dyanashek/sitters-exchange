import os

import django
from aiogram import Router, F
from aiogram.types import CallbackQuery
from asgiref.sync import sync_to_async
from aiogram.fsm.context import FSMContext

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'work_exchange.settings')
django.setup()

from middlewares.change_username import UpdateUsernameMiddleware
from states.pages_navigation import PageNavigation
from core.models import Text, Employer
from keyboards.callbacks import EmployerPagesSectionsCallBackFactory
from keyboards import keyboards


router = Router()
router.callback_query.middleware(UpdateUsernameMiddleware())


@router.callback_query(EmployerPagesSectionsCallBackFactory.filter(F.destination.contains('jobs')))
async def handle_jobs_section(callback: CallbackQuery, callback_data: EmployerPagesSectionsCallBackFactory, state=FSMContext):
    await state.clear()
    await state.set_state(PageNavigation.page_navigation)
    await state.set_data({'destination': callback_data.destination, 'page': callback_data.page})

    if callback_data.destination == 'jobs-active':
        reply_text = await sync_to_async(Text.objects.get)(slug='jobs_active')
    elif callback_data.destination == 'jobs-archive':
        reply_text = await sync_to_async(Text.objects.get)(slug='jobs_archive')
    elif callback_data.destination == 'jobs-declined':
        reply_text = await sync_to_async(Text.objects.get)(slug='jobs_declined')

    try:
        await callback.message.edit_text(
            text=f'\u202B{reply_text.heb}',
            reply_markup=await keyboards.employer_jobs_list_keyboard(
                callback_data.page, 
                callback_data.destination, 
                callback.from_user.id),
        )
    except:
        pass


@router.callback_query(EmployerPagesSectionsCallBackFactory.filter(F.destination.contains('workers')))
async def handle_workers_section(callback: CallbackQuery, callback_data: EmployerPagesSectionsCallBackFactory, state=FSMContext):
    await state.clear()
    await state.set_state(PageNavigation.page_navigation)
    await state.set_data({'destination': callback_data.destination, 'page': callback_data.page})

    if callback_data.destination == 'workers-all':
        reply_text = await sync_to_async(Text.objects.get)(slug='workers_all')
    elif callback_data.destination == 'workers-suitable':
        reply_text = await sync_to_async(Text.objects.get)(slug='workers_suitable')

    try:
        await callback.message.edit_text(
            text=f'\u202B{reply_text.heb}',
            reply_markup=await keyboards.employer_workers_list_keyboard(
                callback_data.page, 
                callback_data.destination, 
                callback.from_user.id),
        )   
    except:
        pass


@router.callback_query(EmployerPagesSectionsCallBackFactory.filter(F.destination.contains('proposals')))
async def handle_workers_section(callback: CallbackQuery, callback_data: EmployerPagesSectionsCallBackFactory, state=FSMContext):
    await state.clear()
    await state.set_state(PageNavigation.page_navigation)
    await state.set_data({'destination': callback_data.destination, 'page': callback_data.page})

    if callback_data.destination == 'inbox-proposals':
        reply_text = await sync_to_async(Text.objects.get)(slug='inbox_proposals')
    elif callback_data.destination == 'outbox-proposals':
        reply_text = await sync_to_async(Text.objects.get)(slug='outbox_proposals')

    try:
        await callback.message.edit_text(
            text=f'\u202B{reply_text.heb}',
            reply_markup=await keyboards.employer_proposals_list_keyboard(
                callback_data.page, 
                callback_data.destination, 
                callback.from_user.id),
        )   
    except:
        pass


@router.callback_query(EmployerPagesSectionsCallBackFactory.filter(F.destination.contains('reviews')))
async def handle_workers_section(callback: CallbackQuery, callback_data: EmployerPagesSectionsCallBackFactory, state=FSMContext):
    await state.clear()
    await state.set_state(PageNavigation.page_navigation)
    await state.set_data({'destination': callback_data.destination, 'page': callback_data.page})

    if callback_data.destination == 'inbox-reviews':
        reply_text = await sync_to_async(Text.objects.get)(slug='inbox_reviews')
    elif callback_data.destination == 'outbox-reviews':
        reply_text = await sync_to_async(Text.objects.get)(slug='outbox_reviews')

    try:
        await callback.message.edit_text(
            text=f'\u202B{reply_text.heb}',
            reply_markup=await keyboards.employer_reviews_list_keyboard(
                callback_data.page, 
                callback_data.destination, 
                callback.from_user.id),
        ) 
    except:
        pass 