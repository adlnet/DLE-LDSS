from api import views
from django.urls import path
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

app_name = 'api'

urlpatterns = [
     path('data-ingest/', views.DataIngest.as_view(), name='data-ingest'),

     path('instances', views.api_get_instances, name="instances"),
     path("mapped-terms", views.api_mapped_nodes, name="mapped-terms"),
     path('neo4j-health-check/', views.check_neo4j_status,name='neo4j-health-check'),
     path('upload-csv/', views.upload_csv, name='upload-csv'),
     path('create-local-mappings/', views.create_local_mappings, name='create-local-mappings'),

     path("catalog/all/", views.api_get_catalog, name="catalog-all"),
     path("catalog/entry/", views.api_get_catalog_entry, name="catalog-entry")
]
