from django.conf import settings
from django.contrib.auth.models import Group
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.forms import ValidationError
from django.urls import reverse
from model_utils.models import TimeStampedModel

from users.models import UserProfile

# Create your models here.


class XMSConfigurations(models.Model):
    """Model for XMS Configuration"""

    class Meta:
        # change the name shown
        verbose_name = "XMS Connection"

    # the following fields are required for XMS to connect to XIS

    target_xis_host = models.CharField(
        help_text="Enter the XIS host to query data",
        max_length=200,
    )
    default_user_group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        help_text='Select the group to assign new users to',
        blank=True,
        null=True
    )
    xis_api_key = models.CharField(
        help_text="Enter the XIS API Key",
        max_length=40
    )

    def get_absolute_url(self):
        """
        URL for displaying individual model records.
        """
        return reverse("xms-configuration", args=[str(self.id)])

    def __str__(self) -> str:
        """
        String for representing the Model object.
        """
        return f"{self.id}"

    def save(self, *args, **kwargs):
        """
        Override the save method to check if the XMSConfigurations already
        exists. Notifies the user if the model already exists.
        """
        if not self.pk and XMSConfigurations.objects.exists():
            raise ValidationError("XMSConfigurations model already exists")
        return super(XMSConfigurations, self).save(*args, **kwargs)


@receiver(post_save, sender=UserProfile)
def add_default_group(sender, instance, created, **kwargs):
    """
    Adds new users to a default group specified in XMSConfigurations
    Note: not applied to users created through admin panel, as they manually
    select groups for the new user
    """
    # if new and default_user_group from XMSConfigurations is defined
    if created and len(XMSConfigurations.objects.all()) > 0 and \
            XMSConfigurations.objects.first().default_user_group is not None:
        base_permission_group = XMSConfigurations.objects.first() \
            .default_user_group
        # add the new user to that group
        instance.groups.add(base_permission_group)
        instance.save()


class CatalogConfigurations(models.Model):
    """Model for Catalogs Configuration"""

    class Meta:
        # change the name shown
        verbose_name = "Catalog"

    name = models.CharField(
        unique=True, help_text="Enter the name of the catalog", max_length=255)
    image = models.ImageField(upload_to='images/', blank=True)
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL, 'catalogs', blank=True)

    def image_path(self):
        """Path to image without leading slash"""
        if not self.image:
            return None
        return str(self.image.url)[1:]

    def __str__(self):
        """String for representing the Model object."""
        return f'{self.name}'


class CourseInformationMapping(TimeStampedModel):
    """ Model to map course information"""

    course_title = models.CharField(max_length=200,
                                    default="metadata.Course.CourseTitle",
                                    help_text="Enter the mapping for the "
                                              "title of the course found in "
                                              "XIS")

    course_short_description = models.CharField(max_length=200,
                                                default="metadata.Course."
                                                "CourseShortDescription",
                                                help_text="Enter the mapping "
                                                "for the"
                                                " short description of"
                                                " the course found in XIS")

    course_full_description = models.CharField(max_length=200,
                                               default="metadata.Course."
                                               "CourseFullDescription",
                                               help_text="Enter the mapping "
                                               "for the"
                                               " full description of"
                                               " the course found in XIS")

    course_code = models.CharField(max_length=200,
                                   default="metadata.Course.CourseCode",
                                   help_text="Enter the mapping for the "
                                             "code of the course "
                                             "found in XIS")

    def get_absolute_url(self):
        """ URL for displaying individual model records."""
        return reverse('configurations:course-information')

    def __str__(self):
        """String for representing the Model object."""
        return f'{self.id}'

    def list_fields(self):
        """list of fields to use"""
        return [
            self.course_title, self.course_code,
            self.course_short_description,
            self.course_full_description
        ]

    def save(self, *args, **kwargs):
        num_active_mappings = CourseInformationMapping.objects.filter().count()

        # if there is more than one
        if num_active_mappings > 1:
            raise ValidationError(
                'Max of 1 Information Mapping has been reached.')

        return super(CourseInformationMapping, self).save(*args, **kwargs)
