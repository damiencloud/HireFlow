from django.db import models
from django.conf import settings
from companies.models import Company

class Job(models.Model):
    """
    Represents an employment opening posted by a company.
    """
    CATEGORY_CHOICES = [
        ('development', 'Development'),
        ('design', 'Design & UX'),
        ('marketing', 'Marketing'),
        ('management', 'Management'),
    ]

    JOB_TYPE_CHOICES = [
        ('full_time', 'Full-Time'),
        ('part_time', 'Part-Time'),
        ('contract', 'Contract'),
        ('internship', 'Internship'),
        ('remote', 'Remote'),
    ]

    EXPERIENCE_CHOICES = [
        ('entry', 'Entry Level'),
        ('mid', 'Mid Level'),
        ('senior', 'Senior Level'),
        ('lead', 'Lead / Executive'),
    ]

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='jobs',
        help_text="Company listing this employment opportunity"
    )
    title = models.CharField(
        max_length=255,
        help_text="Official title of the job opening"
    )
    description = models.TextField(
        help_text="Detailed description of responsibilities and requirements"
    )
    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        default='development',
        help_text="Primary industry/sector classification"
    )
    location = models.CharField(
        max_length=255,
        help_text="Physical location (e.g., 'San Francisco, CA' or 'Remote')"
    )
    salary = models.CharField(
        max_length=100,
        blank=True,
        help_text="Optional salary display range (e.g. '$120k - $150k')"
    )
    job_type = models.CharField(
        max_length=50,
        choices=JOB_TYPE_CHOICES,
        default='full_time',
        help_text="Work arrangement standard"
    )
    experience_level = models.CharField(
        max_length=50,
        choices=EXPERIENCE_CHOICES,
        default='mid',
        help_text="Target professional seniority level"
    )
    posted_date = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the job listing was created"
    )
    deadline = models.DateField(
        blank=True,
        null=True,
        help_text="Optional application closing date"
    )

    class Meta:
        ordering = ['-posted_date']

    def __str__(self):
        return f"{self.title} at {self.company.name}"

class JobApplication(models.Model):
    """
    Records a candidate's submission to an active job opening.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('reviewing', 'Under Review'),
        ('interview', 'Interviewing'),
        ('offered', 'Offered'),
        ('rejected', 'Rejected'),
    ]

    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name='applications',
        help_text="The position being applied to"
    )
    applicant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='applications',
        help_text="The candidate submitting this application"
    )
    resume = models.FileField(
        upload_to='resumes/',
        help_text="Upload applicant resume file (PDF or Doc)"
    )
    cover_letter = models.TextField(
        blank=True,
        help_text="Optional message to the hiring manager"
    )
    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default='pending',
        help_text="Current selection stage status"
    )
    applied_date = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when application was submitted"
    )

    class Meta:
        ordering = ['-applied_date']
        # Prevent candidate from submitting duplicate applications for the same job listing
        unique_together = ('job', 'applicant')

    def __str__(self):
        return f"{self.applicant.username} - {self.job.title}"

class SavedJob(models.Model):
    """
    Represents a job vacancy bookmarked/saved by a candidate.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='saved_jobs',
        help_text="Candidate bookmarking this listing"
    )
    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name='saved_by_users',
        help_text="The bookmarked job vacancy"
    )
    saved_date = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the candidate saved this listing"
    )

    class Meta:
        ordering = ['-saved_date']
        unique_together = ('user', 'job')

    def __str__(self):
        return f"{self.user.username} saved {self.job.title}"
