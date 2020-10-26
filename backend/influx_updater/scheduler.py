import logging
from django.conf import settings
from apscheduler.schedulers.background import BackgroundScheduler

logging.basicConfig()
logging.getLogger('apscheduler').setLevel(logging.WARNING)

scheduler = BackgroundScheduler(settings.SCHEDULER_CONFIG)

def config_scheduler():
    if settings.SCHEDULER_AUTOSTART:
        scheduler.start()







