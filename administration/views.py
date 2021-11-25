from django.shortcuts import render, redirect
from connection.models import *
from .forms import *
from django.core.mail import send_mail
from django.conf import settings
import folium
from django.contrib import messages
import json
import random

# ________________________________ LES VUES _________________________



# la vue home
def homeA(request):
    # rains = RainData.objects.filter()
    # for rain in rains:
    #     dateRain = int(str(rain.created_at).split('-')[1])
    #     if  dateRain <= 6 or dateRain > 9:
    #         rain.value = 0
    #         rain.save()
    #     else:
    #         rain.value = random.randint(0,120)
    #         rain.save()
        

    if 'email' in request.session:
        email = request.session['email']
        demandsW = len(Technician.objects.filter(is_valid=False)) + len(Station.objects.filter(is_valid=False))
        # met
        metsInactifs = len(Meteorologist.objects.filter(statut=False, trash=False))
        metsActifs = len(Meteorologist.objects.filter(statut=True,trash=False))
        mets = metsInactifs + metsActifs

        # technicien
        techInactifs = len(Technician.objects.filter(statut=False, is_valid=True, trash=False))
        techActifs = len(Technician.objects.filter(statut=True,is_valid=True, trash=False))
        techs = techInactifs + techActifs

        # stations
        stationInactifs = len(Station.objects.filter(statut=False, is_valid=True, trash=False))
        stationActifs = len(Station.objects.filter(statut=True,is_valid=True ,trash=False))
        stations = stationInactifs + stationActifs

        admin = Administrator.objects.get(email=email)
        users = []
        for t in Technician.objects.filter(is_valid=True):
            users.append(t)
        
        for m in Meteorologist.objects.all():
            users.append(m)
        

        return render(request,'homeA.html', locals())
    else:
        return redirect('connection')


# verifier si téléphone est bon
def okTel(tel):
    for c in tel:
        if c not in '1234567890 ':
            return False
    return True

# verifier firstname
def firstnameOk(firstname):
    for c in firstname:
        if c in '1234567890 ':
            return False
    return True


# verifier lastname
def lastnameOk(lastname):
    for c in lastname:
        if c in '1234567890 ':
            return False
    return True


# gestion technicien
def gestion_technician(request):
    
    # on verifie si l'utilisateur est connecté
    if 'email' and 'role' in request.session and request.session['role'] == 'admin':
        stationsChoice = Station.objects.filter(trash=False)
        demandsW = len(Technician.objects.filter(is_valid=False)) + len(Station.objects.filter(is_valid=False))
        page = 'technician'
        email = request.session['email']
        admin = Administrator.objects.get(email=email) 
        # liste techniciens
        technicians = Technician.objects.filter(trash=False, is_valid=True)
        liste = json.dumps(list(Technician.objects.values('email','id','role').filter(trash=False, is_valid=True)))
        typ = 'tech'
        techniciansInTrash = Technician.objects.filter(trash=True , is_valid=True)
        techLen = len(technicians)
        techTrashLen = len(techniciansInTrash)
        # 1. ajouter technicien
        formAdd = AddTechnician(request.POST or None)
        
        # recupérer methode de request
        method = request.method

        # verifier si method == 'POST'
        if request.method == 'POST':
            mete = Meteorologist.objects.filter(email=request.POST['email'])
            techn = Technician.objects.filter(email=request.POST['email'])
            adm = Administrator.objects.filter(email=request.POST['email'])
            if len(techn)>= 1 or len(mete) >= 1 or len(adm) >= 1:
                messages.add_message(request, messages.INFO, 'Adresse mail déjà existante.')
                return redirect('gestion_technician')
            # verification formulaire
            if formAdd.is_valid():                
                # verification mail  
                
                if not okTel(formAdd.cleaned_data['tel']):
                    errorTel = "Numéro de téléphone invalide."
                elif not firstnameOk(formAdd.cleaned_data['firstname']):
                    errorFirstname = "Valeur prénom invalide."
                elif not lastnameOk(formAdd.cleaned_data['firstname']):
                    errorLastname = "Valeur nom invalide."
                else:                    
                    # envoie paramètre de connexion au technicien
                    sendMail = formAdd.cleaned_data['email']
                    
                    subject = "Paramètres de Connexion"
                    password = Technician().password
                    message = "Email: "+ sendMail +" mot de passe: "+password
                    email = formAdd.cleaned_data['email']
                    # try:
                    

                    try:
                        send_mail(subject, message, settings.EMAIL_HOST_USER,
                        [email], fail_silently=False)
                        # réinitiamisé champs
                        technician = Technician()
                        technician.firstname = formAdd.cleaned_data['firstname']
                        technician.lastname = formAdd.cleaned_data['lastname']
                        technician.address = formAdd.cleaned_data['address']
                        technician.tel = formAdd.cleaned_data['tel']
                        technician.email = email
                        technician.password = password
                        technician.statut = True
                        technician.is_valid = True
                        technician.meteorologist = formAdd.cleaned_data['meteorologist']
                        technician.save()                        
                        messages.add_message(request, messages.SUCCESS, 'Techncien créer avec succés.')
                        return redirect('gestion_technician')
                    except:
                        messages.add_message(request, messages.SUCCESS, 'Probléme de chargement des données. Veuillez vérifier votre connexion internet svp!')
                        return redirect('gestion_technician')
    
        return render(request,'technicians/gestion_technician.html', locals())
    
    
    # si utilisateur n'est pas connecté il 
    # sera rediriger dans la page connexion
    else:
        return redirect('connection')


# mettre un technicien dans la corbeil
def trashTechnician(request, id):
    if 'email' and 'role' in request.session and request.session['role'] == 'admin':
        tech = Technician.objects.get(id=id)
        tech.trash_at = datetime.now()
        tech.trash = True
        tech.statut = False
        tech.save()
        messages.add_message(request, messages.SUCCESS, 'technicien archivé avec succèss.')
        return redirect('gestion_technician')
    else:
        return redirect('connection')

# désactiver un technicien
def disableTech(request, id):
    if 'email' and 'role' in request.session and request.session['role'] == 'admin':
        try:
            tech = Technician.objects.get(id=id)
            tech.statut = False
            tech.save()
            messages.add_message(request, messages.SUCCESS, 'Désactivation éffectuée avec succès.')
            return redirect('gestion_technician')
        except Technician.DoesNotExist:
            return redirect('gestion_technician')

    else:
        return redirect('connection')

# activer technicien
def enableTech(request, id):
    if 'email' and 'role' in request.session and request.session['role'] == 'admin':
        try:
            tech = Technician.objects.get(id=id)
            tech.statut = True
            tech.save()
            messages.add_message(request, messages.SUCCESS, 'technicien activé avec succès.')
            return redirect('gestion_technician')
        except Technician.DoesNotExist:
            return redirect('gestion_technician')

    else:
        return redirect('connection')



def editTech(request, id):
    if 'email' and 'role' in request.session and request.session['role'] == 'admin':
        demandsW = len(Technician.objects.filter(is_valid=False)) + len(Station.objects.filter(is_valid=False))
        page = 'technician'
        # formulaire pour editer un technicien
        # on utilise le même formulaire seulement on y met les valeur par défaut
        email = request.session['email']
        admin = Administrator.objects.get(email=email)
        try:
            technician = Technician.objects.get(id=id)
            idMet = technician.meteorologist.id
            formEdit = EditTechnician(request.POST or None, instance=technician)
            method = request.method
            if method == 'POST':
                
                # verification formulaire
                if formEdit.is_valid():                
                    if not okTel(formEdit.cleaned_data['tel']):
                        errorTel = "Numéro de téléphone invalide."
                    elif not firstnameOk(formEdit.cleaned_data['firstname']):
                        errorFirstname = "Valeur prénom invalide."
                    elif not lastnameOk(formEdit.cleaned_data['lastname']):
                        errorLastname = "Valeur nom invalide."
                    else:
                        if idMet != formEdit.cleaned_data['meteorologist'].id:
                            technician.station = None
                        technician.firstname = formEdit.cleaned_data['firstname'].capitalize()
                        technician.lastname = formEdit.cleaned_data['lastname'].capitalize()
                        technician.save()
                        formEdit = EditTechnician()
                        messages.add_message(request, messages.SUCCESS, 'Modification éffectuée avec.')
                        return redirect('gestion_technician')
                else:
                    
                    # verification mail  
                    tech_mail_ok = Technician.objects.filter(email=request.POST['email'])
                    met_mail_ok = Meteorologist.objects.filter(email=request.POST['email'])
                    admin_mail_ok = Administrator.objects.filter(email=request.POST['email']) 
                    if len(tech_mail_ok) != 0 or len(met_mail_ok) or len(admin_mail_ok):
                        emailNotOk = 'Adresse email déjà prise.'
            return render(request,'technicians/editTech.html', locals())
        except Technician.DoesNotExist:
            return redirect('gestion_technician')
    else:
        return redirect('connection')


# restaurer technicien
def restorTechnician(request, id):
    if 'email' and 'role' in request.session and request.session['role'] == 'admin':
        try:
            tech = Technician.objects.get(id=id)
            tech.trash_at = None
            tech.trash = False
            tech.statut = True
            tech.save()
            messages.add_message(request, messages.SUCCESS, 'Désarchivage éffectué avec succés.')
            return redirect('gestion_technician')
        except Technician.DoesNotExist:
            return redirect('gestion_technician')

    return redirect('connection')

# supprimer technicien
def deleteTechnician(request, id):
    if 'email' and 'role' in request.session and request.session['role'] == 'admin':
        try:
            tech = Technician.objects.get(id=id).delete()
            messages.add_message(request, messages.SUCCESS, 'Suppréssion réussie.')
            return redirect('gestion_technician')
        except Technician.DoesNotExist:
            return redirect('gestion_technician')
    else:
        return redirect('connection')


# ____________________gestion météorologist __________________
def gestion_meteorologist(request):
    if 'email' and 'role' in request.session and request.session['role'] == 'admin':
        demandsW = len(Technician.objects.filter(is_valid=False)) + len(Station.objects.filter(is_valid=False))
        page = 'meteorologist'
        email = request.session['email']
        admin = Administrator.objects.get(email=email)
        meteorologists = Meteorologist.objects.filter(trash=False)
        liste = json.dumps(list(Meteorologist.objects.values('email','id','role').filter(trash=False)))
        typ = 'met'
        meteorologistsInTrash = Meteorologist.objects.filter(trash=True)
        metTrashLen = len(meteorologistsInTrash)
        metLen = len(meteorologists)
        formAdd = AddMeteorologist(request.POST or None)
        if request.method == 'POST':
            mete = Meteorologist.objects.filter(email=request.POST['email'])
            techn = Technician.objects.filter(email=request.POST['email'])
            adm = Administrator.objects.filter(email=request.POST['email'])
            if len(techn)>= 1 or len(mete) >= 1 or len(adm) >= 1:
                messages.add_message(request, messages.INFO, 'Adresse mail déjà existante.')
                return redirect('gestion_meteorologist')
            
            # verification formulaire
            if formAdd.is_valid():                
                #  verification mail  
                formAdd = AddMeteorologist(request.POST or None, request.FILES)
                if not okTel(request.POST['tel']):
                    errorTel = "Numéro de téléphone invalide."

                elif not firstnameOk(request.POST['firstname']):
                    errorFirstname = "Valeur prénom invalide."
                elif not lastnameOk(request.POST['firstname']):
                    errorLastname = "Valeur nom invalide."

                # else:   
                password = Meteorologist().password
                sendMail = request.POST['email']
                    
                subject = "Bonjour " +request.POST['firstname'] + " " +request.POST['lastname']+","
                message = "\nVous êtes un nouveau météorologue de ANMS(Agence Nationale de la Météologie Sénégalaise) un\nVos Paramètres de Connexion\n:" + "\Email: "+ sendMail +"\nmot de passe: "+password
                
                
                
                email = request.POST['email']
                # try:
                send_mail(subject, message, settings.EMAIL_HOST_USER,
                [email], fail_silently=False)
                # formAdd.save()
            
                # réinitialisé champs
                met = Meteorologist()
                met.firstname = request.POST['firstname'].capitalize()
                met.lastname =request.POST['lastname'].capitalize()
                met.address = request.POST['address']
                met.tel = request.POST['tel']
                met.email = email
                met.password = password
                met.statut = True
                met.role = 'meteorologue'
                met.save()
                formAdd = AddMeteorologist()
                
                messages.add_message(request, messages.SUCCESS, 'Météorologue créer avec succés.')
                return redirect('gestion_meteorologist')
                    # except:
                        # messages.add_message(request, messages.SUCCESS, 'Probléme de chargement des données. Veuillez vérifier votre connexion internet svp!')
                        # return redirect('gestion_meteorologist')
                                       
            # else:

                # # verification mail  
                # tech_mail_ok = Technician.objects.filter(email=request.POST['email'])
                # met_mail_ok = Meteorologist.objects.filter(email=request.POST['email'])
                # admin_mail_ok = Administrator.objects.filter(email=request.POST['email']) 
                # if len(tech_mail_ok) != 0 or len(met_mail_ok) or len(admin_mail_ok):
                #     messages.add_message(request, messages.SUCCESS, 'adresse email déjà prise.')
    return render(request,'meteorologist/gestion_meteologist.html', locals())


# modifier meteorologue
def editMet(request, id):
    if 'email' and 'role' in request.session and request.session['role'] == 'admin':
        demandsW = len(Technician.objects.filter(is_valid=False)) + len(Station.objects.filter(is_valid=False))
        page ='meteorologist'
        # formulaire pour editer un technicien
        # on utilise le même formulaire seulement on y met les valeur par défaut
        email = request.session['email']
        admin = Administrator.objects.get(email=email)
        try:

            meteorologist = Meteorologist.objects.get(id=id)
            formEdit = EditMeteologist(request.POST or None, instance=meteorologist)
            method = request.method
            if method == 'POST':
                # verification formulaire
                if formEdit.is_valid():                
                    
                    if not okTel(formEdit.cleaned_data['tel']):
                        errorTel = "Numéro de téléphone invalide."
                    elif not firstnameOk(formEdit.cleaned_data['firstname']):
                        errorFirstname = "Valeur prénom invalide."
                    elif not lastnameOk(formEdit.cleaned_data['lastname']):
                        errorLastname = "Valeur nom invalide."
                    else:
                        meteorologist.firstname = formEdit.cleaned_data['firstname'].capitalize()
                        meteorologist.lastname = formEdit.cleaned_data['lastname'].capitalize() 
                        meteorologist.save()
                        formEdit = EditMeteologist()
                        messages.add_message(request, messages.SUCCESS, 'Modification réussie avec succès.')
                        return redirect('gestion_meteorologist')
                else:
                    
                    # verification mail  
                    tech_mail_ok = Technician.objects.filter(email=request.POST['email'])
                    met_mail_ok = Meteorologist.objects.filter(email=request.POST['email'])
                    admin_mail_ok = Administrator.objects.filter(email=request.POST['email']) 
                    if len(tech_mail_ok) != 0 or len(met_mail_ok) or len(admin_mail_ok):
                        emailNotOk = 'Adresse email déjà prise.'
            return render(request,'meteorologist/editMet.html', locals())
        except Meteorologist.DoesNotExist:
            return redirect('gestion_meteorologist')
    else:
        return redirect('connection')


# mettre un meteorologue dangs la corbeil
def trashMet(request, id):
    if 'email' and 'role' in request.session and request.session['role'] == 'admin':
        try:
            met = Meteorologist.objects.get(id=id)
            met.trash_at = datetime.now()
            met.trash = True
            met.statut = False
            met.save()
            messages.add_message(request, messages.SUCCESS, 'Météorologue archivé.')
            return redirect('gestion_meteorologist')
        except Meteorologist.DoesNotExist:
            return redirect('gestion_meteorologist')
    else:
        return redirect('connection')

# désactiver un met
def disableMet(request, id):
    if 'email' and 'role' in request.session and request.session['role'] == 'admin':
        try:
            met = Meteorologist.objects.get(id=id)
            met.statut = False
            met.save()
            messages.add_message(request, messages.SUCCESS, 'Météorologue désactivé.')
            return redirect('gestion_meteorologist')
        except Meteorologist.DoesNotExist:
            return redirect('gestion_meteorologist')
    else:
        return redirect('connection')

# activer met
def enableMet(request, id):
    if 'email' and 'role' in request.session and request.session['role'] == 'admin':
        try:
            met = Meteorologist.objects.get(id=id)
            met.statut = True
            met.save()
            messages.add_message(request, messages.SUCCESS, 'Météorologue activé.')
            return redirect('gestion_meteorologist')
        except Meteorologist.DoesNotExist:
            return redirect('gestion_meteorologist')
    else:
        return redirect('connection')



# restaurer met
def restorMet(request, id):
    if 'email' and 'role' in request.session and request.session['role'] == 'admin':
        try:
            met = Meteorologist.objects.get(id=id)
            met.trash_at = None
            met.trash = False
            met.statut = True
            met.save()
            messages.add_message(request, messages.SUCCESS, 'Désarchivage réussi.')
            return redirect('gestion_meteorologist')
        except Meteorologist.DoesNotExist:
                return redirect('gestion_meteorologist')
    return redirect('connection')

# supprimer met
def deleteMet(request, id):
    if 'email' and 'role' in request.session and request.session['role'] == 'admin':
        try:
            met = Meteorologist.objects.get(id=id).delete()
            messages.add_message(request, messages.SUCCESS, 'Météorologue supprimer.')

            return redirect('gestion_meteorologist')
        except Meteorologist.DoesNotExist:
            return redirect('gestion_meteorologist')
    return redirect('connection')


# _____________________________ gestion station ____________

# détails station
def gestion_station(request):
    if 'email' and 'role' in request.session and request.session['role'] == 'admin':
        demandsW = len(Technician.objects.filter(is_valid=False)) + len(Station.objects.filter(is_valid=False))
        page = "station"
        email = request.session['email']
        admin = Administrator.objects.get(email=email)

        # les station qui ne sont pas dans archives
        stations = Station.objects.filter(trash=False, is_valid=True).order_by('-id')
        liste = json.dumps(list(Station.objects.values('name','id').filter(trash=False, is_valid=True)))
        typ = 'stat'
        if 'stat' in request.GET:
            sta = int(request.GET['stat'])
            
        # tous les station
        all_stations = Station.objects.all()
        stationsInTrash = Station.objects.filter(trash=True , is_valid=True)
        # nombre de statino sur corbeil
        stationTrashLen =len(stationsInTrash)

        # nombre de station pas sur le corbeil
        stationLen = len(stations)
        # afficher station sur carte
        
        m = folium.Map(location=[13, -13], zoom_start=6,
            min_zoom = 5,
            max_zoom = 12)
        for stat in all_stations:
            if not stat.trash:
                if stat.statut == True:            
                    folium.Marker([stat.latitude, stat.longitude],
                            popup=stat.name,
                            tooltip=stat.name+' active, clicker pour + info',  icon=folium.Icon(color='green')).add_to(m)
                elif stat.statut == False:
                    folium.Marker([stat.latitude, stat.longitude],
                        popup=stat.name,
                        tooltip=stat.name+' non active,clicker pour + info', icon=folium.Icon(color='red')).add_to(m)
            else:
                folium.Marker([stat.latitude, stat.longitude],
                    popup=stat.name,
                    tooltip='station archivée, clicker pour + info', icon=folium.Icon(color='red')).add_to(m)
                
        m = m._repr_html_()
        
        formAdd = AddStation(request.POST or None)
        if request.method == 'POST':
            if formAdd.is_valid():
                latitude = formAdd.cleaned_data['latitude']
                longitude = formAdd.cleaned_data['longitude']
                stat = Station()
                m = folium.Map(location=[13, -13], zoom_start=6,
                    min_zoom = 5,
                    max_zoom = 12)

                name = formAdd.cleaned_data['name']
                
                meteorologist = formAdd.cleaned_data['meteorologist']
                department = formAdd.cleaned_data['department']

                stat.name = name.upper()
                stat.latitude = latitude
                stat.longitude = longitude
                stat.meteorologist = meteorologist
                stat.department = department
                stat.is_valid = True
                folium.Marker([latitude, longitude],
                        popup=stat.name,
                        tooltip='station non active,clicker pour + info', icon=folium.Icon(color='green')).add_to(m)
                m = m._repr_html_()
                stat.map = m
                m = None
                stat.save()
                formAdd = AddStation()
                messages.add_message(request, messages.SUCCESS, 'Station créer avec succés.')
                return redirect('gestion_station')
        else:
            formAdd = AddStation()

        return render(request,'station/gestion_station.html', locals())
    else:
        return redirect('connection')

# désactiver un station
def disableStation(request, id):
    if 'email' and 'role' in request.session and request.session['role'] == 'admin':
        try:
            station = Station.objects.get(id=id)
            station.statut = False
            m = folium.Map(location=[13, -13], zoom_start=6,
                    min_zoom = 5,
                    max_zoom = 12)
            folium.Marker([station.latitude, station.longitude],
                    popup=station.name,
                    tooltip='station non active,clicker pour + info', icon=folium.Icon(color='red')).add_to(m)
            m = m._repr_html_()
            station.map = m
            m = None
            station.save()
            messages.add_message(request, messages.SUCCESS, 'Station désactivée.')
            return redirect('gestion_station')
        except Station.DoesNotExist:
            return redirect('gestion_station')
    else:
        return redirect('connection')

# activer met
def enableStation(request, id):
    if 'email' and 'role' in request.session and request.session['role'] == 'admin':
        try:
            station = Station.objects.get(id=id)
            station.statut = True
            m = folium.Map(location=[13, -13], zoom_start=6,
                    min_zoom = 5,
                    max_zoom = 12)
            folium.Marker([station.latitude, station.longitude],
                    popup=station.name,
                    tooltip='station non active,clicker pour + info', icon=folium.Icon(color='green')).add_to(m)
            m = m._repr_html_()
            station.map = m
            m = None
            station.save()
            messages.add_message(request, messages.SUCCESS, 'Station activée.')
            return redirect('gestion_station')
        except Station.DoesNotExist:
            return redirect('gestion_station')
        
    else:
        return redirect('connection')

# mettre un station dans la corbeil
def trashStation(request, id):
    if 'email' and 'role' in request.session and request.session['role'] == 'admin':
        try:
            station = Station.objects.get(id=id)
            station.trash_at = datetime.now()
            station.trash = True
            station.statut = False
            m = folium.Map(location=[13, -13], zoom_start=6,
                    min_zoom = 5,
                    max_zoom = 12)
            folium.Marker([station.latitude, station.longitude],
                    popup=station.name,
                    tooltip='station non active,clicker pour + info', icon=folium.Icon(color='red')).add_to(m)
            m = m._repr_html_()
            station.map = m
            m = None
            station.save()
            messages.add_message(request, messages.SUCCESS, 'Station archivée.')

            return redirect('gestion_station')
        except Station.DoesNotExist:
            return redirect('gestion_station')
    else:
        return redirect('connection')


# restaurer station
def restorStation(request, id):
    if 'email' and 'role' in request.session and request.session['role'] == 'admin':
        try:
            station = Station.objects.get(id=id)
            station.trash_at = None
            station.trash = False
            station.statut = True
            m = folium.Map(location=[13, -13], zoom_start=6,
                        min_zoom = 5,
                        max_zoom = 12)
            folium.Marker([station.latitude, station.longitude],
                    popup=station.name,
                    tooltip='station non active,clicker pour + info', icon=folium.Icon(color='green')).add_to(m)
            m = m._repr_html_()
            station.map = m
            m = None
            station.save()
            messages.add_message(request, messages.SUCCESS, 'Station désarchivée.')

            return redirect('gestion_station')
        except Station.DoesNotExist:
                return redirect('gestion_station')
    else:
        return redirect('connection')
 
# vider les archive de station
def emptyTrash(request):
    if 'email' and 'role' in request.session and request.session['role'] == 'admin':
        try:
            Station.objects.filter(trash=True).delete()
            messages.add_message(request, messages.SUCCESS, 'Archives station vider.')

            return redirect('gestion_station')
        except:
            return redirect('connection')
    return redirect('connection')




# vider les archive de met
def emptyTrashMet(request):
    if 'email' and 'role' in request.session and request.session['role'] == 'admin':
        try:
            Meteorologist.objects.filter(trash=True).delete()
            return redirect('gestion_meteorologist')
        except:
            return redirect('connection')
    return redirect('connection')


# vider les archive de tech
def emptyTrashTech(request):
    if 'email' and 'role' in request.session and request.session['role'] == 'admin':
        try:
            Technician.objects.filter(trash=True).delete()
            messages.add_message(request, messages.SUCCESS, 'Archive vider.')
            return redirect('gestion_technician')
        except:
            return redirect('connection')        
    return redirect('connection')

# modifier station
def editStation(request, id):
    if 'email' and 'role' in request.session and request.session['role'] == 'admin':
        try:
            page = 'station'
            demandsW = len(Technician.objects.filter(is_valid=False)) + len(Station.objects.filter(is_valid=False))
            email = request.session['email']
            admin = Administrator.objects.get(email=email)
            station = Station.objects.get(id=id)
            metId = station.meteorologist.id
            formEdit = AddStation(request.POST or None, instance=station)
            
            if request.method=='POST':
                if formEdit.is_valid():
                    station.name = station.name.upper()
                    print(metId,formEdit.cleaned_data['meteorologist'].id)
                    if metId != formEdit.cleaned_data['meteorologist'].id:
                        techs = Technician.objects.filter(station=station)
                        for tech in techs:
                            tech.station = None
                            tech.save()
                    m = folium.Map(location=[13, -13], zoom_start=6,
                    min_zoom = 5,
                    max_zoom = 12)
                    if station.statut == True:            
                        folium.Marker([station.latitude, station.longitude],
                                popup=station.name,
                                tooltip='station active, clicker pour + info',  icon=folium.Icon(color='green')).add_to(m)
                    elif staton.statut == False:
                        folium.Marker([station.latitude, station.longitude],
                            popup=stat.name,
                            tooltip='station non active,clicker pour + info', icon=folium.Icon(color='red')).add_to(m)
                    m = m._repr_html_()
                    station.map = m
                    station.save()
                    messages.add_message(request, messages.SUCCESS, 'Station modifiée.')

                    return redirect('gestion_station')
            return render(request,'station/editStation.html', locals())
            if request.method == 'GET':
                print('GET')


        except Station.DoesNotExist:
            return redirect('gestion_station')
    return redirect('connection')

# supprimer station
def deleteStation(request,id):
    if 'email' and 'role' in request.session and request.session['role'] == 'admin':
        try:
            Station.objects.get(id=id).delete()
        except Station.DoesNotExist:
            return redirect('gestion_station')

    return redirect('gestion_station')

# gestion régions
def gestion_regions(request):
    if 'email' and 'role' in request.session and request.session['role'] == 'admin':
        demandsW = len(Technician.objects.filter(is_valid=False)) + len(Station.objects.filter(is_valid=False))
        page = 'gestion_regions'
        if 'reg' in request.GET:
            reg = int(request.GET['reg'])
            print(reg)
        email = request.session['email']
        admin = Administrator.objects.get(email=email)
        regions = Region.objects.all().order_by('-id')
        regionLen = len(regions)
        liste = json.dumps(list(Region.objects.values('name','id')))
        
            
        typ = 'reg'
        formAddRegion = AddRegion(request.POST or None)
        departments = Department.objects.all().order_by('-id')
        if request.method == 'POST':
            if formAddRegion.is_valid():
                region = Region()
                region.name = formAddRegion.cleaned_data['name'].upper()
                region.admin = admin
                region.save()
                department = Department()
                department.name = region.name
                department.region = region
                department.save()
                return redirect('gestion_regions')
        return render(request,'regions/gestion_region.html', locals())
    return redirect('connection')


# gestion départments
def gestion_departments(request):
    if 'email' and 'role' in request.session and request.session['role'] == 'admin':
        page = 'regDept'
        return render(request,'departments/gestion_department.html', locals())
    return redirect('connection')

# ajouter departement à partir de region
def regionAddDept(request, id):
    if 'email' and 'role' in request.session and request.session['role'] == 'admin':
        try:
            demandsW = len(Technician.objects.filter(is_valid=False)) + len(Station.objects.filter(is_valid=False))
            page = 'regDept'
            region = Region.objects.get(id=id)
            email =  request.session['email']
            admin = Administrator.objects.get(email=email)
            region = Region.objects.get(id=id)
            formAddDept = AddDept(request.POST or None)
            if request.method == 'POST':
                if formAddDept.is_valid():
                    department = Department()
                    department.name = formAddDept.cleaned_data['name'].upper()
                    department.region = region
                    department.save()
                    messages.add_message(request, messages.SUCCESS, 'Département ajouté avec succès.')
                    return redirect('gestion_regions')
            return render(request, 'regions/regionAddDept.html', locals())
        except Region.DoesNotExist:
            return redirect('gestion_regions')
    return redirect('connection')

# supprimer département
def deleteDept(request, id):
    if 'email' and 'role' in request.session and request.session['role'] == 'admin':
        try:
            page = 'regDept'
            Department.objects.get(id=id).delete()
            messages.add_message(request, messages.SUCCESS, 'Département supprimé.')
            return redirect('gestion_regions')
        except Department.DoesNotExist:
            return redirect('gestion_regions')
    return redirect('connection')

# editer département
def editDept(request, id):
    if 'email' and 'role' in request.session and request.session['role'] == 'admin':
        try:
            admin = Administrator.objects.get(email=request.session['email'])
            demandsW = len(Technician.objects.filter(is_valid=False)) + len(Station.objects.filter(is_valid=False))
            page = 'regDept'
            dept = Department.objects.get(id=id)
            region = dept.region
            formEditDept = AddDept(request.POST or None, instance=dept)
            if request.method == 'POST':
                if formEditDept.is_valid():
                    dept.name = formEditDept.cleaned_data['name'].upper()
                    dept.region = region
                    dept.save()
                    messages.add_message(request, messages.SUCCESS, 'Département modifié.')
                    return redirect('gestion_regions')
            return render(request, 'regions/RegionEditDept.html', locals())
        except Department.DoesNotExist:
            return redirect('gestion_regions')
    return redirect('connection')

# supprimer region
def deleteRegion(request, id):
    if 'email' and 'role' in request.session and request.session['role'] == 'admin':
        try:
            page = 'regDept'
            Region.objects.get(id=id).delete()
            messages.add_message(request, messages.SUCCESS, 'Région supprimée.')
            return redirect('gestion_regions')
        except Region.DoesNotExist:
            return redirect('gestion_regions')
    return redirect('connection')


# modifier region
def editRegion(request, id):
    if 'email' and 'role' in request.session and request.session['role'] == 'admin':
        try:
            demandsW = len(Technician.objects.filter(is_valid=False)) + len(Station.objects.filter(is_valid=False))
            page = 'regDept'
            email = request.session['email']
            admin= Administrator.objects.get(email=email)
            region = Region.objects.get(id=id)
            formEdit = AddRegion(request.POST or None, instance=region)
            if request.method == 'POST':
                if formEdit.is_valid():
                    region.name = formEdit.cleaned_data['name'].upper()
                    region.save()
                    messages.add_message(request, messages.SUCCESS, 'Région modifiée.')

                    return redirect('gestion_regions')
            return render(request, 'regions/editRegion.html', locals())
        except Region.DoesNotExist:
            return redirect('gestion_regions')
    return redirect('connection')

# gestion demande
def gestion_demandes(request):
    if 'email' and 'role' in request.session and request.session['role'] == 'admin':
        demandsW = len(Technician.objects.filter(is_valid=False)) + len(Station.objects.filter(is_valid=False))
        page = 'gestion_demandes'
        email = request.session['email']
        admin = Administrator.objects.get(email=email)

        # technician
        technicians = Technician.objects.filter(is_valid=False).order_by('-id')
        demandesTech = len(technicians)

        # station 
        stations = Station.objects.filter(is_valid=False).order_by('-id')
        demandesStation = len(stations)

        return render(request, 'demandes/gestion_demandes.html', locals())
    return redirect('connection')


# accept demande tech
def acceptDemand(request, id):
    if 'email' and 'role' in request.session and request.session['role'] == 'admin':
        try:
            technician = Technician.objects.get(id=id)
            subject = "accusée de demande"
            # mail tech
            try:
                
                message = "Bonjour "+technician.firstname+" "+technician.lastname+",\nVous êtes un Technicien dans ANMS (Agence Nationale de la Mététorologie Sénégalaise),: \nParamètre de connexion:\n\tEmail: "+ technician.email + "\n\tMot de passe: "+ technician.password + "\n\tAcceder à l'application: http://127.0.0.1:8000/"
                send_mail(subject, message, settings.EMAIL_HOST_USER,
                        [technician.email], fail_silently=False)
                message = "Bonjour "+technician.meteorologist.firstname+" "+technician.meteorologist.lastname+",\nVotre demande de création de technicien est accépté.\nDétails:\n\tPrénom: "+technician.firstname+ "\n\tNom: "+technician.lastname+ "\n\tMail: "+technician.email
                send_mail(subject, message, settings.EMAIL_HOST_USER,
                        [technician.meteorologist.email], fail_silently=False)
                
                technician.is_valid = True
                technician.save()
                messages.add_message(request, messages.SUCCESS, 'Demande création technicien acceptée.')
                return redirect('gestion_demandes')
            except:
                messages.add_message(request, messages.SUCCESS, 'Probléme de chargement ... Veuillez vérifier votre connexion internet svp.')
                return redirect('gestion_demandes')
            
        except Technician.DoesNotExist:
            return redirect('gestion_demandes')
    return redirect('connection')

# rejeter demande tech
def declineDemand(request,id):
    if 'email' and 'role' in request.session and request.session['role'] == 'admin':
        try:
            if request.method == 'POST':
                if 'message' in request.POST:
                    tech = Technician.objects.get(id=id)
                    message = request.POST['message']
                    try:
                        send_mail("Rejet demande", message, settings.EMAIL_HOST_USER,
                        [tech.meteorologist.email], fail_silently=False)
                        tech.delete()
                        messages.add_message(request, messages.SUCCESS, 'Demande création technicien rejetée.')
                        return redirect('gestion_demandes')
                    except:
                        messages.add_message(request, messages.SUCCESS, 'Probléme de chargement ... Veuillez vérifier votre connexion internet svp.')
                        return redirect('gestion_demandes')
            
        except Technician.DoesNotExist:
            return redirect('gestion_demandes')
    return redirect('connection')

# valider demande station
def acceptDemandStation(request, id):
    if 'email' and 'role' in request.session and request.session['role'] == 'admin':
        try:
            try:
                station = Station.objects.get(id=id)
                send_mail("Accusé demande", "La demande de création de la station "+station.name+" est accepté.", settings.EMAIL_HOST_USER,
                        [station.meteorologist.email], fail_silently=False)
                station.is_valid = True
                station.save()
                messages.add_message(request, messages.SUCCESS, 'Demande création station acceptée.')
                return redirect('gestion_demandes')
            except:
                messages.add_message(request, messages.SUCCESS, 'Probléme de chargement ... Veuillez vérifier votre connexion internet svp.')
                return redirect('gestion_demandes')
        except Station.DoesNotExist:
            return redirect('gestion_demandes')
    return redirect('connection')

# rejeter demande station
def declineDemandStation(request, id):
    if 'email' and 'role' in request.session and request.session['role'] == 'admin':
        try:
            station = Station.objects.get(id=id)
            if request.method == 'POST':
                if 'message' in request.POST:
                    try:
                        send_mail("Demande rejeter", "La demande de création de la station "+station.name+" est rejetée.", settings.EMAIL_HOST_USER,
                        [station.meteorologist.email], fail_silently=False)
                        messages.add_message(request, messages.SUCCESS, 'Demande création station rejetée.')
                        station.delete()
                    except:
                        messages.add_message(request, messages.SUCCESS, 'Probléme de chargement ... Veuillez vérifier votre connexion internet svp.')
                        return redirect('gestion_demandes')
            return redirect('gestion_demandes')
        except Station.DoesNotExist:
            return redirect('gestion_demandes')
    return redirect('connection')


# ____________ gestion profil ___________
def gestion_profil(request):
    if 'email' and 'role' in request.session and request.session['role'] == 'admin':
        demandsW = len(Technician.objects.filter(is_valid=False)) + len(Station.objects.filter(is_valid=False))

        email = request.session['email']
        admin = Administrator.objects.get(email=email)
        formEdit = AdminForm(request.POST or None, instance=admin)
        if request.method == 'POST':
            formEdit = AdminForm(request.POST or None,request.FILES, instance=admin)
            if formEdit.is_valid():
                
                old = request.POST['old']
                new = request.POST['new']
                if not okTel(formEdit.cleaned_data['tel']):
                    messages.add_message(request, messages.SUCCESS, 'Numéro te téléphone invalide.')
                    return redirect('gestion_profil')
                if not firstnameOk(formEdit.cleaned_data['firstname']):
                    messages.add_message(request, messages.SUCCESS, 'Prénom invalide.')
                    return redirect('gestion_profil')
                if not lastnameOk(formEdit.cleaned_data['lastname']):
                    messages.add_message(request, messages.SUCCESS, 'Nom invalide.')
                    return redirect('gestion_profil')

                if len(new) != 0 and len(old) !=0:
                    if old == admin.password:
                        if len(new) >= 8:
                            admin.password = new
                        else:
                            messages.add_message(request, messages.SUCCESS, 'Mots de passe trop court (8 caratères minimums).')
                            return redirect('gestion_profil')
                    else:
                        messages.add_message(request, messages.SUCCESS, 'Ancien mot de passe pas bon.')
                        return redirect('gestion_profil')
                techs = Technician.objects.filter(email=formEdit.cleaned_data['email'])
                mets = Meteorologist.objects.filter(email=formEdit.cleaned_data['email'])
                admins = Administrator.objects.filter(email=formEdit.cleaned_data['email'])

                if len(techs) == 0 and len(mets) == 0:
                    admin.firstname = admin.firstname.capitalize()
                    admin.lastname = admin.lastname.capitalize()
                    admin.save()
                    request.session['email'] = formEdit.cleaned_data['email']
                    messages.add_message(request, messages.SUCCESS, 'Profil mis à jour !.')
                    return redirect('gestion_profil')
                else:
                    messages.add_message(request, messages.SUCCESS, 'Mail déja prise !')
                    return redirect('gestion_profil')
                    formEdit = AdminForm(request.POST or None, instance=admin)
        return render(request,'profil/gestion_profil.html',locals())
    return redirect('connection')




# result rechercher
def resultSearch(request, id, role):
    if 'email' and 'role' in request.session and request.session['role'] == 'admin':
        try:
            demandsW = len(Technician.objects.filter(is_valid=False)) + len(Station.objects.filter(is_valid=False))

            email = request.session['email']
            admin = Administrator.objects.get(email=email)
            user = None
            if role == 'technicien':
                user = Technician.objects.get(id=id)
            elif role=='meteorologue':
                user = Meteorologist.objects.get(id=id)
            else:
                return redirect('homeA')
            return render(request,'search/search.html', locals())
        except Technician.DoesNotExist or Meteorologist.DoesNotExist:
            return redirect('homeA')
    return redirect('connection')


def changeStationForTech(request,idTech, idStation):
    if 'email' and 'role' in request.session and request.session['role'] == 'admin':
        tech = Technician.objects.get(id=idTech)
        station = Station.objects.get(id=idStation)
        tech.station = station
        tech.save()
        messages.add_message(request, messages.SUCCESS, 'Changement de station effectuer !')
        return redirect('gestion_technician')
    return redirect('gestion_technician')
    