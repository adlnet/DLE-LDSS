from django.urls import path
from . import views
from .views import generate_report
from .views import report_generated_uids, api_generate_uid, api_terms, api_terms_slim

app_name = 'uid'

urlpatterns = [
    path('generate-uid/', views.generate_uid_node, name='generate_uid'),
    path('report/<str:echelon_level>/', generate_report, name='generate_report'),
    path('api/log', report_generated_uids, name='uid-log'),
    path('api/generate', api_generate_uid, name='uid-generated'),
    path("api/terms/slim", api_terms_slim, name="export-terms-slim"),
    path("api/terms", api_terms, name="export-terms"),
]
