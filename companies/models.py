from django.db import models
from django.conf import settings

class Company(models.Model):
    """
    Represents an employer or organization posting jobs.
    """
    name = models.CharField(
        max_length=255,
        unique=True,
        help_text="Unique name of the organization"
    )
    description = models.TextField(
        blank=True,
        help_text="Detailed company profile and description"
    )
    website = models.URLField(
        blank=True,
        help_text="Link to the official company homepage"
    )
    location = models.CharField(
        max_length=255,
        blank=True,
        help_text="Headquarters physical address/location"
    )
    logo = models.FileField(
        upload_to='company_logos/',
        blank=True,
        null=True,
        help_text="Upload official company logo image/vector"
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owned_companies',
        help_text="Recruiter who manages this company profile"
    )

    class Meta:
        verbose_name_plural = "Companies"
        ordering = ['name']

    def __str__(self):
        return self.name
