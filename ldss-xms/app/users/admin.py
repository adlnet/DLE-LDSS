from django.contrib import admin

from configurations.models import CatalogConfigurations

from .models import UserProfile

# Register your models here.


class CatalogInline(admin.TabularInline):
    model = CatalogConfigurations.members.through
    verbose_name = 'Catalog'
    verbose_name_plural = 'Catalogs'


@admin.register(UserProfile)
class UserAdmin(admin.ModelAdmin):
    """
    Admin View for User
    """
    inlines = [
        CatalogInline,
    ]
    # things shown in the row
    list_display = ('email', 'first_name', 'is_active', 'is_staff')
    # things that can be filtered
    list_filter = ('is_active', 'is_staff', 'is_superuser')
    # things that can be searched
    search_fields = ('email', 'first_name', 'last_name')

    # things that can be edited
    fieldsets = (
        ('Account Info', {'fields': ('email',)}),
        ('Personal Info', {'fields': ('first_name', 'last_name',)}),
        ('Permissions', {'fields': ('is_active', 'is_staff',
                                    'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name',
                       'password1', 'password2', 'is_active', 'is_staff',
                       'groups', )
        }),)

    filter_horizontal = ('groups', 'user_permissions', )
    change_user_password_template = None
