from django.test import TestCase
from django.urls import reverse
from contact.models import ContactMessage

class ContactSystemTests(TestCase):
    """
    Test suite for support inquiry form submissions, validation, message storage, and user feedback.
    """

    def test_contact_page_render(self):
        """
        Verify contact us page loads with HTTP 200 OK.
        """
        response = self.client.get(reverse('contact'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Get in Touch')

    def test_contact_form_valid_submission(self):
        """
        Verify valid form submission saves ContactMessage to database and shows success notification.
        """
        response = self.client.post(reverse('contact'), {
            'name': 'Jane Doe',
            'email': 'janedoe@example.com',
            'subject': 'General Inquiry',
            'message': 'Hello, I have a question regarding job postings on HireFlow.',
        })
        self.assertRedirects(response, reverse('contact'))
        self.assertTrue(ContactMessage.objects.filter(email='janedoe@example.com').exists())
        saved_msg = ContactMessage.objects.get(email='janedoe@example.com')
        self.assertEqual(saved_msg.subject, 'General Inquiry')
        self.assertFalse(saved_msg.is_read)

    def test_contact_form_invalid_submission(self):
        """
        Verify submitting empty or invalid data displays form error feedback.
        """
        response = self.client.post(reverse('contact'), {
            'name': 'Jane Doe',
            'email': 'invalid-email-format',
            'subject': '',
            'message': '',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(ContactMessage.objects.filter(name='Jane Doe').exists())
        self.assertContains(response, 'Failed to submit message')
