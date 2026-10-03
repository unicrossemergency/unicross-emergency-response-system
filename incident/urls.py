from django.urls import path
from . import views

urlpatterns = [
    path('report/', views.report_incident, name='report_incident'),
    
]