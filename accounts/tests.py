from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from accounts.models import CandidateProfile, RecruiterProfile

User = get_user_model()

class AuthenticationTests(TestCase):
    """
    Test suite for user registration, authentication, login variants, and session management.
    """

    def setUp(self):
        # Create a sample candidate user
        self.candidate_user = User.objects.create_user(
            username='candidate_test',
            email='candidate@example.com',
            password='Password123!',
            first_name='Candidate',
            last_name='User',
            is_candidate=True
        )
        CandidateProfile.objects.get_or_create(user=self.candidate_user)

        # Create a sample recruiter user
        self.recruiter_user = User.objects.create_user(
            username='recruiter_test',
            email='recruiter@example.com',
            password='Password123!',
            first_name='Recruiter',
            last_name='User',
            is_recruiter=True
        )
        RecruiterProfile.objects.get_or_create(user=self.recruiter_user)

    def test_candidate_registration(self):
        """
        Verify candidate registration creates user account and candidate profile.
        """
        response = self.client.post(reverse('register'), {
            'full_name': 'New Candidate',
            'email': 'newcandidate@example.com',
            'role': 'candidate',
            'password': 'Password123!',
            'confirm_password': 'Password123!',
        })
        self.assertRedirects(response, reverse('dashboard'))
        self.assertTrue(User.objects.filter(email='newcandidate@example.com').exists())
        user = User.objects.get(email='newcandidate@example.com')
        self.assertTrue(user.is_candidate)
        self.assertTrue(CandidateProfile.objects.filter(user=user).exists())

    def test_recruiter_registration(self):
        """
        Verify recruiter registration creates user account and recruiter profile.
        """
        response = self.client.post(reverse('register'), {
            'full_name': 'New Recruiter',
            'email': 'newrecruiter@example.com',
            'role': 'recruiter',
            'password': 'Password123!',
            'confirm_password': 'Password123!',
        })
        self.assertRedirects(response, reverse('dashboard'))
        self.assertTrue(User.objects.filter(email='newrecruiter@example.com').exists())
        user = User.objects.get(email='newrecruiter@example.com')
        self.assertTrue(user.is_recruiter)
        self.assertTrue(RecruiterProfile.objects.filter(user=user).exists())

    def test_login_success(self):
        """
        Verify successful login using email address via custom EmailBackend.
        """
        response = self.client.post(reverse('login'), {
            'username': 'candidate@example.com',
            'password': 'Password123!',
        })
        self.assertRedirects(response, reverse('dashboard'))
        self.assertEqual(int(self.client.session['_auth_user_id']), self.candidate_user.pk)

    def test_invalid_login_credentials(self):
        """
        Verify login failure with wrong password.
        """
        response = self.client.post(reverse('login'), {
            'username': 'candidate@example.com',
            'password': 'WrongPassword!',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid email or password.")

    def test_logout(self):
        """
        Verify user logout terminates active session.
        """
        self.client.force_login(self.candidate_user)
        response = self.client.get(reverse('logout'))
        self.assertRedirects(response, reverse('index'))
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_dashboard_unauthenticated_redirect(self):
        """
        Verify unauthenticated requests to dashboard redirect to login page.
        """
        response = self.client.get(reverse('dashboard'))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('dashboard')}")

    def test_edit_profile_view_get_and_post(self):
        """
        Verify logged-in candidate can view and update their profile details.
        """
        self.client.force_login(self.candidate_user)
        response = self.client.get(reverse('edit_profile'))
        self.assertEqual(response.status_code, 200)

        post_data = {
            'full_name': 'Candidate Updated',
            'bio': 'Updated professional bio text.',
            'phone_number': '+1234567890',
            'location': 'New York, NY',
            'skills': 'Python, Django, React',
        }
        response = self.client.post(reverse('edit_profile'), post_data)
        self.assertRedirects(response, reverse('dashboard'))
        
        self.candidate_user.refresh_from_db()
        self.assertEqual(self.candidate_user.first_name, 'Candidate')
        self.assertEqual(self.candidate_user.last_name, 'Updated')
        profile = CandidateProfile.objects.get(user=self.candidate_user)
        self.assertEqual(profile.phone_number, '+1234567890')
        self.assertEqual(profile.skills, 'Python, Django, React')
