import os
import math

import django
from django.db.models import Q
from aiogram.types import InlineKeyboardButton, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from asgiref.sync import sync_to_async
from aiogram.fsm.context import FSMContext

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'work_exchange.settings')
django.setup()

from config import BOT_NAME, PER_PAGE
from core.models import (Button, Area, Worker, Job, Employer, Text,
                         WorkerCooperationProposal, EmployerCooperationProposal,
                         WorkerReview, EmployerReview)
from keyboards.callbacks import (
    AdminControlsCallBackFactory,

    TargetCallbackFactory,
    ZoneCallbackFactory,
    PhotoCallbackFactory,
    WorkTypeCallbackFactory,

    WorkerNotificationCallbackFactory,
    WorkerProfileConfirmationCallbackFactory,
    WorkerBackCallBackFactory,
    WorkerControlsCallBackFactory,
    WorkerMainSectionsCallBackFactory,
    WorkerPagesSectionsCallBackFactory,
    WorkerDetailsCallBackFactory,
    WorkerRedirectDetailsCallBackFactory,

    EmployerBackCallBackFactory,
    EmployerControlsCallBackFactory,
    EmployerMainSectionsCallBackFactory,
    EmployerPagesSectionsCallBackFactory,
    EmployerDetailsCallBackFactory,
    EmployerRedirectDetailsCallBackFactory,
)


#* <------------------------------------------------->
#! Клавиатуры для администраторов
#* <------------------------------------------------->
async def admin_worker_keyboard(target, object_id):
    keyboard = InlineKeyboardBuilder()

    accept_kb = InlineKeyboardButton(text='Принять', callback_data=AdminControlsCallBackFactory(target=target, action='accept', object_id=object_id).pack())
    decline_kb = InlineKeyboardButton(text='Отклонить', callback_data=AdminControlsCallBackFactory(target=target, action='decline', object_id=object_id).pack())

    keyboard.row(accept_kb, decline_kb)

    return keyboard.as_markup()


#* <------------------------------------------------->
#! Клавиатуры для каналов
#* <------------------------------------------------->
async def more_workers_channel_keyboard():
    keyboard = InlineKeyboardBuilder()

    more_button = await sync_to_async(Button.objects.get)(slug='more_workers')
    keyboard.row(InlineKeyboardButton(text=f'\u202B{more_button.heb}', url=f'https://t.me/{BOT_NAME}'))

    return keyboard.as_markup()


async def more_jobs_channel_keyboard():
    keyboard = InlineKeyboardBuilder()

    more_button = await sync_to_async(Button.objects.get)(slug='more_jobs')
    keyboard.row(InlineKeyboardButton(text=more_button.rus, url=f'https://t.me/{BOT_NAME}'))

    return keyboard.as_markup()


#* <------------------------------------------------->
#! Общие клавиатуры
#* <------------------------------------------------->
async def choose_target_keyboard():
    keyboard = InlineKeyboardBuilder()

    worker_button = await sync_to_async(Button.objects.get)(slug='search_job')
    employer_button = await sync_to_async(Button.objects.get)(slug='search_workers')

    worker_kb = InlineKeyboardButton(text=worker_button.rus, callback_data=TargetCallbackFactory(target=1).pack())
    employer_kb = InlineKeyboardButton(text=f'\u202B{employer_button.heb}', callback_data=TargetCallbackFactory(target=2).pack())

    keyboard.row(worker_kb, employer_kb)

    return keyboard.as_markup()


async def request_phone_keyboard(language):
    keyboard = ReplyKeyboardBuilder()
    button = await sync_to_async(Button.objects.get)(slug='request_phone')
    if language == 'rus':
        keyboard.row(KeyboardButton(text=button.rus, request_contact=True,))
    elif language == 'heb':
        keyboard.row(KeyboardButton(text=f'\u202B{button.heb}', request_contact=True,))

    return keyboard.as_markup(resize_keyboard=True, one_time_keyboard=True,)


async def zones_keyboard(language, state: FSMContext):
    keyboard = InlineKeyboardBuilder()

    zones = await sync_to_async(lambda: list(Area.objects.all()))()
    confirm_button = await sync_to_async(Button.objects.get)(slug='confirm')

    buttons = []
    state_data = await state.get_data()
    curr_zones = state_data.get('zones', False)
    if not curr_zones:
        curr_zones = []

    for num, zone in enumerate(zones):
        symbol = ''
        if str(zone.number) in curr_zones:
            symbol = f'✅ '
        buttons.append(InlineKeyboardButton(text=f'{symbol}{str(zone.number)}', callback_data=ZoneCallbackFactory(zone=str(zone.number)).pack()))
        if (num + 1) % 3 == 0 or len(zones) == num + 1:
            keyboard.row(*buttons)
            buttons = []

    if language == 'rus':
        keyboard.row(InlineKeyboardButton(text=confirm_button.rus, callback_data=ZoneCallbackFactory(zone='confirm').pack()))
    
    elif language == 'heb':
        keyboard.row(InlineKeyboardButton(text=f'\u202B{confirm_button.heb}', callback_data=ZoneCallbackFactory(zone='confirm').pack()))

    return keyboard.as_markup()


async def work_type_keyboard(language):
    keyboard = InlineKeyboardBuilder()

    permanent_button = await sync_to_async(Button.objects.get)(slug='permanent')
    temporary_button = await sync_to_async(Button.objects.get)(slug='temporary')

    if language == 'rus':
        per_button = InlineKeyboardButton(text=f'{permanent_button.rus}', callback_data=WorkTypeCallbackFactory(work_type='permanent').pack())
        temp_button = InlineKeyboardButton(text=f'{temporary_button.rus}', callback_data=WorkTypeCallbackFactory(work_type='temporary').pack())
    elif language == 'heb':
        per_button = InlineKeyboardButton(text=f'\u202B{permanent_button.heb}', callback_data=WorkTypeCallbackFactory(work_type='permanent').pack())
        temp_button = InlineKeyboardButton(text=f'\u202B{temporary_button.heb}', callback_data=WorkTypeCallbackFactory(work_type='temporary').pack())

    keyboard.row(per_button, temp_button)

    return keyboard.as_markup()
#* <------------------------------------------------->
#! Клавиатуры для работников
#* <------------------------------------------------->
async def object_photo_keyboard():
    keyboard = InlineKeyboardBuilder()

    add_button = await sync_to_async(Button.objects.get)(slug='add_photo')
    next_button = await sync_to_async(Button.objects.get)(slug='next_step')

    keyboard.add(InlineKeyboardButton(text=add_button.rus, callback_data=PhotoCallbackFactory(action='add').pack()))
    keyboard.add(InlineKeyboardButton(text=next_button.rus, callback_data=PhotoCallbackFactory(action='next').pack()))

    return keyboard.as_markup()


async def worker_notification_keyboard():
    keyboard = InlineKeyboardBuilder()

    yes_button = await sync_to_async(Button.objects.get)(slug='yes')
    no_button = await sync_to_async(Button.objects.get)(slug='no')

    yes_kb = InlineKeyboardButton(text=yes_button.rus, callback_data=WorkerNotificationCallbackFactory(action='yes').pack())
    no_kb = InlineKeyboardButton(text=no_button.rus, callback_data=WorkerNotificationCallbackFactory(action='no').pack())

    keyboard.row(yes_kb, no_kb)

    return keyboard.as_markup()


async def worker_profile_confirmation_keyboard():
    keyboard = InlineKeyboardBuilder()

    confirm_button = await sync_to_async(Button.objects.get)(slug='confirm')
    retype_button = await sync_to_async(Button.objects.get)(slug='retype')

    keyboard.add(InlineKeyboardButton(text=confirm_button.rus, callback_data=WorkerProfileConfirmationCallbackFactory(action='confirm').pack()))
    keyboard.add(InlineKeyboardButton(text=retype_button.rus, callback_data=WorkerProfileConfirmationCallbackFactory(action='retype').pack()))

    return keyboard.as_markup()


async def worker_profile_keyboard(worker_id):
    keyboard = InlineKeyboardBuilder()
    worker = await sync_to_async(Worker.objects.filter(id=worker_id).first)()

    if worker:
        if worker.is_searching:
            searching_no = await sync_to_async(Button.objects.get)(slug='searching_no')
            keyboard.row(InlineKeyboardButton(text=searching_no.rus, callback_data=WorkerControlsCallBackFactory(control='searching', action='no').pack()))
        else:
            searching_yes = await sync_to_async(Button.objects.get)(slug='searching_yes')
            keyboard.row(InlineKeyboardButton(text=searching_yes.rus, callback_data=WorkerControlsCallBackFactory(control='searching', action='yes').pack()))

        if worker.notifications:
            disable_notifications = await sync_to_async(Button.objects.get)(slug='disable_notifications')
            keyboard.row(InlineKeyboardButton(text=disable_notifications.rus, callback_data=WorkerControlsCallBackFactory(control='notification', action='disable').pack()))
        else:
            enable_notifications = await sync_to_async(Button.objects.get)(slug='enable_notifications')
            keyboard.row(InlineKeyboardButton(text=enable_notifications.rus, callback_data=WorkerControlsCallBackFactory(control='notification', action='enable').pack()))

        change_cv = await sync_to_async(Button.objects.get)(slug='change_cv')
        main_menu = await sync_to_async(Button.objects.get)(slug='main_menu')

        keyboard.row(InlineKeyboardButton(text=change_cv.rus, callback_data=WorkerControlsCallBackFactory(control='cv', action='change').pack()))
        keyboard.row(InlineKeyboardButton(text=main_menu.rus, callback_data=WorkerBackCallBackFactory(destination='main').pack()))
    
    return keyboard.as_markup()


async def worker_change_cv_keyboard():
    keyboard = InlineKeyboardBuilder()
        
    change_cv = await sync_to_async(Button.objects.get)(slug='change_cv')
    keyboard.row(InlineKeyboardButton(text=change_cv.rus, callback_data=WorkerControlsCallBackFactory(control='cv', action='change').pack()))
    
    return keyboard.as_markup()


async def worker_to_main_menu_keyboard():
    keyboard = InlineKeyboardBuilder()

    main_menu = await sync_to_async(Button.objects.get)(slug='main_menu')
    keyboard.row(InlineKeyboardButton(text=main_menu.rus, callback_data=WorkerBackCallBackFactory(destination='main').pack()))
    
    return keyboard.as_markup()


async def worker_main_menu():
    keyboard = InlineKeyboardBuilder()

    profile = await sync_to_async(Button.objects.get)(slug='profile')
    jobs = await sync_to_async(Button.objects.get)(slug='jobs')
    proposals = await sync_to_async(Button.objects.get)(slug='cooperation_proposals')
    reviews = await sync_to_async(Button.objects.get)(slug='reviews')

    keyboard.row(InlineKeyboardButton(text=profile.rus, callback_data=WorkerMainSectionsCallBackFactory(destination='profile').pack()))
    keyboard.row(InlineKeyboardButton(text=jobs.rus, callback_data=WorkerMainSectionsCallBackFactory(destination='jobs').pack()))
    keyboard.row(InlineKeyboardButton(text=proposals.rus, callback_data=WorkerMainSectionsCallBackFactory(destination='proposals').pack()))
    keyboard.row(InlineKeyboardButton(text=reviews.rus, callback_data=WorkerMainSectionsCallBackFactory(destination='reviews').pack()))

    return keyboard.as_markup()


async def worker_jobs_menu_keyboard():
    keyboard = InlineKeyboardBuilder()

    all_jobs = await sync_to_async(Button.objects.get)(slug='all_jobs')
    suitable_jobs = await sync_to_async(Button.objects.get)(slug='jobs_suitable')
    back = await sync_to_async(Button.objects.get)(slug='back')

    keyboard.row(InlineKeyboardButton(text=all_jobs.rus, callback_data=WorkerPagesSectionsCallBackFactory(destination='all-jobs').pack()))
    keyboard.row(InlineKeyboardButton(text=suitable_jobs.rus, callback_data=WorkerPagesSectionsCallBackFactory(destination='suitable-jobs').pack()))
    keyboard.row(InlineKeyboardButton(text=back.rus, callback_data=WorkerBackCallBackFactory(destination='main').pack()))

    return keyboard.as_markup()


async def worker_proposals_menu_keyboard():
    keyboard = InlineKeyboardBuilder()

    inbox = await sync_to_async(Button.objects.get)(slug='inbox')
    outbox = await sync_to_async(Button.objects.get)(slug='outbox')
    back = await sync_to_async(Button.objects.get)(slug='back')

    keyboard.row(InlineKeyboardButton(text=inbox.rus, callback_data=WorkerPagesSectionsCallBackFactory(destination='inbox-proposals').pack()))
    keyboard.row(InlineKeyboardButton(text=outbox.rus, callback_data=WorkerPagesSectionsCallBackFactory(destination='outbox-proposals').pack()))
    keyboard.row(InlineKeyboardButton(text=back.rus, callback_data=WorkerBackCallBackFactory(destination='main').pack()))

    return keyboard.as_markup()


async def worker_reviews_menu_keyboard():
    keyboard = InlineKeyboardBuilder()

    inbox = await sync_to_async(Button.objects.get)(slug='inbox')
    outbox = await sync_to_async(Button.objects.get)(slug='outbox')
    back = await sync_to_async(Button.objects.get)(slug='back')

    keyboard.row(InlineKeyboardButton(text=inbox.rus, callback_data=WorkerPagesSectionsCallBackFactory(destination='inbox-reviews').pack()))
    keyboard.row(InlineKeyboardButton(text=outbox.rus, callback_data=WorkerPagesSectionsCallBackFactory(destination='outbox-reviews').pack()))
    keyboard.row(InlineKeyboardButton(text=back.rus, callback_data=WorkerBackCallBackFactory(destination='main').pack()))

    return keyboard.as_markup()


async def worker_jobs_list_keyboard(page, destination, user_id):
    keyboard = InlineKeyboardBuilder()

    jobs = []

    if destination == 'all-jobs':
        jobs = await sync_to_async(lambda: list(Job.objects.filter(
            Q(is_active=True) & 
            Q(is_approved=True)
            ).distinct()))()
    elif destination == 'suitable-jobs':
        worker = await sync_to_async(Worker.objects.filter(tg_id=user_id).first)()
        areas = await sync_to_async(lambda: list(worker.areas.all()))()
        jobs = await sync_to_async(lambda: list(Job.objects.filter(
            Q(areas__in=areas) &
            Q(is_active=True) & 
            Q(is_approved=True) &
            Q(min_salary__gte=worker.min_salary) &
            Q(permanent_work=worker.permanent_work)
            ).distinct()))()

    if jobs:
        jobs_count = len(jobs)
        pages_count = math.ceil(jobs_count / PER_PAGE)

        if page > pages_count:
            page = pages_count

        jobs = jobs[(page - 1) * PER_PAGE:page * PER_PAGE]
        salary_hourly = await sync_to_async(Text.objects.get)(slug='salary_hourly')

        for num, job in enumerate(jobs):
            readable_zones = await sync_to_async(lambda: job.readable_zones)()
            order_num = num + 1 + (PER_PAGE * (page -1))
            keyboard.row(InlineKeyboardButton(text=f'{order_num}. {job.min_salary} {salary_hourly.rus}: {readable_zones}', callback_data=WorkerDetailsCallBackFactory(object_name='job', object_id=job.id).pack()))

        nav = []
        if pages_count >= 2:
            if page == 1:
                nav.append(InlineKeyboardButton(text=f'<<', callback_data='nothing'))
            else:
                nav.append(InlineKeyboardButton(text=f'<<', callback_data=WorkerPagesSectionsCallBackFactory(destination=destination, page=page-1).pack()))
            nav.append(InlineKeyboardButton(text=f'\u202B{page}/{pages_count}', callback_data=f'nothing'))
            if page == pages_count:
                nav.append(InlineKeyboardButton(text=f'>>', callback_data='nothing'))
            else:
                nav.append(InlineKeyboardButton(text=f'>>', callback_data=WorkerPagesSectionsCallBackFactory(destination=destination, page=page+1).pack()))
        keyboard.row(*nav)

    back = await sync_to_async(Button.objects.get)(slug='back')
    keyboard.row(InlineKeyboardButton(text=back.rus, callback_data=WorkerMainSectionsCallBackFactory(destination='jobs').pack()))

    return keyboard.as_markup()


async def worker_job_details_keyboard(job_id, worker_tg_id):
    keyboard = InlineKeyboardBuilder()

    job = await sync_to_async(Job.objects.filter(id=job_id).first)()
    worker = await sync_to_async(Worker.objects.filter(tg_id=worker_tg_id).first)()
    if job and worker:
        proposal = await sync_to_async(WorkerCooperationProposal.objects.filter(Q(job=job) & Q(worker=worker)).first)()
        if proposal:
            view_proposal = await sync_to_async(Button.objects.get)(slug='view_proposal')
            keyboard.row(InlineKeyboardButton(text=view_proposal.rus, callback_data=WorkerDetailsCallBackFactory(object_name='proposal', object_id=proposal.id).pack()))
        else:
            make_proposal = await sync_to_async(Button.objects.get)(slug='make_proposal')
            keyboard.row(InlineKeyboardButton(text=make_proposal.rus, callback_data=WorkerControlsCallBackFactory(control='proposal', action='make', object_id=job.id).pack()))
        
        employer = await sync_to_async(lambda: job.employer)()
        reviews = await sync_to_async(lambda: list(employer.received_reviews.filter(is_approved=True).all()))()
        if reviews:
            view_reviews = await sync_to_async(Button.objects.get)(slug='view_reviews')
            keyboard.row(InlineKeyboardButton(text=view_reviews.rus, callback_data=WorkerDetailsCallBackFactory(object_name='reviews(job)', object_id=job.id).pack()))

    back = await sync_to_async(Button.objects.get)(slug='back')
    keyboard.row(InlineKeyboardButton(text=back.rus, callback_data=WorkerBackCallBackFactory(destination='jobs-list').pack()))

    return keyboard.as_markup()


async def worker_job_detail_redirect(redirect, job_id):
    keyboard = InlineKeyboardBuilder()

    job = await sync_to_async(Job.objects.filter(id=job_id).first)()
    if job:
        view = await sync_to_async(Button.objects.get)(slug='view')

        keyboard.row(InlineKeyboardButton(text=view.rus, callback_data=WorkerRedirectDetailsCallBackFactory(redirect=redirect, object_name='job', object_id=job.id).pack()))
    
    return keyboard.as_markup()


async def worker_job_detail_back(job_id, proposal_id):
    keyboard = InlineKeyboardBuilder()

    job = await sync_to_async(Job.objects.filter(id=job_id).first)()
    proposal = await sync_to_async(WorkerCooperationProposal.objects.filter(id=proposal_id).first)()
    if job and proposal:
        if proposal.is_accepted is False:
            resend_proposal = await sync_to_async(Button.objects.get)(slug='resend_proposal')
            keyboard.row(InlineKeyboardButton(text=resend_proposal.rus, callback_data=WorkerControlsCallBackFactory(control='proposal', action='resend', object_id=job.id).pack()))

        back = await sync_to_async(Button.objects.get)(slug='back')
        keyboard.row(InlineKeyboardButton(text=back.rus, callback_data=WorkerDetailsCallBackFactory(object_name='job', object_id=job.id).pack()))
    
    return keyboard.as_markup()


async def worker_proposal_detail_back_only(proposal_id):
    keyboard = InlineKeyboardBuilder()

    back = await sync_to_async(Button.objects.get)(slug='back')
    keyboard.row(InlineKeyboardButton(text=back.rus, callback_data=WorkerDetailsCallBackFactory(object_name='inbox-proposal', object_id=proposal_id).pack()))
    
    return keyboard.as_markup()


async def worker_job_detail_back_only(job_id):
    keyboard = InlineKeyboardBuilder()

    back = await sync_to_async(Button.objects.get)(slug='back')
    keyboard.row(InlineKeyboardButton(text=back.rus, callback_data=WorkerDetailsCallBackFactory(object_name='job', object_id=job_id).pack()))
    
    return keyboard.as_markup()


async def worker_proposals_list_keyboard(page, destination, user_id):
    keyboard = InlineKeyboardBuilder()

    proposals = []

    worker = await sync_to_async(Worker.objects.filter(tg_id=user_id).first)()
    if worker:
        if destination == 'outbox-proposals':
            proposal_type = 'outbox-proposal'
            proposals = await sync_to_async(lambda: list(WorkerCooperationProposal.objects.filter(
                worker=worker,
                ).distinct()))()
        elif destination == 'inbox-proposals':
            proposal_type = 'inbox-proposal'
            proposals = await sync_to_async(lambda: list(EmployerCooperationProposal.objects.filter(
                worker=worker,
                ).distinct()))()

    if proposals:
        proposals_count = len(proposals)
        pages_count = math.ceil(proposals_count / PER_PAGE)

        if page > pages_count:
            page = pages_count

        proposals = proposals[(page - 1) * PER_PAGE:page * PER_PAGE]

        for num, proposal in enumerate(proposals):
            order_num = num + 1 + (PER_PAGE * (page -1))
            updated_date = proposal.updated_at.strftime('%d.%m.%Y')
            symbol = ''
            if proposal.is_accepted is True:
                symbol = '✅'
            elif proposal.is_accepted is False:
                symbol = '❌'
            elif proposal.is_accepted is None:
                symbol = '⏳'

            keyboard.row(InlineKeyboardButton(text=f'{order_num}. {symbol} {updated_date}', callback_data=WorkerDetailsCallBackFactory(object_name=proposal_type, object_id=proposal.id).pack()))

        nav = []
        if pages_count >= 2:
            if page == 1:
                nav.append(InlineKeyboardButton(text=f'<<', callback_data='nothing'))
            else:
                nav.append(InlineKeyboardButton(text=f'<<', callback_data=WorkerPagesSectionsCallBackFactory(destination=destination, page=page-1).pack()))
            nav.append(InlineKeyboardButton(text=f'{page}/{pages_count}', callback_data=f'nothing'))
            if page == pages_count:
                nav.append(InlineKeyboardButton(text=f'>>', callback_data='nothing'))
            else:
                nav.append(InlineKeyboardButton(text=f'>>', callback_data=WorkerPagesSectionsCallBackFactory(destination=destination, page=page+1).pack()))
        keyboard.row(*nav)

    back = await sync_to_async(Button.objects.get)(slug='back')
    keyboard.row(InlineKeyboardButton(text=back.rus, callback_data=WorkerMainSectionsCallBackFactory(destination='proposals').pack()))

    return keyboard.as_markup()


async def worker_outbox_proposal_details_keyboard(job_id, proposal_id):
    keyboard = InlineKeyboardBuilder()

    job = await sync_to_async(Job.objects.filter(id=job_id).first)()
    proposal = await sync_to_async(WorkerCooperationProposal.objects.filter(id=proposal_id).first)()
    if job and proposal:
        if proposal.is_accepted is False:
            resend_proposal = await sync_to_async(Button.objects.get)(slug='resend_proposal')
            keyboard.row(InlineKeyboardButton(text=resend_proposal.rus, callback_data=WorkerControlsCallBackFactory(control='outbox-proposal', action='resend', object_id=job.id).pack()))
        elif proposal.is_accepted is True:
            employer = await sync_to_async(lambda: proposal.employer)()
            worker = await sync_to_async(lambda: proposal.worker)()
            prev_review = await sync_to_async(WorkerReview.objects.filter(Q(worker=worker) & Q(employer=employer)).first)()
            if not prev_review:
                add_review = await sync_to_async(Button.objects.get)(slug='add_review')
                keyboard.row(InlineKeyboardButton(text=add_review.rus, callback_data=WorkerControlsCallBackFactory(control='review', action='add', object_id=employer.id).pack()))
                
    back = await sync_to_async(Button.objects.get)(slug='back')
    keyboard.row(InlineKeyboardButton(text=back.rus, callback_data=WorkerBackCallBackFactory(destination='proposals-list').pack()))

    return keyboard.as_markup()


async def worker_inbox_proposal_details_keyboard(proposal_id):
    keyboard = InlineKeyboardBuilder()

    proposal = await sync_to_async(EmployerCooperationProposal.objects.filter(id=proposal_id).first)()
    if proposal:
        if proposal.is_accepted is None:
            accept = await sync_to_async(Button.objects.get)(slug='accept')
            decline = await sync_to_async(Button.objects.get)(slug='decline')
            keyboard.row(InlineKeyboardButton(text=accept.rus, callback_data=WorkerControlsCallBackFactory(control='inbox-proposal', action='accept', object_id=proposal.id).pack()))
            keyboard.row(InlineKeyboardButton(text=decline.rus, callback_data=WorkerControlsCallBackFactory(control='inbox-proposal', action='decline', object_id=proposal.id).pack()))
        elif proposal.is_accepted is True:
            employer = await sync_to_async(lambda: proposal.employer)()
            worker = await sync_to_async(lambda: proposal.worker)()
            prev_review = await sync_to_async(WorkerReview.objects.filter(Q(worker=worker) & Q(employer=employer)).first)()
            if not prev_review:
                add_review = await sync_to_async(Button.objects.get)(slug='add_review')
                keyboard.row(InlineKeyboardButton(text=add_review.rus, callback_data=WorkerControlsCallBackFactory(control='review', action='add', object_id=employer.id).pack()))

    employer = await sync_to_async(lambda: proposal.employer)()
    if employer:
        jobs = await sync_to_async(lambda: list(employer.jobs.filter(Q(is_approved=True) & Q(is_active=True)).all()))()
        if jobs:
            view_jobs = await sync_to_async(Button.objects.get)(slug='view_employer_jobs')
            keyboard.row(InlineKeyboardButton(text=view_jobs.rus, callback_data=WorkerDetailsCallBackFactory(object_name='jobs', object_id=proposal.id).pack()))

        reviews = await sync_to_async(lambda: list(employer.received_reviews.filter(is_approved=True).all()))()
        if reviews:
            view_reviews = await sync_to_async(Button.objects.get)(slug='view_reviews')
            keyboard.row(InlineKeyboardButton(text=view_reviews.rus, callback_data=WorkerDetailsCallBackFactory(object_name='reviews(proposal)', object_id=proposal.id).pack()))

    back = await sync_to_async(Button.objects.get)(slug='back')
    keyboard.row(InlineKeyboardButton(text=back.rus, callback_data=WorkerBackCallBackFactory(destination='proposals-list').pack()))

    return keyboard.as_markup()


async def worker_outbox_response_detail_redirect(proposal_id):
    keyboard = InlineKeyboardBuilder()

    proposal = await sync_to_async(WorkerCooperationProposal.objects.filter(id=proposal_id).first)()
    if proposal:
        view = await sync_to_async(Button.objects.get)(slug='view')

        keyboard.row(InlineKeyboardButton(text=view.rus, callback_data=WorkerRedirectDetailsCallBackFactory(redirect='outbox-proposals', object_name='outbox-proposal', object_id=proposal.id).pack()))
    
    return keyboard.as_markup()


async def worker_inbox_response_detail_redirect(proposal_id):
    keyboard = InlineKeyboardBuilder()

    proposal = await sync_to_async(EmployerCooperationProposal.objects.filter(id=proposal_id).first)()
    if proposal:
        view = await sync_to_async(Button.objects.get)(slug='view')

        keyboard.row(InlineKeyboardButton(text=view.rus, callback_data=WorkerRedirectDetailsCallBackFactory(redirect='inbox-proposals', object_name='inbox-proposal', object_id=proposal.id).pack()))
    
    return keyboard.as_markup()


async def worker_review_rate_keyboard():
    keyboard = InlineKeyboardBuilder()

    one = InlineKeyboardButton(text=f'1', callback_data=WorkerControlsCallBackFactory(control='review', action='rate', object_id=1).pack())
    two = InlineKeyboardButton(text=f'2', callback_data=WorkerControlsCallBackFactory(control='review', action='rate', object_id=2).pack())
    three = InlineKeyboardButton(text=f'3', callback_data=WorkerControlsCallBackFactory(control='review', action='rate', object_id=3).pack())
    four = InlineKeyboardButton(text=f'4', callback_data=WorkerControlsCallBackFactory(control='review', action='rate', object_id=4).pack())
    five = InlineKeyboardButton(text=f'5', callback_data=WorkerControlsCallBackFactory(control='review', action='rate', object_id=5).pack())

    keyboard.row(one, two, three, four, five)
    
    return keyboard.as_markup()


async def worker_review_text_keyboard():
    keyboard = InlineKeyboardBuilder()

    add_review = await sync_to_async(Button.objects.get)(slug='add_review')
    next_step = await sync_to_async(Button.objects.get)(slug='next_step')

    keyboard.row(InlineKeyboardButton(text=add_review.rus, callback_data=WorkerControlsCallBackFactory(control='review', action='text').pack()))
    keyboard.row(InlineKeyboardButton(text=next_step.rus, callback_data=WorkerControlsCallBackFactory(control='review', action='skip').pack()))
    
    return keyboard.as_markup()


async def worker_review_confirmation_keyboard():
    keyboard = InlineKeyboardBuilder()

    confirm = await sync_to_async(Button.objects.get)(slug='confirm')
    retype = await sync_to_async(Button.objects.get)(slug='retype')

    keyboard.row(InlineKeyboardButton(text=confirm.rus, callback_data=WorkerControlsCallBackFactory(control='review', action='confirm').pack()))
    keyboard.row(InlineKeyboardButton(text=retype.rus, callback_data=WorkerControlsCallBackFactory(control='review', action='retype').pack()))
    
    return keyboard.as_markup()


async def worker_reviews_list_keyboard(page, destination, user_id):
    keyboard = InlineKeyboardBuilder()

    reviews = []

    worker = await sync_to_async(Worker.objects.filter(tg_id=user_id).first)()
    if worker:
        if destination == 'outbox-reviews':
            review_type = 'outbox-review'
            reviews = await sync_to_async(lambda: list(WorkerReview.objects.filter(
                worker=worker,
                ).distinct()))()
        elif destination == 'inbox-reviews':
            review_type = 'inbox-review'
            reviews = await sync_to_async(lambda: list(EmployerReview.objects.filter(
                Q(worker=worker) &
                Q(is_approved=True)
                ).distinct()))()

    if reviews:
        reviews_count = len(reviews)
        pages_count = math.ceil(reviews_count / PER_PAGE)

        if page > pages_count:
            page = pages_count

        reviews = reviews[(page - 1) * PER_PAGE:page * PER_PAGE]

        for num, review in enumerate(reviews):
            order_num = num + 1 + (PER_PAGE * (page -1))
            created_date = review.created_at.strftime('%d.%m.%Y')
            symbol = ''
            if review.is_approved is True:
                symbol = '✅'
            elif review.is_approved is False:
                symbol = '❌'
            elif review.is_approved is None:
                symbol = '⏳'

            if review_type == 'outbox-review':
                text_button = f'{order_num}. {symbol} {created_date}'
            elif review_type == 'inbox-review':
                text_button = f'{order_num}. {created_date}'

            keyboard.row(InlineKeyboardButton(text=text_button, callback_data=WorkerDetailsCallBackFactory(object_name=review_type, object_id=review.id).pack()))

        nav = []
        if pages_count >= 2:
            if page == 1:
                nav.append(InlineKeyboardButton(text=f'<<', callback_data='nothing'))
            else:
                nav.append(InlineKeyboardButton(text=f'<<', callback_data=WorkerPagesSectionsCallBackFactory(destination=destination, page=page-1).pack()))
            nav.append(InlineKeyboardButton(text=f'{page}/{pages_count}', callback_data=f'nothing'))
            if page == pages_count:
                nav.append(InlineKeyboardButton(text=f'>>', callback_data='nothing'))
            else:
                nav.append(InlineKeyboardButton(text=f'>>', callback_data=WorkerPagesSectionsCallBackFactory(destination=destination, page=page+1).pack()))
        keyboard.row(*nav)

    back = await sync_to_async(Button.objects.get)(slug='back')
    keyboard.row(InlineKeyboardButton(text=back.rus, callback_data=WorkerMainSectionsCallBackFactory(destination='reviews').pack()))

    return keyboard.as_markup()


async def worker_reviews_back_keyboard():
    keyboard = InlineKeyboardBuilder()

    back = await sync_to_async(Button.objects.get)(slug='back')
    keyboard.row(InlineKeyboardButton(text=back.rus, callback_data=WorkerBackCallBackFactory(destination='reviews-list').pack()))

    return keyboard.as_markup()


async def worker_outbox_review_detail_redirect(review_id):
    keyboard = InlineKeyboardBuilder()

    review = await sync_to_async(WorkerReview.objects.filter(id=review_id).first)()
    if review:
        view = await sync_to_async(Button.objects.get)(slug='view')
        keyboard.row(InlineKeyboardButton(text=view.rus, callback_data=WorkerRedirectDetailsCallBackFactory(redirect='outbox-reviews', object_name='outbox-review', object_id=review.id).pack()))
    
    return keyboard.as_markup()


async def worker_inbox_review_detail_redirect(review_id):
    keyboard = InlineKeyboardBuilder()

    review = await sync_to_async(EmployerReview.objects.filter(id=review_id).first)()
    if review:
        view = await sync_to_async(Button.objects.get)(slug='view')
        keyboard.row(InlineKeyboardButton(text=view.rus, callback_data=WorkerRedirectDetailsCallBackFactory(redirect='inbox-reviews', object_name='inbox-review', object_id=review.id).pack()))
    
    return keyboard.as_markup()


#* <------------------------------------------------->
#! Клавиатуры для работодателей
#* <------------------------------------------------->
async def employer_profile_keyboard():
    keyboard = InlineKeyboardBuilder()

    change_data = await sync_to_async(Button.objects.get)(slug='change_data')
    main_menu = await sync_to_async(Button.objects.get)(slug='main_menu')

    keyboard.row(InlineKeyboardButton(text=f'\u202B{change_data.heb}', callback_data=EmployerControlsCallBackFactory(control='data', action='change').pack()))
    keyboard.row(InlineKeyboardButton(text=f'\u202B{main_menu.heb}', callback_data=EmployerBackCallBackFactory(destination='main').pack()))
    
    return keyboard.as_markup()


async def employer_main_menu():
    keyboard = InlineKeyboardBuilder()

    profile = await sync_to_async(Button.objects.get)(slug='profile')
    jobs = await sync_to_async(Button.objects.get)(slug='my_jobs')
    workers = await sync_to_async(Button.objects.get)(slug='workers')
    proposals = await sync_to_async(Button.objects.get)(slug='cooperation_proposals')
    reviews = await sync_to_async(Button.objects.get)(slug='reviews')

    keyboard.row(InlineKeyboardButton(text=f'\u202B{profile.heb}', callback_data=EmployerMainSectionsCallBackFactory(destination='profile').pack()))
    keyboard.row(InlineKeyboardButton(text=f'\u202B{jobs.heb}', callback_data=EmployerMainSectionsCallBackFactory(destination='jobs').pack()))
    keyboard.row(InlineKeyboardButton(text=f'\u202B{workers.heb}', callback_data=EmployerMainSectionsCallBackFactory(destination='workers').pack()))
    keyboard.row(InlineKeyboardButton(text=f'\u202B{proposals.heb}', callback_data=EmployerMainSectionsCallBackFactory(destination='proposals').pack()))
    keyboard.row(InlineKeyboardButton(text=f'\u202B{reviews.heb}', callback_data=EmployerMainSectionsCallBackFactory(destination='reviews').pack()))

    return keyboard.as_markup()


async def employer_jobs_menu_keyboard():
    keyboard = InlineKeyboardBuilder()

    jobs_active = await sync_to_async(Button.objects.get)(slug='jobs_active')
    jobs_archive = await sync_to_async(Button.objects.get)(slug='jobs_archive')
    jobs_declined = await sync_to_async(Button.objects.get)(slug='jobs_declined')
    job_create = await sync_to_async(Button.objects.get)(slug='job_create')
    back = await sync_to_async(Button.objects.get)(slug='back')


    keyboard.row(InlineKeyboardButton(text=f'\u202B{jobs_active.heb}', callback_data=EmployerPagesSectionsCallBackFactory(destination='jobs-active').pack()))
    keyboard.row(InlineKeyboardButton(text=f'\u202B{jobs_archive.heb}', callback_data=EmployerPagesSectionsCallBackFactory(destination='jobs-archive').pack()))
    keyboard.row(InlineKeyboardButton(text=f'\u202B{jobs_declined.heb}', callback_data=EmployerPagesSectionsCallBackFactory(destination='jobs-declined').pack()))
    keyboard.row(InlineKeyboardButton(text=f'\u202B{job_create.heb}', callback_data=EmployerControlsCallBackFactory(control='jobs', action='add').pack()))
    keyboard.row(InlineKeyboardButton(text=f'\u202B{back.heb}', callback_data=EmployerBackCallBackFactory(destination='main').pack()))

    return keyboard.as_markup()


async def employer_workers_menu_keyboard():
    keyboard = InlineKeyboardBuilder()

    workers_all = await sync_to_async(Button.objects.get)(slug='workers_all')
    workers_suitable = await sync_to_async(Button.objects.get)(slug='workers_suitable')
    back = await sync_to_async(Button.objects.get)(slug='back')


    keyboard.row(InlineKeyboardButton(text=f'\u202B{workers_all.heb}', callback_data=EmployerPagesSectionsCallBackFactory(destination='workers-all').pack()))
    keyboard.row(InlineKeyboardButton(text=f'\u202B{workers_suitable.heb}', callback_data=EmployerPagesSectionsCallBackFactory(destination='workers-suitable').pack()))
    keyboard.row(InlineKeyboardButton(text=f'\u202B{back.heb}', callback_data=EmployerBackCallBackFactory(destination='main').pack()))

    return keyboard.as_markup()


async def employer_proposals_menu_keyboard():
    keyboard = InlineKeyboardBuilder()

    inbox = await sync_to_async(Button.objects.get)(slug='inbox')
    outbox = await sync_to_async(Button.objects.get)(slug='outbox')
    back = await sync_to_async(Button.objects.get)(slug='back')


    keyboard.row(InlineKeyboardButton(text=f'\u202B{inbox.heb}', callback_data=EmployerPagesSectionsCallBackFactory(destination='inbox-proposals').pack()))
    keyboard.row(InlineKeyboardButton(text=f'\u202B{outbox.heb}', callback_data=EmployerPagesSectionsCallBackFactory(destination='outbox-proposals').pack()))
    keyboard.row(InlineKeyboardButton(text=f'\u202B{back.heb}', callback_data=EmployerBackCallBackFactory(destination='main').pack()))

    return keyboard.as_markup()


async def employer_reviews_menu_keyboard():
    keyboard = InlineKeyboardBuilder()

    inbox = await sync_to_async(Button.objects.get)(slug='inbox')
    outbox = await sync_to_async(Button.objects.get)(slug='outbox')
    back = await sync_to_async(Button.objects.get)(slug='back')


    keyboard.row(InlineKeyboardButton(text=f'\u202B{inbox.heb}', callback_data=EmployerPagesSectionsCallBackFactory(destination='inbox-reviews').pack()))
    keyboard.row(InlineKeyboardButton(text=f'\u202B{outbox.heb}', callback_data=EmployerPagesSectionsCallBackFactory(destination='outbox-reviews').pack()))
    keyboard.row(InlineKeyboardButton(text=f'\u202B{back.heb}', callback_data=EmployerBackCallBackFactory(destination='main').pack()))

    return keyboard.as_markup()


async def employer_job_notification_keyboard():
    keyboard = InlineKeyboardBuilder()

    yes_button = await sync_to_async(Button.objects.get)(slug='yes')
    no_button = await sync_to_async(Button.objects.get)(slug='no')

    no_kb = InlineKeyboardButton(text=f'\u202B{no_button.heb}', callback_data=EmployerControlsCallBackFactory(control='notifications', action='no').pack())
    yes_kb = InlineKeyboardButton(text=f'\u202B{yes_button.heb}', callback_data=EmployerControlsCallBackFactory(control='notifications', action='yes').pack())

    keyboard.row(yes_kb, no_kb)

    return keyboard.as_markup()


async def employer_job_confirmation_keyboard():
    keyboard = InlineKeyboardBuilder()

    confirm_button = await sync_to_async(Button.objects.get)(slug='confirm')
    retype_button = await sync_to_async(Button.objects.get)(slug='retype')

    keyboard.add(InlineKeyboardButton(text=f'\u202B{retype_button.heb}', callback_data=EmployerControlsCallBackFactory(control='job', action='retype').pack()))
    keyboard.add(InlineKeyboardButton(text=f'\u202B{confirm_button.heb}', callback_data=EmployerControlsCallBackFactory(control='job', action='confirm').pack()))

    return keyboard.as_markup()


async def employer_to_main_menu_keyboard():
    keyboard = InlineKeyboardBuilder()

    main_menu = await sync_to_async(Button.objects.get)(slug='main_menu')
    keyboard.row(InlineKeyboardButton(text=f'\u202B{main_menu.heb}', callback_data=EmployerBackCallBackFactory(destination='main').pack()))
    
    return keyboard.as_markup()


async def employer_to_jobs_keyboard():
    keyboard = InlineKeyboardBuilder()

    jobs = await sync_to_async(Button.objects.get)(slug='my_jobs')
    keyboard.row(InlineKeyboardButton(text=f'\u202B{jobs.heb}', callback_data=EmployerMainSectionsCallBackFactory(destination='jobs').pack()))
    
    return keyboard.as_markup()


async def employer_jobs_list_keyboard(page, destination, user_id):
    keyboard = InlineKeyboardBuilder()

    jobs = []

    employer = await sync_to_async(Employer.objects.filter(tg_id=user_id).first)()
    if employer:
        if destination == 'jobs-active':
            jobs = await sync_to_async(lambda: list(Job.objects.filter(
                Q(employer=employer) &
                Q(is_active=True) & 
                (Q(is_approved=True) | Q(is_approved__isnull=True))
                ).order_by('-updated_at').distinct()))()
        elif destination == 'jobs-archive':
            jobs = await sync_to_async(lambda: list(Job.objects.filter(
                Q(employer=employer) &
                Q(is_active=False) & 
                Q(is_approved=True)
                ).order_by('-updated_at').distinct()))()
        elif destination == 'jobs-declined':
            jobs = await sync_to_async(lambda: list(Job.objects.filter(
                Q(employer=employer) &
                Q(is_approved=False)
                ).order_by('-updated_at').distinct()))()

    if jobs:
        jobs_count = len(jobs)
        pages_count = math.ceil(jobs_count / PER_PAGE)

        if page > pages_count:
            page = pages_count

        jobs = jobs[(page - 1) * PER_PAGE:page * PER_PAGE]
        salary_hourly = await sync_to_async(Text.objects.get)(slug='salary_hourly')

        for num, job in enumerate(jobs):
            readable_zones = await sync_to_async(lambda: job.readable_zones)()
            order_num = num + 1 + (PER_PAGE * (page -1))
            keyboard.row(InlineKeyboardButton(text=f'\u202B{order_num}. {job.min_salary} {salary_hourly.heb}: {readable_zones}', callback_data=EmployerDetailsCallBackFactory(object_name='job', object_id=job.id).pack()))

        nav = []
        if pages_count >= 2:
            if page == 1:
                nav.append(InlineKeyboardButton(text=f'<<', callback_data='nothing'))
            else:
                nav.append(InlineKeyboardButton(text=f'<<', callback_data=EmployerPagesSectionsCallBackFactory(destination=destination, page=page-1).pack()))
            nav.append(InlineKeyboardButton(text=f'\u202B{page}/{pages_count}', callback_data=f'nothing'))
            if page == pages_count:
                nav.append(InlineKeyboardButton(text=f'>>', callback_data='nothing'))
            else:
                nav.append(InlineKeyboardButton(text=f'>>', callback_data=EmployerPagesSectionsCallBackFactory(destination=destination, page=page+1).pack()))
        keyboard.row(*nav)

    back = await sync_to_async(Button.objects.get)(slug='back')
    keyboard.row(InlineKeyboardButton(text=f'\u202B{back.heb}', callback_data=EmployerMainSectionsCallBackFactory(destination='jobs').pack()))

    return keyboard.as_markup()


async def employer_jobs_edit_keyboard(job_id):
    keyboard = InlineKeyboardBuilder()

    job = await sync_to_async(Job.objects.filter(id=job_id).first)()
    if job:
        activate = await sync_to_async(Button.objects.get)(slug='activate')
        deactivate = await sync_to_async(Button.objects.get)(slug='deactivate')
        enable_notifications = await sync_to_async(Button.objects.get)(slug='enable_notifications')
        disable_notifications = await sync_to_async(Button.objects.get)(slug='disable_notifications')

        if job.is_approved:
            if job.is_active:
                keyboard.row(InlineKeyboardButton(text=f'\u202B{deactivate.heb}', callback_data=EmployerControlsCallBackFactory(control='active', action='no', object_id=job_id).pack()))

                if job.notifications:
                    keyboard.row(InlineKeyboardButton(text=f'\u202B{disable_notifications.heb}', callback_data=EmployerControlsCallBackFactory(control='notification', action='disable', object_id=job_id).pack()))
                else:
                    keyboard.row(InlineKeyboardButton(text=f'\u202B{enable_notifications.heb}', callback_data=EmployerControlsCallBackFactory(control='notification', action='enable', object_id=job_id).pack()))
            else:
                keyboard.row(InlineKeyboardButton(text=f'\u202B{activate.heb}', callback_data=EmployerControlsCallBackFactory(control='active', action='yes', object_id=job_id).pack()))

    back = await sync_to_async(Button.objects.get)(slug='back')
    keyboard.row(InlineKeyboardButton(text=f'\u202B{back.heb}', callback_data=EmployerBackCallBackFactory(destination='jobs-list').pack()))

    return keyboard.as_markup()


async def employer_workers_list_keyboard(page, destination, user_id):
    keyboard = InlineKeyboardBuilder()

    workers = []

    if destination == 'workers-all':
        workers = await sync_to_async(lambda: list(Worker.objects.filter(
            Q(is_approved=True) & 
            Q(is_searching=True)
            ).distinct()))()
    elif destination == 'workers-suitable':
        employer = await sync_to_async(Employer.objects.filter(tg_id=user_id).first)()
        if employer:
            workers = []
            employer_jobs = await sync_to_async(lambda: list(employer.jobs.filter(
                Q(is_approved=True) & 
                Q(is_active=True)
                ).distinct()))()

            for job in employer_jobs:
                zones = await sync_to_async(lambda: list(job.areas.all()))()
                suitable_workers = await sync_to_async(lambda: list(Worker.objects.filter(
                    Q(is_searching=True) & 
                    Q(is_approved=True) &
                    Q(min_salary__lte=job.min_salary) &
                    Q(areas__in=zones) &
                    Q(permanent_work=job.permanent_work)
                    ).distinct()))()
                
                for worker in suitable_workers:
                    if worker not in workers:
                        workers.append(worker)

    if workers:
        workers_count = len(workers)
        pages_count = math.ceil(workers_count / PER_PAGE)

        if page > pages_count:
            page = pages_count

        workers = workers[(page - 1) * PER_PAGE:page * PER_PAGE]
        salary_hourly = await sync_to_async(Text.objects.get)(slug='salary_hourly')

        for num, worker in enumerate(workers):
            readable_zones = await sync_to_async(lambda: worker.readable_zones)()
            order_num = num + 1 + (PER_PAGE * (page -1))
            keyboard.row(InlineKeyboardButton(text=f'\u202B{order_num}. {worker.min_salary} {salary_hourly.heb}: {readable_zones}', callback_data=EmployerDetailsCallBackFactory(object_name='worker', object_id=worker.id).pack()))

        nav = []
        if pages_count >= 2:
            if page == 1:
                nav.append(InlineKeyboardButton(text=f'<<', callback_data='nothing'))
            else:
                nav.append(InlineKeyboardButton(text=f'<<', callback_data=EmployerPagesSectionsCallBackFactory(destination=destination, page=page-1).pack()))
            nav.append(InlineKeyboardButton(text=f'\u202B{page}/{pages_count}', callback_data=f'nothing'))
            if page == pages_count:
                nav.append(InlineKeyboardButton(text=f'>>', callback_data='nothing'))
            else:
                nav.append(InlineKeyboardButton(text=f'>>', callback_data=EmployerPagesSectionsCallBackFactory(destination=destination, page=page+1).pack()))
        keyboard.row(*nav)

    back = await sync_to_async(Button.objects.get)(slug='back')
    keyboard.row(InlineKeyboardButton(text=f'\u202B{back.heb}', callback_data=EmployerMainSectionsCallBackFactory(destination='workers').pack()))

    return keyboard.as_markup()


async def employer_worker_details_keyboard(worker_id, employer_tg_id):
    keyboard = InlineKeyboardBuilder()

    worker = await sync_to_async(Worker.objects.filter(id=worker_id).first)()
    employer = await sync_to_async(Employer.objects.filter(tg_id=employer_tg_id).first)()
    if worker and employer:
        proposal = await sync_to_async(EmployerCooperationProposal.objects.filter(Q(worker=worker) & Q(employer=employer)).first)()
        if proposal:
            view_proposal = await sync_to_async(Button.objects.get)(slug='view_proposal')
            keyboard.row(InlineKeyboardButton(text=f'\u202B{view_proposal.heb}', callback_data=EmployerDetailsCallBackFactory(object_name='proposal', object_id=proposal.id).pack()))
        else:
            make_proposal = await sync_to_async(Button.objects.get)(slug='make_proposal')
            keyboard.row(InlineKeyboardButton(text=f'\u202B{make_proposal.heb}', callback_data=EmployerControlsCallBackFactory(control='proposal', action='make', object_id=worker.id).pack()))

        reviews = await sync_to_async(lambda: list(worker.received_reviews.filter(is_approved=True).all()))()
        if reviews:
            view_reviews = await sync_to_async(Button.objects.get)(slug='view_reviews')
            keyboard.row(InlineKeyboardButton(text=f'\u202B{view_reviews.heb}', callback_data=EmployerDetailsCallBackFactory(object_name='reviews(worker)', object_id=worker.id).pack()))

    back = await sync_to_async(Button.objects.get)(slug='back')
    keyboard.row(InlineKeyboardButton(text=f'\u202B{back.heb}', callback_data=EmployerBackCallBackFactory(destination='workers-list').pack()))

    return keyboard.as_markup()


async def employer_job_detail_redirect(redirect, job_id):
    keyboard = InlineKeyboardBuilder()

    job = await sync_to_async(Job.objects.filter(id=job_id).first)()
    if job:
        view = await sync_to_async(Button.objects.get)(slug='view')

        keyboard.row(InlineKeyboardButton(text=f'\u202B{view.heb}', callback_data=EmployerRedirectDetailsCallBackFactory(redirect=redirect, object_name='job', object_id=job.id).pack()))
    
    return keyboard.as_markup()


async def employer_worker_detail_redirect(redirect, worker_id):
    keyboard = InlineKeyboardBuilder()

    worker = await sync_to_async(Worker.objects.filter(id=worker_id).first)()
    if worker:
        view = await sync_to_async(Button.objects.get)(slug='view')

        keyboard.row(InlineKeyboardButton(text=f'\u202B{view.heb}', callback_data=EmployerRedirectDetailsCallBackFactory(redirect=redirect, object_name='worker', object_id=worker.id).pack()))
    
    return keyboard.as_markup()


async def employer_worker_detail_back(worker_id, proposal_id):
    keyboard = InlineKeyboardBuilder()

    worker = await sync_to_async(Worker.objects.filter(id=worker_id).first)()
    proposal = await sync_to_async(EmployerCooperationProposal.objects.filter(id=proposal_id).first)()
    if worker and proposal:
        if proposal.is_accepted is False:
            resend_proposal = await sync_to_async(Button.objects.get)(slug='resend_proposal')
            keyboard.row(InlineKeyboardButton(text=f'\u202B{resend_proposal.heb}', callback_data=EmployerControlsCallBackFactory(control='proposal', action='resend', object_id=worker.id).pack()))

        back = await sync_to_async(Button.objects.get)(slug='back')
        keyboard.row(InlineKeyboardButton(text=f'\u202B{back.heb}', callback_data=EmployerDetailsCallBackFactory(object_name='worker', object_id=worker.id).pack()))
    
    return keyboard.as_markup()


async def employer_proposals_list_keyboard(page, destination, user_id):
    keyboard = InlineKeyboardBuilder()

    proposals = []

    employer = await sync_to_async(Employer.objects.filter(tg_id=user_id).first)()
    if employer:
        if destination == 'outbox-proposals':
            proposal_type = 'outbox-proposal'
            proposals = await sync_to_async(lambda: list(EmployerCooperationProposal.objects.filter(
                employer=employer,
                ).distinct()))()
        elif destination == 'inbox-proposals':
            proposal_type = 'inbox-proposal'
            proposals = await sync_to_async(lambda: list(WorkerCooperationProposal.objects.filter(
                employer=employer,
                ).distinct()))()

    if proposals:
        proposals_count = len(proposals)
        pages_count = math.ceil(proposals_count / PER_PAGE)

        if page > pages_count:
            page = pages_count

        proposals = proposals[(page - 1) * PER_PAGE:page * PER_PAGE]

        for num, proposal in enumerate(proposals):
            order_num = num + 1 + (PER_PAGE * (page -1))
            updated_date = proposal.updated_at.strftime('%d.%m.%Y')
            symbol = ''
            if proposal.is_accepted is True:
                symbol = '✅'
            elif proposal.is_accepted is False:
                symbol = '❌'
            elif proposal.is_accepted is None:
                symbol = '⏳'

            keyboard.row(InlineKeyboardButton(text=f'\u202B{updated_date} {symbol} .{order_num}', callback_data=EmployerDetailsCallBackFactory(object_name=proposal_type, object_id=proposal.id).pack()))

        nav = []
        if pages_count >= 2:
            if page == 1:
                nav.append(InlineKeyboardButton(text=f'<<', callback_data='nothing'))
            else:
                nav.append(InlineKeyboardButton(text=f'<<', callback_data=EmployerPagesSectionsCallBackFactory(destination=destination, page=page-1).pack()))
            nav.append(InlineKeyboardButton(text=f'\u202B{page}/{pages_count}', callback_data=f'nothing'))
            if page == pages_count:
                nav.append(InlineKeyboardButton(text=f'>>', callback_data='nothing'))
            else:
                nav.append(InlineKeyboardButton(text=f'>>', callback_data=EmployerPagesSectionsCallBackFactory(destination=destination, page=page+1).pack()))
        keyboard.row(*nav)

    back = await sync_to_async(Button.objects.get)(slug='back')
    keyboard.row(InlineKeyboardButton(text=f'\u202B{back.heb}', callback_data=EmployerMainSectionsCallBackFactory(destination='proposals').pack()))

    return keyboard.as_markup()


async def employer_outbox_proposal_details_keyboard(worker_id, proposal_id):
    keyboard = InlineKeyboardBuilder()

    worker = await sync_to_async(Worker.objects.filter(id=worker_id).first)()
    proposal = await sync_to_async(EmployerCooperationProposal.objects.filter(id=proposal_id).first)()
    if worker and proposal:
        if proposal.is_accepted is False:
            resend_proposal = await sync_to_async(Button.objects.get)(slug='resend_proposal')
            keyboard.row(InlineKeyboardButton(text=f'\u202B{resend_proposal.heb}', callback_data=EmployerControlsCallBackFactory(control='outbox-proposal', action='resend', object_id=worker.id).pack()))
        elif proposal.is_accepted is True:
            employer = await sync_to_async(lambda: proposal.employer)()
            prev_review = await sync_to_async(EmployerReview.objects.filter(Q(worker=worker) & Q(employer=employer)).first)()
            if not prev_review:
                add_review = await sync_to_async(Button.objects.get)(slug='add_review')
                keyboard.row(InlineKeyboardButton(text=f'\u202B{add_review.heb}', callback_data=EmployerControlsCallBackFactory(control='review', action='add', object_id=worker.id).pack()))

    back = await sync_to_async(Button.objects.get)(slug='back')
    keyboard.row(InlineKeyboardButton(text=f'\u202B{back.heb}', callback_data=EmployerBackCallBackFactory(destination='proposals-list').pack()))

    return keyboard.as_markup()


async def employer_inbox_proposal_details_keyboard(proposal_id):
    keyboard = InlineKeyboardBuilder()

    proposal = await sync_to_async(WorkerCooperationProposal.objects.filter(id=proposal_id).first)()
    if proposal:
        worker = await sync_to_async(lambda: proposal.worker)()
        if proposal.is_accepted is None:
            accept = await sync_to_async(Button.objects.get)(slug='accept')
            decline = await sync_to_async(Button.objects.get)(slug='decline')
            keyboard.row(InlineKeyboardButton(text=f'\u202B{accept.heb}', callback_data=EmployerControlsCallBackFactory(control='inbox-proposal', action='accept', object_id=proposal.id).pack()))
            keyboard.row(InlineKeyboardButton(text=f'\u202B{decline.heb}', callback_data=EmployerControlsCallBackFactory(control='inbox-proposal', action='decline', object_id=proposal.id).pack()))
        elif proposal.is_accepted is True:
            employer = await sync_to_async(lambda: proposal.employer)()
            prev_review = await sync_to_async(EmployerReview.objects.filter(Q(worker=worker) & Q(employer=employer)).first)()
            if not prev_review:
                add_review = await sync_to_async(Button.objects.get)(slug='add_review')
                keyboard.row(InlineKeyboardButton(text=f'\u202B{add_review.heb}', callback_data=EmployerControlsCallBackFactory(control='review', action='add', object_id=worker.id).pack()))

        reviews = await sync_to_async(lambda: list(worker.received_reviews.filter(is_approved=True).all()))()
        if reviews:
            view_reviews = await sync_to_async(Button.objects.get)(slug='view_reviews')
            keyboard.row(InlineKeyboardButton(text=f'\u202B{view_reviews.heb}', callback_data=EmployerDetailsCallBackFactory(object_name='reviews(proposal)', object_id=proposal.id).pack()))

    back = await sync_to_async(Button.objects.get)(slug='back')
    keyboard.row(InlineKeyboardButton(text=f'\u202B{back.heb}', callback_data=EmployerBackCallBackFactory(destination='proposals-list').pack()))

    return keyboard.as_markup()


async def employer_outbox_response_detail_redirect(proposal_id):
    keyboard = InlineKeyboardBuilder()

    proposal = await sync_to_async(EmployerCooperationProposal.objects.filter(id=proposal_id).first)()
    if proposal:
        view = await sync_to_async(Button.objects.get)(slug='view')
        keyboard.row(InlineKeyboardButton(text=f'\u202B{view.heb}', callback_data=EmployerRedirectDetailsCallBackFactory(redirect='outbox-proposals', object_name='outbox-proposal', object_id=proposal.id).pack()))
    
    return keyboard.as_markup()


async def employer_inbox_response_detail_redirect(proposal_id):
    keyboard = InlineKeyboardBuilder()

    proposal = await sync_to_async(WorkerCooperationProposal.objects.filter(id=proposal_id).first)()
    if proposal:
        view = await sync_to_async(Button.objects.get)(slug='view')
        keyboard.row(InlineKeyboardButton(text=f'\u202B{view.heb}', callback_data=EmployerRedirectDetailsCallBackFactory(redirect='inbox-proposals', object_name='inbox-proposal', object_id=proposal.id).pack()))
    
    return keyboard.as_markup()


async def employer_review_rate_keyboard():
    keyboard = InlineKeyboardBuilder()

    one = InlineKeyboardButton(text=f'1', callback_data=EmployerControlsCallBackFactory(control='review', action='rate', object_id=1).pack())
    two = InlineKeyboardButton(text=f'2', callback_data=EmployerControlsCallBackFactory(control='review', action='rate', object_id=2).pack())
    three = InlineKeyboardButton(text=f'3', callback_data=EmployerControlsCallBackFactory(control='review', action='rate', object_id=3).pack())
    four = InlineKeyboardButton(text=f'4', callback_data=EmployerControlsCallBackFactory(control='review', action='rate', object_id=4).pack())
    five = InlineKeyboardButton(text=f'5', callback_data=EmployerControlsCallBackFactory(control='review', action='rate', object_id=5).pack())

    keyboard.row(five, four, three, two, one)
    
    return keyboard.as_markup()


async def employer_review_text_keyboard():
    keyboard = InlineKeyboardBuilder()

    add_review = await sync_to_async(Button.objects.get)(slug='add_review')
    next_step = await sync_to_async(Button.objects.get)(slug='next_step')

    keyboard.row(InlineKeyboardButton(text=f'\u202B{add_review.heb}', callback_data=EmployerControlsCallBackFactory(control='review', action='text').pack()))
    keyboard.row(InlineKeyboardButton(text=f'\u202B{next_step.heb}', callback_data=EmployerControlsCallBackFactory(control='review', action='skip').pack()))
    
    return keyboard.as_markup()


async def employer_review_confirmation_keyboard():
    keyboard = InlineKeyboardBuilder()

    confirm = await sync_to_async(Button.objects.get)(slug='confirm')
    retype = await sync_to_async(Button.objects.get)(slug='retype')

    keyboard.row(InlineKeyboardButton(text=f'\u202B{confirm.heb}', callback_data=EmployerControlsCallBackFactory(control='review', action='confirm').pack()))
    keyboard.row(InlineKeyboardButton(text=f'\u202B{retype.heb}', callback_data=EmployerControlsCallBackFactory(control='review', action='retype').pack()))
    
    return keyboard.as_markup()


async def employer_reviews_list_keyboard(page, destination, user_id):
    keyboard = InlineKeyboardBuilder()

    reviews = []

    employer = await sync_to_async(Employer.objects.filter(tg_id=user_id).first)()
    if employer:
        if destination == 'outbox-reviews':
            review_type = 'outbox-review'
            reviews = await sync_to_async(lambda: list(EmployerReview.objects.filter(
                employer=employer,
                ).distinct()))()
        elif destination == 'inbox-reviews':
            review_type = 'inbox-review'
            reviews = await sync_to_async(lambda: list(WorkerReview.objects.filter(
                Q(employer=employer) &
                Q(is_approved=True)
                ).distinct()))()

    if reviews:
        reviews_count = len(reviews)
        pages_count = math.ceil(reviews_count / PER_PAGE)

        if page > pages_count:
            page = pages_count

        reviews = reviews[(page - 1) * PER_PAGE:page * PER_PAGE]

        for num, review in enumerate(reviews):
            order_num = num + 1 + (PER_PAGE * (page -1))
            created_date = review.created_at.strftime('%d.%m.%Y')
            symbol = ''
            if review.is_approved is True:
                symbol = '✅'
            elif review.is_approved is False:
                symbol = '❌'
            elif review.is_approved is None:
                symbol = '⏳'

            if review_type == 'outbox-review':
                text_button = f'\u202B{created_date} {symbol} .{order_num}'
            elif review_type == 'inbox-review':
                text_button = f'\u202B{created_date} .{order_num}'

            keyboard.row(InlineKeyboardButton(text=text_button, callback_data=EmployerDetailsCallBackFactory(object_name=review_type, object_id=review.id).pack()))

        nav = []
        if pages_count >= 2:
            if page == 1:
                nav.append(InlineKeyboardButton(text=f'<<', callback_data='nothing'))
            else:
                nav.append(InlineKeyboardButton(text=f'<<', callback_data=EmployerPagesSectionsCallBackFactory(destination=destination, page=page-1).pack()))
            nav.append(InlineKeyboardButton(text=f'\u202B{page}/{pages_count}', callback_data=f'nothing'))
            if page == pages_count:
                nav.append(InlineKeyboardButton(text=f'>>', callback_data='nothing'))
            else:
                nav.append(InlineKeyboardButton(text=f'>>', callback_data=EmployerPagesSectionsCallBackFactory(destination=destination, page=page+1).pack()))
        keyboard.row(*nav)

    back = await sync_to_async(Button.objects.get)(slug='back')
    keyboard.row(InlineKeyboardButton(text=f'\u202B{back.heb}', callback_data=EmployerMainSectionsCallBackFactory(destination='reviews').pack()))

    return keyboard.as_markup()


async def employer_reviews_back_keyboard():
    keyboard = InlineKeyboardBuilder()

    back = await sync_to_async(Button.objects.get)(slug='back')
    keyboard.row(InlineKeyboardButton(text=f'\u202B{back.heb}', callback_data=EmployerBackCallBackFactory(destination='reviews-list').pack()))

    return keyboard.as_markup()


async def employer_outbox_review_detail_redirect(review_id):
    keyboard = InlineKeyboardBuilder()

    review = await sync_to_async(EmployerReview.objects.filter(id=review_id).first)()
    if review:
        view = await sync_to_async(Button.objects.get)(slug='view')
        keyboard.row(InlineKeyboardButton(text=f'\u202B{view.heb}', callback_data=EmployerRedirectDetailsCallBackFactory(redirect='outbox-reviews', object_name='outbox-review', object_id=review.id).pack()))
    
    return keyboard.as_markup()


async def employer_inbox_review_detail_redirect(review_id):
    keyboard = InlineKeyboardBuilder()

    review = await sync_to_async(WorkerReview.objects.filter(id=review_id).first)()
    if review:
        view = await sync_to_async(Button.objects.get)(slug='view')
        keyboard.row(InlineKeyboardButton(text=f'\u202B{view.heb}', callback_data=EmployerRedirectDetailsCallBackFactory(redirect='inbox-reviews', object_name='inbox-review', object_id=review.id).pack()))
    
    return keyboard.as_markup()


async def employer_proposal_detail_back_only(proposal_id):
    keyboard = InlineKeyboardBuilder()

    back = await sync_to_async(Button.objects.get)(slug='back')
    keyboard.row(InlineKeyboardButton(text=f'\u202B{back.heb}', callback_data=EmployerDetailsCallBackFactory(object_name='inbox-proposal', object_id=proposal_id).pack()))
    
    return keyboard.as_markup()


async def employer_worker_detail_back_only(worker_id):
    keyboard = InlineKeyboardBuilder()

    back = await sync_to_async(Button.objects.get)(slug='back')
    keyboard.row(InlineKeyboardButton(text=f'\u202B{back.heb}', callback_data=EmployerDetailsCallBackFactory(object_name='worker', object_id=worker_id).pack()))
    
    return keyboard.as_markup()
