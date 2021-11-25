from django.urls import path
from technician import views

urlpatterns = [
    path('homeT/',views.homeT, name='homeT'),
    path('techStation/',views.techStation, name='techStation'),
    path('trashComment/<int:id>',views.trashComment, name='trashComment'),
    path('profileTech',views.profileTech, name='profileTech'),
    path('releveToolbox',views.releveToolbox, name='releveToolbox'),
    path('monthStat/<int:id>',views.monthStat, name='monthStat'), 
    path('hebdo/<int:id>',views.hebdo, name='hebdo'), 
    
]
