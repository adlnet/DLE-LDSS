from rest_framework import serializers

from .models import CatalogConfigurations, CourseInformationMapping


# config serializers
class CatalogsSerializer(serializers.ModelSerializer):
    """Serializes the Catalogs Model"""
    image = serializers.CharField(source='image_path')

    class Meta:
        model = CatalogConfigurations

        fields = ['name', 'image', ]


class CourseInformationMappingSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseInformationMapping

        fields = ['course_title', 'course_short_description',
                  'course_full_description', 'course_code']
