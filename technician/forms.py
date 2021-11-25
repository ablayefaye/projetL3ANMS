from django import forms
from connection.models import *




# formulaire administrateur
class addCommentForm(forms.Form):
	content = forms.CharField(label='', widget=forms.Textarea(attrs={ 'autofocus':'autofocus','class':'form-control','placeholder':'Votre commentaire ici *'}), required=True)
	

class TechForm(forms.ModelForm):
	firstname = forms.CharField(label='Prénom', widget=forms.TextInput(attrs={'autofocus':'autofocus','class':'form-control','placeholder':'Prénom *'}))
	lastname = forms.CharField(label='Nom',widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Nom *'}))
	address = forms.CharField(label='Adresse',widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Adresse *'}))
	tel = forms.CharField(label='Téléphone',widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Téléphone *'}))
	email = forms.EmailField(label='Mail',widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Mail *', 'type':'email'}))
	profile = forms.ImageField(required=False)
	
	class Meta:
		model = Technician
		exclude = ('station','is_valid','trash','trash_at', 'role','password','statut','theme', 'meteorologist','is_online','last_connection')