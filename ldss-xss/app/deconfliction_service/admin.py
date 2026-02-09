from django.contrib import admin
from django.urls import path
from django.db import models
from django.shortcuts import redirect
from . import views

class Deconfliction(models.Model):
    class Meta:
        verbose_name_plural = "Deconfliction"
        managed = False

class DeconflictionAdmin(admin.ModelAdmin):
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            # path('', self.admin_site.admin_view(self.redirect_to_deconfliction),
            #      name='deconfliction_service_deconfliction_changelist'),
            path(
                route='', 
                view=self.admin_site.admin_view(views.deconfliction_admin_view), 
                name='admin_deconfliction_view'
            ),
            path(
                route='resolve-collision/<str:definition_1>/<str:definition_2>/<str:entity_id_1>/<str:entity_id_2>/',
                view=self.admin_site.admin_view(views.resolve_collision),
                name='admin_resolve_collision'
            ),
            path(
                route='deconfliction/merge_definitions/<int:keep_id>/<int:remove_id>/',
                view=views.merge_duplicate_definitions,
                name='admin_merge_definitions'
            ),
            path(
                route='upgrade-definition/<str:definition>/<str:entity_id>/', 
                view=views.admin_upgrade_definition, 
                name='admin_upgrade_definition'
            ),
            path(
                route='deprecate/<str:term_uid>/', 
                view=views.deprecate_term_and_definition, 
                name='deprecate_term_and_definition'
            ),
        ]
        return custom_urls + urls

    def redirect_to_deconfliction(self, request):
        """Redirect the default list view to our custom view"""
        return redirect('admin:admin_deconfliction_view')

    def has_add_permission(self, request):
        """Disable add permission since this is just for the custom view"""
        return False

    def has_change_permission(self, request, obj=None):
        """Disable change permission since this is just for the custom view"""
        return False

    def has_delete_permission(self, request, obj=None):
        """Disable delete permission since this is just for the custom view"""
        return False

    def has_view_permission(self, request, obj=None):
        """Enable view permission to allow access to the custom view"""
        return True

admin.site.register(Deconfliction, DeconflictionAdmin)
