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
from middlewares.worker_active_profile import IsActiveProfileMiddleware, IsReviewedByAdminsMiddleware
from core.models import Worker, Text, Job, WorkerCooperationProposal, EmployerCooperationProposal, WorkerReview, Employer
from keyboards import keyboards
from keyboards.callbacks import WorkerControlsCallBackFactory
from states.create_worker import CreateWorker
from states.create_worker_review import CreateReview
from notifications_center import employer_proposal_accepted, new_worker_review
from utils import escape_markdown


router = Router()
router.callback_query.middleware(UpdateUsernameMiddleware())
router.message.middleware(UpdateUsernameMiddleware())
router.callback_query.middleware(IsActiveProfileMiddleware())

cv_router = Router()
cv_router.callback_query.middleware(UpdateUsernameMiddleware())
cv_router.callback_query.middleware(IsReviewedByAdminsMiddleware())


@router.callback_query(WorkerControlsCallBackFactory.filter(F.control == 'notification'))
async def handle_notifications_controls(callback: CallbackQuery, callback_data: WorkerControlsCallBackFactory):
    worker = await sync_to_async(Worker.objects.filter(tg_id=callback.from_user.id).first)()
    if worker:
        if callback_data.action == 'disable':
            worker.notifications = False
        elif callback_data.action == 'enable':
            worker.notifications = True

        await sync_to_async(worker.save)()

        readable_approved_status = await sync_to_async(lambda: worker.readable_approved_status)()
        readable_search_status = await sync_to_async(lambda: worker.readable_search_status)()
        readable_notifications_status = await sync_to_async(lambda: worker.readable_notifications_status)()
        readable_zones = await sync_to_async(lambda: worker.readable_zones)()
        readable_work_type = await sync_to_async(lambda: worker.readable_work_type_rus)()
        rating = await sync_to_async(lambda: worker.rating_rus)()

        work_type_text = await sync_to_async(Text.objects.get)(slug='work_type')
        rating_text = await sync_to_async(Text.objects.get)(slug='rating')
        name_text = await sync_to_async(Text.objects.get)(slug='name')
        phone_text = await sync_to_async(Text.objects.get)(slug='phone')
        zones_text = await sync_to_async(Text.objects.get)(slug='zones')
        min_salary_text = await sync_to_async(Text.objects.get)(slug='min_salary')
        about_text = await sync_to_async(Text.objects.get)(slug='about')
        notification_text = await sync_to_async(Text.objects.get)(slug='notifications')
        worker_approved = await sync_to_async(Text.objects.get)(slug='worker_approved')
        search_status = await sync_to_async(Text.objects.get)(slug='search_status')
        your_profile = await sync_to_async(Text.objects.get)(slug='your_profile')
        
        reply_text = f'''
                *{your_profile.rus}*\
                \n\
                \n*{worker_approved.rus}* {readable_approved_status}\
                \n*{search_status.rus}* {readable_search_status}\
                \n*{notification_text.rus}* {readable_notifications_status}\
                \n\
                \n*{rating_text.rus}* {rating}\
                \n*{name_text.rus}* {worker.name}\
                \n*{phone_text.rus}* {worker.phone}\
                \n*{zones_text.rus}* {readable_zones}\
                \n*{min_salary_text.rus}* {worker.min_salary} ₪\
                \n*{work_type_text.rus}* {readable_work_type}\
                \n*{about_text.rus}* {worker.about}\
                '''

        try:
            await callback.message.edit_text(
                text=reply_text,
                reply_markup=await keyboards.worker_profile_keyboard(worker.id),
                parse_mode='Markdown',
            )
        except:
            pass


@router.callback_query(WorkerControlsCallBackFactory.filter(F.control == 'searching'))
async def handle_search_controls(callback: CallbackQuery, callback_data: WorkerControlsCallBackFactory):
    worker = await sync_to_async(Worker.objects.filter(tg_id=callback.from_user.id).first)()
    if worker:
        if callback_data.action == 'yes':
            worker.is_searching = True
        elif callback_data.action == 'no':
            worker.is_searching = False

        await sync_to_async(worker.save)()

        readable_approved_status = await sync_to_async(lambda: worker.readable_approved_status)()
        readable_search_status = await sync_to_async(lambda: worker.readable_search_status)()
        readable_notifications_status = await sync_to_async(lambda: worker.readable_notifications_status)()
        readable_zones = await sync_to_async(lambda: worker.readable_zones)()
        readable_work_type = await sync_to_async(lambda: worker.readable_work_type_rus)()
        rating = await sync_to_async(lambda: worker.rating_rus)()

        work_type_text = await sync_to_async(Text.objects.get)(slug='work_type')
        rating_text = await sync_to_async(Text.objects.get)(slug='rating')
        name_text = await sync_to_async(Text.objects.get)(slug='name')
        phone_text = await sync_to_async(Text.objects.get)(slug='phone')
        zones_text = await sync_to_async(Text.objects.get)(slug='zones')
        min_salary_text = await sync_to_async(Text.objects.get)(slug='min_salary')
        about_text = await sync_to_async(Text.objects.get)(slug='about')
        notification_text = await sync_to_async(Text.objects.get)(slug='notifications')
        worker_approved = await sync_to_async(Text.objects.get)(slug='worker_approved')
        search_status = await sync_to_async(Text.objects.get)(slug='search_status')
        your_profile = await sync_to_async(Text.objects.get)(slug='your_profile')
        
        reply_text = f'''
                *{your_profile.rus}*\
                \n\
                \n*{worker_approved.rus}* {readable_approved_status}\
                \n*{search_status.rus}* {readable_search_status}\
                \n*{notification_text.rus}* {readable_notifications_status}\
                \n\
                \n*{rating_text.rus}* {rating}\
                \n*{name_text.rus}* {worker.name}\
                \n*{phone_text.rus}* {worker.phone}\
                \n*{zones_text.rus}* {readable_zones}\
                \n*{min_salary_text.rus}* {worker.min_salary} ₪\
                \n*{work_type_text.rus}* {readable_work_type}\
                \n*{about_text.rus}* {worker.about}\
                '''

        try:
            await callback.message.edit_text(
                text=reply_text,
                reply_markup=await keyboards.worker_profile_keyboard(worker.id),
                parse_mode='Markdown',
            )
        except:
            pass


@cv_router.callback_query(WorkerControlsCallBackFactory.filter((F.control == 'cv') & (F.action == 'change')))
async def handle_search_controls(callback: CallbackQuery, callback_data: WorkerControlsCallBackFactory, state=FSMContext):
    worker = await sync_to_async(Worker.objects.filter(tg_id=callback.from_user.id).first)()
    if worker:
        worker.is_approved = None
        worker.about_heb = None
        worker.is_searching = True
        await sync_to_async(worker.areas.clear)()
        await sync_to_async(worker.save)()

        await state.clear()
        await state.set_state(CreateWorker.input_name)

        reply_text = await sync_to_async(Text.objects.get)(slug='worker_name')

        try:
            await callback.message.edit_text(
                    text=reply_text.rus,
                    reply_markup=InlineKeyboardBuilder().as_markup(),
                )
        except:
            pass


@router.callback_query(WorkerControlsCallBackFactory.filter((F.control == 'proposal') & (F.action == 'make')))
async def handle_search_controls(callback: CallbackQuery, callback_data: WorkerControlsCallBackFactory, state=FSMContext):
    job = await sync_to_async(Job.objects.filter(id=callback_data.object_id).first)()
    worker = await sync_to_async(Worker.objects.filter(tg_id=callback.from_user.id).first)()
    if worker and job:
        proposal = await sync_to_async(WorkerCooperationProposal.objects.filter(Q(worker=worker) & Q(job=job)).first)()
        if not proposal:
            employer = await sync_to_async(lambda: job.employer)()
            proposal = await sync_to_async(WorkerCooperationProposal.objects.create)(
                employer=employer,
                worker=worker,
                job=job,
            )

            if job.is_active and job.is_approved:
                try:
                    new_proposal_text = await sync_to_async(Text.objects.get)(slug='new_proposal')
                    await callback.bot.send_message(
                        chat_id=employer.tg_id,
                        text=f'\u202B{new_proposal_text.heb}',
                        reply_markup=await keyboards.employer_inbox_response_detail_redirect(proposal.id),
                    )
                except:
                    pass
            else:
                proposal.is_accepted = False
                await sync_to_async(proposal.save)()
        
        await callback.message.edit_reply_markup(
            reply_markup=await keyboards.worker_job_details_keyboard(job.id, worker.tg_id)
        )


@router.callback_query(WorkerControlsCallBackFactory.filter((F.control == 'proposal') & (F.action == 'resend')))
async def handle_search_controls(callback: CallbackQuery, callback_data: WorkerControlsCallBackFactory, state=FSMContext):
    job = await sync_to_async(Job.objects.filter(id=callback_data.object_id).first)()
    worker = await sync_to_async(Worker.objects.filter(tg_id=callback.from_user.id).first)()
    if worker and job:
        proposal = await sync_to_async(WorkerCooperationProposal.objects.filter(Q(worker=worker) & Q(job=job)).first)()
        if proposal:
            proposal.is_accepted = None
            proposal.is_proceeded = False
            await sync_to_async(proposal.save)()

            if job.is_active and job.is_approved:
                employer = await sync_to_async(lambda: job.employer)()
                new_proposal_text = await sync_to_async(Text.objects.get)(slug='new_proposal')
                try:
                    await callback.bot.send_message(
                        chat_id=employer.tg_id,
                        text=f'\u202B{new_proposal_text.heb}',
                        reply_markup=await keyboards.employer_inbox_response_detail_redirect(proposal.id),
                    )
                except:
                    pass
            else:
                proposal.is_accepted = False
                await sync_to_async(proposal.save)()
        
            status = await sync_to_async(lambda: proposal.readable_rus_accepted_status)()

            status_text = await sync_to_async(Text.objects.get)(slug='status')
            created_at = await sync_to_async(Text.objects.get)(slug='created_at')
            updated_at = await sync_to_async(Text.objects.get)(slug='updated_at')

            created_date = proposal.created_at.strftime('%d.%m.%Y')
            updated_date = proposal.updated_at.strftime('%d.%m.%Y')

            reply_text = f'''
                        *{status_text.rus}* {status}\
                        \n*{created_at.rus}* {created_date}\
                        \n*{updated_at.rus}* {updated_date}\
                        '''

            try:
                await callback.message.edit_text(
                    text=reply_text,
                    reply_markup=await keyboards.worker_job_detail_back(job.id, proposal.id),
                    parse_mode='Markdown',
                )
            except:
                pass


@router.callback_query(WorkerControlsCallBackFactory.filter((F.control == 'outbox-proposal') & (F.action == 'resend')))
async def handle_search_controls(callback: CallbackQuery, callback_data: WorkerControlsCallBackFactory, state=FSMContext):
    job = await sync_to_async(Job.objects.filter(id=callback_data.object_id).first)()
    worker = await sync_to_async(Worker.objects.filter(tg_id=callback.from_user.id).first)()
    if worker and job:
        proposal = await sync_to_async(WorkerCooperationProposal.objects.filter(Q(worker=worker) & Q(job=job)).first)()
        if proposal:
            proposal.is_accepted = None
            proposal.is_proceeded = False

            if job.is_active and job.is_approved:
                try:
                    employer = await sync_to_async(lambda: job.employer)()
                    employer_name = employer.name
                    new_proposal_text = await sync_to_async(Text.objects.get)(slug='new_proposal')

                    await callback.bot.send_message(
                        chat_id=employer.tg_id,
                        text=f'\u202B{new_proposal_text.heb}',
                        reply_markup=await keyboards.employer_inbox_response_detail_redirect(proposal.id),
                    )
                except:
                    pass
            else:
                proposal.is_accepted = False

            await sync_to_async(proposal.save)()

            job_text = await sync_to_async(Text.objects.get)(slug='job')
            outbox_proposal_text = await sync_to_async(Text.objects.get)(slug='outbox_proposal')

            readable_zones = await sync_to_async(lambda: job.readable_zones)()

            zones_text = await sync_to_async(Text.objects.get)(slug='zones')
            min_salary_text = await sync_to_async(Text.objects.get)(slug='min_salary')
            description_text = await sync_to_async(Text.objects.get)(slug='description')
            salary_hourly = await sync_to_async(Text.objects.get)(slug='salary_hourly')
            employer_name_text = await sync_to_async(Text.objects.get)(slug='employer_company_name')
            readable_zones = await sync_to_async(lambda: worker.readable_zones)()
            readable_work_type = await sync_to_async(lambda: job.readable_work_type_rus)()

            work_type_text = await sync_to_async(Text.objects.get)(slug='work_type')
            status = await sync_to_async(lambda: proposal.readable_rus_accepted_status)()

            status_text = await sync_to_async(Text.objects.get)(slug='status')
            created_at = await sync_to_async(Text.objects.get)(slug='created_at')
            updated_at = await sync_to_async(Text.objects.get)(slug='updated_at')

            created_date = proposal.created_at.strftime('%d.%m.%Y')
            updated_date = proposal.updated_at.strftime('%d.%m.%Y')

            reply_text = f'''
                    *{job_text.rus}*\
                    \n*{employer_name_text.rus}* {employer_name}\
                    \n*{zones_text.rus}* {readable_zones}\
                    \n*{min_salary_text.rus}* {job.min_salary} {salary_hourly.rus}\
                    \n*{work_type_text.rus}* {readable_work_type}\
                    \n*{description_text.rus}* {job.description_rus}\
                    \n\
                    \n*{outbox_proposal_text.rus}*\
                    \n*{status_text.rus}* {status}\
                    \n*{created_at.rus}* {created_date}\
                    \n*{updated_at.rus}* {updated_date}\
                    '''

            try:
                await callback.message.edit_text(
                    text=reply_text,
                    reply_markup=await keyboards.worker_outbox_proposal_details_keyboard(job.id, proposal.id),
                    parse_mode='Markdown',
                )
            except:
                pass


@router.callback_query(WorkerControlsCallBackFactory.filter((F.control == 'inbox-proposal') & (F.action.in_(['accept', 'decline']))))
async def handle_search_controls(callback: CallbackQuery, callback_data: WorkerControlsCallBackFactory, state=FSMContext):
    proposal_id = callback_data.object_id
    proposal = await sync_to_async(EmployerCooperationProposal.objects.filter(id=proposal_id).first)()
    employer = await sync_to_async(lambda: proposal.employer)()

    if proposal and employer:
        action = callback_data.action
        if action == 'accept':
            proposal.is_accepted = True
            proposal_result = await sync_to_async(Text.objects.get)(slug='proposal_accepted')
            asyncio.create_task(employer_proposal_accepted(callback.bot, proposal.id))

        elif action == 'decline':
            proposal.is_accepted = False
            proposal_result = await sync_to_async(Text.objects.get)(slug='proposal_declined')

        await sync_to_async(proposal.save)()

        try:
            employer = await sync_to_async(lambda: proposal.employer)()
            employer_name = employer.name
            await callback.bot.send_message(
                chat_id=employer.tg_id,
                text=f'\u202B{proposal_result.heb}',
                reply_markup=await keyboards.employer_outbox_response_detail_redirect(proposal.id)
            )
        except:
            pass

        employer_text = await sync_to_async(Text.objects.get)(slug='employer')
        inbox_proposal_text = await sync_to_async(Text.objects.get)(slug='inbox_proposal')
        employer_name_text = await sync_to_async(Text.objects.get)(slug='employer_company_name')

        work_type_text = await sync_to_async(Text.objects.get)(slug='work_type')
        zones_text = await sync_to_async(Text.objects.get)(slug='zones')
        zones = await sync_to_async(lambda: employer.all_offered_zones)()

        min_min_salary = await sync_to_async(lambda: employer.min_min_salary)()
        max_min_salary = await sync_to_async(lambda: employer.max_min_salary)()
        if min_min_salary == max_min_salary:
            min_salary_text = await sync_to_async(Text.objects.get)(slug='min_salary')
            salary_info = f'*{min_salary_text.rus}* {min_min_salary}'
        else:
            min_salary_text = await sync_to_async(Text.objects.get)(slug='min_min_salary')
            max_salary_text = await sync_to_async(Text.objects.get)(slug='max_min_salary')
            salary_info = f'*{min_salary_text.rus}* {min_min_salary}\n*{max_salary_text.rus}* {max_min_salary}'

        status = await sync_to_async(lambda: proposal.readable_rus_accepted_status)()
        all_work_types = await sync_to_async(lambda: employer.all_work_types)()

        status_text = await sync_to_async(Text.objects.get)(slug='status')
        created_at = await sync_to_async(Text.objects.get)(slug='created_at')
        updated_at = await sync_to_async(Text.objects.get)(slug='updated_at')

        created_date = proposal.created_at.strftime('%d.%m.%Y')
        updated_date = proposal.updated_at.strftime('%d.%m.%Y')

        rating_text = await sync_to_async(Text.objects.get)(slug='rating_employer')
        rating = await sync_to_async(lambda: employer.rating_rus)()

        reply_text = f'''
                *{employer_text.rus}*\
                \n*{employer_name_text.rus}* {employer_name}\
                \n*{zones_text.rus}* {zones}\
                \n*{work_type_text.rus}* {all_work_types}\
                \n*{rating_text.rus}* {rating}\
                \n{salary_info}\
                \n\
                \n*{inbox_proposal_text.rus}*\
                \n*{status_text.rus}* {status}\
                \n*{created_at.rus}* {created_date}\
                \n*{updated_at.rus}* {updated_date}\
                '''

        try:
            await callback.message.edit_text(
                text=reply_text,
                reply_markup=await keyboards.worker_inbox_proposal_details_keyboard(proposal.id),
                parse_mode='Markdown',
            )
        except:
            pass


@router.callback_query(WorkerControlsCallBackFactory.filter((F.control == 'review') & (F.action == 'add')))
async def handle_add_review(callback: CallbackQuery, callback_data: WorkerControlsCallBackFactory, state=FSMContext):
    await state.clear()
    await state.set_state(CreateReview.rate)
    await state.update_data(employer=callback_data.object_id)

    add_rate = await sync_to_async(Text.objects.get)(slug='add_rate')

    try:
        await callback.message.edit_text(
            text=add_rate.rus,
            reply_markup=await keyboards.worker_review_rate_keyboard(),
        )
    except:
        pass


@router.callback_query(WorkerControlsCallBackFactory.filter((F.control == 'review') & (F.action == 'rate')), CreateReview.rate)
async def handle_rate_review(callback: CallbackQuery, callback_data: WorkerControlsCallBackFactory, state=FSMContext):
    await state.set_state(CreateReview.review)
    await state.update_data(rate=callback_data.object_id)

    add_review = await sync_to_async(Text.objects.get)(slug='add_review')

    try:
        await callback.message.edit_text(
            text=add_review.rus,
            reply_markup=await keyboards.worker_review_text_keyboard(),
        )
    except:
        pass


@router.callback_query(WorkerControlsCallBackFactory.filter((F.control == 'review') & (F.action == 'text')), CreateReview.review)
async def handle_text_review(callback: CallbackQuery, callback_data: WorkerControlsCallBackFactory, state=FSMContext):
    add_text_review = await sync_to_async(Text.objects.get)(slug='add_text_review')
    await callback.message.edit_text(
        text=add_text_review.rus,
        reply_markup=InlineKeyboardBuilder().as_markup(),
    )


@router.callback_query(WorkerControlsCallBackFactory.filter((F.control == 'review') & (F.action == 'skip')), CreateReview.review)
async def handle_skip_text_review(callback: CallbackQuery, callback_data: WorkerControlsCallBackFactory, state=FSMContext):
    await state.set_state(CreateReview.confirmation)

    confirmation_text = await sync_to_async(Text.objects.get)(slug='worker_confirmation')
    rate_text = await sync_to_async(Text.objects.get)(slug='rate')
    review_text = await sync_to_async(Text.objects.get)(slug='review')
    empty_text = await sync_to_async(Text.objects.get)(slug='empty')

    state_data = await state.get_data()
    rate = state_data.get('rate')
    reply_text = f'''*{confirmation_text.rus}*\
                  \n\
                  \n*{rate_text.rus}* {rate} ⭐️\
                  \n*{review_text.rus}* {empty_text.rus}'''

    try:
        await callback.message.edit_text(
            text=reply_text,
            reply_markup=await keyboards.worker_review_confirmation_keyboard(),
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
    reply_text = f'''*{confirmation_text.rus}*\
                  \n\
                  \n*{rate_text.rus}* {rate} ⭐️\
                  \n*{review_text.rus}* {review}'''
    
    try:
        await message.answer(
            text=reply_text,
            reply_markup=await keyboards.worker_review_confirmation_keyboard(),
            parse_mode='Markdown',
        ) 
    except:
        pass  


@router.callback_query(WorkerControlsCallBackFactory.filter((F.control == 'review') & (F.action == 'retype')), CreateReview.confirmation)
async def handle_retype_review(callback: CallbackQuery, callback_data: WorkerControlsCallBackFactory, state=FSMContext):
    state_data = await state.get_data()
    employer_id = state_data.get('employer')

    await state.clear()
    await state.set_state(CreateReview.rate)
    await state.update_data(employer=employer_id)

    add_rate = await sync_to_async(Text.objects.get)(slug='add_rate')

    try:
        await callback.message.edit_text(
            text=add_rate.rus,
            reply_markup=await keyboards.worker_review_rate_keyboard(),
        )
    except:
        pass


@router.callback_query(WorkerControlsCallBackFactory.filter((F.control == 'review') & (F.action == 'confirm')), CreateReview.confirmation)
async def handle_confirm_review(callback: CallbackQuery, callback_data: WorkerControlsCallBackFactory, state=FSMContext):
    state_data = await state.get_data()

    employer_id = state_data.get('employer')
    rate = state_data.get('rate')
    review = state_data.get('review')

    prev_review = await sync_to_async(WorkerReview.objects.filter(Q(employer__id=employer_id) & Q(worker__tg_id=callback.from_user.id)).first)()
    if not prev_review:
        employer = await sync_to_async(Employer.objects.filter(id=employer_id).first)()
        worker = await sync_to_async(Worker.objects.filter(tg_id=callback.from_user.id).first)()
        new_review = await sync_to_async(WorkerReview.objects.create)(
            employer=employer,
            worker=worker,
            rate=rate,
            review=review,
        )

        review_wait_check = await sync_to_async(Text.objects.get)(slug='review_wait_check')
        try:
            await callback.message.edit_text(
                text=review_wait_check.rus,
                reply_markup=await keyboards.worker_to_main_menu_keyboard(),
            )
        except:
            pass
        
        asyncio.create_task(new_worker_review(callback.bot, new_review.id))
