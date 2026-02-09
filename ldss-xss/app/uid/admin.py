from django.contrib import admin
from .models import ProviderDjangoModel, UIDRequestToken

class ProviderAdmin(admin.ModelAdmin):
    list_display = ('name', )
    search_fields = ('name', )

class UIDRequestAdmin(admin.ModelAdmin):
    list_display = ('provider_name', 'token', 'uid', 'uid_chain')
    search_fields = ('provider_name', 'token', 'uid', 'uid_chain')
    exclude = ('token', 'echelon', 'termset', 'uid', 'uid_chain')

admin.site.register(ProviderDjangoModel, ProviderAdmin)
admin.site.register(UIDRequestToken, UIDRequestAdmin)
