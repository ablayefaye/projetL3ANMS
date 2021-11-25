from django.db import models
from django.db import connection
from datetime import datetime
import random
import string
# role : the role that the user have
ROLE = (("admin","admin"),("technicien","technicien"),("meteorologue","meteorologue"))


# mot de passe par défaut
def getPassword(length):
    """Générer une chaîne aléatoire de longueur fixe"""
    str = string.ascii_lowercase
    return ''.join(random.choice(str) for i in range(length))
 

# class User: the main class
class Person(models.Model):
    firstname = models.CharField(max_length=255)
    lastname = models.CharField(max_length=255)
    address = models.TextField()
    tel = models.CharField(max_length=255)
    email = models.EmailField(max_length=254, unique=True, null=False)
    password = models.CharField(max_length=50, blank=True, default=getPassword(8))
    role = models.CharField(max_length=50, choices=ROLE,default="technicien", null=False)
    theme = models.CharField(max_length=50, default="secondary", null=True, blank=True)
    profile = models.ImageField(upload_to='images/', null=True, blank=True)
    last_connection = models.DateTimeField(null=True, blank=True)
    is_online = models.BooleanField(default=False, null=True, blank=True)
    class Meta:
        abstract = True
        

    def __str__(self):
        return "{} {}, {}".format(self.firstname,self.lastname,self.email)

class Administrator(Person):
    pass
  

class Region(models.Model):
    name = models.CharField(max_length=255,unique=True)
    created_at = models.DateField(auto_now_add=True)
    update_at = models.DateField(auto_now=True)
    admin = models.ForeignKey(Administrator, on_delete=models.CASCADE)
    trash = models.BooleanField(default=False)
    trash_at = models.DateField(null=True, blank=True)
    def __str__(self):
        return self.name
    


class Department(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateField(auto_now_add=True)
    update_at = models.DateField(auto_now=True)
    trash = models.BooleanField(default=False)
    trash_at = models.DateField(null=True, blank=True)
    region = models.ForeignKey(Region, on_delete=models.CASCADE, blank=True)
    def __str__(self):
        return self.name 

class Meteorologist(Person):
    statut = models.BooleanField(default=True)
    trash = models.BooleanField(default=False)
    trash_at = models.DateField(null=True , blank=True)


class Station(models.Model):
    name = models.CharField(max_length=50)
    latitude =models.FloatField()
    longitude = models.FloatField()
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    trash_at = models.DateField(null=True,  blank=True)
    activate_at = models.DateTimeField(null=True,  blank=True)
    trash = models.BooleanField(default=False)
    meteorologist = models.ForeignKey(Meteorologist, on_delete=models.SET_NULL, null=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    statut = models.BooleanField(default=True)
    map = models.TextField(null=True, blank=True)
    is_valid = models.BooleanField(default=True)
    def __str__(self):
        return self.name

    def my_stations_sql(id):
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM pluie_technician t, pluie_station s where t.station_id=s.id and  t.id = "+ str(id))
            row = cursor.fetchall()

        return row


class Technician(Person):
    statut = models.BooleanField(default=True)
    trash = models.BooleanField(default=False)
    trash_at = models.DateField(null=True, blank=True)
    station = models.ForeignKey(Station,  models.SET_NULL, blank=True, null=True)
    meteorologist = models.ForeignKey(Meteorologist, on_delete=models.CASCADE)
    is_valid = models.BooleanField(default=True, blank=False)


class RainData(models.Model):

    value = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    created_at = models.DateField(default=datetime.now())
    update_at = models.DateField(auto_now=True)
    station = models.ForeignKey(Station, on_delete=models.CASCADE)
    technician = models.ForeignKey(Technician,on_delete=models.CASCADE)
    trash = models.BooleanField(default=False)
    trash_at = models.DateField(null=True , blank=True)
    def __str__(self):
        return str(self.value)+" mm "+str(self.created_at)
    

class Comments(models.Model):
    station = models.ForeignKey(Station, on_delete=models.CASCADE)
    technician = models.ForeignKey(Technician, on_delete=models.CASCADE)
    date_note = models.DateField(auto_now_add=True)
    content = models.TextField()
    trash = models.BooleanField(default=False)
    trash_at = models.DateField(null=True, blank=True)
