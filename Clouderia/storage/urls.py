from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.upload_file, name='upload_file'),
    path('', views.storage_view, name='storage_view'),
    path('download/<int:work_id>/', views.download_file, name='download_file'),
    path('download_zip/<int:work_id>/', views.download_zip, name='download_zip'),  # Corrected URL
    path('delete/<int:file_id>/', views.delete_file, name='delete_file'),
    path('file/<int:file_id>/details/', views.file_details, name='file_details'),
]
