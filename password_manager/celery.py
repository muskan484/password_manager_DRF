from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'password_manager.settings')

app = Celery('password_manager')
app.config_from_object('django.conf:settings', namespace='CELERY')

app.conf.beat_schedule = {
    'send_weekly_password_data_on_monday':{
        'task': 'password_app.tasks.upload_password_data_weekly_to_firebase',
        # 'schedule' :crontab(minute='*/3', hour='*', day_of_week='*', day_of_month='*', month_of_year='*')
        'schedule' : crontab(minute = 0, hour= 0, day_of_week='monday')
    },
    "send_weekly_user_data_on_monday":{
        "task":"user_app.tasks.upload_user_data_weekly_to_firebase",
        'schedule' : crontab(minute = 0, hour= 0, day_of_week='monday')
    }
}
app.conf.enable_utc = False

app.conf.update(timezone = 'utc')

app.autodiscover_tasks()