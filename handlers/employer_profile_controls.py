import os
import asyncio

import django
from django.db.models import Q
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from asgiref.sync import sync_to_async
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'work_exchange.settings')
django.setup()

from config import MAX_LEN
from middlewares.change_username import UpdateUsernameMiddleware
from core.models import Text, Employer, Worker, EmployerCooperationProposal, WorkerCooperationProposal, EmployerReview
from keyboards.callbacks import EmployerControlsCallBackFactory
from states.create_employer import CreateEmployer
from states.create_employer_review import CreateReview
from keyboards import keyboards
from notifications_center import worker_proposal_accepted, new_employer_review
from utils import escape_markdown, translate_to_rus


router = Router()
router.callback_query.middleware(UpdateUsernameMiddleware())
router.message.middleware(UpdateUsernameMiddleware())


@router.callback_query(EmployerControlsCallBackFactory.filter((F.control == 'data') & (F.action == 'change')))
async def handle_change_phone(callback: CallbackQuery, callback_data: EmployerControlsCallBackFactory, state=FSMContext):
    employer= await sync_to_async(Employer.objects.filter(tg_id=callback.from_user.id).first)()
    if employer:
        await state.clear()
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


@router.callback_query(EmployerControlsCallBackFactory.filter((F.control == 'proposal') & (F.action == 'make')))
async def handle_make_proposal(callback: CallbackQuery, callback_data: EmployerControlsCallBackFactory, state=FSMContext):
    worker = await sync_to_async(Worker.objects.filter(id=callback_data.object_id).first)()
    employer = await sync_to_async(Employer.objects.filter(tg_id=callback.from_user.id).first)()
    if worker and employer:
        proposal = await sync_to_async(EmployerCooperationProposal.objects.filter(Q(worker=worker) & Q(employer=employer)).first)()
        if not proposal:
            proposal = await sync_to_async(EmployerCooperationProposal.objects.create)(
                employer=employer,
                worker=worker,
            )

            if worker.is_approved and worker.is_searching:
                try:
                    new_proposal_text = await sync_to_async(Text.objects.get)(slug='new_proposal')
                    await callback.bot.send_message(
                        chat_id=worker.tg_id,
                        text=new_proposal_text.rus,
                        reply_markup=await keyboards.worker_inbox_response_detail_redirect(proposal.id),
                    )
                except:
                    pass
            else:
                proposal.is_accepted = False
                await sync_to_async(proposal.save)()
        
        await callback.message.edit_reply_markup(
            reply_markup=await keyboards.employer_worker_details_keyboard(worker.id, employer.tg_id)
        )


@router.callback_query(EmployerControlsCallBackFactory.filter((F.control == 'proposal') & (F.action == 'resend')))
async def handle_resend_proposal(callback: CallbackQuery, callback_data: EmployerControlsCallBackFactory, state=FSMContext):
    worker = await sync_to_async(Worker.objects.filter(id=callback_data.object_id).first)()
    employer = await sync_to_async(Employer.objects.filter(tg_id=callback.from_user.id).first)()
    if worker and employer:
        proposal = await sync_to_async(EmployerCooperationProposal.objects.filter(Q(worker=worker) & Q(employer=employer)).first)()
        if proposal:
            proposal.is_accepted = None
            proposal.is_proceeded = False
            await sync_to_async(proposal.save)()

            if worker.is_approved and worker.is_searching:
                try:
                    new_proposal_text = await sync_to_async(Text.objects.get)(slug='new_proposal')
                    await callback.bot.send_message(
                        chat_id=worker.tg_id,
                        text=new_proposal_text.rus,
                        reply_markup=await keyboards.worker_inbox_response_detail_redirect(proposal.id),
                    )
                except:
                    pass
            else:
                proposal.is_accepted = False
                await sync_to_async(proposal.save)()
        
            status = await sync_to_async(lambda: proposal.readable_heb_accepted_status)()

            status_text = await sync_to_async(Text.objects.get)(slug='status')
            created_at = await sync_to_async(Text.objects.get)(slug='created_at')
            updated_at = await sync_to_async(Text.objects.get)(slug='updated_at')

            created_date = proposal.created_at.strftime('%d.%m.%Y')
            updated_date = proposal.updated_at.strftime('%d.%m.%Y')

            reply_text = f'''\u202B*{status_text.heb}* {status}\
                        \n*{created_at.heb}* {created_date}\
                        \n*{updated_at.heb}* {updated_date}'''

            try:
                await callback.message.edit_text(
                    text=reply_text,
                    reply_markup=await keyboards.employer_worker_detail_back(worker.id, proposal.id),
                    parse_mode='Markdown',
                )
            except:
                pass


@router.callback_query(EmployerControlsCallBackFactory.filter((F.control == 'outbox-proposal') & (F.action == 'resend')))
async def handle_resend_outbox_proposal(callback: CallbackQuery, callback_data: EmployerControlsCallBackFactory, state=FSMContext):
    worker = await sync_to_async(Worker.objects.filter(id=callback_data.object_id).first)()
    employer = await sync_to_async(Employer.objects.filter(tg_id=callback.from_user.id).first)()
    if worker and employer:
        proposal = await sync_to_async(EmployerCooperationProposal.objects.filter(Q(worker=worker) & Q(employer=employer)).first)()
        if proposal:
            proposal.is_accepted = None
            proposal.is_proceeded = False
            await sync_to_async(proposal.save)()

            if worker.is_approved and worker.is_searching:
                try:
                    new_proposal_text = await sync_to_async(Text.objects.get)(slug='new_proposal')
                    await callback.bot.send_message(
                        chat_id=worker.tg_id,
                        text=new_proposal_text.rus,
                        reply_markup=await keyboards.worker_inbox_response_detail_redirect(proposal.id),
                    )
                except:
                    pass
            else:
                proposal.is_accepted = False
                await sync_to_async(proposal.save)()

            worker_text = await sync_to_async(Text.objects.get)(slug='worker')
            outbox_proposal_text = await sync_to_async(Text.objects.get)(slug='outbox_proposal')

            readable_zones = await sync_to_async(lambda: worker.readable_zones)()

            zones_text = await sync_to_async(Text.objects.get)(slug='zones')
            min_salary_text = await sync_to_async(Text.objects.get)(slug='min_salary')
            about_text = await sync_to_async(Text.objects.get)(slug='about')
            salary_hourly = await sync_to_async(Text.objects.get)(slug='salary_hourly')
            work_type_text = await sync_to_async(Text.objects.get)(slug='work_type')

            status = await sync_to_async(lambda: proposal.readable_heb_accepted_status)()
            readable_work_type = await sync_to_async(lambda: worker.readable_work_type_heb)()

            status_text = await sync_to_async(Text.objects.get)(slug='status')
            created_at = await sync_to_async(Text.objects.get)(slug='created_at')
            updated_at = await sync_to_async(Text.objects.get)(slug='updated_at')

            created_date = proposal.created_at.strftime('%d.%m.%Y')
            updated_date = proposal.updated_at.strftime('%d.%m.%Y')

            reply_text = f'''\u202B*{worker_text.heb}*\
                \n*{zones_text.heb}* {readable_zones}\
                \n*{min_salary_text.heb}* {worker.min_salary} {salary_hourly.heb}\
                \n*{work_type_text.heb}* {readable_work_type}\
                \n*{about_text.heb}* {worker.about_heb}\
                \n\
                \n*{outbox_proposal_text.heb}*\
                \n*{status_text.heb}* {status}\
                \n*{created_at.heb}* {created_date}\
                \n*{updated_at.heb}* {updated_date}'''

            try:
                await callback.message.edit_text(
                    text=reply_text,
                    reply_markup=await keyboards.employer_outbox_proposal_details_keyboard(worker.id, proposal.id),
                    parse_mode='Markdown',
                )
            except:
                pass


@router.callback_query(EmployerControlsCallBackFactory.filter((F.control == 'inbox-proposal') & (F.action.in_(['accept', 'decline']))))
async def handle_inbox_proposal(callback: CallbackQuery, callback_data: EmployerControlsCallBackFactory, state=FSMContext):
    proposal_id = callback_data.object_id
    proposal = await sync_to_async(WorkerCooperationProposal.objects.filter(id=proposal_id).first)()
    job = await sync_to_async(lambda: proposal.job)()
    worker = await sync_to_async(lambda: proposal.worker)()

    if proposal and job and worker:
        action = callback_data.action
        if action == 'accept':
            proposal.is_accepted = True
            proposal_result = await sync_to_async(Text.objects.get)(slug='proposal_accepted')
            asyncio.create_task(worker_proposal_accepted(callback.bot, proposal.id))
        elif action == 'decline':
            proposal.is_accepted = False
            proposal_result = await sync_to_async(Text.objects.get)(slug='proposal_declined')

        await sync_to_async(proposal.save)()

        try:
            await callback.bot.send_message(
                chat_id=worker.tg_id,
                text=proposal_result.rus,
                reply_markup=await keyboards.worker_outbox_response_detail_redirect(proposal.id)
            )
        except:
            pass

        worker_text = await sync_to_async(Text.objects.get)(slug='worker')
        job_text = await sync_to_async(Text.objects.get)(slug='job')
        inbox_proposal_text = await sync_to_async(Text.objects.get)(slug='inbox_proposal')

        readable_zones = await sync_to_async(lambda: worker.readable_zones)()
        readable_zones_job = await sync_to_async(lambda: job.readable_zones)()

        zones_text = await sync_to_async(Text.objects.get)(slug='zones')
        min_salary_text = await sync_to_async(Text.objects.get)(slug='min_salary')
        about_text = await sync_to_async(Text.objects.get)(slug='about')
        salary_hourly = await sync_to_async(Text.objects.get)(slug='salary_hourly')
        work_type_text = await sync_to_async(Text.objects.get)(slug='work_type')
        
        readable_approve_status = await sync_to_async(lambda: job.readable_approved_status)()
        readable_active_status = await sync_to_async(lambda: job.readable_active_status)()
        readable_notifications_status = await sync_to_async(lambda: job.readable_notifications_heb_status)()


        job_approved_text = await sync_to_async(Text.objects.get)(slug='job_approved_text')
        job_active_text = await sync_to_async(Text.objects.get)(slug='is_job_active')
        notifications_text = await sync_to_async(Text.objects.get)(slug='notifications')

        description_text = await sync_to_async(Text.objects.get)(slug='description')

        status = await sync_to_async(lambda: proposal.readable_heb_accepted_status)()
        readable_work_type = await sync_to_async(lambda: worker.readable_work_type_heb)()
        readable_work_type_job = await sync_to_async(lambda: job.readable_work_type_heb)()

        status_text = await sync_to_async(Text.objects.get)(slug='status')
        created_at = await sync_to_async(Text.objects.get)(slug='created_at')
        updated_at = await sync_to_async(Text.objects.get)(slug='updated_at')

        created_date = proposal.created_at.strftime('%d.%m.%Y')
        updated_date = proposal.updated_at.strftime('%d.%m.%Y')

        reply_text = f'''\u202B*{worker_text.heb}*\
                \n*{zones_text.heb}* {readable_zones}\
                \n*{min_salary_text.heb}* {worker.min_salary} {salary_hourly.heb}\
                \n*{work_type_text.heb}* {readable_work_type}\
                \n*{about_text.heb}* {worker.about_heb}\
                \n\
                \n*{job_text.heb}*\
                \n*{job_approved_text.heb}* {readable_approve_status}\
                \n*{job_active_text.heb}* {readable_active_status}\
                \n*{notifications_text.heb}* {readable_notifications_status}\
                \n*{zones_text.heb}* {readable_zones_job}\
                \n*{min_salary_text.heb}* {job.min_salary} {salary_hourly.heb}\
                \n*{work_type_text.heb}* {readable_work_type_job}\
                \n*{description_text.heb}* {job.description}\
                \n\
                \n*{inbox_proposal_text.heb}*\
                \n*{status_text.heb}* {status}\
                \n*{created_at.heb}* {created_date}\
                \n*{updated_at.heb}* {updated_date}'''

        try:
            await callback.message.edit_text(
                text=reply_text,
                reply_markup=await keyboards.employer_inbox_proposal_details_keyboard(proposal.id),
                parse_mode='Markdown',
            )
        except:
            pass


@router.callback_query(EmployerControlsCallBackFactory.filter((F.control == 'review') & (F.action == 'add')))
async def handle_add_review(callback: CallbackQuery, callback_data: EmployerControlsCallBackFactory, state=FSMContext):
    await state.clear()
    await state.set_state(CreateReview.rate)
    await state.update_data(worker=callback_data.object_id)

    add_rate = await sync_to_async(Text.objects.get)(slug='add_rate')

    try:
        await callback.message.edit_text(
            text=f'\u202B{add_rate.heb}',
            reply_markup=await keyboards.employer_review_rate_keyboard(),
        )
    except:
        pass


@router.callback_query(EmployerControlsCallBackFactory.filter((F.control == 'review') & (F.action == 'rate')), CreateReview.rate)
async def handle_rate_review(callback: CallbackQuery, callback_data: EmployerControlsCallBackFactory, state=FSMContext):
    await state.set_state(CreateReview.review)
    await state.update_data(rate=callback_data.object_id)

    add_review = await sync_to_async(Text.objects.get)(slug='add_review')
    try:
        await callback.message.edit_text(
            text=f'\u202B{add_review.heb}',
            reply_markup=await keyboards.employer_review_text_keyboard(),
        )
    except:
        pass


@router.callback_query(EmployerControlsCallBackFactory.filter((F.control == 'review') & (F.action == 'text')), CreateReview.review)
async def handle_text_review(callback: CallbackQuery, callback_data: EmployerControlsCallBackFactory, state=FSMContext):
    add_text_review = await sync_to_async(Text.objects.get)(slug='add_text_review')
    await callback.message.edit_text(
        text=f'\u202B{add_text_review.heb}',
        reply_markup=InlineKeyboardBuilder().as_markup(),
    )


@router.callback_query(EmployerControlsCallBackFactory.filter((F.control == 'review') & (F.action == 'skip')), CreateReview.review)
async def handle_skip_text_review(callback: CallbackQuery, callback_data: EmployerControlsCallBackFactory, state=FSMContext):
    await state.set_state(CreateReview.confirmation)

    confirmation_text = await sync_to_async(Text.objects.get)(slug='worker_confirmation')
    rate_text = await sync_to_async(Text.objects.get)(slug='rate')
    review_text = await sync_to_async(Text.objects.get)(slug='review')
    empty_text = await sync_to_async(Text.objects.get)(slug='empty')

    state_data = await state.get_data()
    rate = state_data.get('rate')
    reply_text = f'''\u202B*{confirmation_text.heb}*\
                  \n\
                  \n*{rate_text.heb}* {rate} ⭐️\
                  \n*{review_text.heb}* {empty_text.heb}'''

    try:
        await callback.message.edit_text(
            text=reply_text,
            reply_markup=await keyboards.employer_review_confirmation_keyboard(),
            parse_mode='Markdown',
        )   
    except:
        pass


@router.message(F.text, CreateReview.review)
async def handle_add_text_review(message: Message, state: FSMContext):
    review = await escape_markdown(message.text)
    review = review[:MAX_LEN]

    await state.update_data(review=review)
    await state.set_state(CreateReview.confirmation)
    
    confirmation_text = await sync_to_async(Text.objects.get)(slug='worker_confirmation')
    rate_text = await sync_to_async(Text.objects.get)(slug='rate')
    review_text = await sync_to_async(Text.objects.get)(slug='review')

    state_data = await state.get_data()
    rate = state_data.get('rate')
    reply_text = f'''\u202B*{confirmation_text.heb}*\
                  \n\
                  \n*{rate_text.heb}* {rate} ⭐️\
                  \n*{review_text.heb}* {review}'''
    
    try:
        await message.answer(
            text=reply_text,
            reply_markup=await keyboards.employer_review_confirmation_keyboard(),
            parse_mode='Markdown',
        )   
    except:
        pass


@router.callback_query(EmployerControlsCallBackFactory.filter((F.control == 'review') & (F.action == 'retype')), CreateReview.confirmation)
async def handle_retype_review(callback: CallbackQuery, callback_data: EmployerControlsCallBackFactory, state=FSMContext):
    state_data = await state.get_data()
    worker_id = state_data.get('worker')

    await state.clear()
    await state.set_state(CreateReview.rate)
    await state.update_data(worker=worker_id)

    add_rate = await sync_to_async(Text.objects.get)(slug='add_rate')

    try:
        await callback.message.edit_text(
            text=f'\u202B{add_rate.heb}',
            reply_markup=await keyboards.employer_review_rate_keyboard(),
        )
    except:
        pass


@router.callback_query(EmployerControlsCallBackFactory.filter((F.control == 'review') & (F.action == 'confirm')), CreateReview.confirmation)
async def handle_confirm_review(callback: CallbackQuery, callback_data: EmployerControlsCallBackFactory, state=FSMContext):
    state_data = await state.get_data()

    worker_id = state_data.get('worker')
    rate = state_data.get('rate')
    review = state_data.get('review')
    review_rus = None
    if review:
        review_rus = await translate_to_rus(review)

    prev_review = await sync_to_async(EmployerReview.objects.filter(Q(worker__id=worker_id) & Q(employer__tg_id=callback.from_user.id)).first)()
    if not prev_review:
        worker = await sync_to_async(Worker.objects.filter(id=worker_id).first)()
        employer = await sync_to_async(Employer.objects.filter(tg_id=callback.from_user.id).first)()
        new_review = await sync_to_async(EmployerReview.objects.create)(
            employer=employer,
            worker=worker,
            rate=rate,
            review=review,
            review_rus=review_rus,
        )

        review_wait_check = await sync_to_async(Text.objects.get)(slug='review_wait_check')

        try:
            await callback.message.edit_text(
                text=f'\u202B{review_wait_check.heb}',
                reply_markup=await keyboards.employer_to_main_menu_keyboard(),
            )
        except:
            pass
        
        asyncio.create_task(new_employer_review(callback.bot, new_review.id))
