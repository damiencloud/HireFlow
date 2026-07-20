from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from companies.models import Company

User = get_user_model()

class CompanyManagementTests(TestCase):
    """
    Test suite for company creation, editing, deletion, permissions, logo upload, and details rendering.
    """

    def setUp(self):
        # Create primary recruiter user
        self.recruiter_1 = User.objects.create_user(
            username='recruiter1',
            email='recruiter1@example.com',
            password='Password123!',
            is_recruiter=True
        )

        # Create secondary recruiter user (for permission check tests)
        self.recruiter_2 = User.objects.create_user(
            username='recruiter2',
            email='recruiter2@example.com',
            password='Password123!',
            is_recruiter=True
        )

        # Create candidate user
        self.candidate = User.objects.create_user(
            username='candidate1',
            email='candidate1@example.com',
            password='Password123!',
            is_candidate=True
        )

        # Pre-create a company owned by recruiter_1
        self.company = Company.objects.create(
            name='Stripe Inc.',
            description='Financial infrastructure for the internet.',
            website='https://stripe.com',
            location='San Francisco, CA',
            owner=self.recruiter_1
        )

    def test_companies_directory_list_and_search(self):
        """
        Verify public companies directory renders and filters by name query.
        """
        response = self.client.get(reverse('companies'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Stripe Inc.')

        # Search for non-existent company
        response_search = self.client.get(reverse('companies') + '?q=NonExistent')
        self.assertEqual(response_search.status_code, 200)
        self.assertNotContains(response_search, 'Stripe Inc.')

    def test_company_details_view(self):
        """
        Verify public company details page renders profile and overview.
        """
        response = self.client.get(reverse('company_details', args=[self.company.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Stripe Inc.')
        self.assertContains(response, 'San Francisco, CA')

    def test_recruiter_create_company_with_logo(self):
        """
        Verify recruiters can register a company profile with logo file upload.
        """
        self.client.force_login(self.recruiter_2)
        
        # Create a small dummy image file
        dummy_image = SimpleUploadedFile(
            name='company_logo.png',
            content=b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89',
            content_type='image/png'
        )

        response = self.client.post(reverse('create_company'), {
            'name': 'Google LLC',
            'description': 'Organize the world information.',
            'website': 'https://google.com',
            'location': 'Mountain View, CA',
            'logo': dummy_image
        })

        self.assertRedirects(response, reverse('dashboard'))
        self.assertTrue(Company.objects.filter(name='Google LLC').exists())
        created_company = Company.objects.get(name='Google LLC')
        self.assertEqual(created_company.owner, self.recruiter_2)
        self.assertTrue(bool(created_company.logo))

    def test_recruiter_edit_own_company(self):
        """
        Verify company owner can update company details.
        """
        self.client.force_login(self.recruiter_1)
        response = self.client.post(reverse('edit_company', args=[self.company.id]), {
            'name': 'Stripe Corporation',
            'description': 'Updated description.',
            'website': 'https://stripe.com',
            'location': 'New York, NY',
        })
        self.assertRedirects(response, reverse('dashboard'))
        self.company.refresh_from_db()
        self.assertEqual(self.company.name, 'Stripe Corporation')
        self.assertEqual(self.company.location, 'New York, NY')

    def test_candidate_cannot_create_company(self):
        """
        Verify candidates are blocked from creating company profiles.
        """
        self.client.force_login(self.candidate)
        response = self.client.post(reverse('create_company'), {
            'name': 'Candidate Firm',
            'description': 'Test',
        })
        self.assertRedirects(response, reverse('dashboard'))
        self.assertFalse(Company.objects.filter(name='Candidate Firm').exists())

    def test_unauthorized_recruiter_cannot_edit_other_company(self):
        """
        Verify recruiter cannot edit a company owned by another recruiter.
        """
        self.client.force_login(self.recruiter_2)
        response = self.client.post(reverse('edit_company', args=[self.company.id]), {
            'name': 'Hacked Stripe Name',
            'description': 'Unauthorized modification',
        })
        self.assertRedirects(response, reverse('dashboard'))
        self.company.refresh_from_db()
        self.assertEqual(self.company.name, 'Stripe Inc.')

    def test_recruiter_delete_own_company(self):
        """
        Verify company owner can delete their company profile.
        """
        self.client.force_login(self.recruiter_1)
        response = self.client.post(reverse('delete_company', args=[self.company.id]))
        self.assertRedirects(response, reverse('dashboard'))
        self.assertFalse(Company.objects.filter(id=self.company.id).exists())
