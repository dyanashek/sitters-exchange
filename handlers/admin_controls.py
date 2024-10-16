import os

import asyncio
import django
from aiogram import Router, F
from aiogram.types import CallbackQuery
from asgiref.sync import sync_to_async
from aiogram.utils.keyboard import InlineKeyboardBuilder

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'work_exchange.settings')
django.setup()

from core.models import Worker, Text, Job, WorkerReview, EmployerReview
from keyboards.callbacks import AdminControlsCallBackFactory
from keyboards import keyboards
from utils import translate_to_heb, translate_to_rus, escape_markdown
from notifications_center import (new_worker_to_employers_channels, 
                                  new_jobs_to_workers_channels, 
                                  new_job_to_workers,
                                  new_worker_to_employers,
                                  )

router = Router()


@router.callback_query(AdminControlsCallBackFactory.filter(F.target == 'worker'))
async def admin_worker_controls(callback: CallbackQuery, callback_data: AdminControlsCallBackFactory):
    worker_id = callback_data.object_id
    worker = await sync_to_async(Worker.objects.filter(id=worker_id).first)()
    if worker:
        if callback_data.action == 'accept':
            worker.is_approved = True
            admin_reply_text = 'Резюме одобрено. Инициализирована рассылка по работодателям и каналам.'
            keyboard = await keyboards.worker_to_main_menu_keyboard()
            reply_text = await sync_to_async(Text.objects.get)(slug='worker_cv_approved')

            about_heb = await translate_to_heb(worker.about)
            if about_heb:
                about_heb = await escape_markdown(about_heb)
                worker.about_heb = about_heb
                asyncio.create_task(new_worker_to_employers_channels(callback.bot, worker, about_heb))
                asyncio.create_task(new_worker_to_employers(callback.bot, worker, about_heb))
            
        elif callback_data.action == 'decline':
            admin_reply_text = 'Резюме отклонено, пользователь уведомлен о необходимости заполнить заново.'
            worker.is_approved = False
            keyboard = await keyboards.worker_change_cv_keyboard()
            reply_text = await sync_to_async(Text.objects.get)(slug='worker_cv_declined')
        
        await sync_to_async(worker.save)()

        try:
            await callback.bot.send_message(
                chat_id=worker.tg_id,
                text=reply_text.rus,
                reply_markup=keyboard,
                )
        except:
            pass
        
        try:
            await callback.message.edit_reply_markup(reply_markup=InlineKeyboardBuilder().as_markup())
            await callback.message.reply(admin_reply_text)
        except:
            pass


@router.callback_query(AdminControlsCallBackFactory.filter(F.target == 'job'))
async def admin_job_controls(callback: CallbackQuery, callback_data: AdminControlsCallBackFactory):
    job_id = callback_data.object_id
    job = await sync_to_async(Job.objects.filter(id=job_id).first)()
    employer = await sync_to_async(lambda: job.employer)()
    if job:
        if callback_data.action == 'accept':
            job.is_approved = True
            admin_reply_text = 'Вакансия одобрена. Инициализирована рассылка по работникам и каналам.'
            reply_text = await sync_to_async(Text.objects.get)(slug='job_approved')
            keyboard = await keyboards.employer_job_detail_redirect('jobs-active', job_id)
            asyncio.create_task(new_jobs_to_workers_channels(callback.bot, job))
            asyncio.create_task(new_job_to_workers(callback.bot, job))

        elif callback_data.action == 'decline':
            admin_reply_text = 'Вакансия отклонена, работодатель уведомлен.'
            job.is_approved = False
            keyboard = await keyboards.employer_job_detail_redirect('jobs-declined', job_id)
            reply_text = await sync_to_async(Text.objects.get)(slug='job_declined')
        
        await sync_to_async(job.save)()

        try:
            await callback.bot.send_message(
                chat_id=employer.tg_id,
                text=f'\u202B{reply_text.heb}',
                reply_markup=keyboard,
                )
        except:
            pass
        
        try:
            await callback.message.edit_reply_markup(reply_markup=InlineKeyboardBuilder().as_markup())
            await callback.message.reply(admin_reply_text)
        except:
            pass


@router.callback_query(AdminControlsCallBackFactory.filter(F.target == 'employer-review'))
async def admin_review_controls(callback: CallbackQuery, callback_data: AdminControlsCallBackFactory):
    review_id = callback_data.object_id
    review = await sync_to_async(EmployerReview.objects.filter(id=review_id).first)()
    if review:
        if callback_data.action == 'accept':
            review.is_approved = True
            admin_reply_text = 'Отзыв одобрен.'
            reply_employer_text = await sync_to_async(Text.objects.get)(slug='review_accepted')
            reply_worker_text = await sync_to_async(Text.objects.get)(slug='review_new')

            
        elif callback_data.action == 'decline':
            review.is_approved = False
            admin_reply_text = 'Отзыв отклонен.'
            reply_employer_text = await sync_to_async(Text.objects.get)(slug='review_declined')
            reply_worker_text = ''
        
        await sync_to_async(review.save)()

        try:
            await callback.message.edit_reply_markup(reply_markup=InlineKeyboardBuilder().as_markup())
            await callback.message.reply(admin_reply_text)
        except:
            pass

        try:
            employer= await sync_to_async(lambda: review.employer)()
            await callback.bot.send_message(
                chat_id=employer.tg_id,
                text=f'\u202B{reply_employer_text.heb}',
                reply_markup=await keyboards.employer_outbox_review_detail_redirect(review.id),
                )
        except:
            pass

        if reply_worker_text:
            try:
                worker = await sync_to_async(lambda: review.worker)()
                await callback.bot.send_message(
                    chat_id=worker.tg_id,
                    text=reply_worker_text.rus,
                    reply_markup=await keyboards.worker_inbox_review_detail_redirect(review.id),
                    )
            except:
                pass


@router.callback_query(AdminControlsCallBackFactory.filter(F.target == 'worker-review'))
async def admin_worker_review_controls(callback: CallbackQuery, callback_data: AdminControlsCallBackFactory):
    review_id = callback_data.object_id
    review = await sync_to_async(WorkerReview.objects.filter(id=review_id).first)()
    if review:
        if callback_data.action == 'accept':
            review.is_approved = True
            admin_reply_text = 'Отзыв одобрен.'
            reply_worker_text = await sync_to_async(Text.objects.get)(slug='review_accepted')
            reply_employer_text = await sync_to_async(Text.objects.get)(slug='review_new')
            review_heb = await translate_to_heb(review.review)
            review.review_heb = review_heb
            await sync_to_async(review.save)()
            
        elif callback_data.action == 'decline':
            review.is_approved = False
            admin_reply_text = 'Отзыв отклонен.'
            reply_worker_text = await sync_to_async(Text.objects.get)(slug='review_declined')
            reply_employer_text = ''
        
        await sync_to_async(review.save)()

        try:
            await callback.message.edit_reply_markup(reply_markup=InlineKeyboardBuilder().as_markup())
            await callback.message.reply(admin_reply_text)
        except:
            pass

        try:
            worker= await sync_to_async(lambda: review.worker)()
            await callback.bot.send_message(
                chat_id=worker.tg_id,
                text=reply_worker_text.rus,
                reply_markup=await keyboards.worker_outbox_review_detail_redirect(review.id),
                )
        except:
            pass

        if reply_employer_text:
            try:
                employer = await sync_to_async(lambda: review.employer)()
                await callback.bot.send_message(
                    chat_id=employer.tg_id,
                    text=f'\u202B{reply_employer_text.heb}',
                    reply_markup=await keyboards.employer_inbox_review_detail_redirect(review.id),
                    )
            except:
                pass
