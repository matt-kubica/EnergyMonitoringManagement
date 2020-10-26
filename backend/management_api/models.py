from django.db import models
from .utils import DataTypes, FunctionCodes, EndianOrder

import os



class EnergyMeter(models.Model):
    meter_type = models.CharField(max_length=32, null=False)
    host = models.TextField(max_length=64, null=False)
    port = models.PositiveIntegerField(null=False)
    slave_address = models.PositiveSmallIntegerField(null=False)
    description = models.CharField(max_length=128, null=True)

    class Meta:
        unique_together = ('host', 'port', 'slave_address',)

    def __str__(self):
        return '{0}:{1}:{2} ({3})'.format(self.host, self.port, self.slave_address, self.description)



class Register(models.Model):
    meter_type = models.CharField(max_length=32, null=False)
    register_address = models.PositiveIntegerField(null=False)
    measurement_name = models.CharField(max_length=64, null=False)
    data_unit = models.CharField(max_length=8, blank=True, null=True)
    data_type = models.PositiveIntegerField(choices=DataTypes.choices(), null=False)
    function_code = models.PositiveIntegerField(choices=FunctionCodes.choices(), null=False)
    word_order = models.PositiveIntegerField(choices=EndianOrder.choices(), null=False)
    byte_order = models.PositiveIntegerField(choices=EndianOrder.choices(), null=False)

    class Meta:
        unique_together = ('meter_type', 'measurement_name',)

    def __str__(self):
        return '{0}:{1}:{2}'.format(self.meter_type, self.measurement_name, self.register_address)



class Assigment(models.Model):
    meter_id = models.ForeignKey(EnergyMeter, on_delete=models.CASCADE)
    register_id = models.ForeignKey(Register, on_delete=models.CASCADE)

    hour_trigger = models.CharField(max_length=4, null=False, default=os.environ.get('DEFAULT_CRON_HOUR_TRIGGER', '*'))
    minute_trigger = models.CharField(max_length=4, null=False, default=os.environ.get('DEFAULT_CRON_MINUTE_TRIGGER', '*/5'))
    second_trigger = models.CharField(max_length=4, null=False, default=os.environ.get('DEFAULT_CRON_SECOND_TRIGGER', '0'))

    class Meta:
        unique_together = ('meter_id', 'register_id', )

    def __str__(self):
        return '{0}:{1}'.format(self.meter_id, self.register_id)

    def __eq__(self, other):
        if not isinstance(other, EnergyMeter):
            return NotImplemented
        return self.pk == other.pk

    def __hash__(self):
        return hash(str(self))