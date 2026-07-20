from django.db import models

class ContactMessage(models.Model):
    """
    Represents a contact or support inquiry submitted by a site visitor.
    """
    name = models.CharField(
        max_length=255, 
        help_text="Full Name of the sender"
    )
    email = models.EmailField(
        help_text="Email address of the sender"
    )
    subject = models.CharField(
        max_length=255, 
        help_text="Subject line of the inquiry"
    )
    message = models.TextField(
        help_text="Inquiry content and message body"
    )
    submitted_date = models.DateTimeField(
        auto_now_add=True, 
        help_text="Timestamp when the message was submitted"
    )
    is_read = models.BooleanField(
        default=False, 
        help_text="Tracks whether this message has been read by administrators"
    )

    class Meta:
        ordering = ['-submitted_date']

    def __str__(self):
        return f"Message from {self.name} - {self.subject}"
