from django.urls import path
from connection import views

urlpatterns = [
    path('connection', views.connection, name='connection'),
    path('disconnect', views.disconnect, name='disconnect'),
    # path('disconnection/<str:disconnection>', views.disconnection, name='disconnection'),
]
