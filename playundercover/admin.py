from django.contrib import admin
from django.forms import models
from models import Pair
from import_export import resources
from import_export.admin import ImportExportMixin, ImportMixin, ImportExportActionModelAdmin

# class PairAdmin(admin.ModelAdmin):
#     pass
#
# admin.site.register(Pair, PairAdmin)

class PairResource(resources.ModelResource):
    class Meta:
        model = Pair


class PairAdmin(ImportExportActionModelAdmin):
    pass

admin.site.register(Pair, PairAdmin)