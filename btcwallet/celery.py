from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab
from django.conf import settings

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'btcwallet.settings')

#app = Celery('coin', broker='redis://localhost:6379')
app = Celery('btcwallet')

# Using a string here means the worker don't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

# app.conf.beat_schedule = {
#     # Executes every Monday morning at 7:30 a.m.
#     'every-minute': {
#         'task': 'bot.tasks.send12_00_2',
#         'schedule': crontab(minute=9,hour=15),
#     },
# }
