from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from connection import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('connection/', include('connection.urls')),
    path('administration/', include('administration.urls')),
    path('meteorologist/', include('meteorologist.urls')),
    path('technician/', include('technician.urls')),
    path('', views.connection, name='connection'),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)