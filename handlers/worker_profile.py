import os
import uuid

import django
from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from asgiref.sync import sync_to_async
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from filer.models import Image, Folder

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'work_exchange.settings')
django.setup()

from config import ADMIN_CHAT_ID, MAX_LEN
from middlewares.change_username import UpdateUsernameMiddleware
from core.models import Worker, Text, Area
from states.create_worker import CreateWorker
from keyboards import keyboards
from utils import validate_phone, validate_salary, escape_markdown
from keyboards.callbacks import (ZoneCallbackFactory, PhotoCallbackFactory, 
                                 WorkerNotificationCallbackFactory,
                                 WorkerProfileConfirmationCallbackFactory,
                                 WorkTypeCallbackFactory
                                )


router = Router()
router.callback_query.middleware(UpdateUsernameMiddleware())
router.message.middleware(UpdateUsernameMiddleware())


@router.message(F.text, CreateWorker.input_name)
async def worker_name(message: Message, state: FSMContext):
    name = await escape_markdown(message.text)

    await state.update_data(name=name)
    await state.set_state(CreateWorker.input_phone)

    reply_text = await sync_to_async(Text.objects.get)(slug='input_phone')
    try:
        await message.answer(
            text=reply_text.rus,
            reply_markup=await keyboards.request_phone_keyboard('rus'),
        )
    except:
        pass


@router.message(F.contact, CreateWorker.input_phone)
async def worker_contact(message: Message, state: FSMContext):
    phone = await validate_phone(phone = message.contact.phone_number)

    if phone:
        await state.update_data(phone=phone)
        await state.set_state(CreateWorker.input_passport_photo)

        reply_text = await sync_to_async(Text.objects.get)(slug='worker_passport_photo')
        try:
            await message.answer(
                text=reply_text.rus,
                reply_markup=ReplyKeyboardRemove(),
            )
        except:
            pass

    else:
        reply_text = await sync_to_async(Text.objects.get)(slug='wrong_phone')
        try:
            await message.reply(text=reply_text.rus)
        except:
            pass


@router.message(F.text, CreateWorker.input_phone)
async def worker_phone(message: Message, state: FSMContext):
    phone = await validate_phone(message.text)

    if phone:
        await state.update_data(phone=phone)
        await state.set_state(CreateWorker.input_passport_photo)

        reply_text = await sync_to_async(Text.objects.get)(slug='worker_passport_photo')
        try:
            await message.answer(
                text=reply_text.rus,
                reply_markup=ReplyKeyboardRemove(),
            )
        except:
            pass

    else:
        reply_text = await sync_to_async(Text.objects.get)(slug='wrong_phone')
        try:
            await message.reply(text=reply_text.rus)
        except:
            pass


@router.message(F.photo, CreateWorker.input_passport_photo)
async def worker_passport_photo(message: Message, state: FSMContext):
    photo_id = message.photo[-1].file_id
    try:
        file_info = await message.bot.get_file(photo_id)
    except:
        file_info = None
    
    if file_info:
        await state.update_data(passport_photo_id=photo_id)
        await state.update_data(passport_photo_path=file_info.file_path)
    await state.set_state(CreateWorker.input_selfie)

    reply_text = await sync_to_async(Text.objects.get)(slug='selfie')
    try:
        await message.answer(
            text=reply_text.rus,
        )
    except:
        pass


@router.message(F.photo, CreateWorker.input_selfie)
async def worker_passport_photo(message: Message, state: FSMContext):
    photo_id = message.photo[-1].file_id
    await state.update_data(selfie=photo_id)
    await state.set_state(CreateWorker.input_zones)

    reply_text = await sync_to_async(Text.objects.get)(slug='worker_zones')
    try:
        await message.answer(
            text=reply_text.rus,
            reply_markup=await keyboards.zones_keyboard('rus', state),
        )
    except:
        pass


@router.callback_query(ZoneCallbackFactory.filter(F.zone != "confirm"), CreateWorker.input_zones)
async def worker_change_zones(callback: CallbackQuery, callback_data: ZoneCallbackFactory, state: FSMContext):
    state_data = await state.get_data()
    curr_zones = state_data.get('zones', False)
    if not curr_zones:
        curr_zones = []

    if callback_data.zone in curr_zones:
        curr_zones.remove(callback_data.zone)
    else:
        curr_zones.append(callback_data.zone)
    
    await state.update_data(zones=curr_zones)
    try:
        await callback.message.edit_reply_markup(
            reply_markup=await keyboards.zones_keyboard('rus', state),
            )
    except:
        pass


@router.callback_query(ZoneCallbackFactory.filter(F.zone == "confirm"), CreateWorker.input_zones)
async def worker_confirm_zones(callback: CallbackQuery, callback_data: ZoneCallbackFactory, state: FSMContext):
    state_data = await state.get_data()
    zones = state_data.get('zones', False)

    if zones:
        await state.set_state(CreateWorker.input_about)
        reply_text = await sync_to_async(Text.objects.get)(slug='worker_about')
        try:
            await callback.message.edit_text(
                text=reply_text.rus,
                reply_markup=InlineKeyboardBuilder().as_markup(),
            )
        except:
            pass

    else:
        reply_text = await sync_to_async(Text.objects.get)(slug='need_zone')
        try:
            await callback.bot.answer_callback_query(
                callback_query_id=callback.id,
                text=reply_text.rus,
                show_alert=True,
            )
        except:
            pass


@router.message(F.text, CreateWorker.input_about)
async def worker_about(message: Message, state: FSMContext):
    about = await escape_markdown(message.text)
    about = about[:MAX_LEN]

    await state.update_data(about=about)
    await state.set_state(CreateWorker.input_min_salary)

    reply_text = await sync_to_async(Text.objects.get)(slug='worker_min_salary')
    try:
        await message.answer(
            text=reply_text.rus,
        )
    except:
        pass


@router.message(F.text, CreateWorker.input_min_salary)
async def worker_min_salary(message: Message, state: FSMContext):
    min_salary = await validate_salary(message.text)

    if min_salary:
        await state.update_data(salary=min_salary)
        await state.set_state(CreateWorker.input_work_type)

        reply_text = await sync_to_async(Text.objects.get)(slug='choose_work_type')
        try:
            await message.answer(
                text=reply_text.rus,
                reply_markup=await keyboards.work_type_keyboard('rus'),
            )
        except:
            pass

    else:
        reply_text = await sync_to_async(Text.objects.get)(slug='wrong_min_salary')
        try:
            await message.reply(text=reply_text.rus)
        except:
            pass


@router.callback_query(WorkTypeCallbackFactory.filter(), CreateWorker.input_work_type)
async def worker_work_type(callback: CallbackQuery, callback_data: WorkTypeCallbackFactory, state: FSMContext):
    if callback_data.work_type == 'permanent':
        await state.update_data(permanent=True)
    else:
        await state.update_data(permanent=False)

    await state.set_state(CreateWorker.input_notifications)

    reply_text = await sync_to_async(Text.objects.get)(slug='worker_notifications')
    try:
        await callback.message.edit_text(
            text=reply_text.rus,
            reply_markup=await keyboards.worker_notification_keyboard(),
        )
    except:
        pass


@router.callback_query(WorkerNotificationCallbackFactory.filter(), CreateWorker.input_notifications)
async def worker_notifications(callback: CallbackQuery, callback_data: WorkerNotificationCallbackFactory, state: FSMContext):
    if callback_data.action == 'yes':
        await state.update_data(notifications=True)
        notifications = 'включены'
    else:
        await state.update_data(notifications=False)
        notifications = 'отключены'

    await state.set_state(CreateWorker.confirmation)
    state_data = await state.get_data()

    recheck_text = await sync_to_async(Text.objects.get)(slug='worker_confirmation')
    name_text = await sync_to_async(Text.objects.get)(slug='name')
    phone_text = await sync_to_async(Text.objects.get)(slug='phone')
    zones_text = await sync_to_async(Text.objects.get)(slug='zones')
    min_salary_text = await sync_to_async(Text.objects.get)(slug='min_salary')
    about_text = await sync_to_async(Text.objects.get)(slug='about')
    notification_text = await sync_to_async(Text.objects.get)(slug='notifications')
    work_type_text = await sync_to_async(Text.objects.get)(slug='work_type')
    
    curr_zones = state_data.get('zones', False)
    if not curr_zones:
        curr_zones = []
    
    zones_readable = ', '.join(curr_zones)

    work_type = state_data.get('work_type')
    if work_type:
        work_type = 'постоянная'
    else:
        work_type = 'временная'

    reply_text = f'''
                *{recheck_text.rus}*\
                \n\
                \n*{name_text.rus}* {state_data.get('name', 'не указано')}\
                \n*{phone_text.rus}* {state_data.get('phone', 'не указан')}\
                \n*{zones_text.rus}* {zones_readable}\
                \n*{min_salary_text.rus}* {state_data.get('salary', 'не указана')} ₪\
                \n*{about_text.rus}* {state_data.get('about', 'не заполнено')}\
                \n*{work_type_text.rus}* {work_type}\
                \n*{notification_text.rus}* {notifications}\
                '''

    passport_photo = state_data.get('passport_photo_id', False)
    selfie = state_data.get('selfie', False)

    if selfie:
        try:
            await callback.message.answer_photo(
                photo=selfie,
            )
        except:
            pass
    try:
        await callback.message.answer_photo(
            photo=passport_photo,
            caption=reply_text,
            reply_markup=await keyboards.worker_profile_confirmation_keyboard(),
            parse_mode='Markdown',
        )
        await callback.message.delete()
    except:
        pass


@router.callback_query(WorkerProfileConfirmationCallbackFactory.filter(), CreateWorker.confirmation)
async def worker_confirmation(callback: CallbackQuery, callback_data: WorkerProfileConfirmationCallbackFactory, state: FSMContext):
    if callback_data.action == 'retype':
        await state.clear()
        await state.set_state(CreateWorker.input_name)

        reply_text = await sync_to_async(Text.objects.get)(slug='worker_name')
        try:
            await callback.message.answer(
                text=reply_text.rus,
                reply_markup=InlineKeyboardBuilder().as_markup(),
            )
            await callback.message.delete()
        except:
            pass

    elif callback_data.action == 'confirm':
        state_data = await state.get_data()

        name = state_data.get('name')
        phone = state_data.get('phone')
        min_salary = state_data.get('salary')
        about = state_data.get('about')
        work_type = state_data.get('permanent')
        passport_photo_id = state_data.get('passport_photo_id')
        passport_photo_path = state_data.get('passport_photo_path')
        notifications = state_data.get('notifications')
        zones = state_data.get('zones')
        selfie = state_data.get('selfie')

        passport_photo = None
        try:
            downloaded_file = await callback.bot.download_file(passport_photo_path)
            folder, _ = await sync_to_async(Folder.objects.get_or_create)(name="Паспорта")
            passport_photo = Image(
                folder=folder,
                original_filename=f"{callback.from_user.id}_{uuid.uuid4()}.{passport_photo_path.split('.')[-1]}",
            )
            await sync_to_async(passport_photo.file.save)(passport_photo.original_filename, downloaded_file)
            await sync_to_async(passport_photo.save)()
        except:
            pass
        
        worker = await sync_to_async(Worker.objects.filter(tg_id=callback.from_user.id).first)()

        if worker:
            worker.name = name
            worker.phone = phone
            worker.passport_photo = passport_photo
            worker.passport_photo_tg_id = passport_photo_id
            await sync_to_async(worker.areas.clear)()
            worker.about = about
            worker.min_salary = min_salary
            worker.notifications = notifications
            worker.permanent_work = work_type
            worker.selfie = selfie

        else:
            worker = await sync_to_async(Worker.objects.create)(
                tg_id=callback.from_user.id,
                name=name,
                phone=phone,
                passport_photo=passport_photo,
                passport_photo_tg_id=passport_photo_id,
                about=about,
                min_salary=min_salary,
                notifications=notifications,
                permanent_work=work_type,
                selfie = selfie,
            )

        for zone in zones:
            area = await sync_to_async(Area.objects.filter(number=int(zone)).first)()
            await sync_to_async(worker.areas.add)(area)
        
        await sync_to_async(worker.save)()
        
        readable_approved_status = await sync_to_async(lambda: worker.readable_approved_status)()
        readable_search_status = await sync_to_async(lambda: worker.readable_search_status)()
        readable_notifications_status = await sync_to_async(lambda: worker.readable_notifications_status)()
        readable_work_type = await sync_to_async(lambda: worker.readable_work_type_rus)()
        readable_zones = await sync_to_async(lambda: worker.readable_zones)()

        name_text = await sync_to_async(Text.objects.get)(slug='name')
        phone_text = await sync_to_async(Text.objects.get)(slug='phone')
        zones_text = await sync_to_async(Text.objects.get)(slug='zones')
        min_salary_text = await sync_to_async(Text.objects.get)(slug='min_salary')
        about_text = await sync_to_async(Text.objects.get)(slug='about')
        notification_text = await sync_to_async(Text.objects.get)(slug='notifications')
        worker_approved = await sync_to_async(Text.objects.get)(slug='worker_approved')
        search_status = await sync_to_async(Text.objects.get)(slug='search_status')
        your_profile = await sync_to_async(Text.objects.get)(slug='your_profile')
        work_type_text = await sync_to_async(Text.objects.get)(slug='work_type')
        
        reply_text = f'''
                *{your_profile.rus}*\
                \n\
                \n*{worker_approved.rus}* {readable_approved_status}\
                \n*{search_status.rus}* {readable_search_status}\
                \n*{notification_text.rus}* {readable_notifications_status}\
                \n\
                \n*{name_text.rus}* {name}\
                \n*{phone_text.rus}* {phone}\
                \n*{zones_text.rus}* {readable_zones}\
                \n*{min_salary_text.rus}* {min_salary} ₪\
                \n*{work_type_text.rus}* {readable_work_type}\
                \n*{about_text.rus}* {about}\
                '''
        try:
            await callback.message.answer_photo(
                photo=selfie,
            )
        except:
            pass

        try:
            await callback.message.answer(
                text=reply_text,
                reply_markup=await keyboards.worker_profile_keyboard(worker.id),
                parse_mode='Markdown',
            )
        except:
            pass

        admin_reply_text = f'''
                *Заявка на размещение резюме:*\
                \n\
                \n*{name_text.rus}* {name}\
                \n*{phone_text.rus}* {phone}\
                \n*{zones_text.rus}* {readable_zones}\
                \n*{min_salary_text.rus}* {min_salary} ₪\
                \n*{about_text.rus}* {about}\
                \n*{work_type_text.rus}* {readable_work_type}\
                \n*{notification_text.rus}* {readable_notifications_status}\
                '''

        try:
            await callback.bot.send_photo(
                chat_id=ADMIN_CHAT_ID,
                photo=selfie,
            )
        except:
            pass
        
        try:
            await callback.bot.send_photo(
                chat_id=ADMIN_CHAT_ID,
                photo=worker.passport_photo_tg_id,
                caption=admin_reply_text,
                parse_mode='Markdown',
                reply_markup=await keyboards.admin_worker_keyboard('worker', worker.id),
            )

            await callback.message.delete()
        except:
            pass
