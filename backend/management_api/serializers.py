from rest_framework import serializers
from .models import EnergyMeter, Register, Assigment


class EnergyMeterSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnergyMeter
        fields = '__all__'


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Register
        fields = '__all__'


class AssigmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assigment
        fields = '__all__'
