from django.shortcuts import render, redirect
from .models import *
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from datetime import datetime


# _____________________ LES VUES __________________

# cette vue permet de se connecté a l'application
def connection(request):
    if request.method == 'GET':
        if 'emailForGetting' in request.GET:
            

            # userGettingPass = Person()
            isEmailValid = False
            emailForGetting = request.GET['emailForGetting']
            
            users = []
            admins = Administrator.objects.all()
            techs = Technician.objects.filter(is_valid=True)
            mets = Meteorologist.objects.all()

            for admin in admins:
                users.append(admin)
            for tech in techs:
                users.append(tech)
            for met in mets:
                users.append(tech)

            
            # print(users)
            for user in users:
                if user.email == emailForGetting:
                    isEmailValid = True
                    userGettingPass = user
                    break
            
            if isEmailValid == True:
                try:
                    newPassword = getPassword(8)
                    userGettingPass.password = newPassword
                    message = "Bonjour "+userGettingPass.firstname+" "+userGettingPass.lastname+",vos paramètres de connexion: \nEmail: "+userGettingPass.email+ "\nMot de passe: "+newPassword
                    send_mail("Recupération Mail", message, settings.EMAIL_HOST_USER,[userGettingPass.email], fail_silently=False)
                    
                    
                    userGettingPass.save()
                    messages.add_message(request, messages.SUCCESS, 'Un Mail contenant vos paramètres de connexion vous a été envoyé à l\'adresse '+userGettingPass.email+'.')
                    return redirect('connection')
                except:
                    messages.add_message(request, messages.SUCCESS, 'Assurez-vous que votre connexion internet soit activée pour effectuer cette demande!')
                    return redirect('connection')
            else:
                notGoodMail = 'Adresse Mail inconnue par le systeme.'

            
    # recupération de la méthode de la requête
    method  =  request.method 
    # vérification méthode
    if method == 'POST':

        # recupèrer email 
        email = request.POST['email']

        # recupèrer mot de passe
        password = request.POST['password']

        admins = Administrator.objects.filter(email=email, password=password)       

        technicians = Technician.objects.filter(email=email, password=password, is_valid=True)

        meteorologists = Meteorologist.objects.filter(email=email, password=password)

        len_admin = len(admins)
        len_technicians = len(technicians)
        len_meteorologists = len(meteorologists)


        # c'est un administrateur
        if len_admin == 1:
            request.session['email'] = email
            request.session['role'] = 'admin'
            admin = Administrator.objects.get(email = email)
            admin.is_online = True
            admin.save()
            welcomeMessage = "Bienvenu "+admin.firstname+" "+admin.lastname+". C'est toujour un plaisir de vous accueilir parmi nous!"
            welcomeMessage = welcomeMessage
            messages.add_message(request, messages.INFO, welcomeMessage)
            return redirect('homeA')
        
        # un météorologue
        elif len_meteorologists == 1:
            request.session['email'] = email
            request.session['role'] = 'met'
            met = Meteorologist.objects.get(email=email) 
            if (met.statut == False):
                messages.add_message(request, messages.INFO, 'Vous n\'êtes pas autorisé à acceder à l\'apllication pour le moment, Veuillez contacter l\'administrateur.')
                return redirect('connection')    
            messages.add_message(request, messages.INFO, "Bienvenu "+met.firstname+" "+met.lastname+". C'est toujour un plaisir de vous accueilir parmi nous :)")
            met.is_online = True
            met.save()
            return redirect('homeM')
        # un technicien
        elif len_technicians == 1:
            request.session['email'] = email
            request.session['role'] = 'tech'
            tech = Technician.objects.get(email=email)
            if (tech.statut == False):
                adminMail = Administrator.objects.all().get()
                messages.add_message(request, messages.INFO, 'Vous n\'êtes pas autorisé à acceder à l\'apllication pour le moment, Veuillez contacter l\'administrateur. Son Mail: '+adminMail.email)
                return redirect('connection')
            tech.is_online = True
            tech.save()
            messages.add_message(request, messages.INFO, "Bienvenu "+tech.firstname+" "+tech.lastname+". C'est toujour un plaisir de vous accueilir parmi nous :)")
            return redirect('homeT')
        # données invalides
        else:
            
            messages.add_message(request, messages.INFO, 'Mail et/ou Mot de passe invalide.')
            return redirect('connection')
        
    return render(request, 'connection.html', locals())


                
#     return redirect('connection')

# déconnexion
def disconnect(request):
    if 'role' in request.session:
        email = request.session['email']
        role = request.session['role']
        if role == 'admin':
            admin = Administrator.objects.get(email=email)
            admin.last_connection = datetime.now()
            admin.is_online = False
            admin.save()
        elif role == 'met':
            met = Meteorologist.objects.get(email=email)
            met.last_connection = datetime.now()
            met.is_online = False
            met.save()
        else:
            tech = Technician.objects.get(email=email)
            tech.last_connection = datetime.now()
            tech.is_online = False
            tech.save()
    request.session.clear()
    return redirect('connection')
