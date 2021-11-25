from django import forms
from connection.models import *

# email = ''	
# liste des meteorologists
def meteorologist():
	meteorologists = []
	meteors = Meteorologist.objects.filter(statut=True)
	for meteorologist in meteors:
		meteorologists.append((Meteorologist.objects.get(id=meteorologist.id),meteorologist))
	return meteorologists

# formulaire inscrption
class AddTechnician(forms.ModelForm):
	firstname = forms.CharField(label='Prénom',widget=forms.TextInput(attrs={'autofocus':'autofocus','class':'form-control','placeholder':'Prénom *'}))
	lastname = forms.CharField(label='Nom',widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Nom *'}))
	address = forms.CharField(label='Adresse',widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Adresse *'}))
	tel = forms.CharField(label='Téléphone',widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Téléphone *'}))
	email = forms.EmailField(label='Mail',widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Mail *', 'type':'email'}))
	meteorologist = forms.ModelChoiceField(label='Météorologue', queryset=Meteorologist.objects.filter(trash=False), widget=forms.Select(attrs={'class':'form-control'}))
	# profile = forms.ImageField(required=False)

	class Meta:
		model = Technician
		exclude = ('statut','role','theme','trash','trash_at','password','is_valid','station','profile','is_online','last_connection')


# formulaire inscrption
class EditTechnician(forms.ModelForm):
	firstname = forms.CharField(label='Prénom',widget=forms.TextInput(attrs={'autofocus':'autofocus','class':'form-control','placeholder':'Prénom *'}))
	lastname = forms.CharField(label='Nom',widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Nom *'}))
	address = forms.CharField(label='Adresse',widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Adresse *'}))
	tel = forms.CharField(label='Téléphone',widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Téléphone *'}))
	meteorologist = forms.ModelChoiceField(label='Météorologue',queryset=Meteorologist.objects.filter(trash=False), widget=forms.Select(attrs={'class':'form-control'}))
	# station = forms.ModelChoiceField(label='Station',queryset=Station.objects.filter(trash=False))

	class Meta:
		model = Technician
		exclude = ('password','email','is_valid','role','theme','trash','trash_at','profile','station','is_online','last_connection')

# formulaire inscrption
class EditMeteologist(forms.ModelForm):
	firstname = forms.CharField(label='Prénom',widget=forms.TextInput(attrs={'autofocus':'autofocus','class':'form-control','placeholder':'Prénom *'}))
	lastname = forms.CharField(label='Nom',widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Nom *'}))
	address = forms.CharField(label='Adresse',widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Adresse *'}))
	tel = forms.CharField(label='Téléphone',widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Téléphone *'}))
	# profile = forms.ImageField(label='Image Profile',required=False)
	
	class Meta:
		model = Meteorologist
		exclude = ('password','email','role','trash','theme','trash_at','profile','is_online','last_connection')

# formulaire inscription
class AddMeteorologist(forms.ModelForm):
	firstname = forms.CharField(label='Prénom' ,widget=forms.TextInput(attrs={'autofocus':'autofocus','class':'form-control','placeholder':'Prénom *'}))
	lastname = forms.CharField(label= 'Nom',widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Nom *'}))
	address = forms.CharField(label='Adresse', widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Adresse *'}))
	tel = forms.CharField(label='Téléphone',widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Téléphone *'}))
	email = forms.EmailField(label='Mail',widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Mail *', 'type':'email'}), required=False)
	# profile = forms.ImageField(required=False)
	class Meta:
		model = Meteorologist
		exclude = ('statut','role','trash','password','trash_at','theme','profile','is_online','last_connection')

# formulaire inscription
class AddStation(forms.ModelForm):
	name = forms.CharField(label='Nom station',widget=forms.TextInput(attrs={'autofocus':'autofocus','class':'form-control','placeholder':'Nom Station *'}))
	latitude = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Latitude *'}))
	longitude = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Longitude *'}))
	meteorologist = forms.ModelChoiceField(label='Météorologue',queryset=Meteorologist.objects.filter(trash=False), widget=forms.Select(attrs={'class':'form-control'}))
	department = forms.ModelChoiceField(label='Département',queryset=Department.objects.filter(trash=False),widget=forms.Select(attrs={'class':'form-control'}))

	class Meta:
		model = Station
		exclude = ('statut','trash_at','map','trash','is_valid','activate_at')

# formulaire inscription
class AddDept(forms.ModelForm):
	name = forms.CharField(label='Département',widget=forms.TextInput(attrs={'autofocus':'autofocus','class':'form-control','placeholder':'Nom Département *'}))
	class Meta:
		model = Department
		exclude = ('map','trash','trash_at','admin',)

# formulaire inscription
class AddRegion(forms.ModelForm):
	name = forms.CharField(label='Région',widget=forms.TextInput(attrs={'autofocus':'autofocus','class':'form-control','placeholder':'Nom Région *'}))
	class Meta:
		model = Region
		exclude = ('map','trash','trash_at', 'admin',)

# formulaire administrateur
class AdminForm(forms.ModelForm):
	firstname = forms.CharField(label='Prénom', widget=forms.TextInput(attrs={'autofocus':'autofocus','class':'form-control','placeholder':'Prénom *'}))
	lastname = forms.CharField(label='Nom',widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Nom *'}))
	address = forms.CharField(label='Adresse',widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Adresse *'}))
	tel = forms.CharField(label='Téléphone',widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Téléphone *'}))
	email = forms.EmailField(label='Mail',widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Mail *', 'type':'email'}))
	profile = forms.ImageField(required=False)
	class Meta:
		model = Administrator
		exclude = ('trash','trash_at', 'role','password','theme','is_online','last_connection')
