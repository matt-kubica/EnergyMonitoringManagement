from django.urls import path
from .views import EnergyMetersAPI, EnergyMeterDetailAPI, RegistersAPI, RegisterDetailAPI, AssignmentsAPI, AssignmentsByMeterAPI, AssignmentDetailAPI


urlpatterns = [
    path('energy-meters', EnergyMetersAPI.as_view()),
    path('energy-meters/<int:pk>', EnergyMeterDetailAPI.as_view()),
    path('registers', RegistersAPI.as_view()),
    path('registers/<int:pk>', RegisterDetailAPI.as_view()),
    path('assignments', AssignmentsAPI.as_view()),
    path('assignments/<int:pk>', AssignmentDetailAPI.as_view()),
    path('assignments/by-meter/<int:pk>', AssignmentsByMeterAPI.as_view()),
]