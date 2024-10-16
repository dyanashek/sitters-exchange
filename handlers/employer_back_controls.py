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
from core.models import Text
from keyboards.callbacks import EmployerBackCallBackFactory
from keyboards import keyboards


router = Router()
router.callback_query.middleware(UpdateUsernameMiddleware())


@router.callback_query(EmployerBackCallBackFactory.filter(F.destination == 'main'))
async def handle_search_controls(callback: CallbackQuery, callback_data: EmployerBackCallBackFactory, state=FSMContext):
    await state.clear()

    choose_menu_section = await sync_to_async(Text.objects.get)(slug='choose_menu_section')

    try:
        await callback.message.edit_text(
            text=f'\u202B{choose_menu_section.heb}',
            reply_markup=await keyboards.employer_main_menu(),
        )
    except:
        pass


@router.callback_query(EmployerBackCallBackFactory.filter(F.destination == 'jobs-list'), PageNavigation.page_navigation)
async def back_jobs_list(callback: CallbackQuery, callback_data: EmployerBackCallBackFactory, state=FSMContext):
    state_data = await state.get_data()
    page = state_data.get('page')
    destination = state_data.get('destination')

    if page and destination:
        if destination == 'jobs-active':
            reply_text = await sync_to_async(Text.objects.get)(slug='jobs_active')
        elif destination == 'jobs-archive':
            reply_text = await sync_to_async(Text.objects.get)(slug='jobs_archive')
        elif destination == 'jobs-declined':
            reply_text = await sync_to_async(Text.objects.get)(slug='jobs_declined')

        try:
            await callback.message.edit_text(
                text=f'\u202B{reply_text.heb}',
                reply_markup=await keyboards.employer_jobs_list_keyboard(
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
                text=f'\u202B{choose_jobs_type.heb}',
                reply_markup=await keyboards.employer_jobs_menu_keyboard(),
            )
        except:
            pass
    

@router.callback_query(EmployerBackCallBackFactory.filter(F.destination == 'jobs-list'))
async def back_jobs_section(callback: CallbackQuery, callback_data: EmployerBackCallBackFactory, state=FSMContext):
    await state.clear()

    choose_jobs_type = await sync_to_async(Text.objects.get)(slug='choose_jobs_type')

    try:
        await callback.message.edit_text(
            text=f'\u202B{choose_jobs_type.heb}',
            reply_markup=await keyboards.employer_jobs_menu_keyboard(),
        )
    except:
        pass


@router.callback_query(EmployerBackCallBackFactory.filter(F.destination == 'workers-list'), PageNavigation.page_navigation)
async def back_workers_list(callback: CallbackQuery, callback_data: EmployerBackCallBackFactory, state=FSMContext):
    state_data = await state.get_data()
    page = state_data.get('page')
    destination = state_data.get('destination')

    if page and destination:
        if destination == 'workers-all':
            reply_text = await sync_to_async(Text.objects.get)(slug='workers_all')
        elif destination == 'workers-suitable':
            reply_text = await sync_to_async(Text.objects.get)(slug='workers_suitable')

        try:
            await callback.message.edit_text(
                text=f'\u202B{reply_text.heb}',
                reply_markup=await keyboards.employer_workers_list_keyboard(
                    page, 
                    destination, 
                    callback.from_user.id),
            )
        except:
            pass

    else:
        await state.clear()

        choose_workers_type = await sync_to_async(Text.objects.get)(slug='choose_workers_type')

        try:
            await callback.message.edit_text(
                text=f'\u202B{choose_workers_type.heb}',
                reply_markup=await keyboards.employer_workers_menu_keyboard(),
            )
        except:
            pass
    

@router.callback_query(EmployerBackCallBackFactory.filter(F.destination == 'workers-list'))
async def back_jobs_section(callback: CallbackQuery, callback_data: EmployerBackCallBackFactory, state=FSMContext):
    await state.clear()

    choose_workers_type = await sync_to_async(Text.objects.get)(slug='choose_workers_type')

    try:
        await callback.message.edit_text(
            text=f'\u202B{choose_workers_type.heb}',
            reply_markup=await keyboards.employer_workers_menu_keyboard(),
        )
    except:
        pass


@router.callback_query(EmployerBackCallBackFactory.filter(F.destination == 'proposals-list'), PageNavigation.page_navigation)
async def back_proposals_list(callback: CallbackQuery, callback_data: EmployerBackCallBackFactory, state=FSMContext):
    state_data = await state.get_data()
    page = state_data.get('page')
    destination = state_data.get('destination')

    if page and destination:
        if destination == 'outbox-proposals':
            reply_text = await sync_to_async(Text.objects.get)(slug='outbox_proposals')
        elif destination == 'inbox-proposals':
            reply_text = await sync_to_async(Text.objects.get)(slug='inbox_proposals')

        try:
            await callback.message.edit_text(
                text=f'\u202B{reply_text.heb}',
                reply_markup=await keyboards.employer_proposals_list_keyboard(
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
                text=f'\u202B{choose_proposals_type.heb}',
                reply_markup=await keyboards.employer_proposals_menu_keyboard(),
            )
        except:
            pass
    

@router.callback_query(EmployerBackCallBackFactory.filter(F.destination == 'proposals-list'))
async def back_proposals_section(callback: CallbackQuery, callback_data: EmployerBackCallBackFactory, state=FSMContext):
    await state.clear()

    choose_proposals_type = await sync_to_async(Text.objects.get)(slug='choose_proposals_type')

    try:
        await callback.message.edit_text(
            text=f'\u202B{choose_proposals_type.heb}',
            reply_markup=await keyboards.employer_proposals_menu_keyboard(),
        )
    except:
        pass


@router.callback_query(EmployerBackCallBackFactory.filter(F.destination == 'reviews-list'), PageNavigation.page_navigation)
async def back_reviews_list(callback: CallbackQuery, callback_data: EmployerBackCallBackFactory, state=FSMContext):
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
                text=f'\u202B{reply_text.heb}',
                reply_markup=await keyboards.employer_reviews_list_keyboard(
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
                text=f'\u202B{choose_reviews_type.heb}',
                reply_markup=await keyboards.employer_reviews_menu_keyboard(),
            )
        except:
            pass
    

@router.callback_query(EmployerBackCallBackFactory.filter(F.destination == 'reviews-list'))
async def back_reviews_section(callback: CallbackQuery, callback_data: EmployerBackCallBackFactory, state=FSMContext):
    await state.clear()

    choose_reviews_type = await sync_to_async(Text.objects.get)(slug='choose_reviews_type')

    try:
        await callback.message.edit_text(
            text=f'\u202B{choose_reviews_type.heb}',
            reply_markup=await keyboards.employer_reviews_menu_keyboard(),
        )
    except:
        pass
    