from django.contrib import admin, messages
from django.shortcuts import render

from django import forms
from django.db import models
from django.urls import path, reverse
from core.ccvmodels import LCVDownstream, CCVUpstream
from django_neomodel import admin as neomodel_admin
from core.models import NeoAlias, NeoContext, NeoDefinition, NeoTerm
from core.utils import run_node_creation, validate_csv_file, create_terms_from_csv
import logging
import json

from .views import export_terms_as_json, export_terms_as_csv, search
from api.views import upload_csv

import pandas as pd
import requests

logger = logging.getLogger('dict_config_logger')

HTML_UPLOAD_CSV = "upload_csv.html"

class NeoTermAdminForm(forms.ModelForm):
    alias = forms.CharField(required=False, help_text="Enter alias")
    definition = forms.CharField(required=True, help_text="Enter definition")
    context = forms.CharField(required=False, help_text="Enter context")
    context_description = forms.CharField(required=False, help_text="Enter context description")
    entity_id = forms.CharField(required=True, help_text="Enter entity ID aka Provider name")

    class Meta:
        model = NeoTerm
        fields = ['lcvid', 'alias', 'definition', 'context', 'context_description', 'entity_id']

class NeoTermAdmin(admin.ModelAdmin):
    form = NeoTermAdminForm
    list_display = ('uid_chain', 'uid', 'status')
    actions = ['publish_to_ccv', 'publish_to_lcvs']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model.verbose_name = 'NeoTerm'
        self.model.verbose_name_plural = 'NeoTerms'

    def save_model(self, request, obj, form, change):
        try:
            alias = form.cleaned_data['alias']
            definition = form.cleaned_data['definition']
            context = form.cleaned_data['context']
            context_description = form.cleaned_data['context_description']
            entity_id = form.cleaned_data['entity_id']

            if context == '' and context_description == '' and alias != '':
                definition_node = NeoDefinition.nodes.get_or_none(definition=definition)
                if definition_node:
                    messages.warning(request, 'Adding an alias without a context is not recommended.')
                    run_node_creation(alias=alias, definition=definition, context=context, context_description=context_description, entity_id=entity_id)
                    return
                messages.error(request, 'Adding a definition without a context is not allowed.')
                return
            run_node_creation(alias=alias, definition=definition, context=context, context_description=context_description, entity_id=entity_id)

            messages.success(request, 'NeoTerm saved successfully.')

        except Exception as e:
            logger.error('Error saving NeoTerm: %s', e)
            messages.error(request, 'Error saving NeoTerm: {}'.format(e))
            return

    def delete_model(self, request, obj) -> None:
        messages.error(request, 'Deleting terms is not allowed')

    def delete_queryset(self, request, queryset):
        """Prevent bulk deletion of NeoTerm objects and show a message."""
        messages.error(request, "You cannot delete terms.")

    change_list_template = 'admin/neoterm_change_list.html'

    REQUIRED_COLUMNS = ['Definition', 'Context', 'Context Description']

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('upload-csv-form/', self.admin_site.admin_view(self.upload_csv_form), name="upload_csv"),
            path('export-terms-json/', export_terms_as_json, name='export_terms_as_json'),
            path('export-terms-csv/', export_terms_as_csv, name='export_terms_as_csv')
        ]
        return my_urls + urls
    
    def publish_to_lcvs(self, request, queryset):
        try:
            logger.info("Publishing terms to LCVs...")
            connections = self.get_lcv_connections(request)
            logger.info("LCV connections: %s", connections)
            if not connections:
                messages.error(request, 'Connection to LCV failed. Please check your LCV Downstream configuration.')
                return
            matched_terms = 0
            terms_data = []

            for term in queryset:
                neoterm_node = NeoTerm.get_by_uid(term.uid)
                if not neoterm_node:
                    messages.error(request, f'Term {term.uid} not found in Neo4j')
                    continue
                
                aliases = [alias.alias for alias in neoterm_node.alias.all()]
                neoterm_node = neoterm_node.to_json()

                terms_data.append({**neoterm_node, "aliases": aliases})

            if not terms_data:
                messages.error(request, 'No valid terms found to publish')
                return

            logger.info(terms_data)
            for connection in connections:
                try:
                    logger.info("Publishing terms to LCV: %s", connection)
                    response = requests.post(f"{connection}/api/data-ingest/", json=terms_data, headers={'Content-Type': 'application/json'}, timeout=10)
                    logger.info(response.status_code)
                    response.raise_for_status()

                    logger.info(response.json())
                    if response.status_code == 200:
                        matched_terms += len(terms_data)
                        messages.success(request, f'{len(terms_data)} terms published to LCVs.')

                except requests.RequestException as e:
                    logger.error("Failed to publish terms to LCV: %s", e)
                    messages.error(request, f"Error publishing to {connection}: {str(e)}")
                    return

            messages.success(request, f'{matched_terms} terms published to LCVs.')

        except Exception as e:
            messages.error(request, f'Error publishing terms to LCVs: {str(e)}')
            logger.error('Error publishing terms to LCV: %s', str(e))

    def get_lcv_connections(self, request):
        try:
            return LCVDownstream.get_endpoints()
        except Exception as e:
            logger.error("Failed to get LCV connections: %s", e)
            messages.error(request, f"Failed to get LCV connections: {str(e)}")
            return []

    def publish_to_ccv(self, request, queryset):
        try:
            logger.info("Publishing terms to CCV...")
            connection = self.get_ccv_connection()
            if not connection:
                messages.error(request, 'Connection to CCV failed. Please check your CCV Upstream configuration.')
                return
            
            terms_data = []

            for term in queryset:
                if term.status == 'accepted':
                    messages.error(request, f"Term {term.uid} is already published.")
                    continue

                neoterm_node = NeoTerm.get_by_uid(term.uid)
                if not neoterm_node:
                    messages.error(request, f"Term {term.uid} not found in Neo4j.")
                    continue

                aliases = [alias.alias for alias in neoterm_node.alias.all()]
                node_json = neoterm_node.to_json()

                terms_data.append({**node_json, "aliases": aliases})

            if not terms_data:
                messages.error(request, 'No valid terms found to publish to CCV.')
                return

            response = requests.post(
                f"{connection}/api/data-ingest/",
                json=terms_data,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            response.raise_for_status()

            if response.status_code == 200:
                for term_dict in terms_data:
                    term_obj = queryset.filter(uid=term_dict["uid"]).first()
                    if term_obj:
                        term_obj.status = 'accepted'
                        term_obj.save()

                messages.success(request, f'{len(terms_data)} terms published to CCV.')

        except requests.RequestException as e:
            logger.error("Failed to publish terms to CCV: %s", e)
            messages.error(request, f"Failed to publish terms to CCV. Error: {str(e)}")
        
        except Exception as e:
            messages.success(request, 'Successfully published terms to CCV')
            logger.error('Error publishing terms to CCV: %s', str(e))

    def get_ccv_connection(self):
        return CCVUpstream.get_endpoint()
    
    def upload_csv_form(self, request):

        form_title = 'Upload CSV File'

        if request.method == "POST":

            response = upload_csv(request)

            try:
                payload = json.loads(response.content)
            except (ValueError, TypeError):
                payload = {}

            if response.status_code == 200:
                form = CSVUploadForm()
                context = {
                    'form': form,
                    'opts': self.opts,
                    'title': form_title,
                    'success_message': payload.get('message', 'CSV file processed successfully.'),
                    'csrf_token': request.META.get('CSRF_COOKIE', ''),
                }
                return render(request, HTML_UPLOAD_CSV, context, status=200)
            else:
                form = CSVUploadForm()
                context = {
                    'form': form,
                    'opts': self.opts,
                    'title': form_title,
                    'error_message': payload.get('error', 'An unexpected error occurred.'),
                    'csrf_token': request.META.get('CSRF_COOKIE', ''),
                }
                return render(request, HTML_UPLOAD_CSV, context, status=response.status_code)
            
        form = CSVUploadForm()
        
        context = {
            'form': form,
            'opts': self.opts,
            'title': form_title,
            'csrf_token': request.META.get('CSRF_COOKIE', ''),
        }
        logger.info('Rendering upload CSV form with context: %s', context)
        return render(request, HTML_UPLOAD_CSV, context)
    

neomodel_admin.register(NeoTerm, NeoTermAdmin)
class CSVUploadForm(forms.Form):
    csv_file = forms.FileField()
    entity_id = forms.CharField(required=True, help_text="Enter entity ID aka Provider name")
class NeoAliasAdmin(admin.ModelAdmin):
    list_display = ('alias', 'term')

neomodel_admin.register(NeoAlias, NeoAliasAdmin)

class NeoContextAdmin(admin.ModelAdmin):
    list_display = ('context', 'context_description')
    readonly_fields = ('context', 'context_description')

neomodel_admin.register(NeoContext, NeoContextAdmin)

class NeoDefinitionAdmin(admin.ModelAdmin):
    list_display = ('definition',)
    readonly_fields = ('definition',)

neomodel_admin.register(NeoDefinition, NeoDefinitionAdmin)

class Search(models.Model):
    class Meta:
        verbose_name_plural = "Search"
        managed = False
class SearchAdmin(admin.ModelAdmin):

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('', self.admin_site.admin_view(search), name='search_view'),
        ]
        return custom_urls + urls

    def has_view_permission(self, request, obj=None):
        return True

admin.site.register(Search, SearchAdmin)

@admin.register(CCVUpstream)
class CCVUpstreamAdmin(admin.ModelAdmin):
    list_display = ('ccv_api_endpoint', 'ccv_api_endpoint_status', 'ccv_api_username')
    fields = [('ccv_api_endpoint', 'ccv_api_endpoint_status', 'ccv_api_username', 'ccv_api_password', 'ccv_api_key'), ]
    filter_horizontal = ['metadata_experiences', 'supplemental_experiences']

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        messages.success(request, "API endpoint and credentials have been successfully configured.")

@admin.register(LCVDownstream)
class LCVDownstreamAdmin(admin.ModelAdmin):
    list_display = ('lcv_api_endpoint', 'lcv_api_endpoint_status')
    fields = [('lcv_api_endpoint', 'lcv_api_key', 'lcv_api_endpoint_status')]

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        messages.success(request, "API endpoint and credentials have been successfully configured.")
