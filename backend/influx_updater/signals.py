from influx_updater.scheduler import scheduler
from .utils import update_influx


def add_update_routine(sender, instance, created, **kwargs):
    if created:
        cron_params = {
            'hour': instance.hour_trigger,
            'minute': instance.minute_trigger,
            'second': instance.second_trigger,
        }
        scheduler.add_job(**cron_params, trigger='cron',
                          id=str(instance.pk), func=update_influx,
                          args=[instance.pk])


def delete_update_routine(sender, instance, using, **kwargs):
    scheduler.remove_job(id=str(instance.pk))



