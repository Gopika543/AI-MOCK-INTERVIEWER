from django.contrib import admin  # Add this import
from django.urls import path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),  # Now 'admin' is defined
    path('', views.index, name='index'),
    path('start_interview/', views.start_interview, name='start_interview'),
    path('interview/', views.interview_page, name='interview_page'),
    path('record_answer/', views.record_answer, name='record_answer'),
    path('validate_answer/', views.validate_answer, name='validate_answer'),
    path('result/', views.result_page, name='result'),  # Changed 'result_page' to 'result'
    path('next_question/', views.next_question, name='next_question'),
]
