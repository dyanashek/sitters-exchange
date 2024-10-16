import os

import django
from aiogram import Router, F
from aiogram.types import CallbackQuery
from asgiref.sync import sync_to_async
from aiogram.fsm.context import FSMContext

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'work_exchange.settings')
django.setup()

from states.pages_navigation import PageNavigation
from middlewares.change_username import UpdateUsernameMiddleware
from middlewares.worker_active_profile import IsActiveProfileMiddleware
from core.models import Text
from keyboards.callbacks import WorkerBackCallBackFactory
from keyboards import keyboards


router = Router()
router.callback_query.middleware(UpdateUsernameMiddleware())
router.callback_query.middleware(IsActiveProfileMiddleware())


@router.callback_query(WorkerBackCallBackFactory.filter(F.destination == 'main'))
async def handle_search_controls(callback: CallbackQuery, callback_data: WorkerBackCallBackFactory, state=FSMContext):
    await state.clear()

    choose_menu_section = await sync_to_async(Text.objects.get)(slug='choose_menu_section')

    try:
        await callback.message.edit_text(
            text=choose_menu_section.rus,
            reply_markup=await keyboards.worker_main_menu(),
        )
    except:
        pass
    

@router.callback_query(WorkerBackCallBackFactory.filter(F.destination == 'jobs-list'), PageNavigation.page_navigation)
async def back_jobs_list(callback: CallbackQuery, callback_data: WorkerBackCallBackFactory, state=FSMContext):
    state_data = await state.get_data()
    page = state_data.get('page')
    destination = state_data.get('destination')

    if page and destination:
        if destination == 'all-jobs':
            reply_text = await sync_to_async(Text.objects.get)(slug='all_jobs')
        elif destination == 'suitable-jobs':
            reply_text = await sync_to_async(Text.objects.get)(slug='jobs_suitable')

        try:
            await callback.message.edit_text(
                text=reply_text.rus,
                reply_markup=await keyboards.worker_jobs_list_keyboard(
                    page, 
                    destination, 
                    callback.from_user.id),
            )
        except:
            pass

    else:
        await state.clear()

        choose_jobs_type = await sync_to_async(Text.objects.get)(slug='choose_jobs_type')

        try:
            await callback.message.edit_text(
                text=choose_jobs_type.rus,
                reply_markup=await keyboards.worker_jobs_menu_keyboard(),
            )
        except:
            pass
    

@router.callback_query(WorkerBackCallBackFactory.filter(F.destination == 'jobs-list'))
async def back_jobs_section(callback: CallbackQuery, callback_data: WorkerBackCallBackFactory, state=FSMContext):
    await state.clear()

    choose_jobs_type = await sync_to_async(Text.objects.get)(slug='choose_jobs_type')

    try:
        await callback.message.edit_text(
            text=choose_jobs_type.rus,
            reply_markup=await keyboards.worker_jobs_menu_keyboard(),
        )
    except:
        pass


@router.callback_query(WorkerBackCallBackFactory.filter(F.destination == 'proposals-list'), PageNavigation.page_navigation)
async def back_proposals_list(callback: CallbackQuery, callback_data: WorkerBackCallBackFactory, state=FSMContext):
    state_data = await state.get_data()
    page = state_data.get('page')
    destination = state_data.get('destination')

    if page and destination:
        if destination == 'inbox-proposals':
            reply_text = await sync_to_async(Text.objects.get)(slug='inbox_proposals')
        elif destination == 'outbox-proposals':
            reply_text = await sync_to_async(Text.objects.get)(slug='outbox_proposals')

        try:
            await callback.message.edit_text(
                text=reply_text.rus,
                reply_markup=await keyboards.worker_proposals_list_keyboard(
                    page, 
                    destination, 
                    callback.from_user.id),
            )
        except:
            pass

    else:
        await state.clear()

        choose_proposals_type = await sync_to_async(Text.objects.get)(slug='choose_proposals_type')

        try:
            await callback.message.edit_text(
                text=choose_proposals_type.rus,
                reply_markup=await keyboards.worker_proposals_menu_keyboard(),
            )
        except:
            pass
    

@router.callback_query(WorkerBackCallBackFactory.filter(F.destination == 'proposals-list'))
async def back_proposals_section(callback: CallbackQuery, callback_data: WorkerBackCallBackFactory, state=FSMContext):
    await state.clear()

    choose_proposals_type = await sync_to_async(Text.objects.get)(slug='choose_proposals_type')

    try:
        await callback.message.edit_text(
            text=choose_proposals_type.rus,
            reply_markup=await keyboards.worker_proposals_menu_keyboard(),
        )
    except:
        pass


@router.callback_query(WorkerBackCallBackFactory.filter(F.destination == 'reviews-list'), PageNavigation.page_navigation)
async def back_reviews_list(callback: CallbackQuery, callback_data: WorkerBackCallBackFactory, state=FSMContext):
    state_data = await state.get_data()
    page = state_data.get('page')
    destination = state_data.get('destination')

    if page and destination:
        if destination == 'outbox-reviews':
            reply_text = await sync_to_async(Text.objects.get)(slug='outbox_reviews')
        elif destination == 'inbox-reviews':
            reply_text = await sync_to_async(Text.objects.get)(slug='inbox_reviews')

        try:
            await callback.message.edit_text(
                text=reply_text.rus,
                reply_markup=await keyboards.worker_reviews_list_keyboard(
                    page, 
                    destination, 
                    callback.from_user.id),
            )
        except:
            pass

    else:
        await state.clear()

        choose_reviews_type = await sync_to_async(Text.objects.get)(slug='choose_reviews_type')

        try:
            await callback.message.edit_text(
                text=choose_reviews_type.rus,
                reply_markup=await keyboards.worker_reviews_menu_keyboard(),
            )
        except:
            pass
    

@router.callback_query(WorkerBackCallBackFactory.filter(F.destination == 'reviews-list'))
async def back_reviews_section(callback: CallbackQuery, callback_data: WorkerBackCallBackFactory, state=FSMContext):
    await state.clear()

    choose_reviews_type = await sync_to_async(Text.objects.get)(slug='choose_reviews_type')

    try:
        await callback.message.edit_text(
            text=choose_reviews_type.rus,
            reply_markup=await keyboards.worker_reviews_menu_keyboard(),
        )
    except:
        pass
