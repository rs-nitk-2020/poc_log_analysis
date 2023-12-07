# log_analysis_gui/urls.py
from django.urls import path
from .views import home, validation_rules, process_log_warnings, display_report, download_report

urlpatterns = [
    path('', home, name='home'),
    path('validation_rules/', validation_rules, name='validation_rules'),
    path('process_log_warnings/', process_log_warnings, name='process_log_warnings'),
    path('display_report/', display_report, name='display_report'),
    path('download_report/', download_report, name='download_report')
]
