from import_export import resources
from connection.models import RainData


class RainResource(resources.ModelResource):
    class Meta:
        model = RainData
        # exclude = ('update_at','station','technician','trash',)