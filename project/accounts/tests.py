from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class AdminLoginTests(TestCase):
     # This test creates accounts 
    def setUp(self):
        """
        Create a staff user for testing.
        """
        self.staff_user = User.objects.create_user(
            username="admin",
            email="admin@test.com",
            password="password123",
            is_staff=True
        )

    # This test  the login feature with the correct details
    def test_valid_admin_login(self):
        """
        Test login with correct credentials.
        """
        response = self.client.post(
            reverse("accounts:admin_login"),
            {
                "email": "admin@test.com",
                "password": "password123"
            }
        )

        self.assertRedirects(response, "/admin/")

    # This test the login feature with correct email and wrong password
    def test_invalid_password(self):
        """
        Test login with wrong password.
        """
        response = self.client.post(
            reverse("accounts:admin_login"),
            {
                "email": "admin@test.com",
                "password": "wrongpassword"
            }
        )

        self.assertRedirects(response, "/")

    # This test the login feature with wrong email and correct password
    def test_invalid_email(self):
        """
        Test login with an email that does not exist.
        """
        response = self.client.post(
            reverse("accounts:admin_login"),
            {
                "email": "wrong@test.com",
                "password": "password123"
            }
        )

        self.assertRedirects(response, "/")

    #This test that Non-staff cannot be able to login
    def test_non_staff_user_cannot_login(self):
        """
        Test that non-staff users are not redirected to the admin.
        """
        User.objects.create_user(
            username="student",
            email="student@test.com",
            password="password123",
            is_staff=False
        )

        response = self.client.post(
            reverse("accounts:admin_login"),
            {
                "email": "student@test.com",
                "password": "password123"
            }
        )

        self.assertRedirects(response, "/")

    # This test that a session was created for the authenticated user
    def test_user_is_logged_in(self):
        response = self.client.post(
            reverse("accounts:admin_login"),
            {
                "email": "admin@test.com",
                "password": "password123",
            },
        )

        self.assertRedirects(response, "/admin/")

        user = response.wsgi_request.user
        self.assertTrue(user.is_authenticated)