from django.urls import path
from . import views

urlpatterns = [
    path('report/', views.report_incident, name='report_incident'),
     # 🔥 API endpoint for map
    path('incident-data/', views.incident_data, name='incident_data'),
]