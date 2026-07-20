from datetime import date
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase
from .models import Student,certificate
from django.contrib.auth.models import User
from unittest.mock import patch 


class StudentModelTests(TestCase):

    def setUp(self):
        """
        Create a sample student used by multiple tests.
        """
        self.student = Student.objects.create(
            full_name="John Doe",
            matric_number="21/D/csc/123",
            email="john@example.com",
            phone_number="08012345678",
            date_of_birth=date(2000, 1, 1),
            faculty="science",
            department="computer science",
            year_of_graduation=2024,
            graduation_date=date(2024, 11, 30),
        )

    def test_student_is_created(self):
        """
        Test that a student is successfully created.
        """
        self.assertEqual(Student.objects.count(), 1)

    def test_full_name_is_uppercase(self):
        """
        Full name should automatically be converted to uppercase.
        """
        self.assertEqual(self.student.full_name, "JOHN DOE")

    def test_faculty_is_uppercase(self):
        """
        Faculty should automatically be converted to uppercase.
        """
        self.assertEqual(self.student.faculty, "SCIENCE")

    def test_department_is_uppercase(self):
        """
        Department should automatically be converted to uppercase.
        """
        self.assertEqual(self.student.department, "COMPUTER SCIENCE")

    def test_matric_number_is_uppercase(self):
        """
        Matric number should automatically be converted to uppercase.
        """
        self.assertEqual(self.student.matric_number, "21/D/CSC/123")

    def test_duplicate_matric_number_not_allowed(self):
        """
        Matric numbers must be unique.
        """
        with self.assertRaises(IntegrityError):
            Student.objects.create(
                full_name="Jane Doe",
                matric_number="21/D/CSC/123",
                email="jane@example.com",
                phone_number="08099999999",
                date_of_birth=date(2001, 1, 1),
                faculty="Science",
                department="Physics",
                year_of_graduation=2025,
                graduation_date=date(2025, 11, 30),
            )

    def test_duplicate_email_not_allowed(self):
        """
        Student email must be unique.
        """
        with self.assertRaises(IntegrityError):
            Student.objects.create(
                full_name="Jane Doe",
                matric_number="22/CSC/5678",
                email="john@example.com",
                phone_number="08099999999",
                date_of_birth=date(2001, 1, 1),
                faculty="Science",
                department="Physics",
                year_of_graduation=2025,
                graduation_date=date(2025, 11, 30),
            )

    def test_invalid_matric_number_validation(self):
        """
        Invalid matric number should fail validation.
        """
        student = Student(
            full_name="Invalid Student",
            matric_number="INVALID123",
            email="invalid@example.com",
            phone_number="08012345670",
            date_of_birth=date(2000, 1, 1),
            faculty="Science",
            department="Chemistry",
            year_of_graduation=2024,
            graduation_date=date(2024, 11, 30),
        )

        with self.assertRaises(ValidationError):
            student.full_clean()

#----------------------------------------------------------------------------
# Testing the certificate logic
class CertificateModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="admin",
            password="password123"
        )

        self.student = Student.objects.create(
            full_name="John Doe",
            matric_number="21/CSC/1234",
            email="john@example.com",
            phone_number="08012345678",
            date_of_birth=date(2000, 1, 1),
            faculty="Science",
            department="Computer Science",
            year_of_graduation=2024,
            graduation_date=date(2024, 11, 30),
        )

    # I am using the patch because the generate gr_code and pdf will take a lot of time especially since i am using weasyprint.. so it best i simulate it or make a mock
    #First Certificate Test
    @patch("certificate.models.certificate.generate_qr_code")
    @patch("certificate.models.certificate.generate_certificate_pdf")
    def test_certificate_id_generated(self, mock_pdf, mock_qr):

        cert = certificate.objects.create(
            student=self.student,
            certificate_type="B.Sc.",
            classification="First Class Honours",
            date_of_issue=date.today(),
            created_by=self.user,
        )

        self.assertTrue(cert.certificate_id.startswith("CERT-"))


    # Tset automatic Course name
    @patch("certificate.models.certificate.generate_qr_code")
    @patch("certificate.models.certificate.generate_certificate_pdf")
    def test_course_name_auto_filled(self, mock_pdf, mock_qr):

        cert = certificate.objects.create(
            student=self.student,
            certificate_type="B.Sc.",
            classification="First Class Honours",
            date_of_issue=date.today(),
            created_by=self.user,
        )

        self.assertEqual(
            cert.course_name,
            self.student.department
        )

    #Test Verification Token
    @patch("certificate.models.certificate.generate_qr_code")
    @patch("certificate.models.certificate.generate_certificate_pdf")
    def test_verification_token_generated(self, mock_pdf, mock_qr):

        cert = certificate.objects.create(
            student=self.student,
            certificate_type="B.Sc.",
            classification="First Class Honours",
            date_of_issue=date.today(),
            created_by=self.user,
        )

        self.assertTrue(cert.verification_token)
        self.assertEqual(len(cert.verification_token), 64) # Ensures that the token always have 64 hexadecimal character

    # Test digital signature
    @patch("certificate.models.certificate.generate_qr_code")
    @patch("certificate.models.certificate.generate_certificate_pdf")
    def test_digital_signature_generated(self, mock_pdf, mock_qr):

        cert = certificate.objects.create(
            student=self.student,
            certificate_type="B.Sc.",
            classification="First Class Honours",
            date_of_issue=date.today(),
            created_by=self.user,
        )

        self.assertTrue(cert.digital_signature)
        self.assertEqual(len(cert.digital_signature), 64)  # always produces 64 hexadecimal character

#--------------------------------------------------------------------------------------

# Testing core Application Logic .... The verification Logic

class CertificateVerificationViewTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="admin",
            password="password123"
        )

        self.student = Student.objects.create(
            full_name="John Doe",
            matric_number="21/CSC/1234",
            email="john@example.com",
            phone_number="08012345678",
            date_of_birth=date(2000, 1, 1),
            faculty="Science",
            department="Computer Science",
            year_of_graduation=2024,
            graduation_date=date(2024, 11, 30),
        )

    # Testing verification using Certificate ID
    @patch("certificate.models.certificate.generate_qr_code")
    @patch("certificate.models.certificate.generate_certificate_pdf")
    def test_verify_valid_certificate_by_certificate_id(self, mock_pdf, mock_qr):

        cert = certificate.objects.create(
            student=self.student,
            certificate_type="B.Sc.",
            classification="First Class Honours",
            date_of_issue=date.today(),
            created_by=self.user,
        )

        response = self.client.post(
            "/verify-certificate/",
            {
                "cert_id": cert.certificate_id
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["status"], "valid")

    # Test Verification using Matric Number
    @patch("certificate.models.certificate.generate_qr_code")
    @patch("certificate.models.certificate.generate_certificate_pdf")
    def test_verify_valid_certificate_by_certificate_id(self, mock_pdf, mock_qr):

        cert = certificate.objects.create(
            student=self.student,
            certificate_type="B.Sc.",
            classification="First Class Honours",
            date_of_issue=date.today(),
            created_by=self.user,
        )

        response = self.client.post(
            "/verify-certificate/",
            {
                "cert_id": cert.certificate_id
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["status"], "valid")

    # Test Invalid Certificate
    @patch("certificate.models.certificate.generate_qr_code")
    @patch("certificate.models.certificate.generate_certificate_pdf")
    def test_verify_valid_certificate_by_matric_number(self, mock_pdf, mock_qr):

        certificate.objects.create(
            student=self.student,
            certificate_type="B.Sc.",
            classification="First Class Honours",
            date_of_issue=date.today(),
            created_by=self.user,
        )

        response = self.client.post(
            "/verify-certificate/",
            {
                "cert_id": "21/CSC/1234"
            }
        )

        self.assertEqual(response.context["status"], "valid")

    # Test the Tampered Certificate Verification
    @patch("certificate.models.certificate.generate_qr_code")
    @patch("certificate.models.certificate.generate_certificate_pdf")
    def test_tampered_certificate(self, mock_pdf, mock_qr):

        cert = certificate.objects.create(
            student=self.student,
            certificate_type="B.Sc.",
            classification="First Class Honours",
            date_of_issue=date.today(),
            created_by=self.user,
        )

        certificate.objects.filter(pk=cert.pk).update(
        digital_signature="123456789")


        response = self.client.post(
            "/verify-certificate/",
            {
                "cert_id": cert.certificate_id
            }
        )

        self.assertEqual(response.context["status"], "tampered")

#-------------------------------------------------------------------------------------------------------

# Testing Qr Code Verification
class QRVerificationTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="admin",
            password="password123"
        )

        self.student = Student.objects.create(
            full_name="John Doe",
            matric_number="21/CSC/1234",
            email="john@example.com",
            phone_number="08012345678",
            date_of_birth=date(2000, 1, 1),
            faculty="Science",
            department="Computer Science",
            year_of_graduation=2024,
            graduation_date=date(2024, 11, 30),
        )

    # Testing valid qr code
    @patch("certificate.models.certificate.generate_qr_code")
    @patch("certificate.models.certificate.generate_certificate_pdf")
    def test_valid_qr_verification(self, mock_pdf, mock_qr):

        cert = certificate.objects.create(
            student=self.student,
            certificate_type="B.Sc.",
            classification="First Class Honours",
            date_of_issue=date.today(),
            created_by=self.user,
        )

        response = self.client.get(
            f"/verify/{cert.certificate_id}/?token={cert.verification_token}"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["status"], "valid")
    
    # Testing Invalid Token
    @patch("certificate.models.certificate.generate_qr_code")
    @patch("certificate.models.certificate.generate_certificate_pdf")
    def test_invalid_qr_token(self, mock_pdf, mock_qr):

        cert = certificate.objects.create(
            student=self.student,
            certificate_type="B.Sc.",
            classification="First Class Honours",
            date_of_issue=date.today(),
            created_by=self.user,
        )

        response = self.client.get(
            f"/verify/{cert.certificate_id}/?token=INVALIDTOKEN"
        )

        self.assertEqual(response.context["status"], "not_found")

    # Testing Invalid Certificate Id
    def test_invalid_qr_certificate(self):

        response = self.client.get(
            "/verify/CERT-INVALID/?token=ABC123"
        )

        self.assertEqual(response.context["status"], "not_found")

    # Testing Tampered Certificate Via Qr
    @patch("certificate.models.certificate.generate_qr_code")
    @patch("certificate.models.certificate.generate_certificate_pdf")
    def test_tampered_qr_certificate(self, mock_pdf, mock_qr):

        cert = certificate.objects.create(
            student=self.student,
            certificate_type="B.Sc.",
            classification="First Class Honours",
            date_of_issue=date.today(),
            created_by=self.user,
        )

        certificate.objects.filter(pk=cert.pk).update(
            digital_signature="INVALIDHASH"
        )

        response = self.client.get(
            f"/verify/{cert.certificate_id}/?token={cert.verification_token}"
        )

        self.assertEqual(response.context["status"], "invalid")

    # Testing Verifies Certificate page opens correctly
    @patch("certificate.models.certificate.generate_qr_code")
    @patch("certificate.models.certificate.generate_certificate_pdf")
    def test_view_certificate(self, mock_pdf, mock_qr):

        cert = certificate.objects.create(
            student=self.student,
            certificate_type="B.Sc.",
            classification="First Class Honours",
            date_of_issue=date.today(),
            created_by=self.user,
        )

        response = self.client.get(
            f"/certificate/{cert.certificate_id}/"
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "certificate.html")
        self.assertEqual(response.context["Certificate"], cert)

    # Testing Ensures that Endpoint returns a PDF response
    @patch("certificate.views.HTML.write_pdf")
    @patch("certificate.models.certificate.generate_qr_code")
    @patch("certificate.models.certificate.generate_certificate_pdf")
    def test_download_certificate(
        self,
        mock_generate_pdf,
        mock_generate_qr,
        mock_write_pdf
    ):

        mock_write_pdf.return_value = b"Dummy PDF"

        cert = certificate.objects.create(
            student=self.student,
            certificate_type="B.Sc.",
            classification="First Class Honours",
            date_of_issue=date.today(),
            created_by=self.user,
        )

        response = self.client.get(
            f"/certificate/{cert.certificate_id}/download/"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/pdf")
    
    def test_student_string_representation(self):
        self.assertEqual(
            str(self.student),
            "JOHN DOE (21/CSC/1234)"
        )
    
    @patch("certificate.models.certificate.generate_qr_code")
    @patch("certificate.models.certificate.generate_certificate_pdf")
    def test_certificate_string_representation(
        self,
        mock_pdf,
        mock_qr
    ):

        cert = certificate.objects.create(
            student=self.student,
            certificate_type="B.Sc.",
            classification="First Class Honours",
            date_of_issue=date.today(),
            created_by=self.user,
        )

        expected = (
            "JOHN DOE - B.Sc. - First Class Honours"
        )

        self.assertEqual(str(cert), expected)