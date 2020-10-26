from rest_framework.serializers import ModelSerializer
from .models import EnergyMeter, Register, Assigment


class EnergyMeterSerializer(ModelSerializer):
    class Meta:
        model = EnergyMeter
        fields = '__all__'


class RegisterSerializer(ModelSerializer):
    class Meta:
        model = Register
        fields = '__all__'

class SparseRegisterSerializer(ModelSerializer):
    class Meta:
        model = Register
        fields = ('id', 'meter_type', 'register_address', 'measurement_name')


class AssigmentSerializer(ModelSerializer):
    class Meta:
        model = Assigment
        fields = '__all__'
