from django.contrib import admin
from .models import *
from import_export.admin import ImportExportModelAdmin
# Register your models here.
admin.site.register(Technician)
admin.site.register(RainData)
admin.site.register(Meteorologist)
admin.site.register(Administrator)
admin.site.register(Region)
admin.site.register(Department)
admin.site.register(Station)
admin.site.register(Comments)