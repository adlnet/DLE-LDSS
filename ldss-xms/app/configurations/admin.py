from django.contrib import admin

from configurations.models import (CatalogConfigurations,
                                   CourseInformationMapping, XMSConfigurations)

# Register your models here.


@admin.register(XMSConfigurations)
class XMSConfigurationsAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "target_xis_host",
        "default_user_group",
    )
    # fields to display in the admin site
    fieldsets = (
        (
            "XIS Configuration",
            {
                # on the same line
                "fields": (
                    "target_xis_host",
                    "xis_api_key",
                )
            },
        ),
        (
            "XMS Configuration",
            {
                "fields": (
                    "default_user_group",
                )
            },
        ),
    )


@admin.register(CatalogConfigurations)
class CatalogsAdmin(admin.ModelAdmin):
    list_display = (
        "name",
    )
    # fields to display in the admin site
    fieldsets = (
        (
            "Catalog Configuration",
            {
                # on the same line
                "fields": (
                    "name",
                    "image",
                )
            },
        ),
        (
            "Members",
            {
                "fields": (
                    "members",
                )
            }
        ),
    )
    filter_horizontal = ("members",)


@admin.register(CourseInformationMapping)
class CourseInformationMappingAdmin(admin.ModelAdmin):
    list_display = (
        "course_title",
        "course_code",
        "course_short_description",
        "course_full_description",
    )
    # fields to display in the admin site
    fieldsets = (
        (
            "Display Fields",
            {
                # on the same line
                "fields": (
                    "course_title",
                    "course_code",
                )
            },
        ),
        (
            "Search Fields",
            {
                "fields": (
                    "course_short_description",
                    "course_full_description",
                )
            },
        ),
    )
