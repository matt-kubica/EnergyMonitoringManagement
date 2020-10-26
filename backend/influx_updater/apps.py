from django.apps import AppConfig

from django.db.models.signals import post_save, pre_delete


class InfluxUpdaterConfig(AppConfig):
    name = 'influx_updater'

    def ready(self):
        # scheduler config
        from influx_updater.scheduler import config_scheduler
        config_scheduler()
        print('Scheduler started!!!')

        # signals config
        from .signals import add_update_routine, delete_update_routine
        from management_api.models import Assigment
        post_save.connect(add_update_routine, sender=Assigment)
        pre_delete.connect(delete_update_routine, sender=Assigment)
