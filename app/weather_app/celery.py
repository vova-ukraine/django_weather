import os

from celery import Celery
from django.conf import settings
from kombu import Queue
from celery.signals import celeryd_init

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'weather_app.settings')

app = Celery('admin', broker=settings.CELERY_BROKER_URL)
app.config_from_object('django.conf:settings')
app.conf.broker_transport_options = {
    'max_retries': 3,
    'interval_start': 0,
    'interval_step': 0.2,
    'interval_max': 0.2,
}
app.autodiscover_tasks()

app.conf.task_queues = (
    Queue(
        'weather_app',
        routing_key='weather_app',
        queue_arguments={'x-max-priority': 10}
    ),
)


@celeryd_init.connect
def handle_celeryd_init(sender, instance, conf, options, **kwargs):
    if options['pool'] == 'gevent':
        import psycogreen.gevent
        psycogreen.gevent.patch_psycopg()
