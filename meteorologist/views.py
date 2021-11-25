from django.shortcuts import render, redirect
from connection.models import *
from .forms import *
from django.contrib import messages
import json
import folium
from datetime import datetime
from .resources import RainResource
from tablib import Dataset
from django_xhtml2pdf.utils import pdf_decorator
from administration.views import okTel, firstnameOk, lastnameOk


# Create your views here.

# accueil tech
def homeM(request):
    if 'email' and 'role' in request.session and request.session['role'] == 'met':

        if 'year' and 'month' and 'day' in request.session:
            del request.session['year'], request.session['month'], request.session['day']
        email = request.session['email']
        met = Meteorologist.objects.get(email=email)
        techActifs = Technician.objects.filter(is_valid=True, statut=True, meteorologist=met, trash=False)
        techInactifs = Technician.objects.filter(is_valid=True, statut=False, meteorologist=met, trash=False)
        techs = len(techActifs) + len(techInactifs)

        # station
        stationActifs = Station.objects.filter(is_valid=True, statut=True, meteorologist=met, trash=False)
        stationInactifs = Station.objects.filter(is_valid=True, statut=False, meteorologist=met, trash=False)
        stations = len(stationActifs) + len(stationInactifs)
        return render(request, 'homeM.html', locals())
    return redirect('connection')


# gestion tech
def gestion_technicianMet(request):
    if 'email' and 'role' in request.session and request.session['role'] == 'met':
        if 'year' and 'month' and 'day' in request.session:
            del request.session['year'], request.session['month'], request.session['day']

        page = 'gtech'
        form = AddTechnician(request.POST or None)
        email = request.session['email']
        met = Meteorologist.objects.get(email=email)
        stationDemands = Station.objects.filter(is_valid=False, meteorologist=met)
        techniciansDemandes = Technician.objects.filter(is_valid=False, meteorologist=met)
        demands = len(techniciansDemandes) + len(stationDemands)
        technicians = Technician.objects.filter(meteorologist=met, trash=False, is_valid=True)
        liste = json.dumps(list(Technician.objects.values('email', 'id', 'role').filter(trash=False, is_valid=True)))
        typ = 'tech'
        if 'tech' in request.GET:
            tech = int(request.GET['tech'])
        stations = Station.objects.filter(meteorologist=met, is_valid=True)
        techs = len(technicians)
        if request.method == 'POST':
            mete = Meteorologist.objects.filter(email=request.POST['email'])
            techn = Technician.objects.filter(email=request.POST['email'])
            admin = Administrator.objects.filter(email=request.POST['email'])
            if len(techn) >= 1 or len(mete) >= 1 or len(admin) >= 1:
                messages.add_message(request, messages.INFO, 'Adresse mail déjà existante.')
                return redirect('gestion_technicianMet')
            if form.is_valid():
                tech = Technician()
                tech.firstname = form.cleaned_data['firstname'].capitalize()
                tech.lastname = form.cleaned_data['lastname'].capitalize()
                tech.address = form.cleaned_data['address']
                tech.tel = form.cleaned_data['tel']
                tech.email = form.cleaned_data['email']
                tech.role = 'technicien'
                tech.is_valid = False
                tech.trash = False
                tech.meteorologist = Meteorologist.objects.get(email=email)
                tech.save()

                form = AddTechnician()
                messages.add_message(request, messages.INFO, 'Demande création technicien envoyer.')
                return redirect('gestion_technicianMet')

                # print(technicians)
        return render(request, 'technician/gestion_technician.html', locals())
    return redirect('connection')


# les demandes
def metDemands(request):
    if 'email' and 'role' in request.session and request.session['role'] == 'met':

        if 'year' and 'month' and 'day' in request.session:
            del request.session['year'], request.session['month'], request.session['day']

        page = 'demands'
        email = request.session['email']
        met = Meteorologist.objects.get(email=email)
        stationDemands = Station.objects.filter(is_valid=False, meteorologist=met)
        techniciansDemandes = Technician.objects.filter(is_valid=False, meteorologist=met)
        demands = len(techniciansDemandes) + len(stationDemands)
        return render(request, 'demands/metDemands.html', locals())
    return redirect('connection')


# annuler demandes technicien
def annulDemand(request, id):
    if 'email' and 'role' in request.session and request.session['role'] == 'met':

        try:
            Technician.objects.get(id=id).delete()
            messages.add_message(request, messages.INFO, 'Demande création technicien annulée.')
            return redirect('metDemands')
        except Technician.DoesNotExist:
            return redirect('metDemands')
    return redirect('connection')


# annuler demande station
def annulDemandStation(request, id):
    if 'email' and 'role' in request.session and request.session['role'] == 'met':

        try:
            Station.objects.get(id=id).delete()
            messages.add_message(request, messages.INFO, 'Demande création station annulée.')
            return redirect('metDemands')
        except Station.DoesNotExist:
            return redirect('metDemands')
    return redirect('connection')


# désactiver tech
def disableTechMet(request, id):
    if 'email' and 'role' in request.session and request.session['role'] == 'met':

        try:
            tech = Technician.objects.get(id=id)
            tech.statut = False
            tech.save()
            messages.add_message(request, messages.INFO, 'Technicien désactivé.')
            return redirect('gestion_technicianMet')
        except Technician.DoesNotExist:
            return redirect('gestion_technicianMet')
    return redirect('connection')


# active tech
def enableTechMet(request, id):
    if 'email' and 'role' in request.session and request.session['role'] == 'met':

        try:
            tech = Technician.objects.get(id=id)
            tech.statut = True
            tech.save()
            messages.add_message(request, messages.INFO, 'Technicien activé.')
            return redirect('gestion_technicianMet')
        except Technician.DoesNotExist:
            return redirect('gestion_technicianMet')
    return redirect('connection')


# affectation tech
def affectTech(request, idTech, idStation):
    if 'email' and 'role' in request.session and request.session['role'] == 'met':

        try:
            tech = Technician.objects.get(id=idTech)
            station = Station.objects.get(id=idStation)
            tech.station = station
            tech.save()
            messages.add_message(request, messages.INFO,
                                 'Affectation de ' + tech.firstname + ' ' + tech.lastname + ' sur la station ' + station.name + ' éffectuée.')
            return redirect('gestion_technicianMet')
        except:
            return redirect('gestion_technicianMet')
    return redirect('connection')


# ne pas affecter tech
def noAffect(request, id):
    if 'email' and 'role' in request.session and request.session['role'] == 'met':

        try:
            tech = Technician.objects.get(id=id)
            tech.station = None
            tech.save()
            messages.add_message(request, messages.INFO,
                                 'Technicien ' + tech.firstname + ' ' + tech.lastname + ' est disponible.')
            return redirect('gestion_technicianMet')
        except Technician.DoesNotExist:
            return redirect('gestion_technicianMet')
    return redirect('connection')


# archivé met
def trashTechMet(request, id):
    if 'email' and 'role' in request.session and request.session['role'] == 'met':

        try:
            tech = Technician.objects.get(id=id)
            tech.trash = True
            tech.save()
            messages.add_message(request, messages.INFO,
                                 'Technicien ' + tech.firstname + ' ' + tech.lastname + ' archivé.')
            return redirect('gestion_technicianMet')
        except Technician.DoesNotExist:
            return redirect('gestion_technicianMet')
    return redirect('connection')


# gestion station
def gestion_stationMet(request):
    if 'email' and 'role' in request.session and request.session['role'] == 'met':

        if 'year' and 'month' and 'day' in request.session:
            del request.session['year'], request.session['month'], request.session['day']

        page = 'station'
        met = Meteorologist.objects.get(email=request.session['email'])
        stationDemands = Station.objects.filter(is_valid=False, meteorologist=met)
        techniciansDemandes = Technician.objects.filter(is_valid=False, meteorologist=met)
        demands = len(techniciansDemandes) + len(stationDemands)
        stations = Station.objects.filter(meteorologist=met, is_valid=True)
        technicians = Technician.objects.filter(meteorologist=met, trash=False, is_valid=True)
        m = folium.Map(location=[13, -13], zoom_start=6,
                       min_zoom=5,
                       max_zoom=20)
        for stat in stations:
            if not stat.trash:
                if stat.statut == True:
                    folium.Marker([stat.latitude, stat.longitude],
                                  popup=stat.name,
                                  tooltip='station active, clicker pour + info',
                                  icon=folium.Icon(color='green')).add_to(m)
                elif stat.statut == False:
                    folium.Marker([stat.latitude, stat.longitude],
                                  popup=stat.name,
                                  tooltip='station non active,clicker pour + info',
                                  icon=folium.Icon(color='red')).add_to(m)
            else:
                folium.Marker([stat.latitude, stat.longitude],
                              popup=stat.name,
                              tooltip='station archivée, clicker pour + info', icon=folium.Icon(color='red')).add_to(m)

        m = m._repr_html_()
        # m.save('p.png')
        faye = 'faye'
        formAdd = AddStation(request.POST or None)
        if request.method == 'POST':
            if formAdd.is_valid():
                station = Station()
                m = folium.Map(location=[13, -13], zoom_start=6,
                               min_zoom=5,
                               max_zoom=12)
                station.name = formAdd.cleaned_data['name']
                station.meteorologist = met
                station.is_valid = False
                station.department = formAdd.cleaned_data['department']
                latitude = formAdd.cleaned_data['latitude']
                longitude = formAdd.cleaned_data['longitude']
                folium.Marker([latitude, longitude],
                              popup=station.name,
                              tooltip='station non active,clicker pour + info', icon=folium.Icon(color='green')).add_to(
                    m)
                m = m._repr_html_()
                station.map = m

                station.latitude = latitude
                station.longitude = longitude
                station.save()
                m = None
                messages.add_message(request, messages.INFO,
                                     'Demande de création de la station ' + station.name + ' éffectuée.')
                return redirect('gestion_stationMet')
        return render(request, 'stations/gestion_station.html', locals())
    else:
        return redirect('connection')


def dropTech(request, id):
    if 'email' and 'role' in request.session and request.session['role'] == 'met':

        try:
            tech = Technician.objects.get(id=id)
            tech.station = None
            tech.save()
            messages.add_message(request, messages.INFO,
                                 'Technicien ' + tech.firstname + ' ' + tech.lastname + ' est disponible.')
            return redirect('gestion_stationMet')
        except Meteorologist.DoesNotExist:
            return redirect('gestion_stationMet')
    return redirect('connection')


def G_station(request, id):
    if 'email' and 'role' in request.session and request.session['role'] == 'met':

        try:
            station = Station.objects.get(id=id)
            techs = Technician.objects.filter(station=station)
            statuts = Station.objects.filter(statut=False)
            for statut in statuts:
                if statut.activate_at:
                    # print(datetime.now())
                    date = datetime(year=statut.activate_at.year, month=statut.activate_at.month,
                                    day=statut.activate_at.day, hour=statut.activate_at.hour,
                                    minute=statut.activate_at.minute, second=statut.activate_at.second)
                    if date <= datetime.now():
                        st = Station.objects.get(id=statut.id)
                        st.statut = True
                        st.activate_at = None
                        # st.statut = True
                        st.save()

            met = Meteorologist.objects.get(email=request.session['email'])
            stationDemands = Station.objects.filter(is_valid=False, meteorologist=met)
            techniciansDemandes = Technician.objects.filter(is_valid=False, meteorologist=met)
            demands = len(techniciansDemandes) + len(stationDemands)
            page = 'station'
            p = 'details'
            users = station.technician_set.filter(trash=False, is_valid=True)
            technicians = Technician.objects.filter(is_valid=True, trash=False, station=None, meteorologist=met)
            # comments
            comments = Comments.objects.filter(station=station, trash=False)

            if 'com' in request.GET:
                comId = int(request.GET['com'])
                comm = Comments.objects.get(id=comId)
                comm.trash = True
                comm.save()
                messages.add_message(request, messages.INFO, 'Commentaire archivé.')
            if 'p' in request.GET:
                p = request.GET['p']

            # Programmer activation station
            form = ProgramStationActivation(request.POST or None)
            rains = RainData.objects.filter(station=station)
            if request.method == 'POST':
                if form.is_valid():
                    h = form.cleaned_data['h']
                    m = form.cleaned_data['m']
                    s = form.cleaned_data['s']
                    if s == None:
                        s = 0
                    if m == None:
                        m = 0
                    if h == None:
                        h = 0

                    if m >= 0 and m <= 60 and h >= 0 and h <= 23 and s >= 0 and s <= 60:

                        date = datetime(form.cleaned_data['date'].year, form.cleaned_data['date'].month,
                                        form.cleaned_data['date'].day, h, m, s)
                        if datetime.now() >= date:
                            messages.add_message(request, messages.SUCCESS,
                                                 "La date d'activation de la station doit être une date ultérieure à la date d'aujourd'hui.")
                            return redirect('G_station', id)
                        else:
                            station.activate_at = date
                            station.save()
                            messages.add_message(request, messages.SUCCESS,
                                                 "l'activation de la station " + station.name + " est prévue le " + str(
                                                     station.activate_at.day) + '/' + str(
                                                     station.activate_at.month) + '/' + str(
                                                     station.activate_at.year) + " à " + str(
                                                     station.activate_at.hour) + ":" + str(
                                                     station.activate_at.minute) + ":" + str(
                                                     station.activate_at.second))
                            return redirect('G_station', id)
                    else:
                        messages.add_message(request, messages.SUCCESS,
                                             "Heure doit être comprise entre 0 et 23, minute et seconde doivent être comprise entre 0 et 60.")
                        return redirect('G_station', id)

            return render(request, 'stations/gestion/G_station.html', locals())
        except Station.DoesNotExist:
            return redirect('gestion_stationMet')
    return redirect('connection')


def affectMetStation(request, idTech, id):
    if 'email' and 'role' in request.session and request.session['role'] == 'met':

        try:
            met = Meteorologist.objects.get(email=request.session['email'])
            stationDemands = Station.objects.filter(is_valid=False, meteorologist=met)
            techniciansDemandes = Technician.objects.filter(is_valid=False, meteorologist=met)
            demands = len(techniciansDemandes) + len(stationDemands)
            station = Station.objects.get(id=id)
            users = station.technician_set.filter(trash=False, is_valid=True)
            technicians = Technician.objects.filter(is_valid=True, trash=False, station=None, meteorologist=met)
            comments = Comments.objects.filter(station=station, trash=False)
            p = 'users'
            techN = Technician.objects.get(id=idTech)
            techN.station = station
            techN.save()
            # techEff = "Affectation éffectuée."
            messages.add_message(request, messages.INFO,
                                 'Technicien ' + techN.firstname + ' ' + techN.lastname + ' affecté sur station ' + station.name + '.')

            return render(request, 'stations/gestion/G_station.html', locals())
        except:
            return redirect('gestion_stationMet')
    return redirect('connection')


def deSaffectMetStation(request, idTech, id):
    if 'email' and 'role' in request.session and request.session['role'] == 'met':

        try:
            met = Meteorologist.objects.get(email=request.session['email'])
            stationDemands = Station.objects.filter(is_valid=False, meteorologist=met)
            techniciansDemandes = Technician.objects.filter(is_valid=False, meteorologist=met)
            demands = len(techniciansDemandes) + len(stationDemands)
            station = Station.objects.get(id=id)
            users = station.technician_set.filter(trash=False, is_valid=True)
            technicians = Technician.objects.filter(is_valid=True, trash=False, station=None, meteorologist=met)
            comments = Comments.objects.filter(station=station, trash=False)
            p = 'users'
            techN = Technician.objects.get(id=idTech)
            techN.station = None
            techN.save()
            techEff = "Technicien " + techN.firstname + " " + techN.lastname + " à nouveau disponible."
            messages.add_message(request, messages.SUCCESS, techEff)

            return render(request, 'stations/gestion/G_station.html', locals())
        except:
            return redirect('gestion_stationMet')
    return redirect('connection')


# déactiver station
def disableStationMet(request, id):
    if 'email' and 'role' in request.session and request.session['role'] == 'met':

        try:
            station = Station.objects.get(id=id)
            station.statut = False
            station.activate_at = None
            m = folium.Map(location=[13, -13], zoom_start=6,
                           min_zoom=5,
                           max_zoom=12)
            folium.Marker([station.latitude, station.longitude],
                          popup=station.name,
                          tooltip='station non active,clicker pour + info', icon=folium.Icon(color='red')).add_to(m)
            m = m._repr_html_()
            station.map = m
            m = None
            station.save()
            messages.add_message(request, messages.SUCCESS, 'Station désactivée.')
            return redirect('G_station', id)
        except Station.DoesNotExist:
            return redirect('G_station', id)
    return redirect('connection')


# enable station
def enableStationMet(request, id):
    if 'email' and 'role' in request.session and request.session['role'] == 'met':

        try:
            station = Station.objects.get(id=id)
            station.statut = True
            station.activate_at = None
            m = folium.Map(location=[13, -13], zoom_start=6,
                           min_zoom=5,
                           max_zoom=12)
            folium.Marker([station.latitude, station.longitude],
                          popup=station.name,
                          tooltip='station non active,clicker pour + info', icon=folium.Icon(color='green')).add_to(m)
            m = m._repr_html_()
            station.map = m
            m = None
            station.save()
            messages.add_message(request, messages.SUCCESS, 'Station activée.')
            return redirect('G_station', id)
        except Station.DoesNotExist:
            return redirect('G_station', id)
    return redirect('connection')


def variance(rains, moy):
    h = 0
    if len(rains) > 1:
        for rain in rains:
            h = h + pow((float(rain.value) - float(moy)), 2)
        return h / (len(rains) - 1)
    return rains[0].value


# les statistiques
def statisticStation(request, id):
    if 'email' and 'role' in request.session and request.session['role'] == 'met':

        try:

            page = 'station'
            met = Meteorologist.objects.get(email=request.session['email'])
            stationDemands = Station.objects.filter(is_valid=False, meteorologist=met)
            techniciansDemandes = Technician.objects.filter(is_valid=False, meteorologist=met)
            demands = len(techniciansDemandes) + len(stationDemands)
            station = Station.objects.get(id=id)
            users = station.technician_set.filter(trash=False, is_valid=True)
            comments = Comments.objects.filter(station=station, trash=False)

            if request.method == 'POST':
                if 'releve' and 'idR' in request.POST:
                    releve = request.POST['releve']
                    idR = request.POST['idR']
                    rain = RainData.objects.get(id=idR)

                    tab = request.POST['releve'].split(',')
                    re = '.'.join(tab)

                    try:
                        rain.value = float(re)
                        rain.save()
                        ok = 'relevé effectué à la date ' + str(
                            rain.created_at) + ' par le technicien ' + rain.technician.firstname + ' ' + rain.technician.lastname + ' modifié avec succès.'

                    except:
                        invalid = 'valeur relevé invalide.'

            rains = RainData.objects.filter(station=station)

            if 'filter' in request.POST:
                if request.POST['filter'] != '':
                    tab = request.POST['filter'].split('-')
                    year = int(tab[0])
                    month = int(tab[1])
                    day = int(tab[2])
                    request.session['year'] = year
                    request.session['month'] = month
                    request.session['day'] = day

                    dat = datetime(year=int(year), month=int(month), day=int(day))

            tabId = []
            for rain in rains:
                tabId.append(rain.id)

            if len(tabId) > 0:
                now = RainData.objects.get(id=max(tabId)).created_at

                if 'year' and 'month' and 'day' in request.session:
                    dat = datetime(year=request.session['year'], month=request.session['month'],
                                   day=request.session['day'])
                else:

                    dat = now
            tabList = []
            somme = 0
            p = 'default'

            if 'p' in request.GET:
                p = request.GET['p']

            # par defaut on affiche le dernier mois
            if p == 'default':
                for rain in rains:
                    # print(rain.created_at.w)
                    if dat.year == rain.created_at.year and dat.month == rain.created_at.month:
                        if 'year' and 'month' and 'day' in request.session:
                            day = request.session['day']
                        somme = somme + rain.value
                        tabList.append(rain)

            # semaine 1 du mois
            elif p == 's1':
                for rain in rains:
                    if dat.year == rain.created_at.year and dat.month == rain.created_at.month and int(
                            rain.created_at.day) <= 7:
                        # print()  
                        if 'year' and 'month' and 'day' in request.session:
                            day = request.session['day']
                        somme = somme + rain.value
                        tabList.append(rain)

            # semaine 2 du mois
            elif p == 's2':
                for rain in rains:
                    if dat.year == rain.created_at.year and dat.month == rain.created_at.month and 7 < int(
                            rain.created_at.day) < 15:
                        # print() 
                        if 'year' and 'month' and 'day' in request.session:
                            day = request.session['day']
                        somme = somme + rain.value
                        tabList.append(rain)
            # semaine 3 du mois
            elif p == 's3':
                for rain in rains:
                    if dat.year == rain.created_at.year and dat.month == rain.created_at.month and 15 <= int(
                            rain.created_at.day) < 22:
                        # print()  
                        somme = somme + rain.value
                        tabList.append(rain)

            # semaine 4 du mois
            elif p == 's4':
                for rain in rains:
                    if dat.year == rain.created_at.year and dat.month == rain.created_at.month and int(
                            rain.created_at.day) >= 22:
                        # print()  
                        if 'year' and 'month' and 'day' in request.session:
                            day = request.session['day']
                        somme = somme + rain.value
                        tabList.append(rain)

            if len(tabList) != 0:
                my_rain = tabList[0]
            values = []
            for rain in tabList:
                values.append(rain.value)
            if len(values) != 0:
                # min
                mini = min(values)
                # max
                maxi = max(values)
                moy = float(somme / len(tabList))
                var = variance(tabList, moy)
            tab = []
            if len(tabList) > 0:
                t = tabList[0]

            

            return render(request, 'stations/gestion/statisticStation.html', locals())
        except Station.DoesNotExist:
            return redirect('G_station', id)
    return redirect('connection')

class Month():
    def __init__(self, name, value):
        self.name = name
        self.value = value


class Week():
    def __init__(self, name, value):
        self.name = name
        self.value = value

@pdf_decorator
def exports(request, id, year):
    if 'email' and 'role' in request.session and request.session['role'] == 'met' or request.session['role'] == 'tech':

        station = Station.objects.get(id=id)
        rains = RainData.objects.filter(station=station)
        data = []
        i = 0
        somme = 0
        while i <= 12:
            for rain in rains:
                if rain.created_at.year == year:
                    if rain.created_at.month == i:
                        somme = somme + rain.value
            if i == 1:
                data.append(Month(name='Janvier', value=somme))
                somme = 0
            elif i == 2:
                data.append(Month(name='Février', value=somme))
                somme = 0
            elif i == 3:
                data.append(Month(name='Mars', value=somme))
                somme = 0
            elif i == 4:
                data.append(Month(name='Avril', value=somme))
                somme = 0
            elif i == 5:
                data.append(Month(name='Mai', value=somme))
                somme = 0
            elif i == 6:
                data.append(Month(name='Juin', value=somme))
                somme = 0
            elif i == 7:
                data.append(Month(name='Juillet', value=somme))
                somme = 0
            elif i == 8:
                data.append(Month(name='Août', value=somme))
                somme = 0
            elif i == 9:
                data.append(Month(name='Septembre', value=somme))
                somme = 0
            elif i == 10:
                data.append(Month(name='Octobre', value=somme))
                somme = 0
            elif i == 11:
                data.append(Month(name='Novembre', value=somme))
                somme = 0
            elif i == 12:
                data.append(Month(name='Décembre', value=somme))
                somme = 0
            i = i + 1
        tab = []
        som = 0
        for t in data:
            som = som + t.value
            tab.append(t.value)
        
        # print(tab)
        mini = min(tab)
        maxi = max(tab)
        moy = moy = "{:.2f}".format(som / len(tab))
        return render(request, 'stations/gestion/exports.html', locals())
    else:
        return redirect('connection')


# ____________ gestion profil ___________
def gestion_profilMet(request):
    if 'email' and 'role' in request.session and request.session['role'] == 'met':
        email = request.session['email']
        met = Meteorologist.objects.get(email=email)
        stationDemands = Station.objects.filter(is_valid=False, meteorologist=met)
        techniciansDemandes = Technician.objects.filter(is_valid=False, meteorologist=met)
        demands = len(techniciansDemandes) + len(stationDemands)

        formEdit = MetForm(request.POST or None, instance=met)
        if request.method == 'POST':
            formEdit = MetForm(request.POST or None, request.FILES, instance=met)
            if formEdit.is_valid():
                   
                old = request.POST['old']
                new = request.POST['new']
                if not okTel(formEdit.cleaned_data['tel']):
                    messages.add_message(request, messages.SUCCESS, 'Numéro te téléphone invalide.')
                    return redirect('gestion_profilMet')
                if not firstnameOk(formEdit.cleaned_data['firstname']):
                    messages.add_message(request, messages.SUCCESS, 'Prénom invalide.')
                    return redirect('gestion_profilMet')
                if not lastnameOk(formEdit.cleaned_data['lastname']):
                    messages.add_message(request, messages.SUCCESS, 'Nom invalide.')
                    return redirect('gestion_profilMet')

                techs = Technician.objects.filter(email=formEdit.cleaned_data['email'])
                admins = Administrator.objects.filter(email=formEdit.cleaned_data['email'])
                mets = Meteorologist.objects.filter(email=formEdit.cleaned_data['email'])
                if len(mets) <= 1:
                    if len(techs) == 0 and len(admins) == 0 and met.email == formEdit.cleaned_data['email']:

                        if len(new) != 0 and len(old) != 0:
                            if old == met.password:
                                if len(new) >= 8:
                                    met.password = new
                                    met.save()
                                else:
                                    messages.add_message(request, messages.SUCCESS,
                                                         'Mots de passe trop court (8 caratères minimums).')
                                    return redirect('gestion_profilMet')
                            else:
                                messages.add_message(request, messages.SUCCESS, 'Ancien mot de passe pas bon.')
                                return redirect('gestion_profilMet')
                        met.firstname = met.firstname.capitalize()
                        met.lastname = met.lastname.capitalize()
                        met.save()
                        request.session['email'] = formEdit.cleaned_data['email']
                        messages.add_message(request, messages.SUCCESS, 'Profil mis à jour !.')
                        return redirect('gestion_profilMet')
                    else:
                        messages.add_message(request, messages.SUCCESS, 'Mail déja prise !')
                        return redirect('gestion_profilMet')

                messages.add_message(request, messages.SUCCESS, 'Profil mis à jour !.')
                return redirect('gestion_profilMet')
        return render(request, 'profil/gestion_profilMet.html', locals())
    return redirect('connection')



def yearStatistics(request, id):
    if 'email' and 'role' in request.session and request.session['role'] == 'met':
        page = 'station'
        met = Meteorologist.objects.get(email=request.session['email'])
        stationDemands = Station.objects.filter(is_valid=False, meteorologist=met)
        techniciansDemandes = Technician.objects.filter(is_valid=False, meteorologist=met)
        demands = len(techniciansDemandes) + len(stationDemands)
        station = Station.objects.get(id=id)
        comments = Comments.objects.filter(station=station, trash=False)

        rains = RainData.objects.filter(station=station)
        tabDates = []
        for r in rains:
            tabDates.append(r.created_at.year)
        years = []
        if len(rains) != 0:
            begin = min(tabDates)
            end = max(tabDates)
            between = end - begin
            years.append(begin)
            j = 1
            while j < between:
                print(begin)
                begin = begin + 1
                years.append(begin)
                j = j + 1

        data = []
        minRain = 0
        maxRain = 0
        somme = 0
        i = 1
        if len(rains) != 0:
            year = datetime.now().year-1
        lastYear = datetime.now().year - 1
        if request.method == 'POST':
            if 'year' in request.POST:
                year = request.POST['year']
                if year != '':
                    # print(year)
                    lastYear = int(year)


        while i <= 12:
            for rain in rains:
                if rain.created_at.year == lastYear:
                    if rain.created_at.month == i:
                        somme = somme + rain.value
            if i == 1:
                data.append(Month(name='Janvier', value=somme))
                somme = 0
            elif i == 2:
                data.append(Month(name='Février', value=somme))
                somme = 0
            elif i == 3:
                data.append(Month(name='Mars', value=somme))
                somme = 0
            elif i == 4:
                data.append(Month(name='Avril', value=somme))
                somme = 0
            elif i == 5:
                data.append(Month(name='Mai', value=somme))
                somme = 0
            elif i == 6:
                data.append(Month(name='Juin', value=somme))
                somme = 0
            elif i == 7:
                data.append(Month(name='Juillet', value=somme))
                somme = 0
            elif i == 8:
                data.append(Month(name='Août', value=somme))
                somme = 0
            elif i == 9:
                data.append(Month(name='Septembre', value=somme))
                somme = 0
            elif i == 10:
                data.append(Month(name='Octobre', value=somme))
                somme = 0
            elif i == 11:
                data.append(Month(name='Novembre', value=somme))
                somme = 0
            elif i == 12:
                data.append(Month(name='Décembre', value=somme))
                somme = 0
            i = i + 1
        tab = []
        somme = 0
        for t in data:
            tab.append('.'.join(str(t.value).split(',')))
            somme = somme + t.value
        
        tabR = []
        for d in data:
            tabR.append(d.value)

        minRain = min(tabR)
        maxRain = max(tabR)
        moy = "{:.2f}".format(somme / len(tabR)) 

        return render(request, 'stations/gestion/yearStatistics.html', locals())
    return redirect('connection')

def hebdoStat(request, id):
    if 'email' and 'role' in request.session and request.session['role'] == 'met':
        page = 'station'
        met = Meteorologist.objects.get(email=request.session['email'])
        stationDemands = Station.objects.filter(is_valid=False, meteorologist=met)
        techniciansDemandes = Technician.objects.filter(is_valid=False, meteorologist=met)
        demands = len(techniciansDemandes) + len(stationDemands)
        station = Station.objects.get(id=id)

        rains = RainData.objects.filter(station=station)
        if len(rains) != 0:
            tabDates = []
            for r in rains:
                tabDates.append(r.created_at.year)
            years = []
            if len(rains) != 0:
                begin = min(tabDates)
                end = max(tabDates)
                between = end - begin
                years.append(begin)
                j = 1
                while j < between:
                    # print(begin)
                    begin = begin + 1
                    years.append(begin)
                    j = j + 1
        
            newData = []
            year = datetime.now().year - 1
            month = 8
            now = datetime(year,month,1)
            if request.method == 'POST':
                if 'month' and 'year' in request.POST:
                    month = int(request.POST['month'])
                    year = int(request.POST['year'])
                    now = datetime(year,month,1)
                    # print(year,month)
            realRains = []
            for r in rains:
                if int(r.created_at.year) == year and int(r.created_at.month) == month:
                    realRains.append(r)
        
            semaine1 = 0
            semaine2 = 0
            semaine3 = 0
            semaine4 = 0
            for r in realRains:
                if r.created_at.day <= 7:
                    semaine1 = semaine1 + float(r.value)
                elif 7 < r.created_at.day < 15:
                    semaine2 = semaine2 + float(r.value)
                elif 15 <= r.created_at.day < 21:
                    semaine3 = semaine3 + float(r.value)
                else:
                    semaine4 = semaine4 + float(r.value)

        # the weeks
        week1 = Week('semaine 1(jour 1-7)', semaine1)
        week2 = Week('semaine 2 (jour 8-15)', semaine2)
        week3 = Week('semaine 3 (jour 16-21)', semaine3)
        week4 = Week('semaine 4 (jour 22-fin)', semaine4)

        # appenning weeks
        newData.append(week1)
        newData.append(week2)
        newData.append(week3)
        newData.append(week4)
        tab = []
        somme = 0
        for d in newData:
            somme = somme + d.value
            tab.append(d.value)

        minRain = min(tab)
        maxRain = max(tab)
        moy = "{:.2f}".format(somme / len(tab))
        return render(request, 'stations/gestion/hebdoStat.html', locals())
    return redirect('connection')

def g_releve(request):
    if 'email' and 'role' in request.session and request.session['role'] == 'met':
        page = 'rains'
        met = Meteorologist.objects.get(email=request.session['email'])
        stationDemands = Station.objects.filter(is_valid=False, meteorologist=met)
        techniciansDemandes = Technician.objects.filter(is_valid=False, meteorologist=met)
        demands = len(techniciansDemandes) + len(stationDemands)
        # rains = RainData.objects.all()
        stations = Station.objects.filter(meteorologist=met)
        rains = []
        if stations:
            station = stations.first()           

        # edit rain data
        if request.method == 'GET':
            if 'id' and 'v' and 'stat' in request.GET:
                stat = request.GET['stat']
                station = Station.objects.get(id=int(stat))
                id = int(request.GET['id'])
                v = request.GET['v'].split(',')
                try:
                    val = float('.'.join(v))
                    r = RainData.objects.get(id=id)
                    r.value = val
                    r.save()
                    ok = 'Modification réussie.'
                except:
                    error = 'valeur invalide.'

        if stations:
            if request.method == 'POST':
                if 'stat' in request.POST:
                    stat = request.POST['stat']
                    station = Station.objects.get(id=int(stat))
                
            
            rains = RainData.objects.filter(station=station).order_by('-id')
            if len(rains) >= 10:
                rains = rains[:10]  
                
        else: 
            noStation = "Aucune station n'est gérer par ce météorologue."        

        return render(request,'rains/g_releve.html', locals())
    return redirect('connection')