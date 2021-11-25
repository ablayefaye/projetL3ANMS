from django import forms
from connection.models import *



# formulaire inscrption
class AddTechnician(forms.ModelForm):
	firstname = forms.CharField(label='Prénom', widget=forms.TextInput(attrs={'autofocus':'autofocus','class':'form-control','placeholder':'Prénom *'}))
	lastname = forms.CharField(label='Nom', widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Nom *'}))
	address = forms.CharField(label='Adresse', widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Adresse *'}))
	tel = forms.CharField(label='Téléphone', widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Téléphone *'}))
	email = forms.EmailField(label='Mail', widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Mail *', 'type':'email'}))
	# station = forms.ModelChoiceField(queryset=Station.objects.filter(is_valid=True), required=False)

	class Meta:
		model = Technician
		exclude = ('station','profile','statut','is_valid','trash','password','role','meteorologist','trash_at','theme','is_online','last_connection')

# formulaire inscription
class AddStation(forms.ModelForm):
	name = forms.CharField(widget=forms.TextInput(attrs={'autofocus':'autofocus','class':'form-control','placeholder':'Nom Station *'}))
	latitude = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Latitude *'}))
	longitude = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Longitude *'}))
	class Meta:
		model = Station
		exclude = ('statut','trash_at','map','trash','is_valid', 'meteorologist','activate_at','theme')


# formulaire inscription
class ProgramStationActivation(forms.Form):
	date = forms.DateTimeField(required=True, widget=forms.TextInput(attrs={'type':'date','class':'form-control'}))
	h = forms.IntegerField(label='Heure',widget=forms.TextInput(attrs={'type':'number','class':'form-control', 'placeholder':'12'}), required=False)
	m = forms.IntegerField(label='minute',widget=forms.TextInput(attrs={'type':'number','class':'form-control', 'placeholder':'30'}), required=False)
	s = forms.IntegerField(label='seconde',widget=forms.TextInput(attrs={'type':'number','class':'form-control', 'placeholder':'00'}), required=False)


class SaveRainData(forms.ModelForm):
    value = forms.CharField(widget=forms.TextInput(attrs={'autofocus':'autofocus','class':'form-control','placeholder':'exemple : 1.5  *','type':'text'}))
    # created_at = forms.DateField(widget=forms.TextInput(attrs={'class':'form-control','placeholder':'nom *','type':'date'}), required=False)
    class Meta: 
        model = RainData
        exclude = ('update_at','station','technician','trash','created_at',)


# formulaire administrateur
class MetForm(forms.ModelForm):
	firstname = forms.CharField(label='Prénom', widget=forms.TextInput(attrs={'autofocus':'autofocus','class':'form-control','placeholder':'Prénom *'}))
	lastname = forms.CharField(label='Nom',widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Nom *'}))
	address = forms.CharField(label='Adresse',widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Adresse *'}))
	tel = forms.CharField(label='Téléphone',widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Téléphone *'}))
	email = forms.EmailField(label='Mail',widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Mail *', 'type':'email'}))
	class Meta:
		model = Meteorologist
		exclude = ('is_valid','trash','trash_at', 'role','password','statut','theme','is_online','last_connection')