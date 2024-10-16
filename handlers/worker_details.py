import os

import django
from django.db.models import Q
from aiogram import Router, F
from aiogram.types import CallbackQuery
from asgiref.sync import sync_to_async
from aiogram.fsm.context import FSMContext

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'work_exchange.settings')
django.setup()

from config import MAX_SYMBOLS
from middlewares.change_username import UpdateUsernameMiddleware
from middlewares.worker_active_profile import IsActiveProfileMiddleware
from states.pages_navigation import PageNavigation
from core.models import (Text, Job, Employer, WorkerCooperationProposal, 
                         EmployerCooperationProposal, EmployerReview, WorkerReview)
from keyboards.callbacks import WorkerDetailsCallBackFactory, WorkerRedirectDetailsCallBackFactory
from keyboards import keyboards


router = Router()
router.callback_query.middleware(UpdateUsernameMiddleware())
router.callback_query.middleware(IsActiveProfileMiddleware())


@router.callback_query(WorkerDetailsCallBackFactory.filter(F.object_name == 'job'))
async def view_detailed_job(callback: CallbackQuery, callback_data: WorkerDetailsCallBackFactory, state=FSMContext):
    job_id = callback_data.object_id
    job = await sync_to_async(Job.objects.filter(id=job_id).first)()
    if job:
        readable_zones = await sync_to_async(lambda: job.readable_zones)()
        
        min_salary_text = await sync_to_async(Text.objects.get)(slug='min_salary')
        salary_hourly_text = await sync_to_async(Text.objects.get)(slug='salary_hourly')
        zones_text = await sync_to_async(Text.objects.get)(slug='zones')
        description_text = await sync_to_async(Text.objects.get)(slug='description')
        rating_text = await sync_to_async(Text.objects.get)(slug='rating_employer')
        work_type_text = await sync_to_async(Text.objects.get)(slug='work_type')

        employer = await sync_to_async(lambda: job.employer)()
        readable_work_type = await sync_to_async(lambda: job.readable_work_type_rus)()
        rating = await sync_to_async(lambda: employer.rating_rus)()
        employer_name_text = await sync_to_async(Text.objects.get)(slug='employer_company_name')
        
        reply_text = f'''
                      *{zones_text.rus}* {readable_zones}\
                      \n*{employer_name_text.rus}* {employer.name}\
                      \n*{rating_text.rus}* {rating}\
                      \n*{min_salary_text.rus}* {job.min_salary} {salary_hourly_text.rus}\
                      \n*{work_type_text.rus}* {readable_work_type}\
                      \n*{description_text.rus}* {job.description_rus}\
                      '''

        try:
            await callback.message.edit_text(
                text=reply_text,
                reply_markup=await keyboards.worker_job_details_keyboard(job.id, callback.from_user.id),
                parse_mode='Markdown',
            )
        except:
            pass


@router.callback_query(WorkerRedirectDetailsCallBackFactory.filter(F.object_name == 'job'))
async def view_detailed_job(callback: CallbackQuery, callback_data: WorkerRedirectDetailsCallBackFactory, state=FSMContext):
    job_id = callback_data.object_id
    job = await sync_to_async(Job.objects.filter(id=job_id).first)()
    if job:
        await state.clear()
        await state.set_state(PageNavigation.page_navigation)
        await state.set_data({'destination': callback_data.redirect, 'page': 1})
        
        readable_zones = await sync_to_async(lambda: job.readable_zones)()
        
        min_salary_text = await sync_to_async(Text.objects.get)(slug='min_salary')
        salary_hourly_text = await sync_to_async(Text.objects.get)(slug='salary_hourly')
        zones_text = await sync_to_async(Text.objects.get)(slug='zones')
        description_text = await sync_to_async(Text.objects.get)(slug='description')
        rating_text = await sync_to_async(Text.objects.get)(slug='rating_employer')
        employer_name_text = await sync_to_async(Text.objects.get)(slug='employer_company_name')
        work_type_text = await sync_to_async(Text.objects.get)(slug='work_type')

        employer = await sync_to_async(lambda: job.employer)()
        readable_work_type = await sync_to_async(lambda: job.readable_work_type_rus)()
        rating = await sync_to_async(lambda: employer.rating_rus)()

        reply_text = f'''
                      *{zones_text.rus}* {readable_zones}\
                      \n*{employer_name_text.rus}* {employer.name}\
                      \n*{rating_text.rus}* {rating}\
                      \n*{min_salary_text.rus}* {job.min_salary} {salary_hourly_text.rus}\
                      \n*{work_type_text.rus}* {readable_work_type}\
                      \n*{description_text.rus}* {job.description_rus}\
                      '''

        try:
            await callback.message.edit_text(
                text=reply_text,
                reply_markup=await keyboards.worker_job_details_keyboard(job.id, callback.from_user.id),
                parse_mode='Markdown',
            ) 
        except:
            pass


@router.callback_query(WorkerDetailsCallBackFactory.filter(F.object_name == 'proposal'))
async def view_detailed_proposal(callback: CallbackQuery, callback_data: WorkerDetailsCallBackFactory, state=FSMContext):
    proposal_id = callback_data.object_id
    proposal = await sync_to_async(WorkerCooperationProposal.objects.filter(id=proposal_id).first)()

    if proposal:
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
        
        job = await sync_to_async(lambda: proposal.job)()

        try:
            await callback.message.edit_text(
                text=reply_text,
                reply_markup=await keyboards.worker_job_detail_back(job.id, proposal_id),
                parse_mode='Markdown',
            )
        except:
            pass


@router.callback_query(WorkerDetailsCallBackFactory.filter(F.object_name == 'outbox-proposal'))
async def view_detailed_outbox_proposal(callback: CallbackQuery, callback_data: WorkerDetailsCallBackFactory, state=FSMContext):
    proposal_id = callback_data.object_id
    proposal = await sync_to_async(WorkerCooperationProposal.objects.filter(id=proposal_id).first)()
    job = await sync_to_async(lambda: proposal.job)()
    if job and proposal:
        job_text = await sync_to_async(Text.objects.get)(slug='job')
        outbox_proposal_text = await sync_to_async(Text.objects.get)(slug='outbox_proposal')

        readable_zones = await sync_to_async(lambda: job.readable_zones)()

        zones_text = await sync_to_async(Text.objects.get)(slug='zones')
        min_salary_text = await sync_to_async(Text.objects.get)(slug='min_salary')
        description_text = await sync_to_async(Text.objects.get)(slug='description')
        salary_hourly = await sync_to_async(Text.objects.get)(slug='salary_hourly')
        
        status = await sync_to_async(lambda: proposal.readable_rus_accepted_status)()
        readable_work_type = await sync_to_async(lambda: job.readable_work_type_rus)()

        status_text = await sync_to_async(Text.objects.get)(slug='status')
        created_at = await sync_to_async(Text.objects.get)(slug='created_at')
        updated_at = await sync_to_async(Text.objects.get)(slug='updated_at')

        created_date = proposal.created_at.strftime('%d.%m.%Y')
        updated_date = proposal.updated_at.strftime('%d.%m.%Y')

        rating_text = await sync_to_async(Text.objects.get)(slug='rating_employer')
        employer_name_text = await sync_to_async(Text.objects.get)(slug='employer_company_name')
        work_type_text = await sync_to_async(Text.objects.get)(slug='work_type')

        employer = await sync_to_async(lambda: job.employer)()
        rating = await sync_to_async(lambda: employer.rating_rus)()

        reply_text = f'''
                *{job_text.rus}*\
                \n*{employer_name_text.rus}* {employer.name}\
                \n*{zones_text.rus}* {readable_zones}\
                \n*{rating_text.rus}* {rating}\
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


@router.callback_query(WorkerRedirectDetailsCallBackFactory.filter(F.object_name == 'outbox-proposal'))
async def view_detailed_outbox_proposal_redirect(callback: CallbackQuery, callback_data: WorkerRedirectDetailsCallBackFactory, state=FSMContext):
    proposal_id = callback_data.object_id
    proposal = await sync_to_async(WorkerCooperationProposal.objects.filter(id=proposal_id).first)()
    job = await sync_to_async(lambda: proposal.job)()
    if job and proposal:
        await state.clear()
        await state.set_state(PageNavigation.page_navigation)
        await state.set_data({'destination': callback_data.redirect, 'page': 1})

        job_text = await sync_to_async(Text.objects.get)(slug='job')
        outbox_proposal_text = await sync_to_async(Text.objects.get)(slug='outbox_proposal')

        readable_zones = await sync_to_async(lambda: job.readable_zones)()

        zones_text = await sync_to_async(Text.objects.get)(slug='zones')
        min_salary_text = await sync_to_async(Text.objects.get)(slug='min_salary')
        description_text = await sync_to_async(Text.objects.get)(slug='description')
        salary_hourly = await sync_to_async(Text.objects.get)(slug='salary_hourly')

        status = await sync_to_async(lambda: proposal.readable_rus_accepted_status)()

        status_text = await sync_to_async(Text.objects.get)(slug='status')
        created_at = await sync_to_async(Text.objects.get)(slug='created_at')
        updated_at = await sync_to_async(Text.objects.get)(slug='updated_at')

        created_date = proposal.created_at.strftime('%d.%m.%Y')
        updated_date = proposal.updated_at.strftime('%d.%m.%Y')

        rating_text = await sync_to_async(Text.objects.get)(slug='rating_employer')
        employer_name_text = await sync_to_async(Text.objects.get)(slug='employer_company_name')
        work_type_text = await sync_to_async(Text.objects.get)(slug='work_type')

        employer = await sync_to_async(lambda: job.employer)()
        readable_work_type = await sync_to_async(lambda: job.readable_work_type_rus)()
        rating = await sync_to_async(lambda: employer.rating_rus)()

        reply_text = f'''
                *{job_text.rus}*\
                \n*{employer_name_text.rus}* {employer.name}\
                \n*{zones_text.rus}* {readable_zones}\
                \n*{rating_text.rus}* {rating}\
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


@router.callback_query(WorkerDetailsCallBackFactory.filter(F.object_name == 'inbox-proposal'))
async def view_detailed_inbox_proposal(callback: CallbackQuery, callback_data: WorkerDetailsCallBackFactory, state=FSMContext):
    proposal_id = callback_data.object_id
    proposal = await sync_to_async(EmployerCooperationProposal.objects.filter(id=proposal_id).first)()
    employer = await sync_to_async(lambda: proposal.employer)()
    if employer and proposal:
        employer_text = await sync_to_async(Text.objects.get)(slug='employer')
        inbox_proposal_text = await sync_to_async(Text.objects.get)(slug='inbox_proposal')

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
        employer_name_text = await sync_to_async(Text.objects.get)(slug='employer_company_name')

        rating = await sync_to_async(lambda: employer.rating_rus)()

        reply_text = f'''
                *{employer_text.rus}*\
                \n*{employer_name_text.rus}* {employer.name}\
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


@router.callback_query(WorkerRedirectDetailsCallBackFactory.filter(F.object_name == 'inbox-proposal'))
async def view_detailed_inbox_proposal_redirect(callback: CallbackQuery, callback_data: WorkerRedirectDetailsCallBackFactory, state=FSMContext):
    proposal_id = callback_data.object_id
    proposal = await sync_to_async(EmployerCooperationProposal.objects.filter(id=proposal_id).first)()
    employer = await sync_to_async(lambda: proposal.employer)()
    if employer and proposal:
        await state.clear()
        await state.set_state(PageNavigation.page_navigation)
        await state.set_data({'destination': callback_data.redirect, 'page': 1})

        employer_text = await sync_to_async(Text.objects.get)(slug='employer')
        inbox_proposal_text = await sync_to_async(Text.objects.get)(slug='inbox_proposal')

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

        status_text = await sync_to_async(Text.objects.get)(slug='status')
        created_at = await sync_to_async(Text.objects.get)(slug='created_at')
        updated_at = await sync_to_async(Text.objects.get)(slug='updated_at')

        created_date = proposal.created_at.strftime('%d.%m.%Y')
        updated_date = proposal.updated_at.strftime('%d.%m.%Y')

        rating_text = await sync_to_async(Text.objects.get)(slug='rating_employer')
        employer_name_text = await sync_to_async(Text.objects.get)(slug='employer_company_name')
        
        rating = await sync_to_async(lambda: employer.rating_rus)()
        all_work_types = await sync_to_async(lambda: employer.all_work_types)()

        reply_text = f'''
                *{employer_text.rus}*\
                \n*{employer_name_text.rus}* {employer.name}\
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


@router.callback_query(WorkerDetailsCallBackFactory.filter(F.object_name == 'jobs'))
async def view_detailed_employer_jobs(callback: CallbackQuery, callback_data: WorkerDetailsCallBackFactory, state=FSMContext):
    proposal_id = callback_data.object_id
    proposal = await sync_to_async(EmployerCooperationProposal.objects.filter(id=proposal_id).first)()
    if proposal:
        employer = await sync_to_async(lambda: proposal.employer)()
        jobs = await sync_to_async(lambda: list(employer.jobs.filter(Q(is_approved=True) & Q(is_active=True)).order_by('-min_salary').all()))()
        if jobs:
            min_salary_text = await sync_to_async(Text.objects.get)(slug='min_salary')
            salary_hourly_text = await sync_to_async(Text.objects.get)(slug='salary_hourly')
            zones_text = await sync_to_async(Text.objects.get)(slug='zones')
            description_text = await sync_to_async(Text.objects.get)(slug='description')
            employer_name_text = await sync_to_async(Text.objects.get)(slug='employer_company_name')
            work_type_text = await sync_to_async(Text.objects.get)(slug='work_type')

            reply_texts = []
            reply_text = f'*{employer_name_text.rus}* {employer.name}'
            for job in jobs:
                readable_zones = await sync_to_async(lambda: job.readable_zones)()
                readable_work_type = await sync_to_async(lambda: job.readable_work_type_rus)()

                added_text = f'''\n\n*{zones_text.rus}* {readable_zones}\
                                \n*{min_salary_text.rus}* {job.min_salary} {salary_hourly_text.rus}\
                                \n*{work_type_text.rus}* {readable_work_type}\
                                \n*{description_text.rus}* {job.description_rus}\
                                '''

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
                        reply_markup=await keyboards.worker_proposal_detail_back_only(proposal.id),
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
                                reply_markup=await keyboards.worker_proposal_detail_back_only(proposal.id),
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


@router.callback_query(WorkerDetailsCallBackFactory.filter(F.object_name == 'inbox-review'))
async def view_detailed_inbox_review(callback: CallbackQuery, callback_data: WorkerDetailsCallBackFactory, state=FSMContext):
    review_id = callback_data.object_id
    review = await sync_to_async(EmployerReview.objects.filter(id=review_id).first)()
    if review:
        title = await sync_to_async(Text.objects.get)(slug='inbox_review')

        rate_text = await sync_to_async(Text.objects.get)(slug='rate')
        review_text = await sync_to_async(Text.objects.get)(slug='review')
        created_text = await sync_to_async(Text.objects.get)(slug='created_at')

        created_date = review.created_at.strftime('%d.%m.%Y')

        comment = review.review_rus
        if not comment:
            comment = await sync_to_async(Text.objects.get)(slug='empty')
            comment = comment.rus

        reply_text = f'''*{title.rus}*\
                \n\
                \n*{created_text.rus}* {created_date}\
                \n*{rate_text.rus}* {review.rate} ⭐️\
                \n*{review_text.rus}* {comment}'''

        try:
            await callback.message.edit_text(
                text=reply_text,
                reply_markup=await keyboards.worker_reviews_back_keyboard(),
                parse_mode='Markdown',
            )
        except:
            pass


@router.callback_query(WorkerRedirectDetailsCallBackFactory.filter(F.object_name == 'inbox-review'))
async def view_detailed_inbox_review_redirect(callback: CallbackQuery, callback_data: WorkerRedirectDetailsCallBackFactory, state=FSMContext):
    review_id = callback_data.object_id
    review = await sync_to_async(EmployerReview.objects.filter(id=review_id).first)()
    if review:
        await state.clear()
        await state.set_state(PageNavigation.page_navigation)
        await state.set_data({'destination': callback_data.redirect, 'page': 1})

        title = await sync_to_async(Text.objects.get)(slug='inbox_review')

        rate_text = await sync_to_async(Text.objects.get)(slug='rate')
        review_text = await sync_to_async(Text.objects.get)(slug='review')
        created_text = await sync_to_async(Text.objects.get)(slug='created_at')

        created_date = review.created_at.strftime('%d.%m.%Y')

        comment = review.review_rus
        if not comment:
            comment = await sync_to_async(Text.objects.get)(slug='empty')
            comment = comment.rus

        reply_text = f'''*{title.rus}*\
                \n\
                \n*{created_text.rus}* {created_date}\
                \n*{rate_text.rus}* {review.rate} ⭐️\
                \n*{review_text.rus}* {comment}'''

        try:
            await callback.message.edit_text(
                text=reply_text,
                reply_markup=await keyboards.worker_reviews_back_keyboard(),
                parse_mode='Markdown',
            )
        except:
            pass


@router.callback_query(WorkerDetailsCallBackFactory.filter(F.object_name == 'outbox-review'))
async def view_detailed_outbox_review(callback: CallbackQuery, callback_data: WorkerDetailsCallBackFactory, state=FSMContext):
    review_id = callback_data.object_id
    review = await sync_to_async(WorkerReview.objects.filter(id=review_id).first)()
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
            comment = comment.rus

        reply_text = f'''*{title.rus}*\
                \n\
                \n*{status_text.rus}* {status}\
                \n*{created_text.rus}* {created_date}\
                \n*{rate_text.rus}* {review.rate} ⭐️\
                \n*{review_text.rus}* {comment}'''

        try:
            await callback.message.edit_text(
                text=reply_text,
                reply_markup=await keyboards.worker_reviews_back_keyboard(),
                parse_mode='Markdown',
            )
        except:
            pass


@router.callback_query(WorkerRedirectDetailsCallBackFactory.filter(F.object_name == 'outbox-review'))
async def view_detailed_outbox_review_redirect(callback: CallbackQuery, callback_data: WorkerRedirectDetailsCallBackFactory, state=FSMContext):
    review_id = callback_data.object_id
    review = await sync_to_async(WorkerReview.objects.filter(id=review_id).first)()
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
            comment = comment.rus

        reply_text = f'''*{title.rus}*\
                \n\
                \n*{status_text.rus}* {status}\
                \n*{created_text.rus}* {created_date}\
                \n*{rate_text.rus}* {review.rate} ⭐️\
                \n*{review_text.rus}* {comment}'''

        try:
            await callback.message.edit_text(
                text=reply_text,
                reply_markup=await keyboards.worker_reviews_back_keyboard(),
                parse_mode='Markdown',
            )
        except:
            pass


@router.callback_query(WorkerDetailsCallBackFactory.filter(F.object_name == 'reviews(proposal)'))
async def view_detailed_employer_jobs(callback: CallbackQuery, callback_data: WorkerDetailsCallBackFactory, state=FSMContext):
    proposal_id = callback_data.object_id
    proposal = await sync_to_async(EmployerCooperationProposal.objects.filter(id=proposal_id).first)()
    employer = await sync_to_async(lambda: proposal.employer)()
    if employer:
        reviews = await sync_to_async(lambda: list(employer.received_reviews.filter(is_approved=True).all()))()
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
                    comment = comment.rus
                created_date = review.created_at.strftime('%d.%m.%Y')

                added_text = f'\n\n*{created_text.rus}* {created_date}\
                            \n*{rate_text.rus}* {review.rate} ⭐️\
                            \n*{review_text.rus}* {comment}'''
                
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
                        reply_markup=await keyboards.worker_proposal_detail_back_only(proposal.id),
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
                                reply_markup=await keyboards.worker_proposal_detail_back_only(proposal.id),
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


@router.callback_query(WorkerDetailsCallBackFactory.filter(F.object_name == 'reviews(job)'))
async def view_detailed_employer_jobs(callback: CallbackQuery, callback_data: WorkerDetailsCallBackFactory, state=FSMContext):
    job_id = callback_data.object_id
    job = await sync_to_async(Job.objects.filter(id=job_id).first)()
    employer = await sync_to_async(lambda: job.employer)()
    if employer:
        reviews = await sync_to_async(lambda: list(employer.received_reviews.filter(is_approved=True).all()))()
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
                    comment = comment.rus
                created_date = review.created_at.strftime('%d.%m.%Y')

                added_text = f'\n\n*{created_text.rus}* {created_date}\
                            \n*{rate_text.rus}* {review.rate} ⭐️\
                            \n*{review_text.rus}* {comment}'''
                
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
                        reply_markup=await keyboards.worker_job_detail_back_only(job.id),
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
                                reply_markup=await keyboards.worker_job_detail_back_only(job.id),
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
