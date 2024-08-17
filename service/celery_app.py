import os
import time

from celery import Celery
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'service.settings')  # set the default Django settings module for the 'celery' program.

app = Celery('service')  # Create a new instance of Celery.

app.config_from_object('django.conf:settings')  # Load Celery config from Django settings module.
app.conf.broker_url = settings.CELERY_BROKER_URL  # Load Celery broker URL from Django settings module.
app.autodiscover_tasks()  # Discover any tasks defined in Django settings module.


@app.task()
def debug_task():
    print('Running: ', debug_task.__name__)
    time.sleep(10)
    print('Ended: ', debug_task.__name__)

