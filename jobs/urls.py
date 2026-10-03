from django.urls import path
from . import views

urlpatterns = [
    path('', views.job_list, name='job_list'),
    path('job/<int:pk>/', views.job_detail, name='job_detail'),
    path('post/', views.job_create, name='job_create'),
    path('upload-resume/', views.upload_resume, name='upload_resume'),
    path('applications/', views.my_applications, name='my_applications'),
    path('job/<int:pk>/apply/', views.apply_to_job, name='apply_to_job'),
]