from .models import EnergyMeter, Register, Assigment
from .serializers import EnergyMeterSerializer, RegisterSerializer, SparseRegisterSerializer

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated


class EnergyMetersAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        energy_meters = EnergyMeter.objects.all()
        serializer = EnergyMeterSerializer(energy_meters, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = EnergyMeterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EnergyMeterDetailAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk, format=None):
        try:
            energy_meter = EnergyMeter.objects.get(pk=pk)
        except EnergyMeter.DoesNotExist:
            return Response({'error': 'Cannot find energy meter with pk = {0}'.format(pk)}, status=status.HTTP_404_NOT_FOUND)
        serializer = EnergyMeterSerializer(energy_meter)
        return Response(serializer.data)


    def delete(self, request, pk, format=None):
        try:
            energy_meter = EnergyMeter.objects.get(pk=pk)
            energy_meter.delete()
            return Response({'info': 'Energy meter with id {0} has been deleted'.format(pk)}, status=status.HTTP_200_OK)
        except EnergyMeter.DoesNotExist:
            return Response({'error': 'Cannot find energy meter with pk = {0}'.format(pk)}, status=status.HTTP_404_NOT_FOUND)

    # TODO: patch


class RegistersAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        registers = Register.objects.all()
        serializer = SparseRegisterSerializer(registers, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RegisterDetailAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk, format=None):
        try:
            register = Register.objects.get(pk=pk)
        except Register.DoesNotExist:
            return Response({'error': 'Cannot find register with pk = {0}'.format(pk)}, status=status.HTTP_404_NOT_FOUND)
        serializer = RegisterSerializer(register)
        return Response(serializer.data)

    def delete(self, request, pk, format=None):
        try:
            register = Register.objects.get(pk=pk)
            register.delete()
            return Response({'info': 'Register with id {0} has been deleted'.format(pk)}, status=status.HTTP_200_OK)
        except Register.DoesNotExist:
            return Response({'error': 'Cannot find register with pk = {0}'.format(pk)}, status=status.HTTP_404_NOT_FOUND)

    # TODO: patch