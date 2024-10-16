from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'work_exchange.settings')

app = Celery('WORK')

app.config_from_object('django.conf:settings', namespace='CELERY')
app.conf.broker_connection_retry_on_startup = True
app.conf.beat_schedule = {
    'run-scheduler-every-minute': {
        'task': 'notifications.tasks.send_notifications',
        'schedule': crontab(minute='*/1'),  
    },
}

app.autodiscover_tasks()