from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.main_page, name='main_page'),
    path('profile/<str:username>/', views.user_profile, name='user_profile'),  # Профиль текущего пользователя
    path('view_profile/<str:username>/', views.view_user_profile, name='view_user_profile'),  # Профиль чужого пользователя
    path('like/<int:work_id>/', views.like_work, name='like_work'),
    path('dislike/<int:work_id>/', views.dislike_work, name='dislike_work'),
    path('work/<int:work_id>/', views.view_work, name='view_work'),
    path('report/<int:work_id>/', views.report_work, name='report_work'),
    path('main/settings/', views.profile_settings, name='profile_settings'),
    path('logout/', views.logout_view, name='logout'),
    path('settings/change_password/', views.change_password, name='change_password'),
    path('profile', views.update_profile, name='update_profile'),
    path('upload/', views.upload_file, name='upload_file'),
    path('download_file/<int:work_id>/', views.download_file, name='download_file'),
    path('work/delete/<int:work_id>/', views.delete_work, name='delete_work'),
    path('download_folder/<int:work_id>/', views.download_folder, name='download_folder'),

]
