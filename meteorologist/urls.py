from django.urls import path
from meteorologist import views

urlpatterns = [
    path('homeM', views.homeM, name='homeM'),

    # demnades
    path('metDemands', views.metDemands,name='metDemands'),
    # annuler demande techncien
    path('annulDemand/<int:id>', views.annulDemand,name='annulDemand'),
    # annuler demande station
    path('annulDemandStation/<int:id>',views.annulDemandStation,name='annulDemandStation'),

    # ______________ gestion technician ________
    path('gestion_technicianMet', views.gestion_technicianMet, name='gestion_technicianMet'),
    
    # desactiver technicien
    path('disableTechMet/<int:id>', views.disableTechMet, name='disableTechMet'),

    # activer technicien
    path('enableTechMet/<int:id>', views.enableTechMet, name='enableTechMet'),

    # activer technicien
    path('affectTech/<int:idTech>/<int:idStation>/', views.affectTech, name='affectTech'),

    # ne pas affectée
    path('noAffect/<int:id>', views.noAffect, name='noAffect'),

    # ne pas affectée
    path('trashTechMet/<int:id>', views.trashTechMet, name='trashTechMet'),
    
    # gestion station
    path('gestion_stationMet',views.gestion_stationMet,name='gestion_stationMet'),
    
    # enlever station
    path('dropTech/<int:id>', views.dropTech, name='dropTech'),

    # single station
    path('G_station/<int:id>', views.G_station, name='G_station'),

    # single station
    path('affectMetStation/<int:idTech>/<int:id>', views.affectMetStation, name='affectMetStation'),

    # single retirer affectation tech a station
    path('deSaffectMetStation/<int:idTech>/<int:id>', views.deSaffectMetStation, name='deSaffectMetStation'),

    # desactiver station
    path('disableStationMet/<int:id>', views.disableStationMet, name='disableStationMet'),

    # activer station
    path('enableStationMet/<int:id>', views.enableStationMet, name='enableStationMet'),

    # statistiques station
    path('statisticStation/<int:id>', views.statisticStation, name='statisticStation'),
    
    
    # export somthing
    path('exports/<int:id>/<int:year>',views.exports, name='exports'),
       
    path('gestion_profilMet',views.gestion_profilMet, name='gestion_profilMet'),

    # statistique annuelle
    path('yearStatistics/<int:id>', views.yearStatistics, name='yearStatistics'),

    # statistique hebdomadaire
    path('hebdoStat/<int:id>', views.hebdoStat, name='hebdoStat'),
    
    path('g_releve', views.g_releve, name='g_releve'),
    
]
