from django.urls import path
from .views import EnergyMetersAPI, EnergyMeterDetailAPI, RegistersAPI, RegisterDetailAPI


urlpatterns = [
    path('energy-meters', EnergyMetersAPI.as_view()),
    path('energy-meters/<int:pk>', EnergyMeterDetailAPI.as_view()),
    path('registers', RegistersAPI.as_view()),
    path('registers/<int:pk>', RegisterDetailAPI.as_view()),

]