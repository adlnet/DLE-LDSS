from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import CourseInformationMapping
from .serializers import CatalogsSerializer, CourseInformationMappingSerializer


class CatalogConfigurationView(APIView):
    """Catalog Configuration View"""

    def get(self, request):
        """Returns the XDSUI configuration fields from the model"""
        catalogs = request.user.catalogs.exclude(image='')
        serializer = CatalogsSerializer(catalogs, many=True)

        return Response(serializer.data, status.HTTP_200_OK)


class CourseInformationMappingView(APIView):
    """Course Information Mapping View"""

    def get(self, request):
        """Returns the CourseInformationMapping fields from the model"""
        mapping = CourseInformationMapping.objects.all().first()
        serializer = CourseInformationMappingSerializer(mapping)

        return Response(serializer.data, status.HTTP_200_OK)
