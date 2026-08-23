from django.urls import path
from . import views

app_name = 'qa_app'

urlpatterns = [
    path('ask/', views.query_document_api, name='api_ask'),
    path('upload/', views.upload_document_api, name='api_upload'),
    path('history/', views.get_qa_history_api, name='api_history'),
]