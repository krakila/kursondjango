from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('storage/', include(('storage.urls', 'storage'), namespace='storage')),
    path('', RedirectView.as_view(url='/accounts/login/', permanent=False)),  # Перенаправляем на страницу входа
    path('main/', include('main.urls')),  # Главная страница после входа
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)