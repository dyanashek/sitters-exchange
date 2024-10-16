import os

import django
from aiogram import Router, F
from aiogram.types import CallbackQuery
from asgiref.sync import sync_to_async
from aiogram.fsm.context import FSMContext

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'work_exchange.settings')
django.setup()

from middlewares.change_username import UpdateUsernameMiddleware
from middlewares.worker_active_profile import IsActiveProfileMiddleware
from states.pages_navigation import PageNavigation
from core.models import Text
from keyboards.callbacks import WorkerPagesSectionsCallBackFactory
from keyboards import keyboards


router = Router()
router.callback_query.middleware(UpdateUsernameMiddleware())
router.callback_query.middleware(IsActiveProfileMiddleware())


@router.callback_query(WorkerPagesSectionsCallBackFactory.filter(F.destination.contains('jobs')))
async def handle_search_controls(callback: CallbackQuery, callback_data: WorkerPagesSectionsCallBackFactory, state=FSMContext):
    await state.clear()
    await state.set_state(PageNavigation.page_navigation)
    await state.set_data({'destination': callback_data.destination, 'page': callback_data.page})

    if callback_data.destination == 'all-jobs':
        reply_text = await sync_to_async(Text.objects.get)(slug='all_jobs')
    elif callback_data.destination == 'suitable-jobs':
        reply_text = await sync_to_async(Text.objects.get)(slug='jobs_suitable')

    try:
        await callback.message.edit_text(
            text=reply_text.rus,
            reply_markup=await keyboards.worker_jobs_list_keyboard(
                callback_data.page, 
                callback_data.destination, 
                callback.from_user.id),
        )
    except:
        pass


@router.callback_query(WorkerPagesSectionsCallBackFactory.filter(F.destination.contains('proposals')))
async def handle_workers_section(callback: CallbackQuery, callback_data: WorkerPagesSectionsCallBackFactory, state=FSMContext):
    await state.clear()
    await state.set_state(PageNavigation.page_navigation)
    await state.set_data({'destination': callback_data.destination, 'page': callback_data.page})

    if callback_data.destination == 'inbox-proposals':
        reply_text = await sync_to_async(Text.objects.get)(slug='inbox_proposals')
    elif callback_data.destination == 'outbox-proposals':
        reply_text = await sync_to_async(Text.objects.get)(slug='outbox_proposals')

    try:
        await callback.message.edit_text(
            text=reply_text.rus,
            reply_markup=await keyboards.worker_proposals_list_keyboard(
                callback_data.page, 
                callback_data.destination, 
                callback.from_user.id),
        )   
    except:
        pass


@router.callback_query(WorkerPagesSectionsCallBackFactory.filter(F.destination.contains('reviews')))
async def handle_workers_section(callback: CallbackQuery, callback_data: WorkerPagesSectionsCallBackFactory, state=FSMContext):
    await state.clear()
    await state.set_state(PageNavigation.page_navigation)
    await state.set_data({'destination': callback_data.destination, 'page': callback_data.page})

    if callback_data.destination == 'inbox-reviews':
        reply_text = await sync_to_async(Text.objects.get)(slug='inbox_reviews')
    elif callback_data.destination == 'outbox-reviews':
        reply_text = await sync_to_async(Text.objects.get)(slug='outbox_reviews')

    try:
        await callback.message.edit_text(
            text=reply_text.rus,
            reply_markup=await keyboards.worker_reviews_list_keyboard(
                callback_data.page, 
                callback_data.destination, 
                callback.from_user.id),
        )  
    except:
        pass
    