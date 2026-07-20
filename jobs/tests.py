from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from companies.models import Company
from jobs.models import Job, JobApplication, SavedJob

User = get_user_model()

class JobManagementAndWorkflowTests(TestCase):
    """
    Test suite covering Job CRUD, candidate applications, double application locks,
    resume uploads, saved job bookmarks, recruiter application status updates,
    and search & multi-parameter filtering engines.
    """

    def setUp(self):
        # Create Recruiter 1 & Company
        self.recruiter_1 = User.objects.create_user(
            username='recruiter1',
            email='recruiter1@example.com',
            password='Password123!',
            is_recruiter=True
        )
        self.company_1 = Company.objects.create(
            name='Stripe Inc.',
            description='Online payments platform.',
            location='San Francisco, CA',
            owner=self.recruiter_1
        )

        # Create Recruiter 2 & Company (for security checks)
        self.recruiter_2 = User.objects.create_user(
            username='recruiter2',
            email='recruiter2@example.com',
            password='Password123!',
            is_recruiter=True
        )
        self.company_2 = Company.objects.create(
            name='Google LLC',
            location='Mountain View, CA',
            owner=self.recruiter_2
        )

        # Create Candidate
        self.candidate = User.objects.create_user(
            username='candidate1',
            email='candidate1@example.com',
            password='Password123!',
            is_candidate=True
        )

        # Pre-create a Job listing
        self.job_1 = Job.objects.create(
            company=self.company_1,
            title='Senior Python Developer',
            category='development',
            job_type='full_time',
            experience_level='senior',
            location='San Francisco, CA',
            salary='$150,000 - $180,000 /yr',
            description='Looking for an experienced Python and Django developer.'
        )

    # -------------------------------------------------------------------------
    # STEP 4: JOB MANAGEMENT (CRUD) TESTS
    # -------------------------------------------------------------------------

    def test_job_board_list_and_details_views(self):
        """
        Verify jobs list page and single job details page render properly.
        """
        response_list = self.client.get(reverse('jobs'))
        self.assertEqual(response_list.status_code, 200)
        self.assertContains(response_list, 'Senior Python Developer')

        response_details = self.client.get(reverse('job_details', args=[self.job_1.id]))
        self.assertEqual(response_details.status_code, 200)
        self.assertContains(response_details, 'Senior Python Developer')
        self.assertContains(response_details, 'Stripe Inc.')

    def test_recruiter_create_job_posting(self):
        """
        Verify recruiters can publish new job vacancies for their company.
        """
        self.client.force_login(self.recruiter_1)
        response = self.client.post(reverse('job_posting'), {
            'company': self.company_1.id,
            'title': 'Frontend React Engineer',
            'category': 'design',
            'job_type': 'remote',
            'experience_level': 'mid',
            'location': 'Remote',
            'salary': '$120,000 /yr',
            'description': 'Building sleek user interfaces.',
        })
        self.assertRedirects(response, reverse('jobs'))
        self.assertTrue(Job.objects.filter(title='Frontend React Engineer').exists())
        created_job = Job.objects.get(title='Frontend React Engineer')
        self.assertEqual(created_job.company, self.company_1)

    def test_recruiter_edit_own_job_posting(self):
        """
        Verify job owner can update their job listing.
        """
        self.client.force_login(self.recruiter_1)
        response = self.client.post(reverse('edit_job', args=[self.job_1.id]), {
            'company': self.company_1.id,
            'title': 'Lead Python Architect',
            'category': 'development',
            'job_type': 'full_time',
            'experience_level': 'senior',
            'location': 'San Francisco, CA',
            'salary': '$200,000 /yr',
            'description': 'Updated job description text.',
        })
        self.assertRedirects(response, reverse('dashboard'))
        self.job_1.refresh_from_db()
        self.assertEqual(self.job_1.title, 'Lead Python Architect')

    def test_recruiter_delete_own_job_posting(self):
        """
        Verify job owner can delete a job vacancy.
        """
        self.client.force_login(self.recruiter_1)
        response = self.client.post(reverse('delete_job', args=[self.job_1.id]))
        self.assertRedirects(response, reverse('dashboard'))
        self.assertFalse(Job.objects.filter(id=self.job_1.id).exists())

    def test_unauthorized_recruiter_cannot_edit_or_delete_job(self):
        """
        Verify a recruiter cannot edit or delete a job belonging to another company owner.
        """
        self.client.force_login(self.recruiter_2)
        response_edit = self.client.post(reverse('edit_job', args=[self.job_1.id]), {
            'company': self.company_2.id,
            'title': 'Hacked Title',
        })
        self.assertRedirects(response_edit, reverse('dashboard'))
        self.job_1.refresh_from_db()
        self.assertEqual(self.job_1.title, 'Senior Python Developer')

        response_delete = self.client.post(reverse('delete_job', args=[self.job_1.id]))
        self.assertRedirects(response_delete, reverse('dashboard'))
        self.assertTrue(Job.objects.filter(id=self.job_1.id).exists())

    # -------------------------------------------------------------------------
    # STEP 5: CANDIDATE WORKFLOW TESTS
    # -------------------------------------------------------------------------

    def test_candidate_apply_for_job_with_resume(self):
        """
        Verify candidate can apply for a job with cover letter and resume document.
        """
        self.client.force_login(self.candidate)
        dummy_resume = SimpleUploadedFile('resume.pdf', b'PDF-dummy-content', content_type='application/pdf')

        response = self.client.post(reverse('apply_job', args=[self.job_1.id]), {
            'cover_letter': 'I am highly interested in this role.',
            'resume': dummy_resume
        })
        self.assertRedirects(response, reverse('dashboard'))
        self.assertTrue(JobApplication.objects.filter(job=self.job_1, applicant=self.candidate).exists())

    def test_prevent_duplicate_applications(self):
        """
        Verify double-submission lock prevents duplicate candidate applications.
        """
        # Create initial application
        JobApplication.objects.create(
            job=self.job_1,
            applicant=self.candidate,
            cover_letter='First application'
        )

        self.client.force_login(self.candidate)
        response = self.client.post(reverse('apply_job', args=[self.job_1.id]), {
            'cover_letter': 'Second application attempt'
        })
        self.assertRedirects(response, reverse('job_details', args=[self.job_1.id]))
        self.assertEqual(JobApplication.objects.filter(job=self.job_1, applicant=self.candidate).count(), 1)

    def test_candidate_saved_jobs_bookmarks(self):
        """
        Verify bookmarking, unbookmarking, and viewing saved jobs list.
        """
        self.client.force_login(self.candidate)

        # 1. Bookmark job
        response_save = self.client.get(reverse('save_job', args=[self.job_1.id]))
        self.assertTrue(SavedJob.objects.filter(user=self.candidate, job=self.job_1).exists())

        # 2. View saved jobs list page
        response_saved_list = self.client.get(reverse('saved_jobs'))
        self.assertEqual(response_saved_list.status_code, 200)
        self.assertContains(response_saved_list, 'Senior Python Developer')

        # 3. Unsave job
        response_unsave = self.client.get(reverse('remove_saved_job', args=[self.job_1.id]))
        self.assertFalse(SavedJob.objects.filter(user=self.candidate, job=self.job_1).exists())

    # -------------------------------------------------------------------------
    # STEP 6: RECRUITER WORKFLOW TESTS
    # -------------------------------------------------------------------------

    def test_recruiter_update_application_status(self):
        """
        Verify recruiter can view applications and update pipeline candidate status.
        """
        application = JobApplication.objects.create(
            job=self.job_1,
            applicant=self.candidate,
            cover_letter='Application text'
        )

        self.client.force_login(self.recruiter_1)

        # Check candidate application displays on recruiter dashboard
        response_dashboard = self.client.get(reverse('dashboard'))
        self.assertEqual(response_dashboard.status_code, 200)
        self.assertContains(response_dashboard, self.candidate.username)

        # Update candidate status to 'interview'
        response_status = self.client.post(reverse('update_application_status', args=[application.id]), {
            'status': 'interview'
        })
        self.assertRedirects(response_status, reverse('dashboard'))
        application.refresh_from_db()
        self.assertEqual(application.status, 'interview')

    # -------------------------------------------------------------------------
    # STEP 7: SEARCH & MULTI-PARAMETER FILTERS
    # -------------------------------------------------------------------------

    def test_search_and_filtering_engine(self):
        """
        Verify keyword search, category, location, job_type, and experience filters.
        """
        # Create secondary job for comparison
        Job.objects.create(
            company=self.company_2,
            title='Junior Data Analyst',
            category='marketing',
            job_type='part_time',
            experience_level='entry',
            location='New York, NY',
            salary='$80,000 /yr',
            description='SQL and Excel data modeling.'
        )

        # 1. Keyword search
        resp_q = self.client.get(reverse('jobs') + '?q=Python')
        self.assertContains(resp_q, 'Senior Python Developer')
        self.assertNotContains(resp_q, 'Junior Data Analyst')

        # 2. Location filter
        resp_loc = self.client.get(reverse('jobs') + '?location=New+York')
        self.assertContains(resp_loc, 'Junior Data Analyst')
        self.assertNotContains(resp_loc, 'Senior Python Developer')

        # 3. Category filter
        resp_cat = self.client.get(reverse('jobs') + '?category=development')
        self.assertContains(resp_cat, 'Senior Python Developer')
        self.assertNotContains(resp_cat, 'Junior Data Analyst')

        # 4. Job type filter
        resp_type = self.client.get(reverse('jobs') + '?job_type=part_time')
        self.assertContains(resp_type, 'Junior Data Analyst')
        self.assertNotContains(resp_type, 'Senior Python Developer')

        # 5. Experience level filter
        resp_exp = self.client.get(reverse('jobs') + '?experience_level=senior')
        self.assertContains(resp_exp, 'Senior Python Developer')
        self.assertNotContains(resp_exp, 'Junior Data Analyst')
