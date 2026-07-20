
# Create your tests here.
from django.test import TestCase
from django.urls import reverse,resolve
from django.test import SimpleTestCase
from frontend.views import home

# Test that my homepage are been rendered properly
class HomePageTests(TestCase):

    def test_home_page_status_code(self):
        """
        Test that the home page loads successfully.
        """
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)

    def test_home_page_uses_correct_template(self):
        """
        Test that the correct template is rendered.
        """
        response = self.client.get(reverse("home"))
        self.assertTemplateUsed(response, "index.html")


#Test that my urls routing is correct
class FrontendURLTests(SimpleTestCase):

    def test_home_url_resolves(self):
        url = reverse("home")
        self.assertEqual(resolve(url).func, home)