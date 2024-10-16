import datetime
import json
import time

from django.db.models import Q
from celery import shared_task

from core.models import TGUser
from notifications.models import Notification
from notifications.utils import send_message_on_telegram


def search_notifications():
    return Notification.objects.filter(
        Q(notify_time__lte=datetime.datetime.utcnow()) & 
        Q(is_valid=True) &
        Q(started=False)).select_related('image').all()
    

def check_notification(notification: Notification):
    is_valid = True
    for button in notification.buttons.all():
        if 'https://' not in button.link:
            is_valid = False
            break

    return is_valid
    

def mark_notifications_started(notifications):
    valid_notifications = []
    for notification in notifications:
        is_valid = check_notification(notification)
        if is_valid:
            notification.started = True
            valid_notifications.append(notification)
        else:
            notification.is_valid = False
        
        notification.save()

    return valid_notifications


def select_users_for_notification(notification: Notification):
    if notification.target == '1':
        users = [notification.user]
    elif notification.target == '2':
        users = TGUser.objects.filter(target='1').all()
    elif notification.target == '3':
        users = TGUser.objects.filter(target='2').all()
    elif notification.target == '4':
        users = TGUser.objects.all()
    
    return users


def construct_notification_params(notification: Notification):
    if notification.image:
        image_path = notification.image.path
        params_rus = {
            'caption': notification.text_rus.replace('<p>', '').replace('</p>', '').replace('<br>', '\n').replace('& nbsp;', ''),
            'parse_mode': 'HTML',
            'disable_web_page_preview': True,
        }

        params_heb = {
            'caption':  notification.text_heb.replace('<p>', '').replace('</p>', '').replace('<br>', '\n').replace('& nbsp;', ''),
            'parse_mode': 'HTML',
            'disable_web_page_preview': True,
        }

    else:
        image_path = False
        params_rus = {
                'text': notification.text_rus.replace('<p>', '').replace('</p>', '').replace('<br>', '\n').replace('& nbsp;', ''),
                'parse_mode': 'HTML',
                'disable_web_page_preview': True,
            }
        
        text_heb = notification.text_heb.replace('<p>', '').replace('</p>', '').replace('<br>', '\n').replace('& nbsp;', '')
        params_heb = {
                'text': f'\u202B{text_heb}',
                'parse_mode': 'HTML',
                'disable_web_page_preview': True,
            }
    
    if notification.buttons.all():
        buttons_rus = []
        buttons_heb = []
        for button in notification.buttons.all():
            buttons_rus.append([{
                'text': button.text_rus,
                'url': button.link,
            }])

            buttons_heb.append([{
                'text': f'\u202B{button.text_heb}',
                'url': button.link,
            }])
        
        params_rus['reply_markup'] = json.dumps({'inline_keyboard': buttons_rus})
        params_heb['reply_markup'] = json.dumps({'inline_keyboard': buttons_heb})

    return params_rus, params_heb, image_path
    

@shared_task
def send_notifications():
    notifications = search_notifications()
    valid_notifications = mark_notifications_started(notifications)

    for notification in valid_notifications:
        users = select_users_for_notification(notification)
        params_rus, params_heb, image_path = construct_notification_params(notification)
        total_users = len(users)

        notification.total_users = total_users
        notification.save()
        success = False
        for user in users:
            if user.target == '1':
                params_rus['chat_id'] = user.tg_id
                main_params = params_rus

            elif user.target == '2':
                params_heb['chat_id'] = user.tg_id
                main_params = params_heb

            if image_path:
                with open(image_path, 'rb') as image:
                    files = {
                        'photo': image,
                    }
                    response = send_message_on_telegram(main_params, files=files)
            
            else:
                response = send_message_on_telegram(main_params)
            
            notification.total_send_users += 1
            if response:
                try:
                    if response.json().get('ok'):
                        success = True
                        notification.success_users += 1
                except:
                    pass
            
            notification.save()
            time.sleep(3)
        
        notification.notified = success
        notification.save()
