import os
import datetime

import django
from aiogram import Router, F
from aiogram.types import CallbackQuery
from asgiref.sync import sync_to_async
from aiogram.fsm.context import FSMContext

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'work_exchange.settings')
django.setup()

from config import MAX_SYMBOLS
from middlewares.change_username import UpdateUsernameMiddleware
from states.pages_navigation import PageNavigation
from core.models import Text, Job, Worker, EmployerCooperationProposal, WorkerCooperationProposal, WorkerReview, EmployerReview
from keyboards.callbacks import EmployerDetailsCallBackFactory, EmployerRedirectDetailsCallBackFactory
from keyboards import keyboards


router = Router()
router.callback_query.middleware(UpdateUsernameMiddleware())


@router.callback_query(EmployerDetailsCallBackFactory.filter(F.object_name == 'job'))
async def view_detailed_job(callback: CallbackQuery, callback_data: EmployerDetailsCallBackFactory, state=FSMContext):
    job_id = callback_data.object_id
    job = await sync_to_async(Job.objects.filter(id=job_id).first)()
    if job:
        readable_approve_status = await sync_to_async(lambda: job.readable_approved_status)()
        readable_active_status = await sync_to_async(lambda: job.readable_active_status)()
        readable_notifications_status = await sync_to_async(lambda: job.readable_notifications_heb_status)()
        readable_zones = await sync_to_async(lambda: job.readable_zones)()
        readable_work_type = await sync_to_async(lambda: job.readable_work_type_heb)()

        job_approved_text = await sync_to_async(Text.objects.get)(slug='job_approved_text')
        job_active_text = await sync_to_async(Text.objects.get)(slug='is_job_active')
        notifications_text = await sync_to_async(Text.objects.get)(slug='notifications')
        
        min_salary_text = await sync_to_async(Text.objects.get)(slug='min_salary')
        salary_hourly_text = await sync_to_async(Text.objects.get)(slug='salary_hourly')
        zones_text = await sync_to_async(Text.objects.get)(slug='zones')
        description_text = await sync_to_async(Text.objects.get)(slug='description')
        work_type_text = await sync_to_async(Text.objects.get)(slug='work_type')

        reply_text = f'''\u202B*{job_approved_text.heb}* {readable_approve_status}\
                      \n*{job_active_text.heb}* {readable_active_status}\
                      \n*{notifications_text.heb}* {readable_notifications_status}\
                      \n\
                      \n*{zones_text.heb}* {readable_zones}\
                      \n*{min_salary_text.heb}* {job.min_salary} {salary_hourly_text.heb}\
                      \n*{work_type_text.heb}* {readable_work_type}\
                      \n*{description_text.heb}* {job.description}'''

        try:
            await callback.message.edit_text(
                text=reply_text,
                reply_markup=await keyboards.employer_jobs_edit_keyboard(job.id),
                parse_mode='Markdown',
            )
        except:
            pass


@router.callback_query(EmployerRedirectDetailsCallBackFactory.filter(F.object_name == 'job'))
async def view_detailed_job_redirect(callback: CallbackQuery, callback_data: EmployerRedirectDetailsCallBackFactory, state=FSMContext):
    job_id = callback_data.object_id
    job = await sync_to_async(Job.objects.filter(id=job_id).first)()
    if job:
        await state.clear()
        await state.set_state(PageNavigation.page_navigation)
        await state.set_data({'destination': callback_data.redirect, 'page': 1})

        readable_approve_status = await sync_to_async(lambda: job.readable_approved_status)()
        readable_active_status = await sync_to_async(lambda: job.readable_active_status)()
        readable_notifications_status = await sync_to_async(lambda: job.readable_notifications_heb_status)()
        readable_zones = await sync_to_async(lambda: job.readable_zones)()
        readable_work_type = await sync_to_async(lambda: job.readable_work_type_heb)()

        job_approved_text = await sync_to_async(Text.objects.get)(slug='job_approved_text')
        job_active_text = await sync_to_async(Text.objects.get)(slug='is_job_active')
        notifications_text = await sync_to_async(Text.objects.get)(slug='notifications')
        
        min_salary_text = await sync_to_async(Text.objects.get)(slug='min_salary')
        salary_hourly_text = await sync_to_async(Text.objects.get)(slug='salary_hourly')
        zones_text = await sync_to_async(Text.objects.get)(slug='zones')
        description_text = await sync_to_async(Text.objects.get)(slug='description')
        work_type_text = await sync_to_async(Text.objects.get)(slug='work_type')

        reply_text = f'''\u202B*{job_approved_text.heb}* {readable_approve_status}\
                      \n*{job_active_text.heb}* {readable_active_status}\
                      \n*{notifications_text.heb}* {readable_notifications_status}\
                      \n\
                      \n*{zones_text.heb}* {readable_zones}\
                      \n*{min_salary_text.heb}* {job.min_salary} {salary_hourly_text.heb}\
                      \n*{work_type_text.heb}* {readable_work_type}\
                      \n*{description_text.heb}* {job.description}'''

        try:
            await callback.message.edit_text(
                text=reply_text,
                reply_markup=await keyboards.employer_jobs_edit_keyboard(job.id),
                parse_mode='Markdown',
            )
        except:
            pass


@router.callback_query(EmployerDetailsCallBackFactory.filter(F.object_name == 'worker'))
async def view_detailed_worker(callback: CallbackQuery, callback_data: EmployerDetailsCallBackFactory, state=FSMContext):
    worker_id = callback_data.object_id
    worker = await sync_to_async(Worker.objects.filter(id=worker_id).first)()
    if worker:
        readable_zones = await sync_to_async(lambda: worker.readable_zones)()

        zones_text = await sync_to_async(Text.objects.get)(slug='zones')
        min_salary_text = await sync_to_async(Text.objects.get)(slug='min_salary')
        about_text = await sync_to_async(Text.objects.get)(slug='about')
        salary_hourly = await sync_to_async(Text.objects.get)(slug='salary_hourly')
        rating_text = await sync_to_async(Text.objects.get)(slug='rating_worker')
        work_type_text = await sync_to_async(Text.objects.get)(slug='work_type')

        rating = await sync_to_async(lambda: worker.rating_heb)()
        work_type = await sync_to_async(lambda: worker.readable_work_type_heb)()

        reply_text = f'''\u202B*{zones_text.heb}* {readable_zones}\
                \n*{rating_text.heb}* {rating}\
                \n*{min_salary_text.heb}* {worker.min_salary} {salary_hourly.heb}\
                \n*{work_type_text.heb}* {work_type}\
                \n*{about_text.heb}* {worker.about_heb}'''

        try:
            await callback.message.answer_photo(
                photo=worker.selfie,
            )
        except:
            pass

        try:
            await callback.message.answer(
                text=reply_text,
                reply_markup=await keyboards.employer_worker_details_keyboard(worker.id, callback.from_user.id),
                parse_mode='Markdown',
            )
        except:
            pass

        try:
            await callback.message.delete()
        except:
            pass


@router.callback_query(EmployerRedirectDetailsCallBackFactory.filter(F.object_name == 'worker'))
async def view_detailed_worker_redirect(callback: CallbackQuery, callback_data: EmployerRedirectDetailsCallBackFactory, state=FSMContext):
    worker_id = callback_data.object_id
    worker = await sync_to_async(Worker.objects.filter(id=worker_id).first)()
    if worker:
        await state.clear()
        await state.set_state(PageNavigation.page_navigation)
        await state.set_data({'destination': callback_data.redirect, 'page': 1})
        
        readable_zones = await sync_to_async(lambda: worker.readable_zones)()

        zones_text = await sync_to_async(Text.objects.get)(slug='zones')
        min_salary_text = await sync_to_async(Text.objects.get)(slug='min_salary')
        about_text = await sync_to_async(Text.objects.get)(slug='about')
        salary_hourly = await sync_to_async(Text.objects.get)(slug='salary_hourly')
        rating_text = await sync_to_async(Text.objects.get)(slug='rating_worker')
        work_type_text = await sync_to_async(Text.objects.get)(slug='work_type')

        rating = await sync_to_async(lambda: worker.rating_heb)()
        work_type = await sync_to_async(lambda: worker.readable_work_type_heb)()
        
        reply_text = f'''\u202B*{zones_text.heb}* {readable_zones}\
                \n*{rating_text.heb}* {rating}\
                \n*{min_salary_text.heb}* {worker.min_salary} {salary_hourly.heb}\
                \n*{work_type_text.heb}* {work_type}\
                \n*{about_text.heb}* {worker.about_heb}'''

        try:
            await callback.message.answer_photo(
                photo=worker.selfie,
            )
        except:
            pass

        try:
            await callback.message.answer(
                text=reply_text,
                reply_markup=await keyboards.employer_worker_details_keyboard(worker.id, callback.from_user.id),
                parse_mode='Markdown',
            )
        except:
            pass

        try:
            await callback.message.delete()
        except:
            pass


@router.callback_query(EmployerDetailsCallBackFactory.filter(F.object_name == 'proposal'))
async def view_detailed_worker_redirect(callback: CallbackQuery, callback_data: EmployerDetailsCallBackFactory, state=FSMContext):
    proposal_id = callback_data.object_id
    proposal = await sync_to_async(EmployerCooperationProposal.objects.filter(id=proposal_id).first)()

    if proposal:
        status = await sync_to_async(lambda: proposal.readable_heb_accepted_status)()

        status_text = await sync_to_async(Text.objects.get)(slug='status')
        created_at = await sync_to_async(Text.objects.get)(slug='created_at')
        updated_at = await sync_to_async(Text.objects.get)(slug='updated_at')

        created_date = proposal.created_at.strftime('%d.%m.%Y')
        updated_date = proposal.updated_at.strftime('%d.%m.%Y')

        reply_text = f'''\u202B*{status_text.heb}* {status}\
                    \n*{created_at.heb}* {created_date}\
                    \n*{updated_at.heb}* {updated_date}'''
        
        worker = await sync_to_async(lambda: proposal.worker)()

        try:
            await callback.message.edit_text(
                text=reply_text,
                reply_markup=await keyboards.employer_worker_detail_back(worker.id, proposal.id),
                parse_mode='Markdown',
            )
        except:
            pass


@router.callback_query(EmployerDetailsCallBackFactory.filter(F.object_name == 'outbox-proposal'))
async def view_detailed_outbox_proposal(callback: CallbackQuery, callback_data: EmployerDetailsCallBackFactory, state=FSMContext):
    proposal_id = callback_data.object_id
    proposal = await sync_to_async(EmployerCooperationProposal.objects.filter(id=proposal_id).first)()
    worker = await sync_to_async(lambda: proposal.worker)()
    if worker and proposal:
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


@router.callback_query(EmployerRedirectDetailsCallBackFactory.filter(F.object_name == 'outbox-proposal'))
async def view_detailed_outbox_proposal_redirect(callback: CallbackQuery, callback_data: EmployerRedirectDetailsCallBackFactory, state=FSMContext):
    proposal_id = callback_data.object_id
    proposal = await sync_to_async(EmployerCooperationProposal.objects.filter(id=proposal_id).first)()
    worker = await sync_to_async(lambda: proposal.worker)()
    if worker and proposal:
        await state.clear()
        await state.set_state(PageNavigation.page_navigation)
        await state.set_data({'destination': callback_data.redirect, 'page': 1})

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


@router.callback_query(EmployerDetailsCallBackFactory.filter(F.object_name == 'inbox-proposal'))
async def view_detailed_inbox_proposal(callback: CallbackQuery, callback_data: EmployerDetailsCallBackFactory, state=FSMContext):
    proposal_id = callback_data.object_id
    proposal = await sync_to_async(WorkerCooperationProposal.objects.filter(id=proposal_id).first)()
    worker = await sync_to_async(lambda: proposal.worker)()
    job = await sync_to_async(lambda: proposal.job)()
    if worker and proposal:
        worker_text = await sync_to_async(Text.objects.get)(slug='worker')
        job_text = await sync_to_async(Text.objects.get)(slug='job')
        inbox_proposal_text = await sync_to_async(Text.objects.get)(slug='inbox_proposal')

        readable_zones = await sync_to_async(lambda: worker.readable_zones)()
        readable_job_zones = await sync_to_async(lambda: job.readable_zones)()

        zones_text = await sync_to_async(Text.objects.get)(slug='zones')
        min_salary_text = await sync_to_async(Text.objects.get)(slug='min_salary')
        about_text = await sync_to_async(Text.objects.get)(slug='about')
        salary_hourly = await sync_to_async(Text.objects.get)(slug='salary_hourly')
        rating_text = await sync_to_async(Text.objects.get)(slug='rating_worker')
        work_type_text = await sync_to_async(Text.objects.get)(slug='work_type')

        rating = await sync_to_async(lambda: worker.rating_heb)()
        
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
                \n*{rating_text.heb}* {rating}\
                \n*{min_salary_text.heb}* {worker.min_salary} {salary_hourly.heb}\
                \n*{work_type_text.heb}* {readable_work_type}\
                \n*{about_text.heb}* {worker.about_heb}\
                \n\
                \n*{job_text.heb}*\
                \n*{job_approved_text.heb}* {readable_approve_status}\
                \n*{job_active_text.heb}* {readable_active_status}\
                \n*{notifications_text.heb}* {readable_notifications_status}\
                \n*{zones_text.heb}* {readable_job_zones}\
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


@router.callback_query(EmployerRedirectDetailsCallBackFactory.filter(F.object_name == 'inbox-proposal'))
async def view_detailed_inbox_proposal_redirect(callback: CallbackQuery, callback_data: EmployerRedirectDetailsCallBackFactory, state=FSMContext):
    proposal_id = callback_data.object_id
    proposal = await sync_to_async(WorkerCooperationProposal.objects.filter(id=proposal_id).first)()
    worker = await sync_to_async(lambda: proposal.worker)()
    job = await sync_to_async(lambda: proposal.job)()
    if worker and proposal:
        await state.clear()
        await state.set_state(PageNavigation.page_navigation)
        await state.set_data({'destination': callback_data.redirect, 'page': 1})

        worker_text = await sync_to_async(Text.objects.get)(slug='worker')
        job_text = await sync_to_async(Text.objects.get)(slug='job')
        inbox_proposal_text = await sync_to_async(Text.objects.get)(slug='inbox_proposal')

        readable_zones = await sync_to_async(lambda: worker.readable_zones)()
        readable_zones_job = await sync_to_async(lambda: job.readable_zones)()

        zones_text = await sync_to_async(Text.objects.get)(slug='zones')
        min_salary_text = await sync_to_async(Text.objects.get)(slug='min_salary')
        about_text = await sync_to_async(Text.objects.get)(slug='about')
        salary_hourly = await sync_to_async(Text.objects.get)(slug='salary_hourly')
        rating_text = await sync_to_async(Text.objects.get)(slug='rating_worker')
        work_type_text = await sync_to_async(Text.objects.get)(slug='work_type')

        rating = await sync_to_async(lambda: worker.rating_heb)()
        readable_work_type = await sync_to_async(lambda: worker.readable_work_type_heb)()
        readable_work_type_job = await sync_to_async(lambda: job.readable_work_type_heb)()
        
        readable_approve_status = await sync_to_async(lambda: job.readable_approved_status)()
        readable_active_status = await sync_to_async(lambda: job.readable_active_status)()
        readable_notifications_status = await sync_to_async(lambda: job.readable_notifications_heb_status)()

        job_approved_text = await sync_to_async(Text.objects.get)(slug='job_approved_text')
        job_active_text = await sync_to_async(Text.objects.get)(slug='is_job_active')
        notifications_text = await sync_to_async(Text.objects.get)(slug='notifications')

        description_text = await sync_to_async(Text.objects.get)(slug='description')

        status = await sync_to_async(lambda: proposal.readable_heb_accepted_status)()

        status_text = await sync_to_async(Text.objects.get)(slug='status')
        created_at = await sync_to_async(Text.objects.get)(slug='created_at')
        updated_at = await sync_to_async(Text.objects.get)(slug='updated_at')

        created_date = proposal.created_at.strftime('%d.%m.%Y')
        updated_date = proposal.updated_at.strftime('%d.%m.%Y')

        reply_text = f'''\u202B*{worker_text.heb}*\
                \n*{zones_text.heb}* {readable_zones}\
                \n*{rating_text.heb}* {rating}\
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


@router.callback_query(EmployerDetailsCallBackFactory.filter(F.object_name == 'inbox-review'))
async def view_detailed_inbox_review(callback: CallbackQuery, callback_data: EmployerDetailsCallBackFactory, state=FSMContext):
    review_id = callback_data.object_id
    review = await sync_to_async(WorkerReview.objects.filter(id=review_id).first)()
    if review:
        title = await sync_to_async(Text.objects.get)(slug='inbox_review')

        rate_text = await sync_to_async(Text.objects.get)(slug='rate')
        review_text = await sync_to_async(Text.objects.get)(slug='review')
        created_text = await sync_to_async(Text.objects.get)(slug='created_at')

        created_date = review.created_at.strftime('%d.%m.%Y')

        comment = review.review_heb
        if not comment:
            comment = await sync_to_async(Text.objects.get)(slug='empty')
            comment = comment.heb

        reply_text = f'''\u202B*{title.heb}*\
                \n\
                \n*{created_text.heb}* {created_date}\
                \n*{rate_text.heb}* {review.rate} ⭐️\
                \n*{review_text.heb}* {comment}'''

        try:
            await callback.message.edit_text(
                text=reply_text,
                reply_markup=await keyboards.employer_reviews_back_keyboard(),
                parse_mode='Markdown',
            )
        except:
            pass


@router.callback_query(EmployerRedirectDetailsCallBackFactory.filter(F.object_name == 'inbox-review'))
async def view_detailed_inbox_review_redirect(callback: CallbackQuery, callback_data: EmployerRedirectDetailsCallBackFactory, state=FSMContext):
    review_id = callback_data.object_id
    review = await sync_to_async(WorkerReview.objects.filter(id=review_id).first)()
    if review:
        await state.clear()
        await state.set_state(PageNavigation.page_navigation)
        await state.set_data({'destination': callback_data.redirect, 'page': 1})

        title = await sync_to_async(Text.objects.get)(slug='inbox_review')

        rate_text = await sync_to_async(Text.objects.get)(slug='rate')
        review_text = await sync_to_async(Text.objects.get)(slug='review')
        created_text = await sync_to_async(Text.objects.get)(slug='created_at')

        created_date = review.created_at.strftime('%d.%m.%Y')

        comment = review.review_heb
        if not comment:
            comment = await sync_to_async(Text.objects.get)(slug='empty')
            comment = comment.heb

        reply_text = f'''\u202B*{title.heb}*\
                \n\
                \n*{created_text.heb}* {created_date}\
                \n*{rate_text.heb}* {review.rate} ⭐️\
                \n*{review_text.heb}* {comment}'''

        try:
            await callback.message.edit_text(
                text=reply_text,
                reply_markup=await keyboards.employer_reviews_back_keyboard(),
                parse_mode='Markdown',
            )
        except:
            pass


@router.callback_query(EmployerDetailsCallBackFactory.filter(F.object_name == 'outbox-review'))
async def view_detailed_outbox_review(callback: CallbackQuery, callback_data: EmployerDetailsCallBackFactory, state=FSMContext):
    review_id = callback_data.object_id
    review = await sync_to_async(EmployerReview.objects.filter(id=review_id).first)()
    if review:
        title = await sync_to_async(Text.objects.get)(slug='outbox_review')

        status_text = await sync_to_async(Text.objects.get)(slug='status')
        rate_text = await sync_to_async(Text.objects.get)(slug='rate')
        review_text = await sync_to_async(Text.objects.get)(slug='review')
        created_text = await sync_to_async(Text.objects.get)(slug='created_at')

        created_date = review.created_at.strftime('%d.%m.%Y')
        status = await sync_to_async(lambda: review.readable_approved_status)()

        comment = review.review
        if not comment:
            comment = await sync_to_async(Text.objects.get)(slug='empty')
            comment = comment.heb

        reply_text = f'''\u202B*{title.heb}*\
                \n\
                \n*{status_text.heb}* {status}\
                \n*{created_text.heb}* {created_date}\
                \n*{rate_text.heb}* {review.rate} ⭐️\
                \n*{review_text.heb}* {comment}'''

        try:
            await callback.message.edit_text(
                text=reply_text,
                reply_markup=await keyboards.employer_reviews_back_keyboard(),
                parse_mode='Markdown',
            )
        except:
            pass


@router.callback_query(EmployerRedirectDetailsCallBackFactory.filter(F.object_name == 'outbox-review'))
async def view_detailed_outbox_review_redirect(callback: CallbackQuery, callback_data: EmployerRedirectDetailsCallBackFactory, state=FSMContext):
    review_id = callback_data.object_id
    review = await sync_to_async(EmployerReview.objects.filter(id=review_id).first)()
    if review:
        await state.clear()
        await state.set_state(PageNavigation.page_navigation)
        await state.set_data({'destination': callback_data.redirect, 'page': 1})

        title = await sync_to_async(Text.objects.get)(slug='outbox_review')

        status_text = await sync_to_async(Text.objects.get)(slug='status')
        rate_text = await sync_to_async(Text.objects.get)(slug='rate')
        review_text = await sync_to_async(Text.objects.get)(slug='review')
        created_text = await sync_to_async(Text.objects.get)(slug='created_at')

        created_date = review.created_at.strftime('%d.%m.%Y')
        status = await sync_to_async(lambda: review.readable_approved_status)()

        comment = review.review
        if not comment:
            comment = await sync_to_async(Text.objects.get)(slug='empty')
            comment = comment.heb

        reply_text = f'''\u202B*{title.heb}*\
                \n\
                \n*{status_text.heb}* {status}\
                \n*{created_text.heb}* {created_date}\
                \n*{rate_text.heb}* {review.rate} ⭐️\
                \n*{review_text.heb}* {comment}'''

        try:
            await callback.message.edit_text(
                text=reply_text,
                reply_markup=await keyboards.employer_reviews_back_keyboard(),
                parse_mode='Markdown',
            )
        except:
            pass


@router.callback_query(EmployerDetailsCallBackFactory.filter(F.object_name == 'reviews(proposal)'))
async def view_detailed_employer_jobs(callback: CallbackQuery, callback_data: EmployerDetailsCallBackFactory, state=FSMContext):
    proposal_id = callback_data.object_id
    proposal = await sync_to_async(WorkerCooperationProposal.objects.filter(id=proposal_id).first)()
    worker = await sync_to_async(lambda: proposal.worker)()
    if worker:
        reviews = await sync_to_async(lambda: list(worker.received_reviews.filter(is_approved=True).all()))()
        if reviews:
            rate_text = await sync_to_async(Text.objects.get)(slug='rate')
            review_text = await sync_to_async(Text.objects.get)(slug='review')
            created_text = await sync_to_async(Text.objects.get)(slug='created_at')

            reply_texts = []
            reply_text = ''
            for review in reviews:
                comment = review.review
                if not comment:
                    comment = await sync_to_async(Text.objects.get)(slug='empty')
                    comment = comment.heb
                created_date = review.created_at.strftime('%d.%m.%Y')

                added_text = f'\n\n\u202B*{created_text.heb}* {created_date}\
                            \n*{rate_text.heb}* {review.rate} ⭐️\
                            \n*{review_text.heb}* {comment}'''
                
                if len(reply_text) + len(added_text) > MAX_SYMBOLS:
                    reply_texts.append(reply_text)
                    reply_text = added_text
                else:
                    reply_text += added_text
            
            if reply_text:
                reply_texts.append(reply_text)

            if len(reply_texts) == 1:     
                try:       
                    await callback.message.edit_text(
                        text=reply_texts[0],
                        reply_markup=await keyboards.employer_proposal_detail_back_only(proposal.id),
                        parse_mode='Markdown',
                    )
                except:
                    pass
            else:
                for num, reply_text in enumerate(reply_texts):
                    if num + 1 == len(reply_texts):
                        try:
                            await callback.message.answer(
                                text=reply_texts[0],
                                reply_markup=await keyboards.employer_proposal_detail_back_only(proposal.id),
                                parse_mode='Markdown',
                            )
                        except:
                            pass
                    else:
                        try:
                            await callback.message.answer(
                                text=reply_texts[0],
                                parse_mode='Markdown',
                            )
                        except:
                            pass
                
                try:
                    await callback.message.delete()
                except:
                    pass


@router.callback_query(EmployerDetailsCallBackFactory.filter(F.object_name == 'reviews(worker)'))
async def view_detailed_employer_jobs(callback: CallbackQuery, callback_data: EmployerDetailsCallBackFactory, state=FSMContext):
    worker_id = callback_data.object_id
    worker = await sync_to_async(Worker.objects.filter(id=worker_id).first)()
    if worker:
        reviews = await sync_to_async(lambda: list(worker.received_reviews.filter(is_approved=True).all()))()
        if reviews:
            rate_text = await sync_to_async(Text.objects.get)(slug='rate')
            review_text = await sync_to_async(Text.objects.get)(slug='review')
            created_text = await sync_to_async(Text.objects.get)(slug='created_at')

            reply_texts = []
            reply_text = ''
            for review in reviews:
                comment = review.review
                if not comment:
                    comment = await sync_to_async(Text.objects.get)(slug='empty')
                    comment = comment.heb
                created_date = review.created_at.strftime('%d.%m.%Y')

                added_text = f'\n\n\u202B*{created_text.heb}* {created_date}\
                            \n*{rate_text.heb}* {review.rate} ⭐️\
                            \n*{review_text.heb}* {comment}'''
                
                if len(reply_text) + len(added_text) > MAX_SYMBOLS:
                    reply_texts.append(reply_text)
                    reply_text = added_text
                else:
                    reply_text += added_text
            
            if reply_text:
                reply_texts.append(reply_text)

            if len(reply_texts) == 1:  
                try:          
                    await callback.message.edit_text(
                        text=reply_texts[0],
                        reply_markup=await keyboards.employer_worker_detail_back_only(worker.id),
                        parse_mode='Markdown',
                    )
                except:
                    pass
            else:
                for num, reply_text in enumerate(reply_texts):
                    if num + 1 == len(reply_texts):
                        try:
                            await callback.message.answer(
                                text=reply_texts[0],
                                reply_markup=await keyboards.employer_worker_detail_back_only(worker.id),
                                parse_mode='Markdown',
                            )
                        except:
                            pass
                    else:
                        try:
                            await callback.message.answer(
                                text=reply_texts[0],
                                parse_mode='Markdown',
                            )
                        except:
                            pass
                
                try:
                    await callback.message.delete()
                except:
                    pass
