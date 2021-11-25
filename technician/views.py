from django.shortcuts import render, redirect
from connection.models import *
from .forms import *
from django.contrib import messages
from datetime import datetime
from tablib import Dataset
from administration.views import okTel, firstnameOk, lastnameOk
from meteorologist.views import Week, Month
# Create your views here.

def homeT(request):
    if 'email' and 'role' in request.session and request.session['role'] == 'tech':
        tech = Technician.objects.get(email=request.session['email'])
        isListEmpty = False
        if tech.station != None:
            techs = Technician.objects.filter(station=tech.station)

        if len(techs) == 0:
            isListEmpty = True

        rains = len(RainData.objects.filter(station=tech.station))
        return render(request,'homeT.html', locals())
    return redirect('connection')

def techStation(request):
    if 'email' and 'role' in request.session and request.session['role'] == 'tech':

        # page active
        page = 'station'

        # utilisateu connecté
        tech = Technician.objects.get(email=request.session['email'])

        # la station
        station = tech.station
        rains = RainData.objects.filter(station=station)
        # partie par defaut
        p = 'details'

        if 'p' in request.GET:
            p = request.GET['p']
        # commentaires sur la station
        comments = Comments.objects.filter(station=station, trash=False).order_by('-id')
        form = addCommentForm(request.POST or None)
        if request.method == 'POST':
            if form.is_valid():
                comment = Comments()
                comment.content = form.cleaned_data['content']
                comment.technician = tech
                comment.station = station
                comment.save()
                messages.add_message(request, messages.SUCCESS, 'Vous venez de commenter la station.')
                return redirect('techStation')
        

        # ____________relevé____________
        # save directly
        if request.method == 'GET':
            
            if 'rain' and 'dateRain' in request.GET:
                rain = request.GET['rain']
                dateRain = request.GET['dateRain']
                print('ok 1')
                # print(type(dateRain))
                try:
                    rains = RainData.objects.all()
                    print('ok 2')
                    r = float(rain)
                    if dateRain != '':
                        dateNow = str(datetime.now()).split(' ')[0]
                        # print(datetime.now())
                        if dateRain <= dateNow:
                            # now = datetime.now()
                            exist = False
                            for rd in rains:
                                if str(rd.created_at) == dateRain:
                                    rd.value = float(rd.value) + r
                                    exist = True
                                    rd.save()
                                    messages.add_message(request, messages.SUCCESS, 'relevé enregistré avec succès.')
                                    return redirect('techStation')
                        else:
                            messages.add_message(request, messages.SUCCESS, 'La date saisie est ultérieure à la date d\'aujourd\'hui.')
                            return redirect('techStation')
                    else:
                        now = datetime.now()
                        exist = False
                        for rd in rains:
                            if now.year == rd.created_at.year and now.month == rd.created_at.month and now.day == rd.created_at.day:
                                rd.value = float(rd.value) + r
                                rd.save()
                                exist = True
                                messages.add_message(request, messages.SUCCESS, 'relevé enregistré avec succès.')
                                return redirect('techStation')
        
                    print('ok 3')
                    if exist == False:
                        newRain = RainData()
                        newRain.station = station
                        newRain.technician = tech
                        newRain.value = r
                        if dateRain != '':
                            newRain.created_at = dateRain
                            print('ok')
                        newRain.save()
                        messages.add_message(request, messages.SUCCESS, 'relevé enregistré avec succès.')
                        return redirect('techStation')
        
                except:
                    msg = 'Valeur invalide. Veuillez saisir un nombre.'

        # imports
        isUploading = False
        if request.method == 'POST':
            if 'file' in request.FILES:
                isUploading = True
                print('ok')
                dataset = Dataset()
                new_rain = request.FILES['file']
                if new_rain.name.endswith('xlsx'):
                    imported_data = dataset.load(new_rain.read(),format='xlsx')
                    length = len(imported_data[0])
                    if length == 2:
                        for data in imported_data:
                            
                            rain = RainData()
                            rain.value = data[0]
                            rain.created_at = data[1]
                            rain.station = station
                            rain.technician = tech
                            # print(rain)
                            try:

                                rains = RainData.objects.filter(station=station)
                                ok = False
                                for r in rains:
                                    if r.created_at.year == rain.created_at.year and r.created_at.month == rain.created_at.month and r.created_at.day == rain.created_at.day:
                                        print('ok')
                                        r.value = float(rain.value) + float(rain.value)
                                        r.save()
                                        ok = True
                                
                                if ok == False:
                                    rain.save()
                                
                                
                                result = rain_resource.import_data(dataset, dry_run=True)
                                
                                
                                if not result.has_errors():
                                    isUploading = False
                                    messages.add_message(request, messages.SUCCESS, 'importation relevés éffectué.')
                                    return redirect('techStation')
                                else:
                                    notOk = "Une erreur s'est produit lors de l'importation des données"
                            except:
                                
                                print('orror')
                    else:
                        errors = 'format fichier invalide. voir image'  
                else:
                    error = "Format fichier invalide."
                    messages.add_message(request, messages.SUCCESS,error)
                    return redirect('techStation')
                    

            
        return render(request,'station/techStation.html', locals())
    return redirect('connection')


# supprimer commentaire
def trashComment(request, id):
    if 'email' and 'role' in request.session and request.session['role'] == 'tech':
        try:
            comment = Comments.objects.get(id=id)
            comment.trash = True
            comment.save()
            messages.add_message(request, messages.SUCCESS, 'Commentaire supprimé.')
            return redirect('techStation')
        except Comments.DoesNotExist:
            return redirect('techStation')
    return redirect('connection')


# ____________ gestion profil ___________
def profileTech(request):
    if 'email' and 'role' in request.session and request.session['role'] == 'tech':

        email = request.session['email']
        tech = Technician.objects.get(email=email)
        formEdit = TechForm(request.POST or None, instance=tech)
        if request.method == 'POST':
            formEdit = TechForm(request.POST or None, request.FILES, instance=tech)
            if formEdit.is_valid():
                print(formEdit.cleaned_data['profile'])
                old = request.POST['old']
                new = request.POST['new']
                if not okTel(formEdit.cleaned_data['tel']):
                    messages.add_message(request, messages.SUCCESS, 'Numéro te téléphone invalide.')
                    return redirect('profileTech')
                if not firstnameOk(formEdit.cleaned_data['firstname']):
                    messages.add_message(request, messages.SUCCESS, 'Prénom invalide.')
                    return redirect('profileTech')
                if not lastnameOk(formEdit.cleaned_data['lastname']):
                    messages.add_message(request, messages.SUCCESS, 'Nom invalide.')
                    return redirect('profileTech')

                techs = Technician.objects.filter(email=formEdit.cleaned_data['email'])
                admins = Administrator.objects.filter(email=formEdit.cleaned_data['email'])
                mets = Meteorologist.objects.filter(email=formEdit.cleaned_data['email'])
                if  len(techs) <= 1:
                    if len(mets) == 0 and len(admins) == 0 and tech.email == formEdit.cleaned_data['email']:
                        
                        if len(new) != 0 and len(old) !=0:
                            if old == tech.password:
                                if len(new) >= 8:
                                    
                                    tech.password = new
                                    tech.save()
                                else:
                                    messages.add_message(request, messages.SUCCESS, 'Mots de passe trop court (8 caratères minimums).')
                                    return redirect('profileTech')
                            else:
                                messages.add_message(request, messages.SUCCESS, 'Ancien mot de passe pas bon.')
                                return redirect('profileTech')
                        tech.firstname = tech.firstname.capitalize()
                        tech.lastname = tech.lastname.capitalize()
                        tech.save()
                        request.session['email'] = formEdit.cleaned_data['email']
                        messages.add_message(request, messages.SUCCESS, 'Profil mis à jour !.')
                        return redirect('profileTech')
                    else:
                        messages.add_message(request, messages.SUCCESS, 'Mail déja prise !')
                        return redirect('profileTech')
                        

                

               
                messages.add_message(request, messages.SUCCESS, 'Profil mis à jour !.')
                return redirect('profileTech')
        return render(request,'profile/profileTech.html',locals())
    return redirect('connection')

def releveToolbox(request):

    if 'email' and 'role' in request.session and request.session['role'] == 'tech':
        tech = Technician.objects.get(email=request.session['email'])
        page = 'rain'
        rains = RainData.objects.filter(station=tech.station, technician=tech)
        if len(rains)>= 10:
            lastRains = RainData.objects.filter(station=tech.station, technician=tech).order_by('-created_at')[:10]
        else:
            lastRains = RainData.objects.filter(station=tech.station, technician=tech)
        if request.method == 'POST':
            if 'id' and 'v' in request.POST:
                id = request.POST['id']
                v = request.POST['v']
                r = RainData.objects.get(id=id)
                try:
                    r.value = float(v)
                    r.save()
                except:
                    messages.add_message(request, messages.SUCCESS, 'Veuillez saisir une valeur valide!')
                    return redirect('releveToolbox')
        return render(request,'rains/releveToolbox.html', locals())
    return redirect('connection')

def monthStat(request, id):
    if 'email' and 'role' in request.session and request.session['role'] == 'tech':
        tech = Technician.objects.get(email=request.session['email'])
        page = 'station'
        station = Station.objects.get(id=id)
    
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
        minRain = min(tab)
        maxRain = max(tab)
        moy = "{:.2f}".format(somme / len(tab)) 


        return render(request,'station/monthStat.html', locals())
    return redirect('connection')


def hebdo(request, id):
    if 'email' and 'role' in request.session and request.session['role'] == 'tech':
        tech = Technician.objects.get(email=request.session['email'])
        page = 'station'
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
        return render(request,'station/hebdo.html', locals())
    return redirect('connection')