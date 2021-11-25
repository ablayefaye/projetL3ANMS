from django.urls import path
from administration import views

urlpatterns = [
    # accueil admin
    path('homeA', views.homeA, name='homeA'),
    # _____ partie gestion technicien _____
    path('gestion_technician', views.gestion_technician, name='gestion_technician'),
    # archiver technicien
    path('trashTechnician/<int:id>', views.trashTechnician,name='trashTechnician'),
    # désactiver technicien
    path('disableTech/<int:id>', views.disableTech,name='disableTech'),
    # activer technicien
    path('enableTech/<int:id>', views.enableTech,name='enableTech'),
    # éditer technicien
    path('editTech/<int:id>', views.editTech,name='editTech'),
    # restaurer technicien
    path('restorTechnician/<int:id>', views.restorTechnician,name='restorTechnician'),

    # supprimer technicien
    path('deleteTechnician/<int:id>', views.deleteTechnician,name='deleteTechnician'),
    
    # _____ partie gestion météorologue _____
    path('gestion_meteorologist', views.gestion_meteorologist, name='gestion_meteorologist'),
    # editer met
    path('editMet/<int:id>', views.editMet, name='editMet'),
    # archiver meteorologue
    path('trashMet/<int:id>', views.trashMet,name='trashMet'),

    # désactivé  meteorologue
    path('disableMet/<int:id>', views.disableMet,name='disableMet'),

    # activé  meteorologue
    path('enableMet/<int:id>', views.enableMet,name='enableMet'),
    # restaurer  meteorologue
    path('restorMet/<int:id>', views.restorMet, name='restorMet'),
    # delete  meteorologue
    path('deleteMet/<int:id>', views.deleteMet, name='deleteMet'),
    
    #___________________ gestion station ___________________
    #
    path('gestion_station', views.gestion_station, name='gestion_station'),

    # désactiver une station
    path('disableStation/<int:id>', views.disableStation, name='disableStation'),

     # activer une station
    path('enableStation/<int:id>', views.enableStation, name='enableStation'),
        
    # corbeil  station
    path('trashStation/<int:id>', views.trashStation, name='trashStation'),

    # restaurer  station
    path('restorStation/<int:id>', views.restorStation, name='restorStation'),

    # vider archive station
    path('emptyTrash/',views.emptyTrash, name='emptyTrash'),

    # vider archive met
    path('emptyTrashMet/',views.emptyTrashMet, name='emptyTrashMet'),

    # vider archive tech
    path('emptyTrashTech/',views.emptyTrashTech, name='emptyTrashTech'),

    path('editStation/<int:id>', views.editStation, name='editStation'),
      
    #  gestion régions
    path('gestion_regions/',views.gestion_regions, name='gestion_regions'),
    
    # gestion départements
    path('gestion_departments/', views.gestion_departments, name='gestion_departments'),

    # ajouter departement a partir de region
    path('regionAddDept/<int:id>', views.regionAddDept, name='regionAddDept'),

    # supprimer station
    path('deleteStation/<int:id>', views.deleteStation, name='deleteStation'),

    # supprimer département
    path('deleteDept/<int:id>', views.deleteDept, name='deleteDept'),

    # modifier département
    path('editDept/<int:id>', views.editDept, name='editDept'),

    # supprimer région
    path('deleteRegion/<int:id>', views.deleteRegion, name='deleteRegion'),
 
    # supprimer région
    path('editRegion/<int:id>', views.editRegion, name='editRegion'),

    # ___________ gestiondemandes ____________
    path('gestion_demandes/', views.gestion_demandes, name='gestion_demandes'),
    # valider demande tech
    path('acceptDemand/<int:id>', views.acceptDemand, name='acceptDemand'),

    # rejeter demande tech
    path('declineDemand/<int:id>', views.declineDemand, name='declineDemand'),

    # valider demande station
    path('acceptDemandStation/<int:id>', views.acceptDemandStation, name='acceptDemandStation'),

    # rejeter demande station
    path('declineDemandStation/<int:id>', views.declineDemandStation, name='declineDemandStation'),
    # rejeter demande station
    path('gestion_profil', views.gestion_profil, name='gestion_profil'),

    # result tech
    path('resultSearch/<int:id>/<str:role>', views.resultSearch,name='resultSearch'),

    # changer technicien de station
    path('changeStationForTech/<int:idTech>/<int:idStation>',views.changeStationForTech,name='changeStationForTech'),
]
