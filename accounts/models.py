from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

class CustomUser(AbstractUser):
    """
    Custom user model to handle authentication and role flags.
    is_candidate: User is a job seeker.
    is_recruiter: User is an employer/recruiter.
    """
    is_candidate = models.BooleanField(default=False)
    is_recruiter = models.BooleanField(default=False)

    def __str__(self):
        return self.username

class CandidateProfile(models.Model):
    """
    Stores professional details for candidate user accounts.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='candidate_profile'
    )
    bio = models.TextField(blank=True, help_text="Tell recruiters about yourself")
    skills = models.CharField(
        max_length=500,
        blank=True,
        help_text="Comma-separated list of key professional skills"
    )

    def __str__(self):
        return f"{self.user.username}'s Candidate Profile"

class RecruiterProfile(models.Model):
    """
    Stores professional details for recruiter/employer accounts.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='recruiter_profile'
    )
    company_name = models.CharField(
        max_length=255,
        blank=True,
        help_text="Affiliated organization name"
    )
    bio = models.TextField(blank=True, help_text="Brief professional bio")

    def __str__(self):
        return f"{self.user.username}'s Recruiter Profile"
