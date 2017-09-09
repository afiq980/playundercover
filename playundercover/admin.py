from django.contrib import admin
from django.forms import models
from models import Pair, CustomUser, UserPair
from import_export import resources
from import_export.admin import ImportExportMixin, ImportMixin, ImportExportActionModelAdmin


class CustomUserAdmin(admin.ModelAdmin):
    pass

class UserPairAdmin(admin.ModelAdmin):
    pass

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(UserPair, UserPairAdmin)


class PairResource(resources.ModelResource):
    class Meta:
        model = Pair


class PairAdmin(ImportExportActionModelAdmin):
    pass

admin.site.register(Pair, PairAdmin)