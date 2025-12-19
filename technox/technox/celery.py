import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'technox.settings')

app = Celery('technox')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()